#!/bin/bash
# 检查开发环境状态

PORT=${1:-8000}
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "========================================="
echo "  环境检查"
echo "========================================="
echo ""

# 检查 Python
echo "🐍 Python:"
if command -v python3.12 &> /dev/null; then
    echo "   ✅ $(python3.12 --version)"
else
    echo "   ❌ Python 3.12 未安装"
fi
echo ""

# 检查虚拟环境
echo "📦 虚拟环境:"
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "   ✅ 虚拟环境存在"
    source "$PROJECT_DIR/venv/bin/activate"
    echo "   Python: $(python --version)"
    echo "   FastAPI: $(python -c 'import fastapi; print(fastapi.__version__)' 2>/dev/null || echo '未安装')"
    deactivate
else
    echo "   ❌ 虚拟环境不存在"
    echo "   运行: python3.12 -m venv venv"
fi
echo ""

# 检查环境变量
echo "⚙️  配置文件:"
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "   ✅ .env 文件存在"
else
    echo "   ⚠️  .env 文件不存在"
    echo "   运行: cp .env.example .env"
fi
echo ""

# 检查端口
echo "🔌 端口状态:"
PID=$(lsof -ti:$PORT 2>/dev/null || true)
if [ ! -z "$PID" ]; then
    echo "   ⚠️  端口 $PORT 被占用 (PID: $PID)"
    PROCESS=$(ps -p $PID -o comm= 2>/dev/null || echo "未知")
    echo "   进程: $PROCESS"
else
    echo "   ✅ 端口 $PORT 可用"
fi
echo ""

# 检查 Docker
echo "🐳 Docker:"
if docker ps &> /dev/null; then
    echo "   ✅ Docker 运行中"
    
    # 检查数据库容器
    if docker ps --format '{{.Names}}' | grep -q "english_tube_db"; then
        echo "   ✅ PostgreSQL 容器运行中"
    else
        echo "   ⚠️  PostgreSQL 容器未运行"
        echo "   运行: docker-compose up -d postgres"
    fi
else
    echo "   ⚠️  Docker 未运行或无权限"
fi
echo ""

echo "========================================="
echo ""
echo "💡 快速启动:"
echo "   ./dev.sh          # 启动开发服务器"
echo "   ./dev.sh 8002     # 指定端口启动"
echo "   ./stop.sh         # 停止服务"
echo ""
