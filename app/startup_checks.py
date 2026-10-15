"""启动安全自检。

目标：把"仍在用出厂弱默认值"这件事**显式喊出来**，而不是静默带病上线。

* 默认只告警（不打断开发/Migration 场景）
* 设置 `TK_STRICT_SECURITY=1` 后改为拒绝启动，适合公网部署
"""

from app.config import (
    ADMIN_PASSWORD_IS_EXPLICIT,
    JWT_SECRET_SOURCE,
    MASTER_PIN_IS_EXPLICIT,
    MASTER_SECURITY_PIN,
    STRICT_SECURITY,
    WEAK_DEFAULTS,
)

_BANNER = "=" * 68


def config_warnings() -> list[str]:
    """仅依赖配置（不查库）的弱凭据检查。"""
    warnings: list[str] = []

    if MASTER_SECURITY_PIN == WEAK_DEFAULTS["TK_MASTER_PIN"]:
        source = "在 .env / 环境变量中显式保留" if MASTER_PIN_IS_EXPLICIT else "代码默认值"
        warnings.append(
            f"管理员密码重置密钥仍是出厂值 "
            f"{WEAK_DEFAULTS['TK_MASTER_PIN']!r}（来源：{source}）。"
            "任何人拿到它都能把 admin 密码重置掉 → 请设置 TK_MASTER_PIN。"
        )

    if not ADMIN_PASSWORD_IS_EXPLICIT:
        warnings.append(
            f"未设置 TK_ADMIN_PASSWORD，新建数据库时会使用出厂密码 "
            f"{WEAK_DEFAULTS['TK_ADMIN_PASSWORD']!r}。"
        )

    if JWT_SECRET_SOURCE.startswith("新生成") or JWT_SECRET_SOURCE.startswith("本地密钥文件"):
        warnings.append(
            f"访问令牌密钥来自 {JWT_SECRET_SOURCE} —— 当前实例自身是安全的，"
            "但多实例部署需共享同一个 TK_JWT_SECRET，否则令牌互相不认。"
        )

    return warnings


def report(warnings: list[str]) -> None:
    """打印自检结果；严格模式下有告警就直接拒绝启动。"""
    if not warnings:
        print("🔒 安全自检通过：未检测到弱默认凭据。")
        return

    print()
    print(_BANNER)
    print("⚠️  安全自检发现 %d 项需要处理：" % len(warnings))
    for i, w in enumerate(warnings, 1):
        print(f"  {i}. {w}")
    print()
    print("  参考：cp .env.example .env 后填入强随机值；")
    print("       改管理员密码：.venv/bin/python scripts/set_admin_password.py")
    print(_BANNER)
    print()

    if STRICT_SECURITY:
        raise RuntimeError(
            "TK_STRICT_SECURITY=1 且存在弱默认凭据，已拒绝启动。"
            "请先处理上述告警，或关闭严格模式。"
        )
