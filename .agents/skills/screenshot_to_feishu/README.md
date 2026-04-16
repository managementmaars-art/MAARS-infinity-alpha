# Screenshot to Feishu Skill - Setup Guide

一个自动截图并发送到飞书的 skill 示例。

## Quick Start

### 1. 创建 Skill 目录结构

```
skills/
└── screenshot-to-feishu/
    ├── SKILL.md          # Skill 配置（关键！）
    └── scripts/
        └── screenshot-to-feishu.sh
```

### 2. SKILL.md 配置（核心）

```yaml
---
name: screenshot_to_feishu
description: Take screenshot and send to Feishu.
user-invocable: true  # ⚠️ 必须设置为 true 才能自动触发
---

# screenshot_to_feishu

## Triggers
- "截图"
- "截图发给我"
- "screenshot"

## 使用方法
nodes.run(node="Apple的Mac mini", command=["bash", "-l", "脚本路径"])
```

### 3. 关键配置说明

| 字段 | 作用 | 必须？ |
|------|------|--------|
| `user-invocable: true` | 允许用户直接通过 trigger 触发 | ✅ |
| `triggers` | 触发关键词列表 | ✅ |

### 4. Trigger 工作流程

```
用户发送 "截图"
    ↓
OpenClaw 检测到 triggers 匹配
    ↓
系统自动执行 skill（无需 agent 主动调用）
    ↓
返回结果给用户
```

## 实际示例

### 脚本示例（screenshot-to-feishu.sh）

```bash
#!/bin/bash
# 截图并发送到飞书

timestamp=$(date +%Y%m%d_%H%M%S)
screenshot_path="/Users/apple/Desktop/screenshot_${timestamp}.png"

# 截图
screencapture "$screenshot_path"

# 发送到飞书
openclaw message send \
    --channel feishu \
    --target "ou_用户ID" \
    --media "$screenshot_path" \
    --message "📸 截图"
```

## 踩坑记录

### ❌ 问题1: Trigger 不生效

**原因**: 漏了 `user-invocable: true`

**解决**: SKILL.md 开头必须包含：
```yaml
user-invocable: true
```

### ❌ 问题2: 节点上缺少依赖

**错误日志**:
```
Cannot find module '@larksuiteoapi/node-sdk'
Unknown channel: feishu
```

**解决**: 在节点上安装依赖
```bash
cd /Users/apple/.openclaw/extensions/feishu && npm install
```

### ❌ 问题3: 脚本发送失败

**原因**: grep 判断条件错误

**解决**: 使用正确的输出匹配
```bash
if openclaw message send ... 2>&1 | grep -q "Sent via Feishu"; then
    echo "✅ 发送成功"
fi
```

## 验证 Trigger 是否生效

查看日志：
```bash
grep "dispatching to agent" /Users/apple/.openclaw/logs/gateway.log
```

如果 `replies=0` → 系统自动触发（正确）
如果 `replies=1` → agent 主动回复（不是 trigger）

## 发布到 ClawHub（可选）

```bash
clawhub publish /path/to/skill --changelog "描述更新内容"
```

## 总结

创建可触发的 skill 只需3步：

1. ✅ 写好 `user-invocable: true`
2. ✅ 配置 `triggers` 关键词
3. ✅ 脚本返回结果

---

*经验来源: TClawdE @ 2026-02-04*
