"""pos batch2: orders.client_id + legacy refund transaction type cleanup

Revision ID: b7d2e4f6a8c1
Revises: 9f3c1a7b2d4e
Create Date: 2026-10-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7d2e4f6a8c1"
down_revision: Union[str, Sequence[str], None] = "9f3c1a7b2d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    全新数据库上 bootstrap() 会先跑迁移、再执行 create_all()，因此每一步都
    先检查表/列是否存在；已有数据库则补列、补索引并清理历史退款流水类型。
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("orders"):
        columns = {c["name"] for c in inspector.get_columns("orders")}
        if "client_id" not in columns:
            op.add_column("orders", sa.Column("client_id", sa.Integer(), nullable=True))
        indexes = {ix["name"] for ix in inspector.get_indexes("orders")}
        if "ix_orders_client_id" not in indexes:
            op.create_index("ix_orders_client_id", "orders", ["client_id"])

    if inspector.has_table("inventorytransaction"):
        # 历史退款流水是 type='IN' + 前缀；统一迁移成独立类型，报表才能净额扣减。
        op.execute(
            sa.text(
                "UPDATE inventorytransaction "
                "SET type = 'REFUND' "
                "WHERE type = 'IN' AND customer_or_supplier LIKE '退货回滚-%'"
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("orders"):
        indexes = {ix["name"] for ix in inspector.get_indexes("orders")}
        if "ix_orders_client_id" in indexes:
            op.drop_index("ix_orders_client_id", table_name="orders")
        columns = {c["name"] for c in inspector.get_columns("orders")}
        if "client_id" in columns:
            op.drop_column("orders", "client_id")
