"""员工账号与细粒度权限管理路由。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
import json

from app.database import get_session
from app.models import StaffUser
from app.deps import require_admin, Actor
from app.security import hash_password  # 👈 这里由 get_password_hash 改为 hash_password

router = APIRouter(prefix="/api/staff", tags=["Staff Management"])

class StaffCreatePayload(BaseModel):
    username: str
    password: str
    role: Optional[str] = "staff"
    permissions: Optional[List[str]] = []


@router.get("")
def get_staff_list(
    session: Session = Depends(get_session),
    actor: Actor = Depends(require_admin)
):
    """获取所有店员/收银员账号列表（含权限）。"""
    staffs = session.exec(select(StaffUser)).all()
    result = []
    for s in staffs:
        try:
            perms = json.loads(s.permissions_json)
        except Exception:
            perms = []
        result.append({
            "id": s.id,
            "username": s.username,
            "role": s.role,
            "permissions": perms,
            "created_at": s.created_at
        })
    return result


@router.post("")
def create_staff(
    payload: StaffCreatePayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(require_admin)
):
    """创建新员工账号并赋予细粒度权限。"""
    existing = session.exec(select(StaffUser).where(StaffUser.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="该用户名已存在")

    hashed_pw = hash_password(payload.password)  # 👈 使用正确的函数名
    new_staff = StaffUser(
        username=payload.username,
        password_hash=hashed_pw,
        role=payload.role or "staff",
        permissions_json=json.dumps(payload.permissions or [])
    )
    session.add(new_staff)
    session.commit()
    session.refresh(new_staff)
    return {"status": "success", "id": new_staff.id, "username": new_staff.username}


@router.delete("/{staff_id}")
def delete_staff(
    staff_id: int,
    session: Session = Depends(get_session),
    actor: Actor = Depends(require_admin)
):
    """删除指定员工账号。"""
    staff = session.get(StaffUser, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="员工账号不存在")
    
    session.delete(staff)
    session.commit()
    return {"status": "success", "deleted_id": staff_id}