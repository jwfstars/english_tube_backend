#!/bin/bash
# 创建 PostgreSQL Docker 容器

set -e

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  创建 PostgreSQL 容器${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 数据库配置（与 .env 文件保持一致）
CONTAINER_NAME="english_tube_db"
DB_USER="english_tube"
DB_PASSWORD="dev_local_password_2024"
DB_NAME="english_tube"
DB_PORT="5432"

# 检查容器是否已存在
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}⚠️  容器 ${CONTAINER_NAME} 已存在${NC}"
    read -p "是否删除并重新创建? (y/n): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo -e "${YELLOW}🗑️  删除旧容器...${NC}"
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        echo -e "${GREEN}   ✅ 旧容器已删除${NC}"
    else
        echo -e "${GREEN}已取消${NC}"
        exit 0
    fi
fi
echo ""

# 创建 Docker volume（持久化数据）
echo -e "${YELLOW}📦 创建数据卷...${NC}"
docker volume create english_tube_postgres_data 2>/dev/null || true
echo -e "${GREEN}   ✅ 数据卷已创建${NC}"
echo ""

# 创建并启动 PostgreSQL 容器
echo -e "${YELLOW}🚀 启动 PostgreSQL 容器...${NC}"
docker run -d \
  --name ${CONTAINER_NAME} \
  -e POSTGRES_USER=${DB_USER} \
  -e POSTGRES_PASSWORD=${DB_PASSWORD} \
  -e POSTGRES_DB=${DB_NAME} \
  -e POSTGRES_INITDB_ARGS="-E UTF8 --locale=C" \
  -p ${DB_PORT}:5432 \
  -v english_tube_postgres_data:/var/lib/postgresql/data \
  --restart unless-stopped \
  postgres:15-alpine

echo -e "${GREEN}   ✅ 容器已启动${NC}"
echo ""

# 等待数据库就绪
echo -e "${YELLOW}⏳ 等待数据库启动...${NC}"
sleep 5

# 检查容器状态
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${GREEN}   ✅ PostgreSQL 运行中${NC}"
else
    echo -e "${RED}   ❌ 容器启动失败${NC}"
    docker logs ${CONTAINER_NAME}
    exit 1
fi
echo ""

# 测试连接
echo -e "${YELLOW}🔌 测试数据库连接...${NC}"
for i in {1..10}; do
    if docker exec ${CONTAINER_NAME} pg_isready -U ${DB_USER} > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ 数据库连接成功${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}   ❌ 数据库连接失败${NC}"
        exit 1
    fi
    sleep 2
done
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🎉 PostgreSQL 安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}数据库信息:${NC}"
echo -e "  容器名称: ${CONTAINER_NAME}"
echo -e "  主机: localhost"
echo -e "  端口: ${DB_PORT}"
echo -e "  用户: ${DB_USER}"
echo -e "  密码: ${DB_PASSWORD}"
echo -e "  数据库: ${DB_NAME}"
echo ""
echo -e "${BLUE}连接命令:${NC}"
echo -e "  docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME}"
echo ""
echo -e "${BLUE}管理命令:${NC}"
echo -e "  查看状态: docker ps | grep ${CONTAINER_NAME}"
echo -e "  查看日志: docker logs ${CONTAINER_NAME}"
echo -e "  停止容器: docker stop ${CONTAINER_NAME}"
echo -e "  启动容器: docker start ${CONTAINER_NAME}"
echo -e "  删除容器: docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME}"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo -e "  1. 运行数据库迁移: ./migrate.sh upgrade"
echo -e "  2. 启动后端服务: ./dev.sh"
echo ""
