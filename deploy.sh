#!/bin/bash

# English Tube Backend 部署脚本
# 用于首次部署到生产服务器

set -e

echo "=========================================="
echo "English Tube Backend 部署脚本"
echo "=========================================="

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误：未找到 docker-compose.yml 文件"
    echo "请在 backend 目录下运行此脚本"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env.production" ]; then
    echo "❌ 错误：未找到 .env.production 文件"
    echo "请复制 .env.production 并填写正确的配置"
    exit 1
fi

echo "✅ 环境检查通过"

# 创建必要的目录
echo ""
echo "📁 创建必要的目录..."
mkdir -p logs backups nginx/ssl nginx/logs uploads

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "安装命令："
    echo "  curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 停止可能运行的旧容器
echo ""
echo "🛑 停止旧容器..."
docker-compose down || true

# 构建镜像
echo ""
echo "🔨 构建 Docker 镜像..."
docker-compose build --no-cache

# 启动数据库并等待健康检查
echo ""
echo "🚀 启动数据库..."
docker-compose up -d postgres

echo "⏳ 等待数据库启动（最多60秒）..."
timeout=60
counter=0
until docker-compose exec -T postgres pg_isready -U english_tube > /dev/null 2>&1; do
    sleep 2
    counter=$((counter + 2))
    if [ $counter -ge $timeout ]; then
        echo "❌ 数据库启动超时"
        docker-compose logs postgres
        exit 1
    fi
    echo "  等待中... ${counter}s"
done

echo "✅ 数据库已启动"

# 运行数据库迁移
echo ""
echo "📊 运行数据库迁移..."
docker-compose run --rm backend alembic upgrade head

# 启动所有服务
echo ""
echo "🚀 启动所有服务..."
docker-compose up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态："
docker-compose ps

# 检查健康状态
echo ""
echo "🏥 检查服务健康状态..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend 健康检查通过"
else
    echo "⚠️  Backend 健康检查失败，请查看日志："
    echo "  docker-compose logs backend"
fi

echo ""
echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo ""
echo "服务访问："
echo "  - Backend API: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - Nginx: http://localhost:80"
echo ""
echo "常用命令："
echo "  - 查看日志: docker-compose logs -f"
echo "  - 查看状态: docker-compose ps"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo ""
echo "⚠️  下一步："
echo "  1. 配置域名解析到服务器 IP"
echo "  2. 申请 SSL 证书"
echo "  3. 配置 nginx/conf.d/default.conf 中的域名和 HTTPS"
echo "  4. 运行 ./backup.sh 设置自动备份"
echo ""
