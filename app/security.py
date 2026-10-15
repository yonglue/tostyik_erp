"""凭据哈希与访问令牌。

全部使用标准库实现，不引入额外依赖：
* 密码派生用 hashlib.scrypt（内存硬，抗 GPU 暴力破解），每个用户独立随机盐。
* 访问令牌用 HMAC-SHA256 签名的精简 JWT（HS256）。

签名密钥的解析（环境变量 → .jwt_secret 文件 → 自动生成）统一在 app/config.py 完成，
这里只消费最终结果，避免出现"忘了配环境变量就用上可预测密钥"的情况。
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from app.config import JWT_SECRET

TOKEN_TTL_MINUTES: int = int(os.getenv("TK_TOKEN_TTL_MINUTES", str(60 * 12)))

_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2 ** 14, 8, 1
_SCRYPT_PREFIX = "scrypt"


# ──────────────────────────── 基础编码 ────────────────────────────
def _b64e(raw: bytes) -> str:
    """URL 安全 base64，去掉末尾填充。"""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(txt: str) -> bytes:
    return base64.urlsafe_b64decode(txt + "=" * (-len(txt) % 4))


# ──────────────────────────── 密码哈希 ────────────────────────────
def hash_password(raw_password: str) -> str:
    """生成 scrypt 哈希，格式：scrypt$N$r$p$盐$哈希。"""
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(
        raw_password.encode(), salt=salt,
        n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=32,
    )
    return f"{_SCRYPT_PREFIX}${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${_b64e(salt)}${_b64e(dk)}"


def _verify_scrypt(raw_password: str, stored: str) -> bool:
    try:
        _, n, r, p, salt_b64, hash_b64 = stored.split("$")
        dk = hashlib.scrypt(
            raw_password.encode(), salt=_b64d(salt_b64),
            n=int(n), r=int(r), p=int(p), dklen=32,
        )
        return hmac.compare_digest(dk, _b64d(hash_b64))
    except Exception:
        return False


def verify_password(raw_password: str, password_hash: str) -> bool:
    """校验密码。兼容迁移前遗留的无盐 SHA-256 哈希。"""
    if not password_hash:
        return False
    if password_hash.startswith(_SCRYPT_PREFIX + "$"):
        return _verify_scrypt(raw_password, password_hash)
    # 存量 SHA-256（无盐）——只为平滑迁移保留，登录成功后会被就地升级
    return hmac.compare_digest(
        hashlib.sha256(raw_password.encode()).hexdigest(), password_hash
    )


def needs_rehash(password_hash: str) -> bool:
    """判断该哈希是否还是旧的弱算法（登录成功后可调用 hash_password 重写）。"""
    return not password_hash.startswith(_SCRYPT_PREFIX + "$")


# ──────────────────────────── 访问令牌 ────────────────────────────
def create_access_token(username: str, role: str, ttl_minutes: int | None = None) -> str:
    """签发 HS256 令牌。"""
    ttl = TOKEN_TTL_MINUTES if ttl_minutes is None else ttl_minutes
    payload = {"sub": username, "role": role, "exp": int(time.time()) + ttl * 60}
    body = _b64e(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode())
    sig = _b64e(hmac.new(JWT_SECRET.encode(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


def decode_access_token(token: str) -> dict | None:
    """校验签名与有效期，失败返回 None。"""
    try:
        body, sig = token.split(".")
        expected = _b64e(hmac.new(JWT_SECRET.encode(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_b64d(body))
        if int(payload.get("exp", 0)) < time.time():
            return None
        return payload
    except Exception:
        return None
