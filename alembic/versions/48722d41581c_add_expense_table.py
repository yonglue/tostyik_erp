"""add expense table

Revision ID: 48722d41581c
Revises: edf6251cee6c
Create Date: 2026-10-20 18:58:54.533250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48722d41581c'
down_revision: Union[str, Sequence[str], None] = 'edf6251cee6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 表已经存在，无需重复创建
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass