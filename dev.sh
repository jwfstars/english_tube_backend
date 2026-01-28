#!/bin/bash
# English Tube Backend - 开发启动脚本
# 功能：激活虚拟环境、杀掉占用端口的进程、启动开发服务器

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PORT=${1:-8000}  # 默认端口 8000，可通过参数覆盖
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$PROJECT_DIR/venv"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  English Tube Backend - 开发环境${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ 虚拟环境不存在！${NC}"
    echo -e "${YELLOW}请先运行: python3.12 -m venv venv${NC}"
    exit 1
fi

# 激活虚拟环境
echo -e "${GREEN}🐍 激活虚拟环境...${NC}"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}   Python: $(python --version)${NC}"
echo -e "${GREEN}   路径: $VENV_DIR${NC}"
echo ""

# 检查端口占用
echo -e "${YELLOW}🔍 检查端口 $PORT 占用情况...${NC}"
PID=$(lsof -ti:$PORT 2>/dev/null || true)

if [ ! -z "$PID" ]; then
    echo -e "${YELLOW}   端口 $PORT 被进程 $PID 占用${NC}"
    echo -e "${YELLOW}   正在杀掉进程...${NC}"
    kill -9 $PID 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}   ✅ 进程已终止${NC}"
else
    echo -e "${GREEN}   ✅ 端口 $PORT 可用${NC}"
fi
echo ""

# 检查环境变量文件
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在，使用默认配置${NC}"
    echo -e "${YELLOW}   建议: cp .env.example .env${NC}"
    echo ""
fi

# 显示信息
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🚀 启动开发服务器...${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}   端口: $PORT${NC}"
echo -e "${GREEN}   热重载: 已启用${NC}"
echo -e "${GREEN}   API 文档: http://localhost:$PORT/api/docs${NC}"
echo -e "${GREEN}   健康检查: http://localhost:$PORT/api/health${NC}"
echo ""
echo -e "${YELLOW}💡 提示: 按 Ctrl+C 停止服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 启动服务
cd "$PROJECT_DIR"
uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT
