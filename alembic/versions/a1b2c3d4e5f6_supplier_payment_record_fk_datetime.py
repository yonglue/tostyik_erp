"""supplier_payment_record: add foreign key to suppliers + created_at as datetime

Revision ID: a1b2c3d4e5f6
Revises: 2abce90f8fce
Create Date: 2026-10-23 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '2abce90f8fce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)

    if "supplierpaymentrecord" in inspector.get_table_names():
        count = bind.execute(
            sa.text("SELECT COUNT(*) FROM supplierpaymentrecord")
        ).scalar()
        if count and count > 0:
            raise RuntimeError(
                f"supplierpaymentrecord 非空（{count} 条），请改用 batch_alter_table 迁移"
            )
        op.drop_table("supplierpaymentrecord")

    op.create_table(
        "supplierpaymentrecord",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("supplier_name", sa.String(), nullable=False),
        sa.Column("amount_usd", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("original_amount", sa.Float(), nullable=False),
        sa.Column("exchange_rate", sa.Float(), nullable=False),
        sa.Column("payment_method", sa.String(), nullable=False),
        sa.Column("reference_no", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
    )
    op.create_index(
        "ix_supplierpaymentrecord_supplier_id",
        "supplierpaymentrecord",
        ["supplier_id"],
    )


def downgrade() -> None:
    from sqlalchemy import inspect
    bind = op.get_bind()
    if "supplierpaymentrecord" in inspect(bind).get_table_names():
        op.drop_index("ix_supplierpaymentrecord_supplier_id", table_name="supplierpaymentrecord")
        op.drop_table("supplierpaymentrecord")

    op.create_table(
        "supplierpaymentrecord",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("supplier_name", sa.String(), nullable=False),
        sa.Column("amount_usd", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("original_amount", sa.Float(), nullable=False),
        sa.Column("exchange_rate", sa.Float(), nullable=False),
        sa.Column("payment_method", sa.String(), nullable=False),
        sa.Column("reference_no", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
    )
    op.create_index(
        "ix_supplierpaymentrecord_supplier_id",
        "supplierpaymentrecord",
        ["supplier_id"],
    )