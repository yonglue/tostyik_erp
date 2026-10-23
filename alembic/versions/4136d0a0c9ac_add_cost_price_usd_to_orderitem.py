"""add cost_price_usd to orderitem

Revision ID: 4136d0a0c9ac
Revises: 48722d41581c
Create Date: 2026-10-20 19:28:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4136d0a0c9ac'
down_revision: Union[str, Sequence[str], None] = '48722d41581c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("order_items")}
    if "cost_price_usd" not in cols:
        op.add_column(
            'order_items',
            sa.Column('cost_price_usd', sa.Float(), nullable=False, server_default='0.0'),
        )


def downgrade() -> None:
    """Downgrade schema."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("order_items")}
    if "cost_price_usd" in cols:
        op.drop_column('order_items', 'cost_price_usd')