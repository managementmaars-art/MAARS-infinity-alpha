---
title: "Claude Code Hook 输出机制：PreToolUse vs SessionStart"
date: 2026-04-11
category: integration-issues
module: claude-code-hooks
problem_type: integration_issue
component: tooling
severity: high
symptoms:
  - "PreToolUse hook 的 echo 输出对 LLM 完全不可见"
  - "PreToolUse 在每次工具调用时触发（50-200+ 次/会话），产生性能浪费"
  - "hook 脚本运行正常、退出码为 0，但 agent 从未响应注入的上下文"
root_cause: wrong_api
resolution_type: code_fix
tags: [hooks, sessionstart, pretooluse, context-injection, settings-json, claude-code]
---

# Claude Code Hook 输出机制：PreToolUse vs SessionStart

## Problem

llm-wiki-skill 需要让 Claude Code 在会话启动时自动检测知识库是否存在，并将该信息注入 agent 上下文。最初用 PreToolUse hook + `echo` 输出实现，但 Phase 0 验证发现 LLM 完全看不到注入的内容。这是一个**静默失效**：脚本正常运行，退出码 0，`echo` 确实打印了文本，但 Claude Code 不转发给 LLM。

## Symptoms

- hook 脚本运行成功（退出码 0），但 agent 行为没有任何变化
- PreToolUse 在每次 Bash、Read、Write、Grep 等工具调用时都触发，一个典型会话触发 50-200+ 次
- `echo` 的输出只出现在 tool stdout 中，Claude Code 不会将其注入 LLM 上下文

## What Didn't Work

**PreToolUse + echo 纯文本输出。**

```json
// settings.json — 错误做法
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "bash -c 'if [ -f .wiki-schema.md ]; then echo \"[llm-wiki] 检测到知识库\"; fi'"
      }
    ]
  }
}
```

两个致命问题：
1. `echo` 输出是 plain text，Claude Code 只处理 PreToolUse 的 `decision` 字段（用于阻断/放行工具调用），不转发纯文本
2. PreToolUse 在每次工具调用时触发，即使输出可见也会产生巨大噪音

## Solution

切换到 **SessionStart hook**，输出 JSON 格式，通过 `additionalContext` 字段注入上下文。

### Hook 脚本模式

```bash
#!/usr/bin/env bash
set -euo pipefail

# 检测 wiki 知识库位置
wiki_index=""  # 实际检测逻辑省略

if [ -z "$wiki_index" ]; then
  # 未检测到 wiki，静默退出
  echo '{}'
  exit 0
fi

# 检测到 wiki，输出 JSON 上下文
cat <<EOF
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"[llm-wiki] 检测到知识库: ${wiki_index}，回答问题时优先查阅 wiki 内容获取上下文"}}
EOF
```

### Hook 注册（install.sh 中用 jq）

```bash
# 幂等注册 — 如果命令已存在则跳过
jq --arg cmd "$hook_command" '
  .hooks = (.hooks // {}) |
  .hooks.SessionStart = ((.hooks.SessionStart // []) + [{"hooks":[{"type":"command","command":$cmd}]}])
' "$settings_path" > "$tmp_file" && mv "$tmp_file" "$settings_path"
```

### 三种 Hook 事件对比

| Hook 事件 | 触发频率 | LLM 可见输出 | 适用场景 |
|-----------|----------|-------------|---------|
| `SessionStart` | 每会话 1 次 | JSON `additionalContext` | 注入全局上下文 |
| `PreToolUse` | 每次工具调用 | 仅 `decision` 字段 | 工具调用过滤/阻断 |
| `PostToolUse` | 每次工具调用后 | 不可见 | 日志、副作用 |

## Why This Works

- SessionStart 每个会话只触发一次，没有性能开销
- `additionalContext` 字段的文本会被 Claude Code 注入到 LLM 的上下文窗口中
- 未检测到时返回 `{}` 完全静默，不浪费 token
- 幂等注册确保重复运行 `install.sh` 不会重复添加 hook

## Prevention

- **永远用 SessionStart 注入一次性会话上下文**，不要用 PreToolUse
- **PreToolUse 只用于工具调用拦截**，输出只有 `decision` 字段对 LLM 可见
- **hook 脚本必须输出 JSON**，plain text `echo` 对大多数 hook 事件不可见
- Phase 0 验证步骤：实现 hook 后先手动测试 LLM 是否真的能看到输出，不要假设 hook 输出一定被转发

## 审查中附带修复的次要 Bug

以下 bug 在同一次对抗性审查中发现并修复：

| Bug | 文件 | 修复 |
|-----|------|------|
| `grep -rl` 把文件名中的 `.` 当作正则通配符 | `scripts/delete-helper.sh` | 加 `-F` 改为固定字符串匹配 |
| `invalidate` 要求文件存在，但级联删除后文件已不存在 | `scripts/cache.sh` | 移除 `require_file` 检查 |
| mkdir 遗漏 `wiki/queries/` 目录 | `scripts/init-wiki.sh` | 在 brace expansion 中补上 |
| Python 内联脚本缺少 `import os` | `scripts/cache.sh` | 添加 import |

## Related

- `scripts/hook-session-start.sh` — SessionStart hook 完整实现
- `install.sh` — `--install-hooks` / `--uninstall-hooks` 注册逻辑
- `tests/regression.sh` — hook 相关的 3 个回归测试
