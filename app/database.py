"""数据库接入层：全项目唯一的 engine / Session / 依赖注入。

历史上这里有两套引擎（SQLAlchemy declarative_base 一套、SQLModel 一套）指向同一个
SQLite 文件，现已统一为下面的单一引擎。
"""

from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine, text

from app.config import DATABASE_URL

# 全项目唯一引擎。SQLite 默认禁止跨线程复用连接，FastAPI 的线程池需要放开该限制。
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 供脚本 / 后台任务直接开 Session 使用；请求内请优先用 get_session 依赖
SessionLocal = Session


def get_session() -> Iterator[Session]:
    """FastAPI 依赖：每个请求一个 Session，退出时自动关闭。"""
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """按模型定义建表（已存在的表不会被改动）。"""
    # 必须在此处导入，确保所有 table=True 的模型都已注册到 SQLModel.metadata
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)

    # 🌟 兼容性热修复：安全检查并自动为旧版 staffuser 表补齐 permissions_json 字段
    with engine.connect() as conn:
        try:
            result = conn.exec_driver_sql("PRAGMA table_info(staffuser);").fetchall()
            if result:
                columns = [row[1] for row in result]
                if "permissions_json" not in columns:
                    conn.exec_driver_sql("ALTER TABLE staffuser ADD COLUMN permissions_json TEXT DEFAULT '[]';")
                    conn.commit()
                    print("✅ 成功为旧版 staffuser 表自动补齐 permissions_json 字段！")
        except Exception as e:
            print(f"⚠️ 自动迁移字段提示: {e}")