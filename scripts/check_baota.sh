#!/bin/bash
# 宝塔面板诊断脚本

echo "=========================================="
echo "宝塔面板诊断"
echo "=========================================="
echo ""

# 1. 检查宝塔是否安装
echo "1. 检查宝塔是否安装..."
if [ -f "/etc/init.d/bt" ]; then
    echo "✅ 宝塔已安装"
else
    echo "❌ 宝塔未安装"
    exit 1
fi

echo ""

# 2. 检查宝塔服务状态
echo "2. 检查宝塔服务状态..."
/etc/init.d/bt status

echo ""

# 3. 获取宝塔面板信息
echo "3. 获取宝塔面板访问信息..."
/etc/init.d/bt default

echo ""

# 4. 检查端口占用
echo "4. 检查端口占用..."
PANEL_PORT=$(cat /www/server/panel/data/port.pl 2>/dev/null || echo "未找到")
echo "宝塔面板端口: $PANEL_PORT"
if [ "$PANEL_PORT" != "未找到" ]; then
    netstat -tlnp | grep ":$PANEL_PORT" || echo "端口 $PANEL_PORT 未被监听"
fi

echo ""

# 5. 检查防火墙状态
echo "5. 检查防火墙状态..."
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --list-ports | grep -q "$PANEL_PORT" && echo "✅ 防火墙已放行端口 $PANEL_PORT" || echo "⚠️  防火墙未放行端口 $PANEL_PORT"
else
    echo "系统未使用 firewalld"
fi

echo ""

# 6. 检查安全入口
echo "6. 检查安全入口..."
ENTRANCE=$(cat /www/server/panel/data/admin_path.pl 2>/dev/null || echo "/")
echo "安全入口路径: $ENTRANCE"

echo ""
echo "=========================================="
echo "完整访问地址应该是："
echo "http://81.68.234.126:$PANEL_PORT$ENTRANCE"
echo "=========================================="
