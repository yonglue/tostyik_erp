"""数据库接入层：全项目唯一的 engine / Session / 依赖注入。"""

from typing import Iterator
from app.config import DATABASE_URL, AUTO_CREATE_TABLES

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

    🌟 新增或修改字段请用 Alembic，不再在此处写 ALTER TABLE。
    """
    # 必须在此处导入，确保所有 table=True 的模型都已注册到 SQLModel.metadata
    from app import models  # noqa: F401

    if not AUTO_CREATE_TABLES:
        print("⏭️  TK_AUTO_CREATE_TABLES=0，已跳过 create_all（表结构由 Alembic 管理）。")
        return

    SQLModel.metadata.create_all(engine)
    print("✅ 数据库表结构初始化完成 (由 SQLModel 接管)。")