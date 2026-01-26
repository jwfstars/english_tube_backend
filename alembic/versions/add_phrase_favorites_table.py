"""add phrase favorites table

Revision ID: c8e7f9a1d2b3
Revises: 3a1dabdd8e2f
Create Date: 2025-12-28

"""
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c8e7f9a1d2b3'
down_revision: Union[str, None] = '3a1dabdd8e2f'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Create user_phrase_favorites table
    op.create_table(
        'user_phrase_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('phrase_card_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('favorited_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['phrase_card_id'], ['phrase_cards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'phrase_card_id', name='uq_user_phrase_favorites_user_phrase')
    )

    # Create indexes
    op.create_index('ix_user_phrase_favorites_user_id', 'user_phrase_favorites', ['user_id'], unique=False)
    op.create_index('ix_user_phrase_favorites_phrase_card_id', 'user_phrase_favorites', ['phrase_card_id'], unique=False)
    op.create_index('ix_user_phrase_favorites_video_id', 'user_phrase_favorites', ['video_id'], unique=False)
    op.create_index('ix_user_phrase_favorites_user_favorited_at', 'user_phrase_favorites', ['user_id', 'favorited_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_user_phrase_favorites_user_favorited_at', table_name='user_phrase_favorites')
    op.drop_index('ix_user_phrase_favorites_video_id', table_name='user_phrase_favorites')
    op.drop_index('ix_user_phrase_favorites_phrase_card_id', table_name='user_phrase_favorites')
    op.drop_index('ix_user_phrase_favorites_user_id', table_name='user_phrase_favorites')

    # Drop table
    op.drop_table('user_phrase_favorites')
