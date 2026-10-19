"""FastAPI 依赖：从 Authorization: Bearer <token> 解析当前操作人与细粒度权限校验。"""

from dataclasses import dataclass
from typing import List, Optional
import json
import logging

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from app.security import decode_access_token
from app.database import get_session
from app.models import StaffUser, AdminUser

logger = logging.getLogger(__name__)

@dataclass
class Actor:
    """当前请求的操作人身份。"""
    username: str
    role: str
    permissions: List[str]


def get_current_actor(
    authorization: str = Header(default=""),
    session: Session = Depends(get_session)
) -> Actor:
    """解析并校验访问令牌；无效则 401，并从数据库加载其最新细粒度权限。"""
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
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="非法令牌载荷")

    # 🌟 核心修复：实时查库，不信任 Token 中的 role
    admin = session.exec(select(AdminUser).where(AdminUser.username == username)).first()
    staff = session.exec(select(StaffUser).where(StaffUser.username == username)).first()

    # 🌟 修复幽灵账号：如果数据库里没这号人，说明被删了，直接拦截！
    if not admin and not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="账号不存在或已被禁用，请重新登录"
        )

    # 管理员逻辑
    if admin:
        return Actor(username=admin.username, role=admin.role, permissions=["*"])

    # 员工逻辑
    permissions = []
    try:
        permissions = json.loads(staff.permissions_json)
    except Exception as e:
        logger.error(f"解析员工 {username} 的权限 JSON 失败: {e}")
        permissions = []

    return Actor(username=staff.username, role=staff.role, permissions=permissions)


def require_admin(actor: Actor = Depends(get_current_actor)) -> Actor:
    """要求管理员及以上角色，否则 403。"""
    if actor.role not in ("super_admin", "admin"):
        raise HTTPException(status_code=403, detail="无权执行此操作")
    return actor


class RequirePermission:
    """细粒度权限校验依赖类。"""
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, actor: Actor = Depends(get_current_actor)) -> Actor:
        if actor.role in ("super_admin", "admin") or "*" in actor.permissions:
            return actor
            
        if self.required_permission not in actor.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 [{self.required_permission}] 操作权限"
            )
        return actor