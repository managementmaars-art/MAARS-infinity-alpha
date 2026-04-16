---
name: discord-notify
description: 向 Discord 用户发送私聊消息。当用户请求发送通知、提醒、消息到 Discord 时使用此 skill。
---

# discord-notify

向指定 Discord 用户发送私聊消息。

## When to use

**当用户说以下类型的话时，使用此 Skill：**
- "给我发个 Discord 消息"
- "通知我..."
- "发个提醒到 Discord"
- "DM 我..."

## 发送消息

```bash
node discord-notify/send.js "消息内容"
```

## 环境变量

- `DISCORD_BOT_TOKEN` - 机器人 Token
- `DISCORD_USER_ID` - 目标用户 ID
- `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` - 代理地址（可选）

## User ID 获取方式

Discord 设置 → 高级 → 开启开发者模式 → 右键自己 → 复制 ID

## 目录结构

```
discord-notify/
├── SKILL.md          # Skill 说明文档
├── send.js           # 发送 DM 消息脚本
└── package.json      # 依赖配置
```
