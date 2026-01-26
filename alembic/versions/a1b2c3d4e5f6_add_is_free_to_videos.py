"""add is_free to videos

Revision ID: a1b2c3d4e5f6
Revises: f9e8d7c6b5a4
Create Date: 2025-12-31 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f9e8d7c6b5a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加 is_free 字段，默认为 False（付费）
    op.add_column('videos', sa.Column('is_free', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # 回滚：删除 is_free 字段
    op.drop_column('videos', 'is_free')
