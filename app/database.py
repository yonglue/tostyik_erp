"""数据库接入层：全项目唯一的 engine / Session / 依赖注入。"""

from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine
from app.config import DATABASE_URL

# 全项目唯一引擎。SQLite 默认禁止跨线程复用连接，FastAPI 的线程池需要放开该限制。
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = Session


def get_session() -> Iterator[Session]:
    """FastAPI 依赖：每个请求一个 Session，退出时自动关闭。"""
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """按模型定义建表（已存在的表不会被改动）。
    
    🌟 注意：现在新增或修改字段，请使用 Alembic 命令行生成迁移脚本，
    不再在此处写 ALTER TABLE 强行补字段。
    """
    # 必须在此处导入，确保所有 table=True 的模型都已注册到 SQLModel.metadata
    from app import models  # noqa: F401

    # 保留 create_all 作为兜底，防止全新的空数据库无法初始化
    SQLModel.metadata.create_all(engine)
    print("✅ 数据库表结构初始化完成 (由 SQLModel 接管)。")