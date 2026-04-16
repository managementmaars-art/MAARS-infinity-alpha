# Hermes Agent 与 Self-Improving Agent CN 集成指南

> **版本**: v1.0.0 | **最后更新**: 2026-04-11

## 概述

本集成方案让 Hermes Agent 和 **Self-Improving Agent CN** 形成完整的**正负反馈闭环**：

```
┌─────────────────────────────────────────────────────────────┐
│                    自改进学习循环                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌───────────────────┐     ┌──────────────────────────┐    │
│   │   Hermes Agent     │     │  Self-Improving Agent   │    │
│   │                   │     │         CN              │    │
│   │  ✅ 成功任务 →     │     │  ❌ 失败/纠正 →          │    │
│   │  提取可复用技能    │ ←→ │  记录错误教训            │    │
│   │                   │     │                          │    │
│   │  存储位置:          │     │  存储位置:               │    │
│   │  ~/.hermes/skills/ │     │  ~/.openclaw/memory/     │    │
│   └───────────────────┘     │  self-improving/         │    │
│                             └──────────────────────────┘    │
│                                                             │
│   Wrapper/Delegate 脚本自动触发错误回调                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 集成方式

### 自动错误回调机制（已内置）

`hermes_wrapper.sh` 和 `hermes_delegate.sh` 已内置 `error_callback()` 函数：

**触发条件**:
1. 命令执行失败（退出码非0）
2. 任务超时（退出码124）
3. 并发限制达到
4. 其他运行时错误

**回调行为**:
- 将错误信息记录到 `~/.openclaw/memory/self-improving/learnings.jsonl`
- 包含时间戳、错误类型、任务描述、原始命令等上下文
- 预留 `lesson` 字段供后续分析填充

### 错误记录格式

```json
{
  "timestamp": "2026-04-11T20:46:00Z",
  "error_type": "TIMEOUT",
  "error_message": "任务执行超时 (300s): 研究竞品产品特性",
  "task": "研究竞品产品特性",
  "command": "hermes run '...' --non-interactive --no-stream --timeout 300",
  "source": "hermes-delegate",
  "context": {
    "hermes_version": "Hermes Agent v0.8.0 (2026.4.8)",
    "platform": "Darwin",
    "user": "chunhaixu"
  },
  "lesson": "TODO: 待分析此错误的根本原因和解决方案"
}
```

---

## 配置与使用

### 启用自动记录（默认启用）

```bash
# 错误回调默认启用，无需额外配置
# 记录文件位置: ~/.openclaw/memory/self-improving/learnings.jsonl
```

### 查看学习记录

```bash
# 查看所有错误记录
cat ~/.openclaw/memory/self-improving/learnings.jsonl | jq .

# 按日期过滤
cat ~/.openclaw/memory/self-improving/learnings.jsonl \
  | jq 'select(.timestamp | startswith("2026-04"))'

# 按错误类型统计
cat ~/.openclaw/memory/self-improving/learnings.jsonl \
  | jq -r '.error_type' | sort | uniq -c | sort -rn

# 查看最近的错误
tail -5 ~/.openclaw/memory/self-improving/learnings.jsonl | jq .
```

### 手动添加教训（填充 lesson 字段）

当分析出错误原因后，更新记录：

```bash
# 使用 jq 更新特定记录的 lesson 字段
RECORD_ID=$(tail -1 learnings.jsonl | jq '.timestamp')
jq "if .timestamp == \"$RECORD_ID\" then .lesson = \"应该增加超时时间到600秒或简化任务范围\" else . end" \
  learnings.jsonl > tmp.jsonl && mv tmp.jsonl learnings.jsonl
```

### 在 WorkBuddy 中使用

WorkBuddy 加载 self-improving-agent-cn Skill 后会自动：

1. **执行前检查**：读取 `learnings.jsonl` 中的历史错误
2. **模式匹配**：识别当前任务是否与历史错误相似
3. **预防性建议**：根据历史教训给出建议

---

## 最佳实践

### 1. 定期审查错误日志

建议每周检查一次学习记录：

```bash
#!/bin/bash
# review_errors.sh - 审查本周 Hermes 错误

ERROR_FILE="$HOME/.openclaw/memory/self-improving/learnings.jsonl"
THIS_WEEK=$(date +%Y-%W)

echo "=== 本周 ($THIS_WEEK) Hermes 错误报告 ==="
echo ""

