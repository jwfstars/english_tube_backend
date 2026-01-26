# English Tube Backend 宝塔面板部署指南

本文档介绍如何在预装宝塔面板的腾讯云轻量服务器上部署 English Tube Backend。

## 📚 相关文档

- [DNS 解析配置指南](../docs/DNS_CONFIG.md) - 域名解析到腾讯云服务器
- [SSL 证书配置指南](../docs/SSL_CONFIG.md) - HTTPS 证书申请和配置
- [环境配置说明](../uploader/README_ENV.md) - Uploader 环境切换

## 🚀 快速开始

已部署用户快速更新：

```bash
cd /www/wwwroot/english_tube
bash scripts/quick_deploy.sh  # 一键更新部署
```

新用户请按照下方完整部署流程操作。

---

## 📋 服务器信息

- **IP地址**: 81.68.234.126
- **配置**: 2核4GB内存，60GB SSD
- **流量包**: 500GB/月（带宽 5Mbps）
- **操作系统**: OpenCloudOS 9
- **预装应用**: 宝塔Linux面板

---

## 🚀 部署方案选择

### 方案一：使用宝塔 + Docker（推荐）⭐
- **优点**: 容器化部署，环境隔离，易于管理和更新
- **适合**: 熟悉 Docker 或想要标准化部署

### 方案二：使用宝塔原生环境
- **优点**: 通过宝塔 Web 界面管理，操作简单直观
- **适合**: 不熟悉 Docker，想要图形化管理

---

## 方案一：宝塔 + Docker 部署（推荐）

### 1. 登录宝塔面板

访问宝塔面板（默认端口 8888）：
```
http://81.68.234.126:8888
```

> **注意**: 首次登录需要查看初始账号密码，在腾讯云控制台的"应用管理"或通过 SSH 登录服务器运行：
> ```bash
> sudo /etc/init.d/bt default
> ```

### 2. 在宝塔面板安装 Docker

**方式 1: 通过宝塔软件商店**
1. 进入宝塔面板
2. 点击左侧 **软件商店**
3. 搜索 **Docker**
4. 点击 **安装**
5. 同时安装 **Docker Compose**

**方式 2: 通过SSH命令行**
```bash
# SSH 登录服务器
ssh root@81.68.234.126

# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 启动 Docker
systemctl start docker
systemctl enable docker

# 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 3. 配置 GitHub SSH 密钥（首次需要）

**生成并添加 SSH 密钥**:
```bash
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"
# 一路回车使用默认设置

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub
# 复制输出的整行内容

# 3. 添加到 GitHub
# 访问 https://github.com/settings/keys
# 点击 "New SSH key"，粘贴公钥并保存

# 4. 测试连接
ssh -T git@github.com
# 首次提示输入 yes，成功会显示欢迎信息
```

### 4. 克隆项目代码

**方式 1: 通过 Git + SSH（推荐）** ⭐
```bash
# 进入网站根目录
cd /www/wwwroot

# 克隆仓库
git clone git@github.com:jwfstars/english_tube.git

# 进入 backend 目录
cd english_tube/backend
```

**方式 2: 通过宝塔文件管理器**
1. 在宝塔面板点击 **文件**
2. 创建目录 `/www/wwwroot/english_tube`
3. 上传 `backend` 文件夹所有内容

### 5. 配置环境变量

在宝塔文件管理器中：
1. 进入 `/www/wwwroot/english_tube/backend`
2. 复制 `.env.production` 为 `.env.production.local`
3. 点击编辑，修改以下配置：

```bash
# 数据库密码（必须改！）
DB_PASSWORD=your_super_strong_password_here

# JWT 密钥（必须改！在服务器上运行 openssl rand -hex 32 生成）
SECRET_KEY=your_generated_64_character_hex_string

# 腾讯云 VOD
VOD_PLAY_KEY=your-vod-play-key

