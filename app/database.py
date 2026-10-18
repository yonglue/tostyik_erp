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
    print("✅ 数据库表结构检查与初始化完成。")

    # 🌟 强制自动补全 shift_records 表的所有拆分字段
    with engine.connect() as conn:
        try:
            # 如果表根本不存在，create_all 已经建了。如果表存在但缺列，这里强制补齐。
            conn.exec_driver_sql("PRAGMA table_info(shift_records);")
            columns = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(shift_records);").fetchall()]
            print(f"📊 当前 shift_records 表的字段有: {columns}")

            columns_to_add = {
                "system_zelle_usd": "FLOAT DEFAULT 0.0",
                "system_pagomovil_usd": "FLOAT DEFAULT 0.0",
                "system_debt_usd": "FLOAT DEFAULT 0.0",
                "notes": "TEXT DEFAULT ''"
            }
            for col_name, col_type in columns_to_add.items():
                if col_name not in columns:
                    conn.exec_driver_sql(f"ALTER TABLE shift_records ADD COLUMN {col_name} {col_type};")
                    conn.commit()
                    print(f"✅ [自动迁移成功] 已为 shift_records 表补齐字段: {col_name}")
        except Exception as e:
            print(f"⚠️ shift_records 自动迁移异常: {e}")