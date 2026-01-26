# English Tube Backend

## 🚀 快速开始（本地开发）

### 1. 启动服务

```bash
cd backend

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

等待看到：`INFO: Application startup complete.`

### 2. 创建管理员账号

```bash
# 创建超级用户（注意使用 -m 模块方式）
docker-compose exec backend python -m scripts.create_superuser \
  --email admin@localhost.com \
  --password admin123 \
  --username admin \
  --display-name "本地管理员"
```

成功后显示：`Created superuser: admin@localhost.com`

### 3. 测试服务

```bash
# 测试健康检查
curl http://localhost:8002/api/health

# 访问 API 文档
open http://localhost:8002/api/docs
```

---

## 👤 用户管理

### 创建超级用户

```bash
# 完整参数
docker-compose exec backend python -m scripts.create_superuser \
  --email admin@localhost.com \
  --password admin123 \
  --username admin \
  --display-name "管理员"

# 最简用法
docker-compose exec backend python -m scripts.create_superuser \
  --email test@example.com \
  --password test123

# 更新现有用户为超级用户
docker-compose exec backend python -m scripts.create_superuser \
  --email existing@example.com
```

**参数说明**:
- `--email` (必填): 管理员邮箱
- `--password` (必填): 管理员密码
- `--username` (可选): 用户名，默认为邮箱前缀
- `--display-name` (可选): 显示名称，默认为用户名

---

## 📋 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启后端
docker-compose restart backend

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 数据库操作

```bash
# 进入数据库
docker-compose exec postgres psql -U english_tube -d english_tube

# 运行迁移
docker-compose exec backend alembic upgrade head

# 查看迁移历史
docker-compose exec backend alembic history
```

---

## 🔧 配置

### 端口映射

| 服务 | 容器内 | 宿主机 | 访问地址 |
|------|-------|-------|---------|
| Backend | 8000 | 8002 | http://localhost:8002 |
| PostgreSQL | 5432 | 5432 | localhost:5432 |

### 环境变量

配置文件：`.env`

```bash
BACKEND_PORT=8002
DB_PASSWORD=dev_local_password_2024
BACKEND_CORS_ORIGINS=["http://localhost:8858"]
```

---

## 📚 API 文档

- **Swagger**: http://localhost:8002/api/docs
- **ReDoc**: http://localhost:8002/api/redoc

---

## 📖 更多文档

- [配置说明](./README_CONFIG.md)
- [部署指南](./DEPLOYMENT.md)
- [配置迁移](./CONFIG_MIGRATION.md)