if [ -f "$ERROR_FILE" ]; then
    # 统计错误数量
    TOTAL=$(grep -c "" "$ERROR_FILE" 2>/dev/null || echo 0)
    
    # 统计各类错误
    echo "📊 错误类型分布:"
    cat "$ERROR_FILE" | jq -r '.error_type' | sort | uniq -c | sort -rn | while read count type; do
        echo "   $count x $type"
    done
    
    echo ""
    echo "📝 未解决的教训 (lesson 为 TODO):"
    cat "$ERROR_FILE" | jq -r 'select(.lesson | startswith("TODO")) | "- \(.error_type): \(.task)"'
    
else
    echo "✅ 无错误记录"
fi
```

### 2. 从错误中提取技能

当同一类型的错误重复出现 3+ 次，考虑将其转化为 Hermes 技能：

```bash
#!/bin/bash
# extract_skill_from_errors.sh - 从错误中提取技能模板

ERROR_FILE="$HOME/.openclaw/memory/self-improving/learnings.jsonl"
SKILLS_DIR="$HOME/.hermes/skills"

# 找出最频繁的错误类型
TOP_ERROR=$(cat "$ERROR_FILE" | jq -r '.error_type' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')

echo "检测到高频错误类型: $TOP_ERROR"

case $TOP_ERROR in
    TIMEOUT)
        SKILL_NAME="timeout-handling"
        echo "建议创建技能: $SKILL_NAME"
        
        mkdir -p "$SKILLS_DIR/$SKILL_NAME"
        cat > "$SKILLS_DIR/$SKILL_NAME/skill.md" << EOF
---
name: timeout-handling
description: 处理可能超时的长时间任务
triggers:
  - 超时任务
  - 大量数据查询
  - 复杂研究
---

# 超时处理技能

## 策略
1. **分解任务**: 将大任务拆分为多个小步骤
2. **设置合理超时**: 简单任务60s, 中等300s, 复杂600s+
3. **工具集限制**: 只启用必要的工具减少 Token 消耗
4. **增量保存**: 每完成一步就保存中间结果
5. **重试机制**: 失败后自动重试1次

## 最佳实践
\`\`\`bash
# 推荐参数
hermes run "任务" --toolset web_search --timeout 120
\`\`\`
EOF
        
        echo "✅ 技能已创建: $SKILLS_DIR/$SKILL_NAME/skill.md"
        ;;
esac
```

### 3. 双向同步

让 Hermes 的技能系统和 Self-Improving 的错误系统互相感知：

```python
# 可选的高级集成代码示例
def sync_hermes_with_self_improving():
    """
    定期同步 Hermes 技能和 Self-Improving 记录
    """
    import json
    
    skills_dir = Path("~/.hermes/skills").expanduser()
    errors_file = Path("~/.openclaw/memory/self-improving/learnings.jsonl").expanduser()
    
    # 1. 将新技能通知给 Self-Improving
    for skill_file in skills_dir.glob("**/skill.md"):
        skill_name = skill_file.parent.name
        # 标记为从成功经验中学到的能力
        log_success(f"New skill available: {skill_name}")
    
    # 2. 分析错误模式并建议技能改进
    if errors_file.exists():
        with open(errors_file) as f:
            errors = [json.loads(line) for line in f]
        
        # 按错误类型分组
        from collections import Counter
        error_types = Counter(e['error_type'] for e in errors)
        
        for error_type, count in error_types.most_common(3):
            if count >= 3 and not any(s.name == f"{error_type}-handling" 
                                       for s in list_skills()):
                suggest_skill_creation(error_type, errors)
```

---

## 故障排除

### Q: 错误记录文件不存在？

```bash
mkdir -p ~/.openclaw/memory/self-improving/
touch ~/.openclaw/memory/self-improving/learnings.jsonl
```

### Q: jq 命令不可用？

```bash
# macOS 安装 jq
brew install jq

# 或使用 Python 替代
python3 -c "
import json
with open('learnings.jsonl') as f:
    for line in f:
        print(json.dumps(json.loads(line), indent=2))
"
```

### Q: 如何禁用错误回调？

临时禁用：
```bash
HERMES_DISABLE_SELF_IMPROVING=true hermes_wrapper.sh run "prompt"
```

永久修改脚本中的 `error_callback()` 调用处即可。

---

## 总结

| 维度 | Hermes Agent | Self-Improving Agent CN |
|------|--------------|------------------------|
| **学习来源** | ✅ 成功任务 | ❌ 失败/纠正 |
| **存储格式** | Markdown 技能文件 | JSONL 记录文件 |
| **触发时机** | 任务完成后 | 用户纠正/失败时 |
| **优化频率** | 每15个任务评估 | 每次执行前检查 |
| **内容类型** | 可复用方法论 | 应避免的错误 |

两者互补，形成**完整的正负反馈闭环**，让 Agent 系统越用越智能！
