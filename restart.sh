#!/bin/bash
# English Tube Backend - 重启服务器脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

ADMIN_DIR="$SCRIPT_DIR/../english_tube_admin"

echo "停止现有服务..."
pkill -f "uvicorn app.main:app" 2>/dev/null

# 通过端口杀掉后端（包括可能冲突的进程）
echo "停止后端进程（端口 8002）..."
# 杀掉所有非 Docker 的 Python 进程占用 8002
lsof -ti:8002 -c Python | xargs kill -9 2>/dev/null || true

# 通过端口杀掉管理后台（包括所有相关进程）
echo "停止管理后台进程（端口 8858）..."
lsof -ti:8858 | xargs kill -9 2>/dev/null || true

# 额外清理可能的残留进程
pkill -f "pnpm dev --host 0.0.0.0 --port 8858" 2>/dev/null || true
pkill -f "vite.js --host 0.0.0.0 --port 8858" 2>/dev/null || true

sleep 2

echo "启动服务器..."
source ../.venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002 &

echo "启动管理后台..."
cd "$ADMIN_DIR" || exit 1
pnpm dev --host 0.0.0.0 --port 8858 &

sleep 2
curl -s http://localhost:8002/health && echo " 后端已启动" || echo " 后端启动失败"
curl -s http://localhost:8858 >/dev/null && echo " 管理后台已启动" || echo " 管理后台启动失败"
