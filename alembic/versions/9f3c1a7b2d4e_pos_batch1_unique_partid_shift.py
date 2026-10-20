"""pos batch1: autopart (oem, brand) unique, order_items.part_id, shift card/cash columns

Revision ID: 9f3c1a7b2d4e
Revises: 082a363b8b44
Create Date: 2026-10-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3c1a7b2d4e"
down_revision: Union[str, Sequence[str], None] = "082a363b8b44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_SHIFT_COLUMNS = (
    "system_card_pos",
    "system_cash_bs",
    "actual_card_pos",
    "actual_cash_bs",
)


def upgrade() -> None:
    """Upgrade schema.

    全新数据库上 bootstrap() 会先跑迁移、再执行 create_all()。此时业务表
    还不存在，迁移必须跳过，让 create_all() 按最新模型建表；已有数据库则
    逐项补齐（每一步都先检查，避免重复执行时炸）。
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1) 先确认现有数据满足 (oem, brand) 唯一，否则不要强行加索引。
    if inspector.has_table("autopart"):
        existing_indexes = {ix["name"] for ix in inspector.get_indexes("autopart")}
        if "uq_autopart_oem_brand" not in existing_indexes:
            duplicate = bind.execute(
                sa.text(
                    """
                    SELECT oem, brand, COUNT(*) AS c
                    FROM autopart
                    GROUP BY oem, brand
                    HAVING COUNT(*) > 1
                    LIMIT 1
                    """
                )
            ).first()
            if duplicate is not None:
                raise RuntimeError(
                    "autopart 存在重复的 (oem, brand)："
                    f"{duplicate.oem!r} / {duplicate.brand!r}。"
                    "请先清理重复商品，再执行本次迁移。"
                )

            op.create_index(
                "uq_autopart_oem_brand",
                "autopart",
                ["oem", "brand"],
                unique=True,
            )

    # 2) 订单明细记录售出的具体库存行。
    #    SQLite 默认不启用外键约束，这里加普通列 + 索引；
    #    退款时会显式校验 part_id 指向的商品是否仍然存在。
    if inspector.has_table("order_items"):
        columns = {c["name"] for c in inspector.get_columns("order_items")}
        if "part_id" not in columns:
            op.add_column("order_items", sa.Column("part_id", sa.Integer(), nullable=True))
        indexes = {ix["name"] for ix in inspector.get_indexes("order_items")}
        if "ix_order_items_part_id" not in indexes:
            op.create_index("ix_order_items_part_id", "order_items", ["part_id"])

    # 3) 交接班缺失的卡机 / 本币现金列。
    if inspector.has_table("cashregistersession"):
        columns = {c["name"] for c in inspector.get_columns("cashregistersession")}
        for column in _SHIFT_COLUMNS:
            if column not in columns:
                op.add_column(
                    "cashregistersession",
                    sa.Column(column, sa.Float(), nullable=False, server_default="0"),
                )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("cashregistersession"):
        columns = {c["name"] for c in inspector.get_columns("cashregistersession")}
        for column in reversed(_SHIFT_COLUMNS):
            if column in columns:
                op.drop_column("cashregistersession", column)

    if inspector.has_table("order_items"):
        indexes = {ix["name"] for ix in inspector.get_indexes("order_items")}
        if "ix_order_items_part_id" in indexes:
            op.drop_index("ix_order_items_part_id", table_name="order_items")
        columns = {c["name"] for c in inspector.get_columns("order_items")}
        if "part_id" in columns:
            op.drop_column("order_items", "part_id")

    if inspector.has_table("autopart"):
        indexes = {ix["name"] for ix in inspector.get_indexes("autopart")}
        if "uq_autopart_oem_brand" in indexes:
            op.drop_index("uq_autopart_oem_brand", table_name="autopart")
