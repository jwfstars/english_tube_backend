"""add categories_zh to videos

Revision ID: ea1b5a3c8f77
Revises: c2b8e1c0a9a1
Create Date: 2025-12-24 11:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ea1b5a3c8f77'
down_revision: Union[str, None] = 'c2b8e1c0a9a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('videos', sa.Column('categories_zh', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('videos', 'categories_zh')
