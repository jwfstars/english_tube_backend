#!/bin/bash
# English Tube Backend - Docker 重启服务器脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "停止现有服务..."
# 停止 Docker 容器
docker-compose stop backend 2>/dev/null || true

# 停止管理后台开发服务器
pkill -f "vite.*english_tube_admin" 2>/dev/null || true
sleep 1

echo "重新构建后端镜像..."
docker-compose build backend

echo "启动后端容器..."
docker-compose up -d backend

echo "启动管理后台..."
cd ../english_tube_admin
nohup pnpm dev > /tmp/admin.log 2>&1 &
ADMIN_PID=$!
cd ..

echo "等待服务启动..."
# 等待后端服务就绪（最多等待 30 秒）
for i in {1..15}; do
  if curl -s http://localhost:8002/api/health >/dev/null 2>&1; then
    break
  fi
  echo "等待后端启动... ($i/15)"
  sleep 2
done

echo "检查服务状态..."
curl -s http://localhost:8002/api/health && echo " ✅ 后端已启动" || echo " ❌ 后端启动失败"
curl -s http://localhost:8858 >/dev/null 2>&1 && echo " ✅ 管理后台已启动" || echo " ❌ 管理后台启动失败"

echo ""
echo "服务访问地址："
echo "  后端 API: http://localhost:8002/api/health"
echo "  管理后台: http://localhost:8858"
echo ""
echo "查看日志："
echo "  后端: docker logs -f english_tube_backend"
echo "  管理后台: tail -f /tmp/admin.log"
