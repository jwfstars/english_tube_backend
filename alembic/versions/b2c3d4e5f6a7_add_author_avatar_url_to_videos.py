"""add author_avatar_url to videos

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-31 16:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加 author_avatar_url 字段（如果不存在）
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'videos' AND column_name = 'author_avatar_url'
            ) THEN
                ALTER TABLE videos ADD COLUMN author_avatar_url TEXT;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # 回滚：删除 author_avatar_url 字段
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'videos' AND column_name = 'author_avatar_url'
            ) THEN
                ALTER TABLE videos DROP COLUMN author_avatar_url;
            END IF;
        END $$;
    """)
