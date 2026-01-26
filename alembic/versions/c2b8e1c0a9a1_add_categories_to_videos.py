"""add categories to videos

Revision ID: c2b8e1c0a9a1
Revises: 7b9f4c2d8e21
Create Date: 2025-12-24 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c2b8e1c0a9a1'
down_revision: Union[str, None] = '7b9f4c2d8e21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('videos', sa.Column('categories', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('videos', 'categories')
