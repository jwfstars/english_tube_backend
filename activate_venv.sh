#!/bin/bash
# 激活 Python 3.12 虚拟环境

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 激活虚拟环境
source "$SCRIPT_DIR/venv/bin/activate"

# 显示 Python 版本
echo "✅ 虚拟环境已激活！"
echo "📍 项目路径: $SCRIPT_DIR"
echo "🐍 Python 版本: $(python --version)"
echo "📦 pip 版本: $(pip --version)"
echo ""
echo "💡 提示："
echo "  - 运行服务: uvicorn app.main:app --reload --port 8000"
echo "  - 数据库迁移: alembic upgrade head"
echo "  - 创建迁移: alembic revision --autogenerate -m \"description\""
echo "  - 退出环境: deactivate"
