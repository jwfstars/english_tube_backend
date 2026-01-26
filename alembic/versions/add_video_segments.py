"""添加视频分段支持

Revision ID: add_video_segments
Revises: 13956fe485c2
Create Date: 2024-12-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_video_segments'
down_revision: Union[str, None] = '13956fe485c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加视频组相关字段
    op.add_column('videos', sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('videos', sa.Column('segment_index', sa.Integer(), nullable=True))
    op.add_column('videos', sa.Column('video_type', sa.String(length=20), server_default='full', nullable=True))

    # 创建外键约束
    op.create_foreign_key(
        'fk_videos_parent_id',
        'videos',
        'videos',
        ['parent_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # 创建索引
    op.create_index('ix_videos_parent_id', 'videos', ['parent_id'], unique=False)
    op.create_index('ix_videos_video_type', 'videos', ['video_type'], unique=False)


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_videos_video_type', table_name='videos')
    op.drop_index('ix_videos_parent_id', table_name='videos')

    # 删除外键
    op.drop_constraint('fk_videos_parent_id', 'videos', type_='foreignkey')

    # 删除字段
    op.drop_column('videos', 'video_type')
    op.drop_column('videos', 'segment_index')
    op.drop_column('videos', 'parent_id')
