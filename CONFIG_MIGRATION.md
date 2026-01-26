# 配置整理总结

## 📋 已完成的修改

### 1. Docker Compose 配置
- ✅ 删除了废弃的 `version: '3.8'` (消除警告)
- ✅ 修改 `env_file` 为 `.env` (统一配置文件)
- ✅ 修改默认端口为 `8002` (避免端口冲突)

### 2. 环境配置文件
- ✅ 创建 `.env.example` 作为配置模板
- ✅ 更新 `.gitignore` 确保不提交敏感文件
- ✅ 更新 `.env.production` 端口为 8002

### 3. 文档
- ✅ 创建 `README_CONFIG.md` 配置说明文档
- ✅ 创建 `migrate_config.sh` 迁移脚本

## 🚀 下一步操作

### 本地开发

```bash
cd /Users/winfield/workspace/Apps/projects/english_tube/backend

# 1. 运行迁移脚本（推荐）
./migrate_config.sh

# 或手动操作：
# 2. 创建 .env 文件
cp .env.example .env

# 3. 编辑 .env 文件
vi .env

# 必须修改的配置：
# - DB_PASSWORD=强密码
# - SECRET_KEY=$(openssl rand -hex 32)
# - BACKEND_CORS_ORIGINS=["http://localhost:8858"]
# - VOD_PLAY_KEY=你的密钥

# 4. 启动服务
docker-compose up -d

# 5. 测试
curl http://localhost:8002/health
```

### 服务器部署

在服务器上 (`/www/wwwroot/english_tube/backend`):

```bash
# 1. 拉取最新代码
git pull

# 2. 创建 .env 文件（从 .env.production 迁移）
cp .env.production .env

# 3. 编辑配置
vi .env

# 确保配置了：
# - BACKEND_PORT=8002
# - DB_PASSWORD=服务器的强密码
# - SECRET_KEY=生产环境密钥
# - BACKEND_CORS_ORIGINS=["http://81.68.234.126:8858","http://81.68.234.126"]
# - VOD_PLAY_KEY=真实密钥

# 4. 停止并重启服务
docker-compose down
docker-compose up -d postgres backend

# 注意：如果宝塔 Nginx 占用 80 端口，不要启动项目的 nginx 容器

# 5. 测试
curl http://localhost:8002/health
```

## 🔧 配置结构（新）

```
backend/
├── .env                    # 实际配置（不提交Git，本地+服务器使用）
├── .env.example            # 配置模板（提交Git）
├── .env.production         # 旧文件，可以删除
├── docker-compose.yml      # 读取 .env
└── README_CONFIG.md        # 配置说明文档
```

## ✨ 新配置方案的优势

1. **简单清晰**：只有一个 `.env` 文件，本地和服务器都用它
2. **安全**：`.env` 不提交，`.env.example` 作为模板提交
3. **统一端口**：默认 8002，避免与其他服务冲突
4. **无警告**：删除了废弃的 `version` 配置

## 📝 待办事项

- [ ] 本地运行 `./migrate_config.sh` 迁移配置
- [ ] 修改本地 `.env` 中的敏感配置
- [ ] 测试本地服务：`docker-compose up -d`
- [ ] 服务器上创建 `.env` 文件
- [ ] 服务器重启服务并测试
- [ ] 删除旧的 `.env.production` 文件（确认无问题后）
- [ ] 提交代码到 Git

## 🎯 前后端端口对照

| 服务 | 端口 | 说明 |
|------|------|------|
| Backend API | 8002 | 后端服务 |
| Admin 前端 | 8858 | 管理后台 |
| 用户端前端 | 3000 | 用户端（如果有）|
| PostgreSQL | 5432 | 数据库 |

## ⚠️ 常见问题

### Q: 端口 8002 还是无法访问？
A: 检查：
1. 防火墙是否开放 8002
2. `.env` 中是否配置 `BACKEND_PORT=8002`
3. 是否重新创建容器 (`docker-compose down && docker-compose up -d`)

### Q: CORS 错误？
A: 确保 `.env` 中配置了前端地址：
```bash
BACKEND_CORS_ORIGINS=["http://localhost:8858"]
```

### Q: 能否继续使用 .env.production？
A: 可以，但不推荐。新方案更简单。

---

**最后更新**: 2025-12-31
**迁移优先级**: 🔴 高（建议立即执行）
