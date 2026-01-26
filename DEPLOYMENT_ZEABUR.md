# Zeabur 部署指南

本文档描述如何将 English Tube 后端部署到 Zeabur 平台。

> **部署方式**：本项目使用 Zeabur 原生部署（无需 Docker），充分利用平台的自动优化和快速启动特性。

## 🚀 部署步骤

### 1. 准备工作

确保你的代码已经推送到 GitHub 仓库。

### 2. 创建 Zeabur 项目

1. 访问 [Zeabur Dashboard](https://dash.zeabur.com/)
2. 点击 "Create Project"
3. 选择部署区域（建议选择距离用户最近的区域）

### 3. 部署 PostgreSQL 数据库

1. 在项目中点击 "Add Service"
2. 选择 "Prebuilt" → "PostgreSQL"
3. 等待数据库部署完成
4. 点击 PostgreSQL 服务，进入详情页
5. 复制以下连接信息：
   - `POSTGRES_HOST`
   - `POSTGRES_PORT`
   - `POSTGRES_USERNAME`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DATABASE`

### 4. 部署后端服务

1. 在项目中点击 "Add Service"
2. 选择 "Git" → 连接你的 GitHub 仓库
3. 选择整个仓库（根目录）
4. Zeabur 会自动检测为 Python 项目（基于 `zbpack.json`）
5. 自动安装依赖并部署

### 5. 配置环境变量

在后端服务的 "Variables" 标签页添加以下环境变量：

#### 必需配置

```bash
# 数据库配置（使用 Zeabur PostgreSQL 的连接信息）
DATABASE_URL=postgresql://${POSTGRES_USERNAME}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DATABASE}
ASYNC_DATABASE_URL=postgresql+asyncpg://${POSTGRES_USERNAME}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DATABASE}

# JWT 配置（⚠️ 生产环境必须使用强密钥）
SECRET_KEY=<使用 openssl rand -hex 32 生成>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# API 配置
API_V1_STR=/api/v1
PROJECT_NAME=English Tube API
VERSION=1.0.0

# CORS 配置（替换为你的实际域名）
BACKEND_CORS_ORIGINS=["https://你的前端域名.zeabur.app","https://你的管理后台域名.zeabur.app"]
```

#### 可选配置

```bash
# 腾讯云 VOD 视频点播
VOD_APP_ID=1253432963
VOD_PLAY_KEY=你的密钥
VOD_PSIGN_EXPIRE_SECONDS=3600
VOD_PSIGN_AUDIO_VIDEO_TYPE=Original
VOD_PSIGN_RAW_ADAPTIVE_DEFINITION=
VOD_PSIGN_TRANSCODE_DEFINITION=

# 腾讯云短信服务（可选）
TENCENT_SMS_SECRET_ID=你的密钥ID
TENCENT_SMS_SECRET_KEY=你的密钥
TENCENT_SMS_SDK_APP_ID=你的APP_ID
TENCENT_SMS_SIGN_NAME=你的签名
TENCENT_SMS_TEMPLATE_ID=你的模板ID
TENCENT_SMS_REGION=ap-guangzhou
SMS_CODE_EXPIRE_MINUTES=10
SMS_DEBUG=false
```

### 6. 获取服务域名

1. 部署成功后，在后端服务详情页找到 "Networking" 标签
2. 点击 "Generate Domain" 生成域名
3. 记录下域名（例如：`https://your-backend.zeabur.app`）

### 7. 配置自定义域名（可选）

1. 在 "Networking" 标签页点击 "Custom Domain"
2. 添加你的域名（例如：`api.yourdomain.com`）
3. 按照提示配置 DNS CNAME 记录

### 8. 验证部署

访问以下端点验证部署是否成功：

```bash
# 健康检查
curl https://your-backend.zeabur.app/api/health

# API 文档
https://your-backend.zeabur.app/api/docs
```

## 🔄 数据库迁移

Zeabur 上的部署会在启动时自动运行数据库迁移（`alembic upgrade head`），见 Dockerfile 的启动命令。

如需手动运行迁移：

1. 在 Zeabur 服务详情页，进入 "Terminal" 标签
2. 运行命令：
   ```bash
   alembic upgrade head
   ```

## 📊 监控与日志

### 查看日志

在 Zeabur 服务详情页的 "Logs" 标签可以查看实时日志。

### 查看资源使用

在 "Metrics" 标签可以查看：
- CPU 使用率
- 内存使用情况
- 网络流量

## 🔧 常见问题

### 1. 数据库连接失败

**问题**：服务启动时报错 "could not connect to server"

**解决方案**：
- 确认 PostgreSQL 服务已经启动
- 检查 `DATABASE_URL` 环境变量是否正确
- 确认使用的是内部连接地址（不是公网地址）

### 2. 数据库迁移失败

**问题**：启动时 alembic 迁移失败

**解决方案**：
- 检查数据库连接是否正常
- 查看迁移脚本是否有语法错误
- 尝试手动在 Terminal 中运行 `alembic upgrade head`

### 3. CORS 错误

**问题**：前端调用 API 时报 CORS 错误

**解决方案**：
- 在 `BACKEND_CORS_ORIGINS` 环境变量中添加前端域名
- 确保域名格式正确（包含 https://）
- 重启服务使配置生效

### 4. 端口配置

Zeabur 会自动设置 `PORT` 环境变量，不需要手动配置。Dockerfile 中已经配置为使用 `${PORT:-8000}`。

## 🔐 安全建议

1. **生产环境密钥**：
   ```bash
   # 使用此命令生成强密钥
   openssl rand -hex 32
   ```

2. **最小权限原则**：
   - 不要在环境变量中存储不必要的敏感信息
   - 定期轮换密钥

3. **CORS 配置**：
   - 不要使用 `"*"` 作为 CORS origin
   - 只添加必要的域名

## 📈 性能优化

### 1. 增加 Worker 数量

根据流量调整 Dockerfile 中的 `--workers` 参数：
```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]
```

### 2. 启用数据库连接池

已在 `app/core/database.py` 中配置，默认启用。

### 3. 使用 CDN

对于静态资源，建议使用 CDN 加速。

## 🔄 更新部署

每次推送到 GitHub 主分支，Zeabur 会自动重新部署：

1. 提交代码并推送：
   ```bash
   git add .
   git commit -m "Update backend"
   git push origin main
   ```

2. Zeabur 会自动检测变更并重新构建部署

## 💰 费用估算

Zeabur 按使用量计费：
- **免费额度**：每月 $5 美元信用额度
- **计费项**：CPU、内存、网络流量、持久化存储
- **数据库**：PostgreSQL 按使用量计费

建议开启预算提醒，避免超支。

## 📞 获取帮助

- [Zeabur 文档](https://zeabur.com/docs)
- [Zeabur Discord 社区](https://discord.gg/zeabur)
- [GitHub Issues](https://github.com/zeabur/zeabur)

## 🎉 部署完成

部署成功后，你的 API 将可以通过以下地址访问：
- API 文档：`https://your-backend.zeabur.app/api/docs`
- 健康检查：`https://your-backend.zeabur.app/api/health`
- API 端点：`https://your-backend.zeabur.app/api/v1/*`
