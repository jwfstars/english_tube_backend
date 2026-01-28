#!/bin/bash
# 停止开发服务器

PORT=${1:-8000}

echo "🛑 停止端口 $PORT 上的服务..."

PID=$(lsof -ti:$PORT 2>/dev/null || true)

if [ ! -z "$PID" ]; then
    echo "   发现进程: $PID"
    kill -9 $PID
    echo "   ✅ 服务已停止"
else
    echo "   ℹ️  端口 $PORT 没有运行的服务"
fi
