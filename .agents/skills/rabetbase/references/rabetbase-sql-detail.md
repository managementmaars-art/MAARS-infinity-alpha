# sql detail

根据 SQL code 获取完整查询详情（含 SQL 内容和参数定义）。

## 命令

```bash
rabetbase sql detail --sqlcode 2305f915-dd48cd4c --format json
rabetbase sql detail --sqlcode 2305f915-dd48cd4c --verbose --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--sqlcode <code>` | string | 是 | — | SQL code 标识符（格式：`xxxxxxxx-xxxxxxxx`） |
| `--verbose` | boolean | 否 | — | 返回完整原始对象 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出

返回 SQL 查询的完整信息：sqlCode、sqlName、sqlContent（完整 SQL 文本）、参数列表、目标数据库。

## 提示

- 修改已有 SQL 前必须先用此命令拉取最新内容
- sqlContent 是完整的 SQL/MyBatis XML 文本

## 参考

- [SKILL.md](../SKILL.md)
- [sql-creation-workflow.md](../guides/sql-creation-workflow.md)
