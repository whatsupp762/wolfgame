# 云端部署指南

本文档介绍如何将 WolfGame 狼人杀游戏部署到云端平台，让所有人都能通过互联网访问。

## 🚀 快速部署选项

### 1. Render 部署（推荐，免费）

[Render](https://render.com) 提供免费的 Web Service 托管，非常适合部署此项目。

**步骤：**

1. 注册 [Render](https://render.com) 账号

2. 在 Render Dashboard 点击 "New +" → "Web Service"

3. 连接你的 GitHub 仓库

4. 配置如下：
   - **Name**: `wolfgame`（或自定义名称）
   - **Environment**: `Python 3`
   - **Build Command**: 留空
   - **Start Command**: `python server.py`
   - **Plan**: 选择 `Free`

5. 点击 "Create Web Service"

6. 等待部署完成，你会获得一个类似 `https://wolfgame-xxxx.onrender.com` 的网址

7. 访问该网址即可开始游戏！

**注意事项：**
- 免费版在无活动30分钟后会休眠，首次访问需要等待几十秒唤醒
- 重启后所有房间数据会丢失（内存存储）

---

### 2. Railway 部署（推荐，免费）

[Railway](https://railway.app) 提供简单的一键部署。

**步骤：**

1. 注册 [Railway](https://railway.app) 账号

2. 点击 "New Project" → "Deploy from GitHub repo"

3. 授权并选择你的 wolfgame 仓库

4. Railway 会自动检测 Python 项目并部署

5. 在 Settings 中添加域名或使用 Railway 提供的默认域名

6. 访问域名即可使用！

---

### 3. Heroku 部署

[Heroku](https://heroku.com) 是经典的云平台（需要信用卡验证）。

**步骤：**

1. 安装 [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

2. 登录 Heroku：
   ```bash
   heroku login
   ```

3. 在项目目录下创建 Heroku 应用：
   ```bash
   cd wolfgame
   heroku create wolfgame-你的名字
   ```

4. 推送代码：
   ```bash
   git push heroku main
   ```

5. 打开应用：
   ```bash
   heroku open
   ```

---

### 4. Fly.io 部署

[Fly.io](https://fly.io) 提供全球边缘计算部署。

**步骤：**

1. 安装 [flyctl](https://fly.io/docs/hands-on/install-flyctl/)

2. 注册并登录：
   ```bash
   fly auth signup
   ```

3. 在项目目录下初始化：
   ```bash
   cd wolfgame
   fly launch
   ```

4. 按提示选择配置，部署完成后会得到访问地址

---

### 5. Vercel 部署（需要配置）

虽然 Vercel 主要用于前端，但也可以部署简单的 Python 应用。

**步骤：**

1. 安装 Vercel CLI：
   ```bash
   npm i -g vercel
   ```

2. 创建 `vercel.json`：
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "server.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "server.py"
       }
     ]
   }
   ```

3. 部署：
   ```bash
   vercel
   ```

---

## 📦 自己的服务器部署

如果你有自己的 VPS 或服务器：

### 使用 systemd（Linux）

1. 上传代码到服务器：
   ```bash
   git clone https://github.com/whatsupp762/wolfgame.git
   cd wolfgame
   ```

2. 创建 systemd 服务文件 `/etc/systemd/system/wolfgame.service`：
   ```ini
   [Unit]
   Description=WolfGame Server
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/wolfgame
   ExecStart=/usr/bin/python3 /path/to/wolfgame/server.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. 启动服务：
   ```bash
   sudo systemctl start wolfgame
   sudo systemctl enable wolfgame
   ```

4. 配置 Nginx 反向代理（可选）：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## 🔧 环境变量配置

部署时可以设置以下环境变量：

- `PORT`: 服务端口（默认 8000，云平台通常自动设置）

---

## 💡 生产环境建议

1. **持久化存储**: 当前游戏数据存储在内存中，服务重启后会丢失。如需持久化，可以：
   - 使用 Redis 存储游戏状态
   - 使用 SQLite/PostgreSQL 数据库
   - 添加定期备份机制

2. **WebSocket 支持**: 当前使用轮询（每2秒刷新），可以升级为 WebSocket 实现实时通信

3. **负载均衡**: 如果玩家很多，考虑使用 gunicorn 或 uWSGI

4. **监控**: 添加日志和监控系统

---

## 🎮 使用云端游戏

部署完成后：

1. 分享你的网站链接给朋友们
2. 所有人打开链接，就能在线一起玩狼人杀
3. 不再需要局域网限制！

---

## ❓ 常见问题

**Q: 为什么游戏数据会丢失？**  
A: 当前使用内存存储，服务重启后数据会清空。这是为了简单起见，生产环境建议使用数据库。

**Q: 可以支持更多玩家吗？**  
A: 当前限制 12 人，可以修改 `server.py` 中的限制。

**Q: 如何自定义域名？**  
A: 大多数云平台都支持绑定自定义域名，查看对应平台的文档。

---

## 📞 技术支持

如有问题，欢迎在 GitHub Issues 中提出。
