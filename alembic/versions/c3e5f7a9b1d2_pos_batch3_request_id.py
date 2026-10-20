"""pos batch3: orders.request_id idempotency key

Revision ID: c3e5f7a9b1d2
Revises: b7d2e4f6a8c1
Create Date: 2026-10-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3e5f7a9b1d2"
down_revision: Union[str, Sequence[str], None] = "b7d2e4f6a8c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    全新数据库上 bootstrap() 先跑迁移、再 create_all()，因此表不存在时跳过；
    已有数据库补列并建立唯一索引。SQLite 的唯一索引允许多个 NULL，
    历史订单没有 request_id 也不会互相冲突。
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("orders"):
        return

    columns = {c["name"] for c in inspector.get_columns("orders")}
    if "request_id" not in columns:
        op.add_column(
            "orders",
            sa.Column("request_id", sa.String(length=64), nullable=True),
        )

    indexes = {ix["name"] for ix in inspector.get_indexes("orders")}
    if "ix_orders_request_id" not in indexes:
        op.create_index(
            "ix_orders_request_id",
            "orders",
            ["request_id"],
            unique=True,
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("orders"):
        return

    indexes = {ix["name"] for ix in inspector.get_indexes("orders")}
    if "ix_orders_request_id" in indexes:
        op.drop_index("ix_orders_request_id", table_name="orders")

    columns = {c["name"] for c in inspector.get_columns("orders")}
    if "request_id" in columns:
        op.drop_column("orders", "request_id")
