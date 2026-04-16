# Discord 交互式机器人

[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Discord.js](https://img.shields.io/badge/discord.js-v14.14.1-blue.svg)](https://discord.js.org/)

一个基于 Discord.js 的交互式机器人，集成 OpenCode 功能，支持私聊对话、定时任务和本地测试。

## 系统架构

### 消息处理流程
```
用户发送消息 → 存入 SQLite 消息队列
                    ↓
           每 2 秒轮询取出一条
                    ↓
           调用 OpenCode 处理（单线程）
                    ↓
           处理完成后发送回复给用户
```

- 消息队列：防止并发，同一时只处理一条消息
- Session 持久化：记住对话上下文

### 定时任务流程
```
AI 调用 CLI 命令 → 添加/删除任务到 DB
                      ↓
           每分钟检查任务是否到期
                      ↓
           到期任务 → 插入消息队列
                      ↓
           OpenCode 处理 → 发送给用户
```

### Skill 架构
```
SKILL.md                   # 项目根目录的 Skill 文件
    ↓ 启动时自动复制（根据 name 字段）
.opencode/skills/schedule/SKILL.md
    ↓
OpenCode 加载 Skill
    ↓
AI 根据指南调用 CLI 命令
    ↓
CLI 操作数据库
```

- `SKILL.md` 放在项目根目录，会被 Git 追踪
- 启动时根据 frontmatter 中的 `name` 字段复制到 `.opencode/skills/{name}/`
- AI 通过 Skill 文档学习如何使用 CLI 命令，无需自定义工具

## 环境要求

- Node.js >= 18.0.0
- npm 或 yarn
- OpenCode CLI（用于 AI 功能）

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/958877748/skills.git
cd discord-bot
```

### 2. 安装依赖

```bash
npm install
```

### 3. 配置 Token

```bash
# 方式一：使用 CLI 配置
dm-bot config --token <your-token>

# 方式二：环境变量
export DISCORD_TOKEN=<your-token>
```

### 4. 获取 Discord 机器人令牌

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 点击 "New Application" 创建新应用
3. 进入 "Bot" 标签页，点击 "Add Bot"
4. 在 "Privileged Gateway Intents" 中启用:
   - MESSAGE CONTENT INTENT
5. 复制 Bot Token

### 5. 启动机器人

```bash
# 生产环境
npm start

# 开发环境（带自动重启）
npm run dev

# Mock 模式（本地测试，无需 Discord 连接）
dm-bot --mock
```

## CLI 命令

```bash
# 启动机器人
dm-bot start [--token <token>] [--mock]

# 配置
dm-bot config --token <token>

# 重置数据库
dm-bot reset

# 定时任务管理
dm-bot schedule create "<cron>" "<content>" [repeat]
dm-bot schedule list
dm-bot schedule delete <id>
```

### Schedule 命令示例

```bash
# 创建每天8点的提醒
dm-bot schedule create "0 8 * * *" "提醒喝水" true

# 创建工作日9:30的提醒
dm-bot schedule create "30 9 * * 1-5" "开会" true

# 创建一次性提醒
dm-bot schedule create "0 10 1 * *" "月初提醒" false

# 查看所有任务
dm-bot schedule list

# 删除任务
dm-bot schedule delete 1
```

### Cron 表达式

```
┌───────────── 分钟 (0-59)
│ ┌───────────── 小时 (0-23)
│ │ ┌───────────── 日 (1-31)
│ │ │ ┌───────────── 月 (1-12)
│ │ │ │ ┌───────────── 星期 (0-6, 0=周日)
│ │ │ │ │
* * * * *
```

## Mock 模式

用于本地测试，无需真实的 Discord 连接：

```bash
# 交互式 Mock 模式
dm-bot --mock

# 非交互式 Mock 模式（代码调用）
const { startBot } = require('./index');
await startBot({ mock: 'non-interactive' });
```

## 项目结构

```
discord-bot/
├── bin/cli.js        # CLI 入口
├── index.js          # 主入口文件
├── db.js             # 数据库操作模块
├── mock.js           # Mock 模式支持
├── package.json      # 项目配置
└── skills/           # Skill 源文件目录
    └── schedule/
        └── SKILL.md  # 定时任务 Skill（AI 指南）

# 启动后自动生成（在 .gitignore 中）
.opencode/
└── skills/           # 从 skills/ 复制而来
    └── schedule/
        └── SKILL.md
```

## 数据库

使用 SQLite 存储数据:
- `message_queue` - 消息队列表
- `user_sessions` - 用户 Session 表（对话上下文）
- `scheduled_tasks` - 定时任务表

数据库文件会自动创建，无需手动初始化。

## 注意事项

- 机器人只处理私聊消息，服务器中的消息将被忽略
- 确保 OpenCode CLI 已安装并可用
- 不要将 `.env` 文件提交到版本控制
- 数据库文件 (`*.db`) 不会被 Git 追踪

## 许可证

[MIT](LICENSE)