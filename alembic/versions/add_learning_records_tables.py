"""add learning records tables

Revision ID: add_learning_records_tables
Revises: add_video_segments
Create Date: 2025-12-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_learning_records_tables'
down_revision: Union[str, None] = 'add_video_segments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_video_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('current_progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_duration', sa.Integer(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('last_watched_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'video_id', name='uq_user_video_progress_user_video'),
    )
    op.create_index('ix_user_video_progress_user_lastwatched', 'user_video_progress', ['user_id', 'last_watched_at'])
    op.create_index(
        'ix_user_video_progress_user_completed',
        'user_video_progress',
        ['user_id', 'is_completed', 'completed_at'],
    )
    op.create_index('ix_user_video_progress_user_id', 'user_video_progress', ['user_id'])
    op.create_index('ix_user_video_progress_video_id', 'user_video_progress', ['video_id'])

    op.create_table(
        'user_video_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('favorited_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'video_id', name='uq_user_video_favorites_user_video'),
    )
    op.create_index('ix_user_video_favorites_user_id', 'user_video_favorites', ['user_id'])
    op.create_index('ix_user_video_favorites_video_id', 'user_video_favorites', ['video_id'])
    op.create_index(
        'ix_user_video_favorites_user_favorited_at',
        'user_video_favorites',
        ['user_id', 'favorited_at'],
    )


def downgrade() -> None:
    op.drop_index('ix_user_video_favorites_user_favorited_at', table_name='user_video_favorites')
    op.drop_index('ix_user_video_favorites_video_id', table_name='user_video_favorites')
    op.drop_index('ix_user_video_favorites_user_id', table_name='user_video_favorites')
    op.drop_table('user_video_favorites')

    op.drop_index('ix_user_video_progress_video_id', table_name='user_video_progress')
    op.drop_index('ix_user_video_progress_user_id', table_name='user_video_progress')
    op.drop_index('ix_user_video_progress_user_completed', table_name='user_video_progress')
    op.drop_index('ix_user_video_progress_user_lastwatched', table_name='user_video_progress')
    op.drop_table('user_video_progress')
