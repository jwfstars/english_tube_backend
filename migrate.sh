#!/bin/bash
# 数据库迁移脚本

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$PROJECT_DIR/venv"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  数据库迁移工具${NC}"
echo -e "${GREEN}========================================${NC}"
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

case "${1:-upgrade}" in
    "upgrade"|"up")
        echo -e "${GREEN}🔄 执行数据库迁移...${NC}"
        alembic upgrade head
        echo -e "${GREEN}✅ 迁移完成${NC}"
        ;;
    
    "downgrade"|"down")
        echo -e "${YELLOW}⬇️  回滚一个版本...${NC}"
        alembic downgrade -1
        echo -e "${GREEN}✅ 回滚完成${NC}"
        ;;
    
    "create"|"new")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ 请提供迁移描述${NC}"
            echo -e "${YELLOW}用法: ./migrate.sh create \"your description\"${NC}"
            exit 1
        fi
        echo -e "${GREEN}📝 创建新迁移: $2${NC}"
        alembic revision --autogenerate -m "$2"
        echo -e "${GREEN}✅ 迁移文件已创建${NC}"
        echo -e "${YELLOW}💡 运行 ./migrate.sh upgrade 来应用迁移${NC}"
        ;;
    
    "history"|"log")
        echo -e "${GREEN}📜 迁移历史:${NC}"
        alembic history
        ;;
    
    "current")
        echo -e "${GREEN}📍 当前版本:${NC}"
        alembic current
        ;;
    
    "help"|"--help"|"-h")
        echo "用法: ./migrate.sh [命令] [参数]"
        echo ""
        echo "命令:"
        echo "  upgrade, up      执行所有待执行的迁移 (默认)"
        echo "  downgrade, down  回滚一个版本"
        echo "  create, new      创建新迁移 (需要描述)"
        echo "  history, log     查看迁移历史"
        echo "  current          查看当前版本"
        echo "  help             显示此帮助信息"
        echo ""
        echo "示例:"
        echo "  ./migrate.sh upgrade"
        echo "  ./migrate.sh create \"add user table\""
        echo "  ./migrate.sh history"
        ;;
    
    *)
        echo -e "${RED}❌ 未知命令: $1${NC}"
        echo -e "${YELLOW}运行 ./migrate.sh help 查看帮助${NC}"
        exit 1
        ;;
esac

echo ""
