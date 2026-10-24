"""系统设置：公司抬头配置 / 数据清理与一键归档 / 汇率配置。"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, text

from app.database import get_session, engine
from app.deps import Actor, get_current_actor, RequirePermission
from app.services.audit import log_action
from app.services.config_service import get_system_settings
from app.models import SystemSettings

router = APIRouter(tags=["系统设置"])

class SystemSettingsPayload(BaseModel):
    company_name: str
    rif: str
    address: str
    phone: str
    email: Optional[str] = ""

class BcvRatePayload(BaseModel):
    rate: float

@router.get("/api/settings")
def get_settings(
    session: Session = Depends(get_session),
    actor: Actor = Depends(get_current_actor)
):
    """获取当前系统抬头配置。"""
    settings = get_system_settings(session)
    # 返回字典格式兼容前端
    return {
        "company_name": settings.company_name,
        "rif": settings.rif,
        "address": settings.address,
        "phone": settings.phone,
        "email": settings.email,
        "bcv_rate": settings.bcv_rate
    }

@router.post("/api/settings")
def update_settings(
    payload: SystemSettingsPayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("settings:manage"))
):
    """更新系统抬头配置。"""
    settings = get_system_settings(session)
    settings.company_name = payload.company_name
    settings.rif = payload.rif
    settings.address = payload.address
    settings.phone = payload.phone
    settings.email = payload.email
    session.add(settings)
    session.commit()

    log_action(session=session, username=actor.username, role=actor.role, action="UPDATE_SETTINGS",
               details=f"更新系统公司抬头配置: {settings.company_name}")
    return {"status": "success", "message": "系统抬头配置已保存"}

@router.get("/api/settings/bcv-rate")
def get_bcv_rate(session: Session = Depends(get_session)):
    settings = get_system_settings(session)
    return {"rate": settings.bcv_rate}

@router.post("/api/settings/bcv-rate")
def update_bcv_rate(
    payload: BcvRatePayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    settings = get_system_settings(session)
    settings.bcv_rate = round(payload.rate, 2)
    session.add(settings)
    session.commit()
    
    log_action(session=session, username=actor.username, role=actor.role, action="UPDATE_BCV",
               details=f"手动更新汇率为: {settings.bcv_rate}")
    return {"status": "success", "rate": settings.bcv_rate}

@router.post("/api/settings/cleanup")
def cleanup_database(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("db:maintenance"))
):
    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text("VACUUM;"))
        log_action(session=session, username=actor.username, role=actor.role, action="DB_CLEANUP",
                   details="执行数据库 VACUUM 空间清理与碎片整理")
        return {"status": "success", "message": "数据库清理成功！"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库清理失败: {str(e)}")