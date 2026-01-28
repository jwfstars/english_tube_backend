#!/bin/bash
# 清空数据库并重置迁移
# ⚠️ 警告：此脚本会删除所有数据！

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$PROJECT_DIR/venv"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}========================================${NC}"
echo -e "${RED}  ⚠️  数据库完全重置 ⚠️${NC}"
echo -e "${RED}========================================${NC}"
echo -e "${YELLOW}此操作将：${NC}"
echo -e "${YELLOW}  1. 删除所有迁移文件${NC}"
echo -e "${YELLOW}  2. 删除数据库所有表${NC}"
echo -e "${YELLOW}  3. 重新创建数据库结构${NC}"
echo ""
echo -e "${RED}⚠️  所有数据将被永久删除！${NC}"
echo ""
read -p "确认继续? (输入 yes 确认): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${GREEN}已取消${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}开始重置...${NC}"
echo ""

# 激活虚拟环境
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✅ 虚拟环境已激活${NC}"
else
    echo -e "${RED}❌ 虚拟环境不存在${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. 删除迁移文件
echo -e "${YELLOW}📁 删除旧的迁移文件...${NC}"
rm -rf alembic/versions/*.py
echo -e "${GREEN}   ✅ 迁移文件已删除${NC}"
echo ""

# 2. 创建重置数据库的 Python 脚本
echo -e "${YELLOW}🗑️  清空数据库...${NC}"

python << 'PYTHON_SCRIPT'
import asyncio
import asyncpg
from app.core.config import settings

async def reset_database():
    try:
        # 从 ASYNC_DATABASE_URL 中提取连接信息
        db_url = settings.ASYNC_DATABASE_URL.replace("postgresql+asyncpg://", "")
        
        conn = await asyncpg.connect(f"postgresql://{db_url}")
        print("   🔌 已连接到数据库")
        
        # 删除所有表
        await conn.execute("""
            DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO public;
        """)
        print("   ✅ 所有表已删除")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

success = asyncio.run(reset_database())
exit(0 if success else 1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✅ 数据库已清空${NC}"
else
    echo -e "${RED}   ❌ 清空数据库失败${NC}"
    exit 1
fi
echo ""

# 3. 创建初始迁移
echo -e "${YELLOW}📝 创建初始迁移...${NC}"
alembic revision --autogenerate -m "Initial database schema"
echo -e "${GREEN}   ✅ 初始迁移已创建${NC}"
echo ""

# 4. 执行迁移
echo -e "${YELLOW}🔄 执行迁移...${NC}"
alembic upgrade head
echo -e "${GREEN}   ✅ 迁移已执行${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🎉 数据库重置完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}下一步：${NC}"
echo -e "${BLUE}  1. 启动服务: ./dev.sh${NC}"
echo -e "${BLUE}  2. 创建管理员: python -m scripts.create_superuser --email admin@test.com --password admin123${NC}"
echo ""
