from sqlmodel import Session
from app.models import SystemSettings
from app.database import engine

def get_system_settings(session: Session = None) -> SystemSettings:
    """获取系统配置，如果没有则初始化默认配置（单行表）。"""
    if session is not None:
        settings = session.get(SystemSettings, 1)
        if not settings:
            settings = SystemSettings(id=1)
            session.add(settings)
            session.commit()
            session.refresh(settings)
        return settings
    else:
        with Session(engine) as new_session:
            return get_system_settings(new_session)