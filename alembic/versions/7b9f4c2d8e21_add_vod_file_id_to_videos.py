"""add vod_file_id to videos

Revision ID: 7b9f4c2d8e21
Revises: 3af549d9e535
Create Date: 2025-12-23 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b9f4c2d8e21'
down_revision: Union[str, None] = '3af549d9e535'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('videos', sa.Column('vod_file_id', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('videos', 'vod_file_id')
