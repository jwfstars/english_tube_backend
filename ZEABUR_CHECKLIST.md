# Zeabur 部署检查清单

## 📋 部署前准备

- [ ] 代码已推送到 GitHub
- [ ] 确认 `requirements.txt` 包含所有依赖
- [ ] 确认 `Dockerfile` 配置正确
- [ ] 准备好腾讯云 VOD 配置信息
- [ ] 生成 JWT 安全密钥（`openssl rand -hex 32`）

## 🚀 Zeabur 部署步骤

### Step 1: 创建项目
- [ ] 登录 [Zeabur Dashboard](https://dash.zeabur.com/)
- [ ] 点击 "Create Project"
- [ ] 选择部署区域（建议：Hong Kong 或 Singapore）
- [ ] 输入项目名称：`english-tube`

### Step 2: 部署数据库
- [ ] 点击 "Add Service"
- [ ] 选择 "Prebuilt" → "PostgreSQL"
- [ ] 等待数据库部署完成（约 30 秒）
- [ ] 进入 PostgreSQL 服务详情页
- [ ] 复制以下变量值：
  - [ ] `POSTGRES_HOST`
  - [ ] `POSTGRES_PORT`
  - [ ] `POSTGRES_USERNAME`
  - [ ] `POSTGRES_PASSWORD`
  - [ ] `POSTGRES_DATABASE`

### Step 3: 部署后端服务
- [ ] 返回项目页面，点击 "Add Service"
- [ ] 选择 "Git"
- [ ] 连接你的 GitHub 账号
- [ ] 选择 `english_tube` 仓库
- [ ] 设置 Root Directory 为 `backend`
- [ ] 点击 "Deploy"，等待构建完成（约 3-5 分钟）

### Step 4: 配置环境变量

在后端服务的 "Variables" 标签页添加以下环境变量：

#### 数据库配置
- [ ] `DATABASE_URL` = `postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}`
- [ ] `ASYNC_DATABASE_URL` = `postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}`

#### JWT 配置
- [ ] `SECRET_KEY` = `你生成的64位密钥`
- [ ] `ALGORITHM` = `HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` = `10080`

#### API 配置
- [ ] `API_V1_STR` = `/api/v1`
- [ ] `PROJECT_NAME` = `English Tube API`
- [ ] `VERSION` = `1.0.0`

#### CORS 配置
- [ ] `BACKEND_CORS_ORIGINS` = `["https://your-domain.zeabur.app"]` （稍后更新为实际域名）

#### VOD 配置（如需要视频功能）
- [ ] `VOD_APP_ID` = `1253432963`
- [ ] `VOD_PLAY_KEY` = `你的密钥`
- [ ] `VOD_PSIGN_EXPIRE_SECONDS` = `3600`
- [ ] `VOD_PSIGN_AUDIO_VIDEO_TYPE` = `Original`

#### 短信配置（如需要）
- [ ] `TENCENT_SMS_SECRET_ID` = `你的ID`
- [ ] `TENCENT_SMS_SECRET_KEY` = `你的密钥`
- [ ] `TENCENT_SMS_SDK_APP_ID` = `你的APP_ID`
- [ ] `TENCENT_SMS_SIGN_NAME` = `你的签名`
- [ ] `TENCENT_SMS_TEMPLATE_ID` = `你的模板ID`
- [ ] `TENCENT_SMS_REGION` = `ap-guangzhou`
- [ ] `SMS_CODE_EXPIRE_MINUTES` = `10`
- [ ] `SMS_DEBUG` = `false`

### Step 5: 生成域名
- [ ] 在后端服务详情页，进入 "Networking" 标签
- [ ] 点击 "Generate Domain"
- [ ] 复制生成的域名（例如：`https://english-tube-backend.zeabur.app`）

### Step 6: 更新 CORS 配置
- [ ] 返回 "Variables" 标签
- [ ] 更新 `BACKEND_CORS_ORIGINS`，添加实际的前端域名
- [ ] 保存后服务会自动重启

### Step 7: 验证部署
- [ ] 访问 `https://你的域名/api/health`，应返回：
  ```json
  {
    "status": "ok",
    "database": "ok",
    "version": "1.0.0"
  }
  ```
- [ ] 访问 `https://你的域名/api/docs`，查看 API 文档
- [ ] 测试几个关键 API 端点

## 🔧 可选配置

### 自定义域名
- [ ] 在 "Networking" 标签点击 "Custom Domain"
- [ ] 添加你的域名（例如：`api.yourdomain.com`）
- [ ] 在你的 DNS 提供商添加 CNAME 记录
- [ ] 等待 SSL 证书自动签发（约 5 分钟）

### 监控告警
- [ ] 在项目设置中配置预算限制
- [ ] 设置资源使用告警
- [ ] 配置错误日志通知

## 📊 部署后检查

### 功能测试
- [ ] 用户注册功能
- [ ] 用户登录功能
- [ ] 视频列表获取
- [ ] 视频播放签名生成
- [ ] 收藏功能
- [ ] 学习进度记录

### 性能检查
- [ ] 检查 API 响应时间（应 < 500ms）
- [ ] 检查数据库查询性能
- [ ] 检查日志输出正常

### 安全检查
- [ ] 确认生产环境使用强密钥
- [ ] 确认 CORS 只允许必要的域名
- [ ] 确认敏感信息未暴露在日志中

## 🎉 部署完成

恭喜！你的后端服务已成功部署到 Zeabur。

**重要信息记录：**
- 后端 API 地址：`____________________________`
- API 文档地址：`____________________________`
- 数据库连接信息：已保存在 Zeabur 环境变量中
- 部署日期：`____________________________`

## 📝 下一步

1. 部署前端应用（Flutter/Admin）
2. 配置 CDN 加速
3. 设置数据库备份策略
4. 配置日志收集和监控

## 🆘 遇到问题？

参考 [DEPLOYMENT_ZEABUR.md](./DEPLOYMENT_ZEABUR.md) 中的常见问题解决方案。
