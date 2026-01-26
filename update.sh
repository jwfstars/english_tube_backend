#!/bin/bash

# English Tube Backend 更新脚本
# 用于更新已部署的服务

set -e

echo "=========================================="
echo "English Tube Backend 更新脚本"
echo "=========================================="

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误：未找到 docker-compose.yml 文件"
    exit 1
fi

# 显示当前运行的服务
echo "📊 当前运行的服务："
docker-compose ps

echo ""
read -p "⚠️  确认要更新服务吗？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消更新"
    exit 0
fi

# 备份数据库（可选）
echo ""
read -p "📦 是否先备份数据库？(推荐) (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "正在备份数据库..."
    ./backup.sh
fi

# 拉取最新代码（如果使用 Git）
if [ -d ".git" ]; then
    echo ""
    echo "📥 拉取最新代码..."
    git pull
fi

# 重新构建镜像
echo ""
echo "🔨 重新构建镜像..."
docker-compose build

# 运行数据库迁移
echo ""
echo "📊 运行数据库迁移..."
docker-compose run --rm backend alembic upgrade head

# 重启服务（零停机更新）
echo ""
echo "🔄 重启服务..."
docker-compose up -d --force-recreate --no-deps backend

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查健康状态
echo ""
echo "🏥 检查服务健康状态..."
max_attempts=10
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 服务更新成功！"
        break
    fi
    attempt=$((attempt + 1))
    echo "  尝试 $attempt/$max_attempts..."
    sleep 3
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ 服务健康检查失败"
    echo "查看日志："
    docker-compose logs --tail=50 backend
    exit 1
fi

# 清理未使用的镜像
echo ""
read -p "🧹 是否清理未使用的 Docker 镜像？(y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker image prune -f
    echo "✅ 清理完成"
fi

echo ""
echo "=========================================="
echo "🎉 更新完成！"
echo "=========================================="
echo ""
docker-compose ps
