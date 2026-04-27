# 🐺 WolfGame - 在线多人狼人杀

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Web-orange.svg)

一个基于 Python 的在线多人网页狼人杀游戏，支持局域网和云端部署。

[在线演示](#) | [快速开始](#快速开始) | [云端部署](DEPLOY.md) | [游戏规则](#游戏规则)

</div>

---

## ✨ 特性

- 🎮 **完整游戏流程** - 标准狼人杀规则，夜晚/白天阶段自动推进
- 👥 **多人在线** - 支持 6-12 人同时游戏
- 🎭 **丰富角色** - 狼人、预言家、女巫、猎人、村民
- 🌐 **纯网页** - 无需安装，浏览器直接玩
- 🚀 **零依赖** - 仅使用 Python 标准库
- ☁️ **云端部署** - 可部署到 Render、Railway、Heroku 等平台
- 📱 **响应式设计** - 支持手机、平板、电脑

---

## 🎯 游戏角色

| 角色 | 阵营 | 技能 |
|------|------|------|
| 🐺 狼人 | 狼人阵营 | 每晚击杀一名玩家 |
| 🔮 预言家 | 好人阵营 | 每晚查验一名玩家身份 |
| 💊 女巫 | 好人阵营 | 拥有解药（救人）和毒药（毒人）各一瓶 |
| 🏹 猎人 | 好人阵营 | 出局时可开枪带走一名玩家（待实现）|
| 👨‍🌾 村民 | 好人阵营 | 无特殊技能 |

---

## 🚀 快速开始

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/whatsupp762/wolfgame.git
cd wolfgame

# 运行服务器（Python 3.7+）
python3 server.py
```

访问 http://127.0.0.1:8000 开始游戏！

### 局域网多人游戏

1. 查看你的本机 IP 地址：
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` 或 `ip addr`

2. 其他玩家访问 `http://你的IP:8000`

3. 例如：`http://192.168.1.8:8000`

### ☁️ 云端部署（推荐）

想让全世界的朋友都能玩？查看 **[云端部署指南](DEPLOY.md)**

#### 一键部署到 Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

#### 一键部署到 Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

> 详细的云端部署步骤请查看 [DEPLOY.md](DEPLOY.md)

---

## 🎮 游戏规则

### 游戏流程

1. **创建/加入房间**
   - 房主创建房间获得房间号
   - 其他玩家输入房间号加入
   - 至少需要 6 名玩家

2. **身份分配**
   - 系统自动随机分配角色
   - 每个玩家只能看到自己的身份
   - 狼人之间可以看到队友

3. **夜晚阶段**
   - 🐺 狼人选择击杀目标
   - 🔮 预言家查验一名玩家身份
   - 💊 女巫决定是否使用药剂

4. **白天阶段**
   - 公布昨夜死亡情况
   - 存活玩家依次发言
   - 全员投票放逐可疑玩家

5. **胜利条件**
   - **狼人胜利**: 狼人数量 ≥ 好人数量
   - **好人胜利**: 所有狼人出局

---

## 📖 使用说明

### 创建房间

1. 输入你的昵称
2. 点击"创建房间"
3. 记下房间号并分享给朋友

### 加入房间

1. 输入你的昵称
2. 输入房间号
3. 点击"加入房间"

### 开始游戏

1. 等待至少 6 名玩家加入
2. 房主点击"开始游戏"
3. 系统自动分配身份并开始第一夜

### 游戏操作

- **狼人**: 夜晚选择击杀目标
- **预言家**: 夜晚选择查验对象
- **女巫**: 夜晚决定是否救人/毒人
- **所有人**: 白天依次发言后投票

---

## 🛠️ 技术栈

- **后端**: Python 3.7+ (标准库)
  - `http.server` - HTTP 服务器
  - `json` - 数据序列化
  - `threading` - 并发处理
  
- **前端**: 原生 HTML/CSS/JavaScript
  - 无框架依赖
  - localStorage 会话管理
  - 轮询实时更新

---

## 📁 项目结构

```
wolfgame/
├── server.py           # 主服务器文件（包含所有逻辑和前端HTML）
├── README.md          # 项目说明
├── DEPLOY.md          # 云端部署指南
├── requirements.txt   # Python 依赖（空，无需额外依赖）
├── Procfile           # Heroku/Render 部署配置
├── runtime.txt        # Python 版本指定
└── .gitignore         # Git 忽略文件
```

---

## 🔧 配置选项

### 环境变量

- `PORT`: 服务器端口（默认 8000）

### 角色配置

编辑 `server.py` 中的 `ROLE_TEMPLATE` 可调整角色分配：

```python
ROLE_TEMPLATE = ["werewolf", "werewolf", "seer", "witch", "hunter", "villager", "villager", "villager"]
```

---

## 🚧 待开发功能

- [ ] WebSocket 实时通信（替代轮询）
- [ ] 猎人开枪机制
- [ ] 守卫、丘比特等更多角色
- [ ] 聊天系统
- [ ] 法官视角
- [ ] 游戏回放
- [ ] 数据持久化（数据库）
- [ ] 房间密码保护
- [ ] 游戏历史记录

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- 狼人杀游戏规则来自经典桌游
- 感谢所有贡献者和玩家

---

## 📞 联系方式

- 提交 Issue: [GitHub Issues](https://github.com/whatsupp762/wolfgame/issues)
- 项目主页: [GitHub](https://github.com/whatsupp762/wolfgame)

---

<div align="center">

**⭐ 如果觉得好玩，请给个 Star！ ⭐**

Made with ❤️ by whatsupp762

</div>
