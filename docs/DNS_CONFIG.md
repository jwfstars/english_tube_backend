# 火山云域名配置腾讯云 DNS 解析指南

## 操作流程

### 第一步：在腾讯云 DNS 解析添加域名

1. **登录腾讯云控制台**
   - 访问：https://console.cloud.tencent.com/cns
   - 进入「DNS 解析 DNSPod」

2. **添加域名**
   - 点击「添加解析」
   - 输入你的域名（例如：`example.com`）
   - 点击「确定」

3. **记录腾讯云的 DNS 服务器地址**

   添加域名后，腾讯云会自动分配 DNS 服务器，通常是：
   ```
   f1g1ns1.dnspod.net
   f1g1ns2.dnspod.net
   ```

   **重要：** 请在「域名解析列表」中找到你的域名，点击进入，在「DNS 服务器」部分查看具体分配给你的 DNS 地址。

### 第二步：在火山云修改 DNS 服务器

1. **登录火山云控制台**
   - 访问：https://console.volcengine.com/domain
   - 进入「域名服务」

2. **修改 DNS 服务器**
   - 找到你的域名，点击「管理」
   - 点击「DNS 修改」或「修改 DNS 服务器」
   - 将原来的 DNS 服务器地址替换为腾讯云的 DNS 地址：
     ```
     f1g1ns1.dnspod.net
     f1g1ns2.dnspod.net
     ```
   - 保存修改

   **注意：** DNS 服务器修改后，生效时间通常为 24-48 小时，但一般几小时内就能生效。

### 第三步：在腾讯云添加解析记录

回到腾讯云 DNS 解析控制台，为域名添加解析记录：

#### 常用解析记录配置

**1. 主域名指向服务器（A 记录）**
```
记录类型: A
主机记录: @
记录值: 81.68.234.126
TTL: 600
```

**2. www 子域名指向服务器（A 记录）**
```
记录类型: A
主机记录: www
记录值: 81.68.234.126
TTL: 600
```

**3. API 子域名指向服务器（A 记录）**
```
记录类型: A
主机记录: api
记录值: 81.68.234.126
TTL: 600
```

**4. CDN 或其他子域名（CNAME 记录）**
```
记录类型: CNAME
主机记录: cdn
记录值: xxx.cdn.myqcloud.com
TTL: 600
```

### 第四步：验证 DNS 解析是否生效

1. **使用 dig 命令检查（macOS/Linux）**
   ```bash
   # 检查主域名
   dig example.com

   # 检查 www 子域名
   dig www.example.com

   # 检查 api 子域名
   dig api.example.com
   ```

2. **使用 nslookup 命令检查（Windows）**
   ```cmd
   nslookup example.com
   nslookup www.example.com
   nslookup api.example.com
   ```

3. **在线 DNS 检测工具**
   - https://tool.chinaz.com/dns
   - https://www.dnspod.cn/dns

### 针对 English Tube 项目的推荐配置

假设你的域名是 `englishtube.com`：

| 记录类型 | 主机记录 | 记录值 | 说明 |
|---------|---------|--------|------|
| A | @ | 81.68.234.126 | 主域名指向服务器 |
| A | www | 81.68.234.126 | www 子域名 |
| A | api | 81.68.234.126 | 后端 API |
| A | admin | 81.68.234.126 | 管理后台 |

配置完成后，访问地址：
- 前端：`https://englishtube.com` 或 `https://www.englishtube.com`
- API：`https://api.englishtube.com`
- 管理后台：`https://admin.englishtube.com`

### 第五步：配置 SSL 证书（HTTPS）

1. **在腾讯云申请免费 SSL 证书**
   - 访问：https://console.cloud.tencent.com/ssl
   - 点击「申请免费证书」
   - 选择「域名型（DV）」
   - 填写域名信息
   - 选择「DNS 验证」（因为域名已经在腾讯云 DNS 解析）
   - 系统会自动添加验证记录，通常几分钟内完成验证
   - 证书颁发后，下载 Nginx 版本的证书

2. **在宝塔面板配置 SSL**
   - 进入宝塔面板：http://81.68.234.126:8888/tencentcloud
   - 点击「网站」→ 你的站点 → 「SSL」
   - 选择「其他证书」
   - 上传下载的 `.crt` 和 `.key` 文件
   - 开启「强制 HTTPS」

## 常见问题

### Q1: DNS 修改后多久生效？
A: 通常 2-24 小时，大部分情况下几小时内就能生效。可以使用 `dig` 命令实时检查。

### Q2: 修改 DNS 后原来的邮箱还能用吗？
A: 需要在腾讯云 DNS 解析中添加相应的 MX 记录（邮箱记录），否则邮箱服务会中断。如果使用火山云的邮箱服务，需要添加火山云提供的 MX 记录。

### Q3: 可以部分记录用腾讯云，部分用火山云吗？
A: 不可以。域名的 DNS 服务器只能指向一个服务商。一旦修改为腾讯云 DNS，所有解析记录都需要在腾讯云配置。

### Q4: 如何回滚到火山云 DNS？
A: 在火山云控制台将 DNS 服务器改回火山云的 DNS 地址即可，但建议先在火山云配置好所有解析记录再切换。

### Q5: 为什么我的域名还没生效？
A: 检查以下几点：
1. DNS 服务器是否已修改为腾讯云的 DNS
2. 解析记录是否正确添加
3. 清除本地 DNS 缓存：`sudo dscacheutil -flushcache` (macOS)
4. 使用手机 4G 网络测试（避免本地缓存影响）

## 参考链接

- [腾讯云 DNS 解析文档](https://cloud.tencent.com/document/product/302)
- [DNSPod 帮助中心](https://docs.dnspod.cn/)
- [火山云域名管理](https://www.volcengine.com/docs/6257/68874)
