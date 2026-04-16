# dataset operations

获取指定 Dataset 的操作列表；可选指定单个操作名获取完整参数定义。

## 命令

```bash
rabetbase dataset operations --alias order --format json
rabetbase dataset operations --alias order --operation filter --format json
rabetbase dataset operations --code 097b7361b76c42bcb12b923fa5a08861 --operation getOne --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--code <code>` | string | 与 alias 二选一 | — | Dataset code（32 位 hex UUID） |
| `--alias <name>` | string | 与 code 二选一 | — | `api.ts` 中定义的别名 |
| `--operation <name>` | string | 否 | — | 操作名（如 `filter` `getOne` `create` `update` `delete`） |
| `--verbose` | boolean | 否 | — | 返回完整操作对象（含 `requestFields` / `responseFields` / `path`） |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出

不传 `--operation` 时返回操作摘要列表；传 `--operation` 时返回该操作的完整参数定义。

## 提示

- 生成 SDK 代码前，先用此命令确认操作是否存在、参数定义
- 常见操作：`filter`（列表查询）、`getOne`（单条）、`create`（新建）、`update`（更新）、`delete`（删除）、`aggregate`（聚合）

## 参考

- [SKILL.md](../SKILL.md)
