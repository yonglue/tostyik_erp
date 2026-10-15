"""FastAPI 依赖：从 Authorization: Bearer <token> 解析当前操作人与细粒度权限校验。"""

from dataclasses import dataclass
from typing import List, Optional
import json

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from app.security import decode_access_token
from app.database import get_session
from app.models import StaffUser, AdminUser


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
    role = payload.get("role", "staff")
    permissions = []

    # 如果是超级管理员，赋予全部虚拟权限
    if role in ("super_admin", "admin"):
        permissions = ["*"]
    else:
        # 从数据库加载 staff 用户的细粒度权限
        staff = session.exec(select(StaffUser).where(StaffUser.username == username)).first()
        if staff:
            try:
                permissions = json.loads(staff.permissions_json)
            except Exception:
                permissions = []

    return Actor(username=username, role=role, permissions=permissions)


def require_admin(actor: Actor = Depends(get_current_actor)) -> Actor:
    """要求管理员及以上角色，否则 403。"""
    if actor.role not in ("super_admin", "admin"):
        raise HTTPException(status_code=403, detail="无权执行此操作")
    return actor


class RequirePermission:
    """细粒度权限校验依赖类。
    
    用法示例：
        @router.post("/api/settings")
        def update_settings(actor: Actor = Depends(RequirePermission("settings:manage"))):
            ...
    """
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, actor: Actor = Depends(get_current_actor)) -> Actor:
        # 超级管理员 / 管理员默认拥有所有权限
        if actor.role in ("super_admin", "admin") or "*" in actor.permissions:
            return actor
            
        # 校验用户权限列表中是否包含所需权限
        if self.required_permission not in actor.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 [{self.required_permission}] 操作权限"
            )
        return actor