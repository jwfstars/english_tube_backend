# English Tube Backend 部署指南

本文档介绍如何将 English Tube Backend 部署到腾讯云服务器（或任何支持 Docker 的服务器）。

## 📋 目录

- [部署架构](#部署架构)
- [准备工作](#准备工作)
- [服务器配置](#服务器配置)
- [部署步骤](#部署步骤)
- [域名和 HTTPS 配置](#域名和-https-配置)
- [日常维护](#日常维护)
- [故障排查](#故障排查)

---

## 🏗️ 部署架构

```
┌─────────────────────────────────────────────┐
│           腾讯云服务器 (CVM)                  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Nginx (反向代理)                    │   │
│  │  - HTTP/HTTPS 端口 80/443           │   │
│  └─────────────┬───────────────────────┘   │
│                │                            │
│  ┌─────────────▼───────────────────────┐   │
│  │  Backend API (Docker)                │   │
│  │  - FastAPI + Uvicorn                │   │
│  │  - 端口 8000                         │   │
│  └─────────────┬───────────────────────┘   │
│                │                            │
│  ┌─────────────▼───────────────────────┐   │
│  │  PostgreSQL 15 (Docker)              │   │
│  │  - 端口 5432                         │   │
│  │  - 数据持久化存储                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
  火山云 TOS              腾讯云 VOD/SMS
  (对象存储)             (视频点播/短信)
```

---

## 📦 准备工作

### 1. 腾讯云资源

#### 云服务器 (CVM)
- **配置建议**: 2核4GB内存，80GB SSD
- **系统镜像**: Ubuntu 22.04 LTS
- **带宽**: 5Mbps 起步
- **费用**: 约 ¥70-100/月

#### 安全组配置
开放以下端口：
- `22` - SSH
- `80` - HTTP
- `443` - HTTPS
- `8000` - Backend API（可选，调试用）

#### 域名（可选）
- 购买或使用已有域名
- 配置 DNS 解析到服务器公网 IP

### 2. 第三方服务密钥

准备以下服务的密钥：

**必需**:
- 火山云 TOS（对象存储）
  - `TOS_ACCESS_KEY`
  - `TOS_SECRET_KEY`
- 腾讯云 VOD（视频点播）
  - `VOD_APP_ID`
  - `VOD_PLAY_KEY`

**可选**:
- 腾讯云 SMS（短信服务）
  - `TENCENT_SMS_SECRET_ID`
  - `TENCENT_SMS_SECRET_KEY`
  - `TENCENT_SMS_SDK_APP_ID`
  - `TENCENT_SMS_SIGN_NAME`
  - `TENCENT_SMS_TEMPLATE_ID`

---

## 🖥️ 服务器配置

### 1. 登录服务器

```bash
ssh root@your-server-ip
```

### 2. 安装 Docker

```bash
# 使用官方安装脚本
curl -fsSL https://get.docker.com | sh

# 启动 Docker 服务
systemctl start docker
systemctl enable docker

# 验证安装
docker --version
docker-compose --version
```

### 3. 安装其他工具

```bash
apt update
apt install -y git curl wget
```

### 4. 克隆项目代码

```bash
# 创建项目目录
mkdir -p /opt/apps
cd /opt/apps

# 克隆代码（替换为你的仓库地址）
git clone https://github.com/yourusername/english_tube.git
cd english_tube/backend
```

---

## 🚀 部署步骤

### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.production .env.production.local

# 编辑配置文件
vim .env.production.local
```

**必须修改的配置**：

```bash
# 数据库密码（必须改！）
DB_PASSWORD=your_strong_password_here

# JWT 密钥（必须改！）
# 生成强密钥：openssl rand -hex 32
SECRET_KEY=your_generated_secret_key_64_characters

# 火山云 TOS
TOS_ACCESS_KEY=your-tos-access-key
TOS_SECRET_KEY=your-tos-secret-key

# 腾讯云 VOD
VOD_PLAY_KEY=your-vod-play-key

# CORS（替换为你的域名）
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://admin.yourdomain.com"]

# 腾讯云短信（如果使用）
TENCENT_SMS_SECRET_ID=your-sms-secret-id
TENCENT_SMS_SECRET_KEY=your-sms-secret-key
TENCENT_SMS_SDK_APP_ID=your-app-id
TENCENT_SMS_SIGN_NAME=your-signature
TENCENT_SMS_TEMPLATE_ID=your-template-id
```

### 2. 修改 docker-compose.yml

```bash
# 确保使用正确的环境文件
vim docker-compose.yml

# 将 .env.production 改为 .env.production.local
```

### 3. 运行部署脚本

```bash
# 给脚本添加执行权限（如果还没有）
chmod +x deploy.sh update.sh backup.sh logs.sh

# 运行部署
./deploy.sh
```

部署脚本会自动：
- 创建必要的目录
- 检查 Docker 环境
- 构建镜像
- 启动数据库
- 运行数据库迁移
- 启动所有服务
- 执行健康检查

### 4. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 检查健康状态
curl http://localhost:8000/health

# 查看日志
./logs.sh
```

如果看到类似输出，说明部署成功：

```json
{
  "status": "ok",
  "database": "ok",
  "version": "1.0.0"
}
```

---

## 🌐 域名和 HTTPS 配置

### 1. 配置域名解析

在你的域名服务商（如腾讯云 DNSPod）添加 A 记录：

```
类型    主机记录    记录值
A       api         your-server-ip
A       @           your-server-ip
```

### 2. 申请 SSL 证书

**方式一：使用 Let's Encrypt（推荐）**

```bash
# 安装 certbot
apt install -y certbot python3-certbot-nginx

# 申请证书
certbot certonly --standalone -d api.yourdomain.com

# 证书位置：
# /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/api.yourdomain.com/privkey.pem
```

**方式二：使用腾讯云免费 DV 证书**

1. 在腾讯云控制台申请免费 SSL 证书
2. 下载 Nginx 格式证书
3. 上传到服务器 `nginx/ssl/` 目录

### 3. 配置 Nginx HTTPS

```bash
# 复制证书到 nginx 目录
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem nginx/ssl/

# 编辑 Nginx 配置
vim nginx/conf.d/default.conf
```

取消 HTTPS 部分的注释，并修改域名：

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;  # 修改为你的域名

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # ... 其他配置
}
```

同时在 HTTP 部分添加重定向：

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;  # 修改为你的域名

    # 强制重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}
```

### 4. 重启 Nginx

```bash
docker-compose restart nginx

# 验证 HTTPS
curl https://api.yourdomain.com/health
```

### 5. 自动续期证书

```bash
# 添加 cron 任务
crontab -e

# 每月1号凌晨2点自动续期
0 2 1 * * certbot renew --quiet && docker-compose restart nginx
```

---

## 🔧 日常维护

### 服务管理

```bash
# 查看服务状态
docker-compose ps

# 查看日志
./logs.sh

# 重启服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 启动所有服务
docker-compose up -d
```

### 代码更新

```bash
# 拉取最新代码并更新服务
./update.sh
```

### 数据库备份

```bash
# 手动备份
./backup.sh

# 设置定时备份（每天凌晨3点）
crontab -e

# 添加以下行
0 3 * * * cd /opt/apps/english_tube/backend && ./backup.sh >> logs/backup.log 2>&1
```

### 恢复备份

```bash
# 列出备份文件
ls -lh backups/

# 恢复指定备份
gunzip -c backups/english_tube_20250101_030000.sql.gz | \
  docker-compose exec -T postgres psql -U english_tube english_tube
```

### 查看资源占用

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看数据库大小
docker-compose exec postgres psql -U english_tube -d english_tube -c "
  SELECT pg_size_pretty(pg_database_size('english_tube')) as size;
"
```

### 清理空间

```bash
# 清理未使用的 Docker 镜像
docker image prune -a

# 清理旧日志（保留最近7天）
find logs/ -name "*.log" -type f -mtime +7 -delete

# 清理旧备份（保留最近30天）
find backups/ -name "*.sql.gz" -type f -mtime +30 -delete
```

---

## 🔍 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 检查配置文件
cat .env.production.local

# 检查端口占用
netstat -tlnp | grep 8000

# 强制重建容器
docker-compose down
docker-compose up -d --force-recreate
```

### 数据库连接失败

```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U english_tube

# 查看数据库日志
docker-compose logs postgres

# 进入数据库容器
docker-compose exec postgres psql -U english_tube -d english_tube

# 检查数据库连接字符串
# 容器内应使用主机名 "postgres" 而非 "localhost"
```

### 健康检查失败

```bash
# 测试健康检查端点
curl -v http://localhost:8000/health

# 检查 Backend 日志
docker-compose logs -f backend

# 检查数据库连接
docker-compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database OK')
"
```

### Nginx 无法访问

```bash
# 检查 Nginx 配置
docker-compose exec nginx nginx -t

# 查看 Nginx 日志
tail -f nginx/logs/error.log

# 检查端口
netstat -tlnp | grep :80
netstat -tlnp | grep :443

# 重启 Nginx
docker-compose restart nginx
```

### 磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 查看 Docker 磁盘占用
docker system df

# 清理 Docker 缓存
docker system prune -a --volumes

# 清理日志
truncate -s 0 logs/*.log

# 清理旧备份
rm backups/english_tube_2024*.sql.gz
```

---

## 📊 监控和告警（可选）

### 使用 UptimeRobot 监控

1. 注册 [UptimeRobot](https://uptimerobot.com/)（免费）
2. 添加 HTTP(s) Monitor
3. 监控 URL: `https://api.yourdomain.com/health`
4. 检查间隔: 5分钟
5. 告警方式: 邮件/微信

### 服务器监控

```bash
# 安装 htop（进程监控）
apt install htop

# 安装 iftop（网络监控）
apt install iftop

# 查看实时资源
htop
iftop
```

---

## 🔒 安全建议

1. **防火墙配置**
   ```bash
   # 安装 UFW
   apt install ufw

   # 配置规则
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ufw enable
   ```

2. **SSH 安全**
   ```bash
   # 禁用密码登录，仅使用密钥
   vim /etc/ssh/sshd_config
   # PasswordAuthentication no

   # 修改 SSH 端口（可选）
   # Port 2222

   systemctl restart sshd
   ```

3. **数据库安全**
   - 使用强密码
   - 不要暴露 5432 端口到公网
   - 定期备份

4. **环境变量安全**
   - `.env.production.local` 设置为 600 权限
   - 不要提交到 Git
   - 定期轮换密钥

---

## 📝 常见问题

**Q: 部署后 API 无法访问？**
A: 检查安全组是否开放 80/443 端口，检查 Nginx 配置是否正确。

**Q: 数据库迁移失败？**
A: 查看日志 `docker-compose logs backend`，确保数据库已完全启动。

**Q: 如何回滚到之前的版本？**
A: 使用 Git 回滚代码后运行 `./update.sh`。

**Q: 容器重启后数据丢失？**
A: 检查 `docker-compose.yml` 中的 volumes 配置是否正确。

**Q: 内存占用过高？**
A: 减少 Uvicorn workers 数量，或升级服务器配置。

---

## 📞 获取帮助

如果遇到问题：
1. 查看日志：`./logs.sh`
2. 检查服务状态：`docker-compose ps`
3. 查看本文档的故障排查部分
4. 提交 Issue 到项目仓库

---

## 📄 相关文件

- `Dockerfile` - Docker 镜像定义
- `docker-compose.yml` - 服务编排配置
- `.env.production` - 环境变量模板
- `nginx/conf.d/default.conf` - Nginx 配置
- `deploy.sh` - 部署脚本
- `update.sh` - 更新脚本
- `backup.sh` - 备份脚本
- `logs.sh` - 日志查看脚本

---

**最后更新**: 2025-12-30
**版本**: 1.0.0
