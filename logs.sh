#!/bin/bash

# English Tube Backend 日志查看脚本

echo "=========================================="
echo "日志查看工具"
echo "=========================================="
echo ""
echo "选择要查看的日志："
echo "  1) Backend API 日志"
echo "  2) PostgreSQL 数据库日志"
echo "  3) Nginx 日志"
echo "  4) 所有服务日志"
echo "  5) 实时跟踪所有日志"
echo ""
read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "📋 Backend API 日志（最近100行）："
        docker-compose logs --tail=100 backend
        ;;
    2)
        echo ""
        echo "📋 PostgreSQL 数据库日志（最近100行）："
        docker-compose logs --tail=100 postgres
        ;;
    3)
        echo ""
        echo "📋 Nginx 日志（最近100行）："
        docker-compose logs --tail=100 nginx
        ;;
    4)
        echo ""
        echo "📋 所有服务日志（最近50行）："
        docker-compose logs --tail=50
        ;;
    5)
        echo ""
        echo "📋 实时跟踪所有日志（按 Ctrl+C 退出）："
        docker-compose logs -f
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "💡 其他有用的命令："
echo "  - 实时查看 Backend: docker-compose logs -f backend"
echo "  - 导出日志到文件: docker-compose logs > logs.txt"
echo "  - 查看容器状态: docker-compose ps"
echo "=========================================="
