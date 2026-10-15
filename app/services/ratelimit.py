"""敏感接口的内存级防爆破限流（滑动窗口 + 锁定）。

设计取舍
--------
* **零依赖**：标准库 `threading` + `time.monotonic` 实现，不引入 slowapi/redis。
* **单进程有效**：状态存在进程内存里，因此只对"单 worker 运行"的部署成立。
  若日后用 `uvicorn --workers N` 或多副本部署，需要把 `_buckets` 换成 Redis，
  否则每个 worker 各算各的，限流强度会被放大 N 倍。
* FastAPI 的同步路由跑在线程池里，所以所有读写都加了锁。
* `time.monotonic()` 不受系统改时间影响。
"""

import threading
import time

from app.config import LOGIN_LOCKOUT_SECONDS, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS

# 桶数量上限：超过后清理过期条目，避免被大量不同 key 撑爆内存
_DEFAULT_MAX_KEYS = 20_000


class SlidingWindowLimiter:
    """同一 key 在 window 秒内失败达到 max_attempts 次，就锁定 lockout 秒。"""

    def __init__(
        self,
        max_attempts: int,
        window_seconds: int,
        lockout_seconds: int,
        max_keys: int = _DEFAULT_MAX_KEYS,
    ) -> None:
        self.max_attempts = max(1, max_attempts)
        self.window_seconds = max(1, window_seconds)
        self.lockout_seconds = max(1, lockout_seconds)
        self.max_keys = max_keys
        self._lock = threading.Lock()
        # key -> {"failures": [时间戳...], "locked_until": 时间戳}
        self._buckets: dict[str, dict] = {}

    # ── 查询 ──
    def retry_after(self, key: str) -> int:
        """返回还需等待的秒数；0 表示当前允许尝试。"""
        now = time.monotonic()
        with self._lock:
            bucket = self._buckets.get(key)
            if not bucket:
                return 0
            if bucket["locked_until"] > now:
                return int(bucket["locked_until"] - now) + 1
            return 0

    # ── 记录 ──
    def record_failure(self, key: str) -> int:
        """记一次失败，返回剩余可尝试次数（0 表示本次已触发锁定）。"""
        now = time.monotonic()
        with self._lock:
            self._evict_if_needed(now)
            bucket = self._buckets.setdefault(key, {"failures": [], "locked_until": 0.0})
            bucket["failures"] = [
                ts for ts in bucket["failures"] if now - ts < self.window_seconds
            ]
            bucket["failures"].append(now)

            if len(bucket["failures"]) >= self.max_attempts:
                bucket["locked_until"] = now + self.lockout_seconds
                bucket["failures"] = []
                return 0
            return self.max_attempts - len(bucket["failures"])

    def reset(self, key: str) -> None:
        """登录成功等场景：清空该 key 的失败记录。"""
        with self._lock:
            self._buckets.pop(key, None)

    def clear(self) -> None:
        """清空全部状态（供测试使用）。"""
        with self._lock:
            self._buckets.clear()

    # ── 维护 ──
    def _evict_if_needed(self, now: float) -> None:
        """调用方必须已持有锁。"""
        if len(self._buckets) <= self.max_keys:
            return
        stale = [
            k for k, b in self._buckets.items()
            if b["locked_until"] < now
            and (not b["failures"] or now - max(b["failures"]) > self.window_seconds)
        ]
        for k in stale:
            self._buckets.pop(k, None)
        # 仍然超限（说明全是活跃桶）时，退化为清空最旧的一半，保证内存可控
        if len(self._buckets) > self.max_keys:
            for k in list(self._buckets)[: self.max_keys // 2]:
                self._buckets.pop(k, None)

    def stats(self) -> dict:
        """仅供诊断/测试使用。"""
        with self._lock:
            now = time.monotonic()
            return {
                "keys": len(self._buckets),
                "locked": sum(1 for b in self._buckets.values() if b["locked_until"] > now),
            }


def _from_config() -> SlidingWindowLimiter:
    return SlidingWindowLimiter(
        max_attempts=LOGIN_MAX_ATTEMPTS,
        window_seconds=LOGIN_WINDOW_SECONDS,
        lockout_seconds=LOGIN_LOCKOUT_SECONDS,
    )


# 登录：按 (客户端 IP + 账号) 维度计数，避免只盯 IP 时误伤同一出口 IP 的其他用户
login_limiter = _from_config()
# 管理员密码重置：该接口只有 PIN、没有账号维度，故按 IP 计数
reset_pin_limiter = _from_config()

