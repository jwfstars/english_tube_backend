"""add sms login tables

Revision ID: 9d7e5c1a4f11
Revises: 6b2b7f5a8c2e
Create Date: 2025-12-24 13:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9d7e5c1a4f11'
down_revision: Union[str, None] = '6b2b7f5a8c2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone', sa.String(length=32), nullable=True))
    op.create_index('ix_users_phone', 'users', ['phone'], unique=True)

    op.create_table(
        'sms_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('phone', sa.String(length=32), nullable=False),
        sa.Column('code_hash', sa.String(length=255), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_sms_codes_phone', 'sms_codes', ['phone'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_sms_codes_phone', table_name='sms_codes')
    op.drop_table('sms_codes')
    op.drop_index('ix_users_phone', table_name='users')
    op.drop_column('users', 'phone')
