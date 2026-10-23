"""add cost_price to autopart

Revision ID: edf6251cee6c
Revises: c3e5f7a9b1d2
Create Date: 2026-10-20 18:44:53.288168

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edf6251cee6c'
down_revision: Union[str, Sequence[str], None] = 'c3e5f7a9b1d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("autopart")}
    if "cost_price" not in cols:
        op.add_column('autopart', sa.Column('cost_price', sa.Float(), nullable=True))
        op.execute("UPDATE autopart SET cost_price = 0.0 WHERE cost_price IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("autopart")}
    if "cost_price" in cols:
        op.drop_column('autopart', 'cost_price')