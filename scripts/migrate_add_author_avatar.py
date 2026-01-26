#!/usr/bin/env python3
"""
数据库迁移：添加 author_avatar_url 字段
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine

async def migrate():
    async with engine.begin() as conn:
        # 添加 author_avatar_url 字段
        await conn.execute(text("""
            ALTER TABLE videos
            ADD COLUMN IF NOT EXISTS author_avatar_url TEXT;
        """))
        print("✅ 成功添加 author_avatar_url 字段")

if __name__ == "__main__":
    asyncio.run(migrate())