# CORS（替换为你的域名，如果暂时没有域名可以先用IP）
BACKEND_CORS_ORIGINS=["http://81.68.234.126","https://yourdomain.com"]

# 腾讯云短信（如果使用）
TENCENT_SMS_SECRET_ID=your-sms-secret-id
TENCENT_SMS_SECRET_KEY=your-sms-secret-key
TENCENT_SMS_SDK_APP_ID=your-app-id
TENCENT_SMS_SIGN_NAME=your-signature
TENCENT_SMS_TEMPLATE_ID=your-template-id
```

**生成 SECRET_KEY**:
在宝塔"终端"或 SSH 中运行：
```bash
openssl rand -hex 32
```

### 6. 修改 docker-compose.yml

将 `env_file` 改为：
```yaml
env_file:
  - .env.production.local
```

### 7. 配置宝塔安全组/防火墙

在宝塔面板 -> **安全** 中放行以下端口：
- `80` - HTTP
- `443` - HTTPS
- `8000` - Backend API（可选，调试用）

**同时在腾讯云控制台配置防火墙：**
1. 进入轻量应用服务器控制台
2. 点击实例 -> **防火墙**
3. 添加规则：
   - 协议: TCP
   - 端口: 80, 443, 8000
   - 来源: 0.0.0.0/0（所有IP）

### 8. 部署服务

#### 首次部署

在 SSH 终端或宝塔终端中：
```bash
cd /www/wwwroot/english_tube/backend

# 给脚本添加执行权限
chmod +x deploy.sh update.sh backup.sh logs.sh

# 一键部署
./deploy.sh
```

#### 日常更新（推荐）⭐

项目提供了便捷的一键部署脚本：

```bash
cd /www/wwwroot/english_tube

# 快速更新部署（推荐）
bash scripts/quick_deploy.sh

# 或完整部署（适合大改动）
bash scripts/deploy_backend.sh
```

**脚本功能**：
- `quick_deploy.sh` - 拉取代码 → 重新构建 → 启动（3步搞定）
- `deploy_backend.sh` - 完整的停止 → 清理 → 构建 → 启动流程，显示详细日志

### 9. 验证部署

```bash
# 查看服务状态
cd /www/wwwroot/english_tube/backend
docker-compose ps

# 检查健康状态
curl http://localhost:8000/api/health

# 应该返回：
# {"status":"ok","database":"ok","version":"1.0.0"}
```

**API 路径结构**（所有 API 相关路径统一在 `/api` 前缀下）：

在浏览器访问：
- 根路径: http://81.68.234.126:8000/
- 健康检查: http://81.68.234.126:8000/api/health
- API 文档: http://81.68.234.126:8000/api/docs
- ReDoc 文档: http://81.68.234.126:8000/api/redoc
- 业务 API: http://81.68.234.126:8000/api/v1/*

---

## 方案二：宝塔原生环境部署

### 1. 安装软件

在宝塔面板 -> **软件商店** 中安装：
- **Nginx** 1.22+
- **PostgreSQL** 15
- **Python项目管理器**（或手动安装 Python 3.11）

### 2. 配置数据库

1. 打开宝塔 -> **数据库**
2. 添加 PostgreSQL 数据库：
   - 数据库名: `english_tube`
   - 用户名: `english_tube`
   - 密码: 设置强密码

### 3. 配置 Python 环境

**安装 Python 3.11**（如果系统没有）:
```bash
# SSH 登录
yum install -y python3.11 python3.11-pip
```

**创建虚拟环境**:
```bash
cd /www/wwwroot/english_tube/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. 配置环境变量

编辑 `.env.production.local`，配置数据库连接：
```bash
DATABASE_URL=postgresql://english_tube:your_password@localhost:5432/english_tube
ASYNC_DATABASE_URL=postgresql+asyncpg://english_tube:your_password@localhost:5432/english_tube
```

### 5. 运行数据库迁移

