"""add users table

Revision ID: 6b2b7f5a8c2e
Revises: ea1b5a3c8f77
Create Date: 2025-12-24 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '6b2b7f5a8c2e'
down_revision: Union[str, None] = 'ea1b5a3c8f77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=320), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('apple_sub', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.execute("DROP INDEX IF EXISTS ix_users_email")
    op.execute("DROP INDEX IF EXISTS ix_users_apple_sub")
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_apple_sub', 'users', ['apple_sub'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_apple_sub', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
