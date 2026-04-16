---
name: screenshot_to_feishu
description: Take screenshot and send to Feishu. Use when user wants to capture screen.
user-invocable: true
---

# screenshot_to_feishu

Take screenshot on Mac mini and send to Feishu.

## Triggers

- "截图"
- "截图发给我"
- "截图发送到飞书"
- "screenshot"
- "截图skill"

## 使用方法

直接在 `Apple的Mac mini` 节点上运行脚本：

```
nodes.run(node="Apple的Mac mini", command=["bash", "-l", "/Users/apple/.openclaw/skills/screenshot-to-feishu/scripts/screenshot-to-feishu.sh"])
```

脚本会自动：
1. 截图并保存到桌面（带时间戳）
2. 自动发送到飞书

## 输出

- 截图文件: `~/Desktop/screenshot_YYYYMMDD_HHMMSS.png`
- 飞书消息: 发送给用户

## 错误处理

- 自动重试 3 次（间隔 2 秒）
- 检查截图文件是否存在且非空
- 检查发送是否成功
- 失败时保留截图文件供手动发送
