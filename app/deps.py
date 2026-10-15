"""FastAPI 依赖：从 Authorization: Bearer <token> 解析当前操作人。"""

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException

from app.security import decode_access_token


@dataclass
class Actor:
    """当前请求的操作人身份。"""
    username: str
    role: str


def get_current_actor(authorization: str = Header(default="")) -> Actor:
    """解析并校验访问令牌；无效则 401。"""
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="未登录或缺少访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(authorization[7:].strip())
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="访问令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Actor(username=payload["sub"], role=payload.get("role", "staff"))


def require_admin(actor: Actor = Depends(get_current_actor)) -> Actor:
    """要求管理员及以上角色，否则 403。"""
    if actor.role not in ("super_admin", "admin"):
        raise HTTPException(status_code=403, detail="无权执行此操作")
    return actor
