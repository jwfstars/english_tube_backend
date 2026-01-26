# 环境配置说明

## 配置文件说明

项目使用单一 `.env` 文件管理所有环境配置：

- **`.env.example`** - 配置模板（提交到 Git，不含敏感信息）
- **`.env`** - 实际配置文件（不提交到 Git，包含真实密码和密钥）
- **`.env.production`** - 已废弃，将被删除

## 快速开始

### 本地开发

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑 .env 文件
vi .env

# 修改以下关键配置：
# - DB_PASSWORD=你的数据库密码
# - SECRET_KEY=$(openssl rand -hex 32)  # 生成强密钥
# - BACKEND_CORS_ORIGINS=["http://localhost:8858"]  # 本地开发允许的跨域地址
# - VOD_PLAY_KEY=你的腾讯云VOD密钥

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f backend
```

### 服务器部署

```bash
# 1. 在服务器上手动创建 .env 文件
vi .env

# 2. 填入生产环境配置
# - 使用强密码
# - 配置生产环境域名的 CORS
# - 端口配置为 8002

# 3. 启动服务
./deploy.sh
```

## 重要配置项

### 必须修改的配置

```bash
# 数据库密码（必须改为强密码！）
DB_PASSWORD=your_strong_password_here

# JWT 密钥（运行 openssl rand -hex 32 生成）
SECRET_KEY=your_generated_64_character_hex_string

# 腾讯云 VOD 播放密钥
VOD_PLAY_KEY=your_vod_play_key
```

### 环境相关配置

```bash
# 本地开发
BACKEND_PORT=8002
BACKEND_CORS_ORIGINS=["http://localhost:8858","http://127.0.0.1:8858"]

# 生产环境
BACKEND_PORT=8002
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://admin.yourdomain.com"]
```

## 安全提示

1. **永远不要提交 `.env` 文件到 Git**
2. 定期轮换密钥和密码
3. 不同环境使用不同的密钥
4. `.env` 文件权限设置为 600：`chmod 600 .env`

## 故障排查

### 配置文件找不到

```bash
# 检查是否存在 .env 文件
ls -la .env

# 如果不存在，从模板创建
cp .env.example .env
```

### 端口冲突

```bash
# 修改 .env 中的端口
BACKEND_PORT=8002  # 或其他未被占用的端口
```

### CORS 错误

```bash
# 确保前端地址在 CORS 配置中
BACKEND_CORS_ORIGINS=["http://localhost:8858","http://你的前端地址"]
```
