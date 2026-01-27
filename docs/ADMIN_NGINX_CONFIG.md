# 管理后台 Nginx 配置指南

## ⚠️ 重要：宝塔目录限制

宝塔面板出于安全考虑，禁止将以下目录设置为网站根目录：
- `/root/` - root 用户主目录
- `/www/server/` - 宝塔服务目录
- `/` - 系统根目录
- 等其他系统关键目录

**因此，管理后台必须部署到宝塔允许的目录**，推荐使用：
- **路径方案（推荐）** ⭐：`/www/wwwroot/englishtube.top/admin/` - 只需一个 SSL 证书
- **子域名方案**：`/www/wwwroot/admin.englishtube.top/` - 需要单独申请子域名 SSL 证书

部署脚本会自动将构建产物从 `english_tube_admin/dist/` 复制到宝塔网站目录。

---

## 在宝塔面板配置管理后台

### 方案一：使用路径（推荐）⭐

在主域名下使用 `/admin` 路径，**只需要一个 SSL 证书**：

1. **确保主站点已创建**
   - 网站 → `englishtube.top` 应该已经存在
   - 如果没有，先添加站点并配置 SSL

2. **在宝塔面板找到主站点配置**
   - 网站 → `englishtube.top` → 设置 → 配置文件

3. **添加管理后台路径配置**

在 SSL 的 `server` 块中添加：

```nginx
# 管理后台（使用 hash 路由模式，无需 try_files）
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

4. **保存并重载 Nginx**
   ```bash
   nginx -t
   nginx -s reload
   ```

5. **运行部署脚本**
   ```bash
   cd /www/wwwroot/english_tube
   bash scripts/quick_deploy.sh
   ```

**说明**：
- Admin 使用 Hash 路由模式（`.env.production` 中配置），URL 格式为 `https://englishtube.top/admin/#/login`
- 因为是 hash 模式，不需要 `try_files` 配置
- `VITE_PUBLIC_PATH = /admin/` 已在 `.env.production` 中配置
- 部署脚本会自动构建并复制文件到 `/www/wwwroot/englishtube.top/admin/`

### 方案二：单独子域名

如果你想用子域名（如 `admin.englishtube.top`），需要单独申请子域名的 SSL 证书：

1. **在宝塔面板添加站点**
   - 网站 → 添加站点
   - 域名：`admin.englishtube.top`
   - 根目录：`/www/wwwroot/admin.englishtube.top`
   - PHP 版本：纯静态

2. **配置 SSL**
   - 站点设置 → SSL
   - 选择 Let's Encrypt
   - 申请证书（需要添加 admin.englishtube.top 的 DNS A 记录）
   - 开启强制 HTTPS

3. **修改 `.env.production`**
   ```bash
   VITE_PUBLIC_PATH = /
   ```

4. **修改部署脚本中的目标目录**为 `/www/wwwroot/admin.englishtube.top/`

### 方案三：使用端口（开发/测试用）

直接暴露 admin 的开发服务器（不推荐生产环境）：

1. **配置防火墙**
   - 宝塔 → 安全 → 放行端口 8858

2. **启动开发服务器**
   ```bash
   cd /www/wwwroot/english_tube/english_tube_admin
   pnpm dev --host 0.0.0.0 --port 8858 &
   ```

3. **访问**
   - http://81.68.234.126:8858

## 完整 Nginx 配置示例

### 方案一：路径方式（englishtube.top.conf）

在主站点的配置文件中添加 admin 相关配置：

```nginx
# HTTPS 主站配置
server {
    listen 443 ssl http2;
    server_name englishtube.top www.englishtube.top;

    # SSL 证书配置
    ssl_certificate /www/server/panel/vhost/cert/englishtube.top/fullchain.pem;
    ssl_certificate_key /www/server/panel/vhost/cert/englishtube.top/privkey.pem;

    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 日志
    access_log /www/wwwlogs/englishtube.top.log;
    error_log /www/wwwlogs/englishtube.top.error.log;

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

    # API 反向代理
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

    # 主站内容（如果有前端）
    location / {
        root /www/wwwroot/englishtube.top;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
```

### 方案二：子域名方式（admin.englishtube.top.conf）

```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name admin.englishtube.top;
    return 301 https://$server_name$request_uri;
}

# HTTPS 管理后台
server {
    listen 443 ssl http2;
    server_name admin.englishtube.top;

    # SSL 证书配置
    ssl_certificate /www/server/panel/vhost/cert/admin.englishtube.top/fullchain.pem;
    ssl_certificate_key /www/server/panel/vhost/cert/admin.englishtube.top/privkey.pem;

    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 日志
    access_log /www/wwwlogs/admin.englishtube.top.log;
    error_log /www/wwwlogs/admin.englishtube.top.error.log;

    # 根目录
    root /www/wwwroot/admin.englishtube.top;
    index index.html;

    # Vue Router History 模式支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 反向代理（如果前端需要通过同域访问）
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

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
```

## DNS 配置

如果使用子域名，需要添加 DNS 解析记录：

1. **腾讯云 DNS 解析**
   - 访问：https://console.cloud.tencent.com/cns
   - 添加记录：
     ```
     类型: A
     主机记录: admin
     记录值: 81.68.234.126
     TTL: 600
     ```

2. **验证解析**
   ```bash
   dig admin.englishtube.top
   ```

## 部署流程

完整的部署步骤：

```bash
# 1. 在服务器上拉取最新代码并构建
cd /www/wwwroot/english_tube
bash scripts/quick_deploy.sh

# 2. 配置 Nginx（首次需要）
# 在宝塔面板添加站点或修改配置文件

# 3. 重载 Nginx
nginx -t  # 测试配置
nginx -s reload  # 重载

# 4. 访问管理后台
# https://admin.englishtube.top
# 或 https://englishtube.top/admin
```

## 验证部署

访问以下 URL 验证：

- ✅ 管理后台首页：`https://englishtube.top/admin`
- ✅ 登录页面：`https://englishtube.top/admin/#/login`
- ✅ API 健康检查：`https://englishtube.top/api/health`

## 常见问题

### Q: 刷新页面出现 404？

A: 如果使用 Hash 路由模式（默认），不会有这个问题。如果切换到 History 模式，需要配置 `try_files $uri $uri/ /admin/index.html;`

### Q: 静态资源加载失败？

A:
1. 检查 `.env.production` 中的 `VITE_PUBLIC_PATH = /admin/` 配置是否正确
2. 确认部署脚本已正确复制文件到 `/www/wwwroot/englishtube.top/admin/`
3. 检查 Nginx 配置中的 `alias` 路径是否正确

### Q: API 请求跨域？

A: Admin 和 API 都在同一个域名 `englishtube.top` 下，不会有跨域问题。如果仍有问题，检查后端 CORS 配置。

### Q: 构建后文件太大？

A: 在 `.env.production` 中设置 `VITE_CDN = true` 使用 CDN 加载依赖。

### Q: 子域名方式需要什么？

A:
1. DNS 添加 A 记录：`admin.englishtube.top` → `81.68.234.126`
2. 在宝塔面板申请子域名的 SSL 证书（Let's Encrypt 支持子域名）
3. 修改 `.env.production` 中 `VITE_PUBLIC_PATH = /`
4. 修改部署脚本目标目录为 `/www/wwwroot/admin.englishtube.top/`
