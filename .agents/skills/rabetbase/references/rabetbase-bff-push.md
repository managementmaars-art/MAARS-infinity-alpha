# bff push

把本地 BFF 脚本上传到远端。

> **风险等级：high-risk-write** — 必须显式 `--yes`。

## 命令

```bash
rabetbase bff push --yes --format json
rabetbase bff push --yes --type ENDPOINT --name getUserList --format json
rabetbase bff push --type ENDPOINT --name getUserList --dry-run --format json
rabetbase bff push --yes --type HOOK --name beforeFilter --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--type <type>` | string | 否 | — | 仅推指定类型：`COMMON` / `ENDPOINT` / `HOOK` |
| `--name <name>` | string | 否 | — | 仅推指定函数名；传时必须搭配 `--type` |
| `--force` | boolean | 否 | — | 忽略 hash 保护强制推送 |
| `--dry-run` | boolean | 否 | — | 仅预览将要推送的本地脚本 |
| `--yes` | boolean | 是 | — | 跳过高风险确认 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出

返回：
- `uploaded`
- `skipped`
- `failed`

常见 `skipped` 原因：
- `unchanged`

`--dry-run` 时返回预览对象，包含本地 `filePath`、目标模式（`create` / `update`）和预期状态（如 `unchanged` / `would_push`）。

## 提示

- 推送前先跑 `bff status`
- `--dry-run` 不会上传远端，也不会改 lock
- 精确推单个函数时用 `--type + --name`
- HOOK 推送依赖数据集 alias / datasetCode 和 operationType/functionNode

## 参考

- [SKILL.md](../SKILL.md)
- [bff-creation-workflow.md](../guides/bff-creation-workflow.md)
- [conflict-detection.md](../guides/conflict-detection.md)
