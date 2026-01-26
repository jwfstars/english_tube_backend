"""add subtitle and word favorites tables

Revision ID: f8d2e3a4b5c6
Revises: add_learning_records_tables
Create Date: 2025-12-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f8d2e3a4b5c6'
down_revision: Union[str, None] = 'add_learning_records_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_subtitle_favorites table
    op.create_table(
        'user_subtitle_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subtitle_id', sa.Integer(), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('favorited_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subtitle_id'], ['subtitles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'subtitle_id', name='uq_user_subtitle_favorites_user_subtitle'),
    )
    op.create_index('ix_user_subtitle_favorites_user_id', 'user_subtitle_favorites', ['user_id'])
    op.create_index('ix_user_subtitle_favorites_subtitle_id', 'user_subtitle_favorites', ['subtitle_id'])
    op.create_index('ix_user_subtitle_favorites_video_id', 'user_subtitle_favorites', ['video_id'])
    op.create_index(
        'ix_user_subtitle_favorites_user_favorited_at',
        'user_subtitle_favorites',
        ['user_id', 'favorited_at'],
    )

    # Create user_word_favorites table
    op.create_table(
        'user_word_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('word_card_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('favorited_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['word_card_id'], ['word_cards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'word_card_id', name='uq_user_word_favorites_user_word'),
    )
    op.create_index('ix_user_word_favorites_user_id', 'user_word_favorites', ['user_id'])
    op.create_index('ix_user_word_favorites_word_card_id', 'user_word_favorites', ['word_card_id'])
    op.create_index('ix_user_word_favorites_video_id', 'user_word_favorites', ['video_id'])
    op.create_index(
        'ix_user_word_favorites_user_favorited_at',
        'user_word_favorites',
        ['user_id', 'favorited_at'],
    )


def downgrade() -> None:
    # Drop user_word_favorites table
    op.drop_index('ix_user_word_favorites_user_favorited_at', table_name='user_word_favorites')
    op.drop_index('ix_user_word_favorites_video_id', table_name='user_word_favorites')
    op.drop_index('ix_user_word_favorites_word_card_id', table_name='user_word_favorites')
    op.drop_index('ix_user_word_favorites_user_id', table_name='user_word_favorites')
    op.drop_table('user_word_favorites')

    # Drop user_subtitle_favorites table
    op.drop_index('ix_user_subtitle_favorites_user_favorited_at', table_name='user_subtitle_favorites')
    op.drop_index('ix_user_subtitle_favorites_video_id', table_name='user_subtitle_favorites')
    op.drop_index('ix_user_subtitle_favorites_subtitle_id', table_name='user_subtitle_favorites')
    op.drop_index('ix_user_subtitle_favorites_user_id', table_name='user_subtitle_favorites')
    op.drop_table('user_subtitle_favorites')
