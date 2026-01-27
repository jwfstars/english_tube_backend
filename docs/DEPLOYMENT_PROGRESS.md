# English Tube 部署进展总结

**最后更新**: 2025-12-30

## 📋 部署概况

### 服务器信息
- **平台**: 腾讯云轻量应用服务器
- **IP**: 81.68.234.126
- **配置**: 2核4GB，60GB SSD
- **系统**: OpenCloudOS 9 + 宝塔面板
- **域名**: englishtube.top

### 已部署服务

| 服务 | 访问地址 | 状态 | 备注 |
|------|---------|------|------|
| 后端 API | https://englishtube.top/api/health | ✅ 运行中 | Docker 部署 |
| API 文档 | https://englishtube.top/api/docs | ✅ 运行中 | Swagger UI |
| 管理后台 | https://englishtube.top/admin/ | ✅ 运行中 | Vue3 + Element Plus |
| 数据库 | localhost:5432 | ✅ 运行中 | PostgreSQL 15 |

---

## ✅ 已完成工作

### 1. 后端部署 (Backend)

**技术栈**: FastAPI + PostgreSQL + Docker

- ✅ Docker + Docker Compose 容器化部署
- ✅ 数据库迁移配置（Alembic）
- ✅ 环境变量配置（`.env.production.local`）
- ✅ Nginx 反向代理配置（`/api` 路径）
- ✅ SSL 证书配置（HTTPS）
- ✅ 健康检查端点（`/api/health`）
- ✅ API 文档自动生成（`/api/docs`）

**部署位置**: `/www/wwwroot/english_tube/backend`

**Docker 容器**:
- `english_tube_backend` - FastAPI 应用（端口 8000）
- `english_tube_db` - PostgreSQL 数据库（端口 5432）

### 2. 管理后台部署 (Admin)

**技术栈**: Vue3 + TypeScript + Element Plus + Vite

- ✅ 从 Git 子模块转换为普通目录
- ✅ 修复 `.gitignore` 误伤 TypeScript 文件的问题
- ✅ 添加所有缺失的源代码文件（78+ 文件）
- ✅ 配置生产环境变量（`VITE_PUBLIC_PATH = /admin/`）
- ✅ 构建生产版本（`pnpm build`）
- ✅ Nginx 路径配置（使用符号链接 + root）
- ✅ 解决浏览器缓存问题

**部署位置**:
- 源码: `/www/wwwroot/english_tube/english_tube_admin`
- 构建产物: `/www/wwwroot/english_tube/english_tube_admin/dist`
- 网站目录: `/www/wwwroot/englishtube.top/admin` (符号链接)

### 3. DNS 和 SSL 配置

- ✅ DNS 解析配置（火山云域名 → 腾讯云 DNSPod）
- ✅ SSL 证书申请（腾讯云免费 DV 证书）
- ✅ HTTPS 强制跳转配置
- ✅ 所有服务统一使用 HTTPS

### 4. Nginx 配置

**配置文件**: `/www/server/panel/vhost/nginx/englishtube.top.conf`

```nginx
# API 反向代理（宝塔自动生成）
location ^~ /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    # ...
}

# 管理后台
location /admin/ {
    alias /www/wwwroot/englishtube.top/admin/;
}

location = /admin {
    return 301 /admin/;
}
```

### 5. 部署脚本

创建了自动化部署脚本：

- ✅ `scripts/quick_deploy.sh` - 快速更新部署
- ✅ `scripts/deploy_backend.sh` - 完整部署（后端+管理后台）
- ✅ 自动拉取代码、构建、重启服务

### 6. 文档完善

- ✅ `backend/DEPLOYMENT_BAOTA.md` - 宝塔面板部署指南
- ✅ `docs/DNS_CONFIG.md` - DNS 解析配置指南
- ✅ `docs/SSL_CONFIG.md` - SSL 证书配置指南
- ✅ `docs/ADMIN_NGINX_CONFIG.md` - 管理后台 Nginx 配置指南
- ✅ `uploader/README_ENV.md` - Uploader 环境配置说明

---

## 🐛 解决的主要问题

### 问题1: Git 子模块导致的文件缺失

**现象**:
- `english_tube_admin` 文件夹大小 800M+，主要是 `node_modules`
- 从子模块转换时，`.gitignore` 的 `*.ts` 规则误伤了所有 TypeScript 源代码

**解决方案**:
1. 移除 admin 的 `.git` 目录（节省 5.5M）
2. 修复 `.gitignore`，只忽略 `uploader/output/` 和 `uploader/downloads/` 目录下的 `.ts` 视频文件
3. 强制添加所有被忽略的 TypeScript 源文件：
   - `src/**/*.ts` - 所有业务代码
   - `build/*.ts` - Vite 构建配置
   - `mock/*.ts` - Mock 数据
   - `types/*.d.ts` - 类型定义
   - `vite.config.ts` - Vite 配置文件

### 问题2: 宝塔面板目录限制

**现象**:
宝塔面板禁止将 `/root/` 目录设为网站根目录

**解决方案**:
- 采用路径方式部署：`englishtube.top/admin`（只需一个 SSL 证书）
- 使用符号链接：`/www/wwwroot/englishtube.top/admin → /www/wwwroot/english_tube/english_tube_admin/dist`
- 更新所有部署脚本和文档

