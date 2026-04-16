# bff pull

把远端 BFF 脚本同步到本地 `.rabetbase/bff/<appCode>/...`。

## 命令

```bash
rabetbase bff pull --format json
rabetbase bff pull --type ENDPOINT --format json
rabetbase bff pull --dry-run --format json
rabetbase bff pull --type HOOK --force --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--type <type>` | string | 否 | — | 仅拉指定类型：`COMMON` / `ENDPOINT` / `HOOK` |
| `--force` | boolean | 否 | — | 强制覆盖本地未同步改动 |
| `--dry-run` | boolean | 否 | — | 仅预览将要拉取的远端脚本与目标本地路径 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出

返回：
- `pulled`
- `skipped`
- `failed`

`--dry-run` 时返回预览对象，包含远端脚本、目标 `filePath` 和预期状态（如 `would_pull` / `conflict`）。

## 提示

- 默认会保护本地未同步改动，冲突时进入 `skipped: local unsynced changes`
- `--dry-run` 不会改本地文件，也不会写 lock
- `HOOK` 落盘目录依赖 alias / datasetCode 解析
- 拉取后建议立刻跑一次 `bff status`

## 参考

- [SKILL.md](../SKILL.md)
- [conflict-detection.md](../guides/conflict-detection.md)
