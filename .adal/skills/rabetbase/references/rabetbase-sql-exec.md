# sql exec

执行已保存的 SQL 查询（通过 sqlCode 调用）。

## 命令

```bash
rabetbase sql exec --sqlcode 2305f915-dd48cd4c --format json
rabetbase sql exec --sqlcode 2305f915-dd48cd4c --params '{"keyword":"alice"}' --format json
rabetbase sql exec --sqlcode 2305f915-dd48cd4c --params '{"page":1,"pageSize":20}' --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--sqlcode <code>` | string | 是 | — | SQL code 标识符（格式：`xxxxxxxx-xxxxxxxx`） |
| `--params <json>` | string | 否 | — | SQL 参数，JSON 格式 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出

返回 SQL 执行结果，包含数据行和执行耗时。

## 提示

- `--params` 的 JSON key 必须匹配 SQL 中的 `#{param}` 占位符名称
- 可先用 `sql validate` 或 `sql detail` 查看 SQL 需要哪些参数
- 执行结果仅包含数据，不含分页元信息（分页由 SQL 本身控制）

## 参考

- [SKILL.md](../SKILL.md)
- [sql-creation-workflow.md](../guides/sql-creation-workflow.md)
