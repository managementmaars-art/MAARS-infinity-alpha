# dataset list

列出当前 App 下所有 Dataset，支持服务端过滤。返回**精简列表**（每行含 `id`、`name`、`code`、`db`、`table`、`fields` 字段名列表等）；单数据集的完整结构请用 **`dataset detail`**。

## 命令

```bash
rabetbase dataset list --format json
rabetbase dataset list --name "用户" --format json
rabetbase dataset list --code "8f737f49c23e4506865b07ebe9dfa316" --format json
rabetbase dataset list --name "用户" --code "abc" --format json
rabetbase dataset list --format table
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--name <name>` | string | 否 | — | 按名称模糊过滤（服务端） |
| `--code <code>` | string | 否 | — | 按 dataset code 精确过滤（服务端） |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式：`json` / `pretty` / `table` |

## 输出

默认返回精简列表（`id`, `name`, `code`, `description`, `source`, `db`, `table`, `datasetKey`, `pk`, `fields` 为字段名字符串数组）。需要完整字段定义、操作、关联页等请执行 `rabetbase dataset detail --code …`。

## 提示

- `--name` 和 `--code` 均为服务端过滤，响应快、带宽小
- `--code` 为精确匹配，适合已知 datasetCode 的场景
- `--name` 为模糊匹配，适合搜索探索
- 两者可组合使用，同时传递时取交集
- AI Agent 推荐始终使用 `--format json`
- 列表项较多时可用 `--jq` 只取需要的键，例如：`--jq '.data.datasets[] | {code, name}'`

## 参考

- [SKILL.md](../SKILL.md)
