# 部署方案说明

## 🎯 推荐部署方式

### Zeabur 原生部署（无 Docker）⭐ 推荐

**为什么选择这个方案？**

1. **更快速**
   - 自动检测 Python 项目
   - 30秒-1分钟完成部署
   - 冷启动时间 < 5秒

2. **更省钱**
   - 按实际使用计费
   - 无 Docker 层开销
   - 智能休眠节省成本

3. **更灵活**
   - 独立扩展后端和数据库
   - 实时日志查看
   - 一键回滚

4. **自动优化**
   - Zeabur 自动优化容器
   - 自动 HTTPS 配置
   - CDN 加速

## 📁 项目配置

### zbpack.json

```json
{
  "python": {
    "version": "3.12",
    "entry": "app/main.py",
    "package_manager": "pip"
  },
  "start_command": "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"
}
```

**关键配置说明**：
- `version: "3.12"` - 使用 Python 3.12（与本地一致）
- `entry` - 应用入口文件
- `start_command` - 启动前先运行数据库迁移

### 数据库连接

代码已自动处理 Zeabur 的 `postgres://` URL 格式：

```python
# app/core/database.py
def _build_async_url(url: str) -> str:
    """支持多种 URL 格式"""
    if url.startswith("postgres://"):
        # Zeabur 格式
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    # ... 其他格式
```

## 🚀 部署步骤

### 1. 推送代码到 GitHub

```bash
git add .
git commit -m "feat: optimize for Zeabur native deployment"
git push origin main
```

### 2. Zeabur 上创建服务

#### 2.1 创建项目
1. 登录 https://dash.zeabur.com/
2. 点击 "Create Project"
3. 选择区域（推荐：Hong Kong 或 Singapore）

#### 2.2 添加 PostgreSQL
1. 点击 "Add Service"
2. 选择 "Marketplace" → "PostgreSQL"
3. 等待部署完成（约30秒）

#### 2.3 添加后端服务
1. 点击 "Add Service"
2. 选择 "Git"
3. 连接 GitHub 仓库 `jwfstars/english_tube_backend`
4. Zeabur 自动检测为 Python 项目
5. 等待部署完成（约1分钟）

### 3. 配置环境变量

在后端服务的 "Variables" 页面添加：

```bash
# 数据库（Zeabur 会自动注入 POSTGRES_URL）
DATABASE_URL=${POSTGRES_URL}
ASYNC_DATABASE_URL=${POSTGRES_URL}

# JWT
SECRET_KEY=<运行: openssl rand -hex 32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS（替换为你的实际域名）
BACKEND_CORS_ORIGINS=["https://your-frontend.zeabur.app"]

# 腾讯云 VOD
VOD_APP_ID=1253432963
VOD_PLAY_KEY=你的密钥
VOD_PSIGN_EXPIRE_SECONDS=3600
VOD_PSIGN_AUDIO_VIDEO_TYPE=Original

# 可选：腾讯云短信
TENCENT_SMS_SECRET_ID=你的ID
TENCENT_SMS_SECRET_KEY=你的密钥
# ... 其他短信配置
```

### 4. 生成域名

1. 进入后端服务详情页
2. 点击 "Networking" 标签
3. 点击 "Generate Domain"
4. 复制生成的域名

### 5. 验证部署

```bash
# 健康检查
curl https://your-backend.zeabur.app/api/health

# 应返回
{
  "status": "ok",
  "database": "ok",
  "version": "1.0.0"
}
```

## 📊 部署对比

| 项目 | Zeabur 原生 | Docker 方式 |
|------|------------|------------|
| 部署速度 | ⚡ 30秒-1分钟 | 🐢 3-5分钟 |
| 冷启动 | ⚡ < 5秒 | 🐢 10-30秒 |
| 配置 | ✅ 简单 | ⚠️ 需要 Dockerfile |
| 成本 | 💰 低 | 💰💰 中 |
| 灵活性 | ✅ 高 | ⚠️ 中 |
| 本地开发 | 用虚拟环境 | 完全一致 |

## 🔧 本地开发环境

虽然线上使用 Zeabur 原生部署，本地开发仍然保留多种选择：

### 方式 1：虚拟环境 + 脚本（推荐）⭐

```bash
# 启动数据库
./setup_postgres.sh  # Docker PostgreSQL

# 启动后端
./dev.sh  # Python 虚拟环境 + 热重载
```

**优势**：
- 快速启动
- 实时重载
- 轻量级

### 方式 2：Docker Compose

```bash
docker-compose up -d
```

**优势**：
- 一次性启动所有服务
- 环境隔离
- 接近生产环境

## 🔄 持续部署

### 自动部署

Zeabur 会自动监听 GitHub 仓库变化：

```bash
git add .
git commit -m "feat: add new feature"
git push origin main
# Zeabur 自动检测并重新部署
```

### 手动部署

在 Zeabur Dashboard 中：
1. 进入服务详情页
2. 点击 "Redeploy"

## 🐛 故障排查

### 1. 部署失败

**检查**：
- `zbpack.json` 配置是否正确
- `requirements.txt` 依赖是否完整
- 环境变量是否配置

**查看日志**：
- Zeabur Dashboard → Logs 标签

### 2. 数据库连接失败

**检查**：
- PostgreSQL 服务是否运行
- `DATABASE_URL` 环境变量是否设置
- 使用的是 Zeabur 提供的内部地址

**解决**：
```bash
# Zeabur 会自动注入 POSTGRES_URL
# 确保环境变量设置为：
DATABASE_URL=${POSTGRES_URL}
ASYNC_DATABASE_URL=${POSTGRES_URL}
```

### 3. 迁移未执行

**原因**：
- `start_command` 未配置

**解决**：
在 `zbpack.json` 中添加：
```json
{
  "start_command": "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"
}
```

### 4. 端口错误

**确保使用**：
```bash
--port ${PORT:-8000}
```

Zeabur 会自动注入 `PORT` 环境变量。

## 💰 成本估算

### Zeabur 计费

- **免费额度**：$5/月
- **计费项**：
  - CPU 使用时间
  - 内存占用
  - 网络流量
  - 持久化存储

### 典型成本

**小型应用**（本项目）：
- 后端：$3-8/月
- PostgreSQL：$3-5/月
- **总计**：约 $6-13/月

**优化建议**：
- 启用自动休眠（低流量时）
- 使用 CDN 减少流量
- 定期清理日志

## 📚 相关文档

- [Zeabur Python 部署文档](https://zeabur.com/docs/en-US/guides/python)
- [Zeabur PostgreSQL 文档](https://zeabur.com/docs/en-US/marketplace/postgresql)
- [项目 README](./README.md)
- [开发指南](./DEVELOPMENT.md)

## 🎉 部署完成

访问你的 API：
- **文档**：https://your-backend.zeabur.app/api/docs
- **健康检查**：https://your-backend.zeabur.app/api/health

现在你可以专注于开发，让 Zeabur 处理运维！🚀
