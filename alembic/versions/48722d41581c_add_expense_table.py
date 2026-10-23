"""add expense table

Revision ID: 48722d41581c
Revises: edf6251cee6c
Create Date: 2026-10-20 18:58:54.533250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '48722d41581c'
down_revision: Union[str, Sequence[str], None] = 'edf6251cee6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    if "expenses" in inspect(bind).get_table_names():
        return

    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('exchange_rate', sa.Float(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('receipt_url', sa.String(), nullable=False),
        sa.Column('created_by', sa.String(length=50), nullable=False),
        sa.Column('expense_date', sa.String(), nullable=False),
        sa.Column('created_at', sa.String(), nullable=False),
    )
    op.create_index('ix_expenses_category', 'expenses', ['category'])


def downgrade() -> None:
    """Downgrade schema."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    if "expenses" in inspect(bind).get_table_names():
        op.drop_index('ix_expenses_category', table_name='expenses')
        op.drop_table('expenses')