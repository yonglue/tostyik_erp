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
    # 1. 添加列，允许为空（对 SQLite 最友好，不会报错）
    op.add_column('autopart', sa.Column('cost_price', sa.Float(), nullable=True))
    
    # 2. 将老数据的 cost_price 填充为 0.0
    op.execute("UPDATE autopart SET cost_price = 0.0 WHERE cost_price IS NULL")
    
    # 注意：我们暂时不在数据库层面强制设为 NOT NULL，
    # 因为你的 models.py 里已经写了 default=0.0，新数据默认就会是 0，
    # 且前端的输入框在保存时也会传值过来，这样处理最安全。


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('autopart', 'cost_price')