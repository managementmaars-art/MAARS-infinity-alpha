# bff save（已废弃）

> `bff save` 文档已废弃，不再作为推荐工作流。
> 
> 当前推荐的 BFF 流程是：
> - 本地创建：`rabetbase bff new`
> - 查看状态：`rabetbase bff status`
> - 推送远端：`rabetbase bff push --yes`
> - 拉取远端：`rabetbase bff pull`
> - 删除脚本：`rabetbase bff delete --yes --target ...`
>
> 如果只是想“新建并同步”一个 BFF，请优先使用 `bff new + bff push`，不要继续基于 `bff save` 设计新流程。

以下内容仅作为历史参考保留。

创建或更新 BFF 脚本。不带 `--id` 为新建，带 `--id` 为更新。

> **风险等级：high-risk-write** — BFF 脚本影响运行时行为，必须 `--yes` 确认。

## 命令

```bash
# 新建
rabetbase bff save --file ./scripts/getUserInfo.js --name getUserInfo --format json

# 更新
rabetbase bff save --file ./scripts/getUserInfo.js --id 42 --yes --format json

# 先预览
rabetbase bff save --file ./scripts/getUserInfo.js --id 42 --dry-run --format json

# CI 模式
rabetbase bff save --file ./scripts/getUserInfo.js --id 42 --yes --non-interactive --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--file <path>` | string | 是 | — | BFF 脚本文件路径 |
| `--id <id>` | number | 否 | — | 更新时指定脚本 ID（不传为新建） |
| `--name <name>` | string | 否 | — | 脚本名称（即 `export default function` 后的函数名） |
| `--description <desc>` | string | 否 | — | 脚本描述 |
| `--type <type>` | string | 否 | `ENDPOINT` | 脚本类型：`ENDPOINT` / `COMMON` |
| `--dry-run` | boolean | 否 | — | 预览，不实际保存 |
| `--yes` | boolean | 否 | — | 跳过高风险操作确认 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 冲突处理

返回 `blocked: true` 时，表示平台检测到冲突：
- 告知用户手动在平台操作
- 将内容写入 `.draft.js` 草稿文件
- 禁止重试或绕过

## 本地文件约定

| 类型 | 路径 |
|------|------|
| ENDPOINT | `.rabetbase/bff/<appCode>/ENDPOINT/<name>.js` |
| HOOK | `.rabetbase/bff/<appCode>/HOOK/<alias>/<operationType>/<functionNode>/<name>.js` |
| COMMON | `.rabetbase/bff/<appCode>/COMMON/<name>.js` |

## 提示

- `--name` 即 BFF 中 `export default function` 后的函数名（`scriptName`），精确匹配
- 新建时推荐传 `--name`、`--description`、`--type`
- 始终先 `--dry-run` 预览，确认无误后再加 `--yes` 执行
- `high-risk-write` 在非交互/CI 模式下必须显式传 `--yes`

## 参考

- [SKILL.md](../SKILL.md)
- [bff-creation-workflow.md](../guides/bff-creation-workflow.md)
- [conflict-detection.md](../guides/conflict-detection.md)
- [rabetbase-bff-new.md](./rabetbase-bff-new.md)
- [rabetbase-bff-push.md](./rabetbase-bff-push.md)
