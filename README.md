# English Tube Backend

[![GitHub](https://img.shields.io/badge/GitHub-english__tube__backend-blue?logo=github)](https://github.com/jwfstars/english_tube_backend)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com)

English Tube 后端 API 服务，基于 FastAPI + PostgreSQL 构建的英语学习平台后端。

## ✨ 主要特性

- 🔐 **用户认证** - JWT Token + 短信验证码登录
- 📹 **视频管理** - 集成腾讯云 VOD 点播服务
- 📝 **学习内容** - 单词卡片、短语卡片、字幕管理
- ⭐ **收藏功能** - 视频、单词、短语、字幕收藏
- 📊 **学习进度** - 视频观看进度追踪
- 🎯 **标签分类** - 视频标签和分类管理
- 🚀 **异步性能** - 基于 asyncio 的高性能异步 API
- 📦 **容器化** - Docker + Docker Compose 一键部署
- ☁️ **云部署** - 支持 Zeabur PaaS 平台快速部署

## 📦 技术栈

- **Web 框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL 15 + SQLAlchemy 2.0 (Async)
- **数据迁移**: Alembic
- **认证**: JWT (python-jose) + Argon2 密码哈希
- **云服务**: 腾讯云 VOD + 腾讯云短信
- **容器化**: Docker + Docker Compose
- **部署**: Zeabur / 宝塔面板 / Docker Compose

## 🚀 快速开始（本地开发）

### 1. 克隆仓库

```bash
git clone https://github.com/jwfstars/english_tube_backend.git
cd english_tube_backend
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，配置数据库密码和其他必要参数
vim .env
```

### 3. 启动服务

```bash
# 启动所有服务（PostgreSQL + Backend + Nginx）
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

等待看到：`INFO: Application startup complete.`

### 4. 验证服务

```bash
# 健康检查
curl http://localhost:8002/api/health
# 应返回: {"status":"ok","database":"ok","version":"1.0.0"}

# 访问 API 文档
open http://localhost:8002/api/docs
```

### 5. 创建管理员账号

```bash
# 创建超级用户（注意使用 -m 模块方式）
docker-compose exec backend python -m scripts.create_superuser \
  --email admin@localhost.com \
  --password admin123 \
  --username admin \
  --display-name "本地管理员"
```

成功后显示：`Created superuser: admin@localhost.com`

---

## ☁️ 云端部署

### Zeabur 部署（推荐）

Zeabur 是一个简单易用的 PaaS 平台，支持自动化部署。

**快速部署步骤**：

1. 登录 [Zeabur Dashboard](https://dash.zeabur.com/)
2. 创建新项目
3. 添加 PostgreSQL 服务
4. 添加 Git 服务，连接此仓库
5. 配置环境变量（参考 `.env.zeabur.example`）
6. 自动部署完成

📖 **详细文档**: [Zeabur 部署指南](./DEPLOYMENT_ZEABUR.md) | [部署检查清单](./ZEABUR_CHECKLIST.md)

### Docker 部署

适用于 VPS 或自建服务器：

```bash
# 1. 克隆仓库
git clone https://github.com/jwfstars/english_tube_backend.git
cd english_tube_backend

# 2. 配置生产环境变量
cp .env.example .env
vim .env  # 修改为生产环境配置

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

📖 **详细文档**: [Docker 部署指南](./DEPLOYMENT.md) | [宝塔面板部署](./DEPLOYMENT_BAOTA.md)

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

## 📁 项目结构

```
english_tube_backend/
├── app/                      # 应用主目录
│   ├── api/                  # API 路由
│   │   └── v1/              # API v1 版本
│   │       ├── endpoints/   # 端点实现
│   │       └── api.py       # 路由汇总
│   ├── core/                # 核心配置
│   │   ├── config.py        # 应用配置
│   │   └── database.py      # 数据库连接
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic 模式
│   ├── services/            # 业务服务
│   ├── utils/               # 工具函数
│   └── main.py              # 应用入口
├── alembic/                 # 数据库迁移
│   └── versions/            # 迁移脚本
├── nginx/                   # Nginx 配置
├── scripts/                 # 管理脚本
├── docker-compose.yml       # Docker 编排
├── Dockerfile               # Docker 镜像
├── requirements.txt         # Python 依赖
├── zbpack.json              # Zeabur 配置
└── .env.example             # 环境变量示例
```

## 🔌 API 端点

### 认证相关
- `POST /api/v1/auth/register` - 用户注册（短信验证码）
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/sms/send` - 发送短信验证码
- `POST /api/v1/auth/refresh` - 刷新 Token

### 视频管理
- `GET /api/v1/videos` - 获取视频列表
- `GET /api/v1/videos/{id}` - 获取视频详情
- `POST /api/v1/videos` - 创建视频（管理员）
- `PUT /api/v1/videos/{id}` - 更新视频（管理员）
- `DELETE /api/v1/videos/{id}` - 删除视频（管理员）

### 学习内容
- `GET /api/v1/subtitles` - 获取字幕
- `GET /api/v1/word-cards` - 获取单词卡片
- `GET /api/v1/phrase-cards` - 获取短语卡片

### 收藏功能
- `POST /api/v1/favorites/videos/{id}` - 收藏视频
- `POST /api/v1/favorites/words/{id}` - 收藏单词
- `POST /api/v1/favorites/phrases/{id}` - 收藏短语
- `GET /api/v1/favorites` - 获取收藏列表

### 学习进度
- `POST /api/v1/learning/progress` - 记录学习进度
- `GET /api/v1/learning/progress` - 获取学习进度

完整 API 文档: http://localhost:8002/api/docs

## 🔐 环境变量说明

核心环境变量（`.env` 文件）：

```bash
# 数据库
DATABASE_URL=postgresql://user:password@host:5432/database
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# JWT 认证
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:8858"]

# 腾讯云 VOD
VOD_APP_ID=your-app-id
VOD_PLAY_KEY=your-play-key

# 腾讯云短信（可选）
TENCENT_SMS_SECRET_ID=your-secret-id
TENCENT_SMS_SECRET_KEY=your-secret-key
```

完整配置说明：[.env.example](./.env.example) | [Zeabur 配置](./.env.zeabur.example)

## 🧪 开发指南

### 数据库迁移

```bash
# 创建新迁移
docker-compose exec backend alembic revision --autogenerate -m "description"

# 执行迁移
docker-compose exec backend alembic upgrade head

# 回滚迁移
docker-compose exec backend alembic downgrade -1

# 查看迁移历史
docker-compose exec backend alembic history
```

### 运行测试

```bash
# 进入容器
docker-compose exec backend bash

# 运行测试（待添加）
pytest
```

### 代码格式化

```bash
# 安装开发依赖
pip install black isort flake8

# 格式化代码
black app/
isort app/

# 代码检查
flake8 app/
```

## 📖 更多文档

- 📘 [配置说明](./README_CONFIG.md)
- 🚀 [Docker 部署指南](./DEPLOYMENT.md)
- ☁️ [Zeabur 部署指南](./DEPLOYMENT_ZEABUR.md)
- ✅ [Zeabur 部署检查清单](./ZEABUR_CHECKLIST.md)
- 🔄 [配置迁移指南](./CONFIG_MIGRATION.md)
- 🏗️ [宝塔面板部署](./DEPLOYMENT_BAOTA.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

## 🔗 相关项目

- [English Tube 前端](https://github.com/jwfstars/english_tube) - Flutter 移动应用
- [English Tube Admin](https://github.com/jwfstars/english_tube_admin) - Vue 3 管理后台

## 📞 联系方式

- GitHub: [@jwfstars](https://github.com/jwfstars)
- 项目仓库: [english_tube_backend](https://github.com/jwfstars/english_tube_backend)