```bash
source venv/bin/activate
alembic upgrade head
```

### 6. 配置进程守护（使用宝塔 Python 项目管理器）

1. 宝塔面板 -> **网站** -> **Python项目**
2. 添加项目：
   - 项目路径: `/www/wwwroot/english_tube/backend`
   - Python版本: 3.11
   - 框架: FastAPI
   - 启动文件: `app/main.py`
   - 端口: 8000
   - 启动方式: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2`

### 7. 配置 Nginx 反向代理

在宝塔面板 -> **网站** -> **添加站点**:
- 域名: 输入你的域名（或暂时用 IP）
- PHP版本: 纯静态

然后点击站点 -> **设置** -> **反向代理**，添加：
```nginx
目标URL: http://127.0.0.1:8000
发送域名: $host
```

---

## 🌐 配置域名和 HTTPS

### 域名配置

如果你在其他平台（如火山云）购买了域名，需要配置 DNS 解析到腾讯云服务器。

**详细配置步骤请参考**：[DNS 解析配置指南](../docs/DNS_CONFIG.md)

**快速配置**：
1. 在腾讯云 DNS 解析添加域名：https://console.cloud.tencent.com/cns
2. 在域名注册商修改 DNS 服务器为腾讯云的 DNS
3. 添加解析记录：

```
类型    主机记录    记录值
A       @           81.68.234.126  # 主域名
A       www         81.68.234.126  # www 子域名
A       api         81.68.234.126  # API（可选）
A       admin       81.68.234.126  # 管理后台（推荐）
```

### SSL 证书配置

**详细配置步骤请参考**：[SSL 证书配置指南](../docs/SSL_CONFIG.md)

#### 方案一：Let's Encrypt 免费证书（推荐）⭐

1. 宝塔面板 → 网站 → 点击你的站点
2. 点击 **SSL** 标签
3. 选择 **Let's Encrypt**
4. 勾选域名（支持多个子域名）：
   - ☑ `englishtube.top`
   - ☑ `www.englishtube.top`
   - ☑ `admin.englishtube.top`
5. 输入邮箱并点击 **申请**
6. 开启 **强制 HTTPS**

**优点**：完全免费，自动续期，支持多个子域名

#### 方案二：腾讯云免费证书

1. 访问：https://console.cloud.tencent.com/ssl
2. 申请免费 DV 证书
3. 下载 Nginx 版本证书
4. 在宝塔面板 SSL 中选择「其他证书」，粘贴证书内容

### 配置 Nginx 反向代理（重要）

在宝塔面板配置反向代理，将域名请求转发到后端：

1. **添加站点**（如果还没添加）
   - 网站 → 添加站点
   - 域名：`englishtube.top` 和 `www.englishtube.top`

2. **配置反向代理**
   - 站点设置 → 配置文件
   - 在 SSL 的 `server` 块中添加：

```nginx
# 反向代理所有 /api 开头的请求到后端
location /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

3. **保存并重载 Nginx**

### 配置管理后台（Admin）

**详细配置请参考**：[管理后台 Nginx 配置指南](../docs/ADMIN_NGINX_CONFIG.md)

**推荐使用路径方式**：`englishtube.top/admin`（只需一个 SSL 证书）

1. **在主站点 Nginx 配置中添加**
   - 网站 → `englishtube.top` → 设置 → 配置文件
   - 在 HTTPS `server` 块中添加：

