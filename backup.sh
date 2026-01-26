#!/bin/bash

# English Tube Backend 数据库备份脚本

set -e

echo "=========================================="
echo "数据库备份脚本"
echo "=========================================="

# 检查备份目录
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

# 生成备份文件名（带时间戳）
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/english_tube_${TIMESTAMP}.sql"
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"

# 从 .env.production 读取数据库配置
if [ -f ".env.production" ]; then
    source .env.production
else
    echo "❌ 未找到 .env.production 文件"
    exit 1
fi

DB_USER=${DB_USER:-english_tube}
DB_NAME=${DB_NAME:-english_tube}

echo "📦 开始备份数据库..."
echo "  数据库: $DB_NAME"
echo "  用户: $DB_USER"
echo ""

# 使用 docker-compose exec 执行备份
docker-compose exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # 压缩备份文件
    echo "🗜️  压缩备份文件..."
    gzip "$BACKUP_FILE"

    # 获取文件大小
    BACKUP_SIZE=$(du -h "$BACKUP_FILE_GZ" | cut -f1)

    echo ""
    echo "✅ 备份成功！"
    echo "  文件: $BACKUP_FILE_GZ"
    echo "  大小: $BACKUP_SIZE"
else
    echo "❌ 备份失败"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# 清理旧备份（保留最近7天）
echo ""
echo "🧹 清理旧备份（保留最近7天）..."
find "$BACKUP_DIR" -name "english_tube_*.sql.gz" -type f -mtime +7 -delete
echo "✅ 清理完成"

# 列出所有备份
echo ""
echo "📋 现有备份列表："
ls -lh "$BACKUP_DIR"/english_tube_*.sql.gz 2>/dev/null || echo "  暂无备份文件"

echo ""
echo "=========================================="
echo "💡 恢复备份的命令："
echo "  gunzip -c $BACKUP_FILE_GZ | docker-compose exec -T postgres psql -U $DB_USER $DB_NAME"
echo "=========================================="
