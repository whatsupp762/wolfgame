# 📦 GitHub 设置指南

本指南将帮助你把 WolfGame 推送到 GitHub 并部署到云端。

## 🎯 第一步：创建 GitHub 仓库

1. 访问 [GitHub](https://github.com) 并登录你的账号 (whatsupp762)

2. 点击右上角的 "+" → "New repository"

3. 填写仓库信息：
   - **Repository name**: `wolfgame`
   - **Description**: `🐺 在线多人狼人杀游戏 - 基于Python的网页版狼人杀`
   - **Public/Private**: 选择 `Public`（公开项目）
   - **不要**勾选 "Initialize this repository with a README"（我们已经有了）

4. 点击 "Create repository"

---

## 🚀 第二步：推送代码到 GitHub

在终端中执行以下命令（已经在 wolfgame 目录下）：

```bash
# 添加远程仓库
git remote add origin https://github.com/whatsupp762/wolfgame.git

# 推送代码到 main 分支
git push -u origin main
```

如果遇到认证问题，按照 GitHub 的提示使用个人访问令牌（Personal Access Token）。

### 生成 GitHub 个人访问令牌（如果需要）：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置权限：勾选 `repo` 完整权限
4. 点击 "Generate token" 并复制令牌
5. 在推送时使用令牌作为密码

---

## ☁️ 第三步：部署到云端（推荐）

### 方法 1: Render 部署（最简单，免费）

1. 访问 [Render](https://render.com) 并注册登录

2. 点击 "New +" → "Web Service"

3. 选择 "Connect a repository" → 授权 GitHub → 选择 `wolfgame` 仓库

4. 配置部署：
   - **Name**: `wolfgame`
   - **Environment**: `Python 3`
   - **Build Command**: 留空
   - **Start Command**: `python server.py`
   - **Instance Type**: `Free`

5. 点击 "Create Web Service"

6. 等待几分钟，部署成功后会得到一个网址，例如：
   ```
   https://wolfgame-xxxx.onrender.com
   ```

7. 🎉 访问这个网址，你的狼人杀游戏就上线了！

**分享给朋友：** 只需要把这个网址发给朋友，大家就可以一起玩了！

---

### 方法 2: Railway 部署（也很简单，免费）

1. 访问 [Railway](https://railway.app) 并登录

2. 点击 "New Project" → "Deploy from GitHub repo"

3. 选择 `wolfgame` 仓库

4. Railway 会自动检测并部署

5. 在 Settings → Networking 中生成域名

6. 访问域名开始游戏！

---

### 方法 3: Heroku 部署

```bash
# 安装 Heroku CLI (如果还没安装)
# Mac: brew install heroku/brew/heroku
# Windows: 下载安装包 https://devcenter.heroku.com/articles/heroku-cli

# 登录 Heroku
heroku login

# 创建 Heroku 应用
cd wolfgame
heroku create wolfgame-yourname

# 推送并部署
git push heroku main

# 打开应用
heroku open
```

---

## 🎮 开始游戏

### 本地测试：
```bash
cd wolfgame
python3 server.py
# 访问 http://127.0.0.1:8000
```

### 局域网游戏：
- 查看你的 IP：`ifconfig` (Mac/Linux) 或 `ipconfig` (Windows)
- 朋友访问：`http://你的IP:8000`

### 云端游戏：
- 部署成功后，直接分享云端网址给朋友！

---

## 📋 快速检查清单

- [x] 创建 GitHub 仓库
- [x] 推送代码到 GitHub
- [ ] 部署到云端平台（Render/Railway/Heroku）
- [ ] 测试游戏是否正常运行
- [ ] 分享链接给朋友一起玩！

---

## 🎯 下一步

1. **测试游戏**: 至少需要 6 个人才能开始游戏
2. **分享项目**: 如果觉得好玩，在 GitHub 上给项目 Star ⭐
3. **改进游戏**: 
   - 添加更多角色（守卫、丘比特等）
   - 实现 WebSocket 实时通信
   - 添加聊天功能
   - 添加游戏回放

---

## 💡 提示

- 免费云平台可能在无活动时休眠，首次访问需要等待几十秒唤醒
- 游戏数据存储在内存中，服务重启后会清空
- 如需持久化存储，可以集成数据库

---

## 🆘 遇到问题？

1. 查看 [README.md](README.md) 了解详细使用说明
2. 查看 [DEPLOY.md](DEPLOY.md) 了解更多部署选项
3. 在 GitHub Issues 提问：https://github.com/whatsupp762/wolfgame/issues

---

**祝游戏愉快！🎉**