```nginx
# 管理后台
location /admin {
    alias /www/wwwroot/englishtube.top/admin;
    index index.html;
}

# 管理后台静态资源缓存
location ~* ^/admin/.*\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    alias /www/wwwroot/englishtube.top/admin;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

2. **运行部署脚本**
   ```bash
   cd /www/wwwroot/english_tube
   bash scripts/quick_deploy.sh
   ```

脚本会自动：
- 构建管理后台
- 创建 `/www/wwwroot/englishtube.top/admin/` 目录
- 复制构建产物到该目录

### 验证 HTTPS 配置

配置完成后，访问以下地址应该都能正常工作（绿色锁标志）：

```bash
# 在服务器或本地测试
curl https://englishtube.top/api/health
curl https://englishtube.top/api/docs
curl https://englishtube.top/admin
```

浏览器访问：
- ✅ https://englishtube.top/api/health - 健康检查
- ✅ https://englishtube.top/api/docs - API 文档
- ✅ https://englishtube.top/api/v1/videos - 业务 API
- ✅ https://englishtube.top/admin - 管理后台

---

## 📊 日常维护（宝塔面板）

### 查看服务状态
- **Docker方案**: 宝塔 -> **Docker** -> 查看容器状态
- **原生方案**: 宝塔 -> **Python项目** -> 查看项目状态

### 查看日志
- **Docker方案**:
  ```bash
  cd /www/wwwroot/english_tube/backend
  ./logs.sh
  ```
- **原生方案**: 宝塔 -> **Python项目** -> 查看日志

### 数据库备份
**自动备份**:
1. 宝塔 -> **计划任务**
2. 添加任务:
   - 任务类型: Shell脚本
   - 脚本内容:
     ```bash
     cd /www/wwwroot/english_tube/backend && ./backup.sh
     ```
   - 执行周期: 每天凌晨3点

### 更新代码
```bash
cd /www/wwwroot/english_tube/backend

# 拉取最新代码
git pull

# Docker方案
./update.sh

# 原生方案
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
# 在宝塔面板重启Python项目
```

---

## 🔍 故障排查

### 查看宝塔日志
- 宝塔面板 -> **日志** -> 查看错误日志

### 查看 Nginx 日志
- 宝塔面板 -> **网站** -> 站点设置 -> **日志**

### 查看数据库状态
- 宝塔面板 -> **数据库** -> PostgreSQL -> 管理

### 端口占用检查
在宝塔终端运行：
```bash
netstat -tlnp | grep 8000
```

---

## 💡 推荐配置

### 磁盘空间管理
当前系统盘 60GB，建议：
- 日志定期清理（保留7天）
- 数据库备份定期清理（保留30天）
- Docker 镜像定期清理

在宝塔 -> **计划任务** 中添加：
```bash
# 清理7天前的日志
find /www/wwwroot/english_tube/backend/logs -name "*.log" -mtime +7 -delete

# 清理30天前的备份
find /www/wwwroot/english_tube/backend/backups -name "*.sql.gz" -mtime +30 -delete

# 清理 Docker（如果使用Docker方案）
docker system prune -af --volumes
```

### 流量包监控
- 当前流量包: 500GB/月
- 建议启用宝塔的流量监控告警
- 考虑启用 CDN（如腾讯云CDN）减轻流量压力

### 性能优化
在宝塔 -> **软件商店** 中：
- 安装 **Redis** 用于缓存（可选）
- 安装 **Memcached** 用于会话存储（可选）

---

## 📞 快捷链接

- **宝塔面板**: http://81.68.234.126:8888
- **Backend API**: http://81.68.234.126:8000
- **API 文档**: http://81.68.234.126:8000/docs
- **腾讯云控制台**: https://console.cloud.tencent.com/lighthouse

---

## ⚠️ 安全建议

1. **修改宝塔默认端口**
   - 宝塔面板 -> **面板设置** -> 修改端口（默认8888改为其他）

2. **开启宝塔BasicAuth**
   - 宝塔面板 -> **面板设置** -> 开启 BasicAuth

3. **定期更新系统**
   ```bash
   yum update -y
   ```

4. **开启宝塔防火墙**
   - 宝塔 -> **安全** -> 配置防火墙规则

5. **禁用root SSH登录**（可选）
   - 创建新用户后再禁用

---

**最后更新**: 2025-12-30
**服务器IP**: 81.68.234.126
**预计部署时间**: 30-60分钟
