#!/bin/bash
# 配置迁移脚本

echo "================================="
echo "环境配置迁移脚本"
echo "================================="
echo ""

# 1. 删除临时目录
if [ -d "../../../english_tube_with_history" ]; then
    echo "❌ 删除临时目录 english_tube_with_history..."
    rm -rf ../../../english_tube_with_history
    echo "✅ 已删除"
fi

# 2. 检查是否存在 .env 文件
if [ -f ".env" ]; then
    echo "⚠️  .env 文件已存在，创建备份..."
    cp .env .env.backup
    echo "✅ 备份已保存到 .env.backup"
else
    echo "📝 从模板创建 .env 文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
fi

# 3. 检查是否需要迁移旧配置
if [ -f ".env.production" ]; then
    echo ""
    echo "⚠️  发现旧的 .env.production 文件"
    read -p "是否从 .env.production 迁移配置到 .env? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.production .env
        echo "✅ 已迁移配置"
    fi
fi

echo ""
echo "================================="
echo "⚠️  重要提醒"
echo "================================="
echo "1. 请编辑 .env 文件，修改以下配置："
echo "   - DB_PASSWORD (数据库密码)"
echo "   - SECRET_KEY (运行: openssl rand -hex 32)"
echo "   - VOD_PLAY_KEY (腾讯云 VOD 密钥)"
echo ""
echo "2. 本地开发配置 CORS:"
echo "   BACKEND_CORS_ORIGINS=[\"http://localhost:8858\"]"
echo ""
echo "3. 启动服务:"
echo "   docker-compose up -d"
echo ""
echo "✅ 配置迁移完成！"
