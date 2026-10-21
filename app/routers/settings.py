"""系统设置：公司抬头配置 / 数据清理与一键归档 / 汇率配置。"""

import json
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select, text

from app.config import DB_PATH
from app.database import get_session, engine
from app.deps import Actor, get_current_actor, RequirePermission
from app.services.audit import log_action

router = APIRouter(tags=["系统设置"])

SETTINGS_FILE = os.path.join(os.path.dirname(DB_PATH), "system_settings.json")

DEFAULT_SETTINGS = {
    "company_name": "TOSTIYK (TK) - AUTOPARTES VENEZUELA",
    "rif": "J-00000000-0",
    "address": "Valera, Estado Trujillo, Venezuela",
    "phone": "+58 412-0000000",
    "email": "tostiyk.ventas@gmail.com",
    "bcv_rate": 36.50, # 🌟 新增：默认汇率
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_SETTINGS

def save_settings(data: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class SystemSettingsPayload(BaseModel):
    company_name: str
    rif: str
    address: str
    phone: str
    email: Optional[str] = ""

# 🌟 新增：汇率载荷
class BcvRatePayload(BaseModel):
    rate: float


@router.get("/api/settings")
def get_system_settings(actor: Actor = Depends(get_current_actor)):
    """获取当前系统抬头配置（需要登录）。"""
    return load_settings()


@router.post("/api/settings")
def update_system_settings(
    payload: SystemSettingsPayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("settings:manage"))
):
    """更新系统抬头配置（需要 settings:manage 细粒度权限）。"""
    current_settings = load_settings()
    new_data = {**current_settings, **payload.model_dump()}
    save_settings(new_data)

    log_action(session=session, username=actor.username, role=actor.role, action="UPDATE_SETTINGS",
               details=f"更新系统公司抬头配置: {new_data.get('company_name')}")
    return {"status": "success", "message": "系统抬头配置已保存"}


# 🌟 新增：获取和保存汇率的接口
@router.get("/api/settings/bcv-rate")
def get_saved_bcv_rate():
    settings = load_settings()
    return {"rate": settings.get("bcv_rate", 36.50)}

@router.post("/api/settings/bcv-rate")
def update_bcv_rate(
    payload: BcvRatePayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access")) # 有收银权限的人就可以改
):
    settings = load_settings()
    settings["bcv_rate"] = round(payload.rate, 2)
    save_settings(settings)
    
    log_action(session=session, username=actor.username, role=actor.role, action="UPDATE_BCV",
               details=f"手动更新汇率为: {settings['bcv_rate']}")
    return {"status": "success", "rate": settings["bcv_rate"]}


@router.post("/api/settings/cleanup")
def cleanup_database(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("db:maintenance"))
):
    # ... 数据库清理逻辑保持不变 ...
    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text("VACUUM;"))
        log_action(session=session, username=actor.username, role=actor.role, action="DB_CLEANUP",
                   details="执行数据库 VACUUM 空间清理与碎片整理")
        return {"status": "success", "message": "数据库清理与空间优化（VACUUM）已成功完成！"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库清理失败: {str(e)}")