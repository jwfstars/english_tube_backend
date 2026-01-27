# 腾讯云 SSL 证书配置指南

## 第一步：下载证书

1. **登录腾讯云 SSL 证书控制台**
   - 访问：https://console.cloud.tencent.com/ssl

2. **下载证书**
   - 找到你申请的证书（状态应该是「已签发」）
   - 点击「下载」
   - 选择「Nginx」服务器类型
   - 下载压缩包到本地

3. **解压证书文件**

   解压后会得到两个文件：
   ```
   englishtube.top_bundle.crt    # 证书文件
   englishtube.top.key            # 私钥文件
   ```

## 第二步：在宝塔面板配置证书

### 方案一：使用宝塔面板管理（推荐）

1. **登录宝塔面板**
   ```
   http://81.68.234.126:8888/tencentcloud
   ```

2. **添加站点**
   - 点击左侧「网站」
   - 点击「添加站点」
   - 域名填写：`englishtube.top` 和 `www.englishtube.top`（一行一个或用逗号分隔）
   - 根目录：`/www/wwwroot/englishtube.top`（可自定义）
   - PHP 版本：选择「纯静态」或根据需要选择
   - 数据库：不需要可以不创建
   - 点击「提交」

3. **配置 SSL 证书**
   - 在站点列表中，找到 `englishtube.top`
   - 点击「设置」
   - 点击「SSL」选项卡
   - 选择「其他证书」
   - 打开下载的证书文件，将内容复制粘贴：
     - **证书 (PEM格式)**：复制 `englishtube.top_bundle.crt` 的内容
     - **密钥 (KEY)**：复制 `englishtube.top.key` 的内容
   - 点击「保存」

4. **开启强制 HTTPS**
   - 在同一个 SSL 页面
   - 开启「强制 HTTPS」开关
   - 这样访问 HTTP 会自动跳转到 HTTPS

5. **配置反向代理（重要）**

   因为你的后端运行在 Docker 的 8000 端口，需要配置反向代理。

   **配置 API 子域名：**

   a. 添加 API 站点：
   - 点击「添加站点」
   - 域名：`api.englishtube.top`
   - 其他设置同上
   - 提交

   b. 配置 API 证书（重复上面的 SSL 配置步骤）

   c. 配置反向代理：
   - 点击站点 `api.englishtube.top` 的「设置」
   - 点击「反向代理」
   - 点击「添加反向代理」
   - 配置如下：
     ```
     代理名称: backend
     目标 URL: http://127.0.0.1:8000
     发送域名: $host
     ```
   - 高级设置中添加以下配置：
     ```nginx
     proxy_set_header Host $host;
     proxy_set_header X-Real-IP $remote_addr;
     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
     proxy_set_header X-Forwarded-Proto $scheme;
     ```
   - 点击「提交」

### 方案二：直接修改 Nginx 配置（高级）

如果你熟悉 Nginx，可以直接修改配置文件。

1. **上传证书到服务器**
   ```bash
   # 在本地执行（替换为你的实际文件路径）
   scp englishtube.top_bundle.crt root@81.68.234.126:/etc/nginx/ssl/
   scp englishtube.top.key root@81.68.234.126:/etc/nginx/ssl/
   ```

2. **修改 Nginx 配置**

   在宝塔面板中：
   - 点击站点 → 设置 → 配置文件
   - 或者 SSH 登录服务器编辑：`/www/server/panel/vhost/nginx/englishtube.top.conf`

   完整配置示例：
   ```nginx
   # HTTP 重定向到 HTTPS
   server {
       listen 80;
       server_name englishtube.top www.englishtube.top;
       return 301 https://$server_name$request_uri;
   }

   # HTTPS 主站
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

       # 网站根目录
       root /www/wwwroot/englishtube.top;
       index index.html index.htm;

       location / {
           try_files $uri $uri/ /index.html;
       }
   }

   # API 子域名 - 反向代理到后端
   server {
       listen 80;
       server_name api.englishtube.top;
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name api.englishtube.top;

       # SSL 证书配置（使用主域名证书或单独申请）
       ssl_certificate /www/server/panel/vhost/cert/englishtube.top/fullchain.pem;
       ssl_certificate_key /www/server/panel/vhost/cert/englishtube.top/privkey.pem;

       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
       ssl_prefer_server_ciphers on;

       # 反向代理到 FastAPI 后端
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;

           # WebSocket 支持（如果需要）
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";

           # 超时设置
           proxy_connect_timeout 60s;
           proxy_send_timeout 60s;
           proxy_read_timeout 60s;
       }
   }
   ```

