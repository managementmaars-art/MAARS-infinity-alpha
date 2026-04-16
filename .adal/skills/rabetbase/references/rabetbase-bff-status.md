# bff status

检查本地 BFF 脚本与 `.rabetbase/bff.lock.json` 的同步状态。

## 命令

```bash
rabetbase bff status --format json
rabetbase bff status --remote --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--remote` | boolean | 否 | — | 额外检查远端存在但本地不存在的脚本 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出字段

- `added`：本地新增、尚未写入 lock 的脚本
- `modified`：本地有变更、和 lock 中 hash 不一致
- `unchanged`：本地与 lock 一致
- `remoteOnly`：仅远端存在（需 `--remote`）

## 提示

- `push` 前先看 `status`
- `pull` 后再次看 `status`，确认是否回到 `unchanged`
- 多应用项目建议带 `--app` 或 `--appcode`

## 参考

- [SKILL.md](../SKILL.md)
- [conflict-detection.md](../guides/conflict-detection.md)

