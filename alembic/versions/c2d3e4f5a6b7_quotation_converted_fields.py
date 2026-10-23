"""quotationrecord: add converted_order_id + converted_at

Revision ID: c2d3e4f5a6b7
Revises: 092e79bcf78e
Create Date: 2026-10-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, Sequence[str], None] = '092e79bcf78e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("quotationrecord")}
    if "converted_order_id" not in cols:
        op.add_column("quotationrecord", sa.Column("converted_order_id", sa.Integer(), nullable=True))
    if "converted_at" not in cols:
        op.add_column("quotationrecord", sa.Column("converted_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    from sqlalchemy import inspect
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("quotationrecord")}
    if "converted_at" in cols:
        op.drop_column("quotationrecord", "converted_at")
    if "converted_order_id" in cols:
        op.drop_column("quotationrecord", "converted_order_id")