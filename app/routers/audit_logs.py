"""审计日志查询。"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import AuditLog

router = APIRouter(tags=["审计"])


@router.get("/api/audit-logs")
def get_audit_logs(session: Session = Depends(get_session)):
    return session.exec(select(AuditLog).order_by(AuditLog.id.desc()).limit(100)).all()
