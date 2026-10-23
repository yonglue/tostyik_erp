"""add_store_name_to_clients

Revision ID: a6950b8ba2e1
Revises: c2d3e4f5a6b7
Create Date: 2026-10-23 15:23:10.578697

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6950b8ba2e1'
down_revision: Union[str, Sequence[str], None] = 'c2d3e4f5a6b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy import inspect
    import sqlalchemy as sa
    bind = op.get_bind()
    
    # 🌟 自动识别真实的表名（兼容单数 client 或复数 clients）
    tables = inspect(bind).get_table_names()
    table_name = "client" if "client" in tables else ("clients" if "clients" in tables else None)
    
    if table_name:
        cols = {c["name"] for c in inspect(bind).get_columns(table_name)}
        if "store_name" not in cols:
            op.add_column(table_name, sa.Column("store_name", sa.String(), nullable=True))
            print(f"✅ 成功为表 {table_name} 添加了 store_name 字段！")
        else:
            print(f"⏭️ 表 {table_name} 中已存在 store_name 字段，跳过。")
    else:
        print("⚠️ 找不到名为 client 或 clients 的表，请检查数据库！")


def downgrade() -> None:
    """Downgrade schema."""
    pass
