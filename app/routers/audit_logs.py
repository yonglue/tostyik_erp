"""审计日志查询。"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models import AuditLog
from app.deps import Actor, require_admin # 🌟 引入权限依赖

router = APIRouter(tags=["审计"])


@router.get("/api/audit-logs")
def get_audit_logs(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(100, ge=1, le=500, description="每页数量"),
    actor: Actor = Depends(require_admin), # 🌟 加上门禁，仅管理员可看
    session: Session = Depends(get_session)
):
    # 获取总数
    total = len(session.exec(select(AuditLog)).all())
    # 获取分页数据
    logs = session.exec(
        select(AuditLog).order_by(AuditLog.id.desc()).offset(skip).limit(limit)
    ).all()
    
    return {
        "total": total,
        "data": logs
    }