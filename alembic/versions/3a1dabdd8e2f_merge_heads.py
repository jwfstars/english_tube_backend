"""merge heads

Revision ID: 3a1dabdd8e2f
Revises: add_learning_records_tables, b7f1c2d3e4f5
Create Date: 2025-12-25 22:48:13.676971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a1dabdd8e2f'
down_revision: Union[str, None] = ('add_learning_records_tables', 'b7f1c2d3e4f5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
