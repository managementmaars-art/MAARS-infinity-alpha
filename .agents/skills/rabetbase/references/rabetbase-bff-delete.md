# bff delete

删除远端 BFF 脚本，并把本地文件移到 `.rabetbase/bff-trash/`。

> **风险等级：high-risk-write** — 必须显式 `--yes`。

## 命令

```bash
rabetbase bff delete --yes --target ENDPOINT/getUserList --format json
rabetbase bff delete --yes --target getUserList --format json
rabetbase bff delete --target ENDPOINT/getUserList --dry-run --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--target <target>` | string | 是 | — | 完整 lockKey（推荐）或短函数名 |
| `--dry-run` | boolean | 否 | — | 仅预览删除目标、远端 ID 和本地 trash 路径 |
| `--yes` | boolean | 是 | — | 跳过高风险确认 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 目标匹配规则

- 传完整 lockKey 时，精确匹配
- 只传短名时：
  - 0 个匹配 → 失败
  - 1 个匹配 → 执行删除
  - 多个匹配 → 失败并要求使用完整 lockKey

## 提示

- 这是破坏性操作，会删远端并清理本地 lock
- `--dry-run` 不会删远端、不会改 lock、不会移动本地文件
- 本地文件不会直接硬删，而是移入 `.rabetbase/bff-trash`
- 实际执行前建议先用 `bff status` / `bff list` 确认目标

## 参考

- [SKILL.md](../SKILL.md)
- [conflict-detection.md](../guides/conflict-detection.md)