### 问题3: Nginx alias 路径斜杠问题

**现象**:
- 资源 URL 末尾自动添加斜杠：`/admin/static/js/index.js/`
- `location` 和 `alias` 斜杠不匹配导致 301 重定向

**解决方案**:
- 使用符号链接 + `root` 指令替代 `alias`
- 配置 301 重定向：`/admin` → `/admin/`
- 统一资源路径配置

### 问题4: 浏览器缓存

**现象**:
代码更新后，浏览器仍加载旧版本

**解决方案**:
- 使用隐私模式测试
- Ctrl+Shift+R 强制刷新
- Nginx 添加静态资源缓存控制

### 问题5: VITE_PUBLIC_PATH 配置

**现象**:
- `/admin` 会导致 URL 拼接错误：`/adminplatform-config.json`
- `/admin/` 会导致资源路径多斜杠

**最终方案**:
- `VITE_PUBLIC_PATH = /admin/`（带斜杠）
- Nginx 使用 `alias` 或符号链接 + `root`
- 确保 `location` 和目录路径斜杠一致

---

## 🔧 环境配置

### Backend 环境变量

**文件**: `backend/.env.production.local` (不提交到 Git)

```bash
# 数据库配置
DB_PASSWORD=强密码
DATABASE_URL=postgresql://english_tube:密码@postgres:5432/english_tube

# JWT 密钥
SECRET_KEY=64位hex字符串（openssl rand -hex 32 生成）

# 腾讯云 VOD
VOD_PLAY_KEY=播放密钥

# CORS 配置
BACKEND_CORS_ORIGINS=["https://englishtube.top","https://admin.englishtube.top"]
```

### Admin 环境变量

**文件**: `english_tube_admin/.env.production` (提交到 Git)

```bash
VITE_PUBLIC_PATH = /admin/
VITE_ROUTER_HISTORY = "hash"
VITE_CDN = false
VITE_COMPRESSION = "gzip"
VITE_API_BASE = https://englishtube.top/api/v1
```

### Uploader 环境变量

**文件**: `uploader/.env` (不提交到 Git)

```bash
ENVIRONMENT=production  # local 或 production
API_BASE_URL=  # 留空则根据 ENVIRONMENT 自动选择
```

---

## 📝 日常维护

### 更新后端代码

```bash
cd /www/wwwroot/english_tube/backend
git pull origin main
docker-compose up -d --build backend
docker-compose logs -f backend  # 查看日志
```

### 更新管理后台

```bash
cd /www/wwwroot/english_tube
git pull origin main
cd english_tube_admin
pnpm build
# 构建产物会自动同步到网站目录（通过符号链接）
```

### 一键部署（推荐）

```bash
cd /www/wwwroot/english_tube
bash scripts/quick_deploy.sh
```

### 查看服务状态

```bash
# 后端容器状态
cd /www/wwwroot/english_tube/backend
docker-compose ps

# 后端日志
docker-compose logs --tail=50 backend

# Nginx 日志
tail -f /www/wwwlogs/englishtube.top.error.log
```

---

## 🚀 下一步计划

### 待完成任务

- [ ] Flutter 移动端应用部署
  - [ ] iOS 应用商店上架
  - [ ] Android 应用市场上架
  - [ ] TestFlight 测试版本

- [ ] 后端功能完善
  - [ ] 用户管理功能
  - [ ] 权限控制系统
  - [ ] 数据统计分析
  - [ ] 日志监控系统

- [ ] 管理后台功能
  - [ ] 视频管理界面
  - [ ] 用户管理界面
  - [ ] 数据统计看板
  - [ ] 系统设置界面

- [ ] 运维优化
  - [ ] 自动备份脚本
  - [ ] 监控告警系统
  - [ ] CDN 加速配置
  - [ ] 负载均衡配置

### 性能优化

- [ ] 启用 Redis 缓存
- [ ] 数据库索引优化
- [ ] 静态资源 CDN
- [ ] 图片压缩优化
- [ ] API 响应缓存

### 安全加固

- [ ] 修改宝塔默认端口
- [ ] 开启宝塔 BasicAuth
- [ ] 配置防火墙规则
- [ ] 定期更新系统
- [ ] 数据库定期备份

---

## 📚 相关文档

- [后端部署指南](../backend/DEPLOYMENT_BAOTA.md)
- [DNS 配置指南](./DNS_CONFIG.md)
- [SSL 证书配置](./SSL_CONFIG.md)
- [管理后台 Nginx 配置](./ADMIN_NGINX_CONFIG.md)
- [Uploader 环境配置](../uploader/README_ENV.md)

---

## 🔗 快捷链接

- **线上服务**:
  - API: https://englishtube.top/api/health
  - API 文档: https://englishtube.top/api/docs
  - 管理后台: https://englishtube.top/admin/

- **服务器管理**:
  - 宝塔面板: http://81.68.234.126:8888
  - 腾讯云控制台: https://console.cloud.tencent.com/lighthouse

- **代码仓库**:
  - GitHub: https://github.com/jwfstars/english_tube

---

**部署完成日期**: 2025-12-30
**部署人员**: Winfield
**技术支持**: Claude Code
