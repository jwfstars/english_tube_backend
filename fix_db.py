#!/usr/bin/env python3
"""
快速修复数据库缺失字段
手动添加 is_free 列到 videos 表
"""

import asyncio
import asyncpg
import sys

# 数据库连接配置（从 .env 文件读取）
DATABASE_URL = "postgresql://english_tube:dev_local_password_2024@localhost:5432/english_tube"

async def fix_database():
    """添加缺失的 is_free 列"""
    try:
        # 连接数据库
        print("🔌 连接数据库...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # 检查列是否存在
        print("🔍 检查 is_free 列是否存在...")
        result = await conn.fetchval("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_name = 'videos'
            AND column_name = 'is_free'
        """)
        
        if result > 0:
            print("✅ is_free 列已经存在！")
        else:
            print("➕ 添加 is_free 列...")
            await conn.execute("""
                ALTER TABLE videos
                ADD COLUMN is_free BOOLEAN DEFAULT true NOT NULL
            """)
            print("✅ is_free 列添加成功！")
        
        # 关闭连接
        await conn.close()
        print("\n🎉 数据库修复完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n💡 请确保：")
        print("   1. PostgreSQL 正在运行")
        print("   2. 数据库连接信息正确")
        print("   3. 你有权限修改数据库")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_database())
    sys.exit(0 if success else 1)
