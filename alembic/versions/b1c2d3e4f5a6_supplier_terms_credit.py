"""supplier: add payment_terms and credit_limit (manual)

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-10-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("suppliers")}
    if "payment_terms" not in cols:
        op.add_column(
            "suppliers",
            sa.Column("payment_terms", sa.Integer(), nullable=False, server_default="30"),
        )
    if "credit_limit" not in cols:
        op.add_column(
            "suppliers",
            sa.Column("credit_limit", sa.Float(), nullable=False, server_default="5000.0"),
        )


def downgrade() -> None:
    from sqlalchemy import inspect
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("suppliers")}
    if "credit_limit" in cols:
        op.drop_column("suppliers", "credit_limit")
    if "payment_terms" in cols:
        op.drop_column("suppliers", "payment_terms")