3. **重载 Nginx**
   ```bash
   nginx -t  # 测试配置
   nginx -s reload  # 重载配置
   ```

## 第三步：更新后端 CORS 配置

修改 `backend/app/core/config.py`，添加你的域名到 CORS 白名单：

```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://englishtube.top",
    "https://www.englishtube.top",
    "https://api.englishtube.top",
]
```

然后重启后端：
```bash
cd /www/wwwroot/english_tube/backend
docker-compose restart backend
```

## 第四步：验证配置

1. **检查证书是否生效**
   ```bash
   curl -I https://englishtube.top
   curl -I https://www.englishtube.top
   curl -I https://api.englishtube.top
   ```

2. **在浏览器访问**
   - https://englishtube.top - 应该显示绿色锁标志
   - https://api.englishtube.top/health - 应该返回健康检查结果

3. **检查证书详情**
   ```bash
   openssl s_client -connect englishtube.top:443 -servername englishtube.top
   ```

4. **在线 SSL 检测**
   - https://myssl.com/
   - https://www.ssllabs.com/ssltest/

## 第五步：配置自动续期（重要）

腾讯云免费证书有效期为 1 年，到期前需要续期。

### 方案一：使用腾讯云自动部署（推荐）

1. 在腾讯云 SSL 证书控制台
2. 点击证书 → 部署
3. 选择「云服务器」
4. 选择你的 CVM 实例
5. 配置部署路径和重启命令

### 方案二：使用 Let's Encrypt（永久免费）

宝塔面板支持一键申请 Let's Encrypt 证书：

1. 在宝塔面板 → 网站 → 设置 → SSL
2. 选择「Let's Encrypt」
3. 输入邮箱
4. 勾选域名（`englishtube.top` 和 `www.englishtube.top`）
5. 点击「申请」

Let's Encrypt 证书有效期 90 天，宝塔会自动续期。

## 常见问题

### Q1: 证书安装后浏览器还是提示不安全？

A: 检查以下几点：
1. 确认证书文件复制完整（包括开头的 `-----BEGIN CERTIFICATE-----` 和结尾的 `-----END CERTIFICATE-----`）
2. 清除浏览器缓存
3. 使用隐私模式重新访问
4. 检查 Nginx 配置是否正确加载证书

### Q2: 配置后无法访问？

A: 检查防火墙：
```bash
# 开放 443 端口
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload

# 或者在宝塔面板 → 安全 → 添加端口 443
```

### Q3: API 请求跨域错误？

A: 确保后端 CORS 配置包含了你的域名，并重启后端服务。

### Q4: HTTP 没有自动跳转到 HTTPS？

A: 在宝塔面板 → 网站 → SSL → 开启「强制 HTTPS」

## 推荐配置总结

对于 English Tube 项目，推荐的域名和证书配置：

| 域名 | 用途 | 指向 | SSL |
|-----|------|------|-----|
| englishtube.top | 主站（前端） | Nginx 静态文件 | ✓ |
| www.englishtube.top | 主站别名 | 同上 | ✓ |
| api.englishtube.top | 后端 API | 反向代理到 :8000 | ✓ |

配置完成后的访问地址：
- 前端：https://englishtube.top
- API：https://api.englishtube.top/api/v1
- 健康检查：https://api.englishtube.top/health
- API 文档：https://api.englishtube.top/docs
