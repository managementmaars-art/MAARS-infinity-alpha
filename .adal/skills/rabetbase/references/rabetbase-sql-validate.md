# sql validate

校验 SQL 内容（类型检测、参数提取、危险语句检查），不实际保存。与 `sql save` 内置校验共用同一个核心。

## 本地路径约定

从文件校验时，团队约定使用项目根 **`.rabetbase/sql/<sqlName>.sql`**（与 `sql save`、`sql pull` 一致）。内联 `--sql` 不受此限。

## 命令

```bash
# 从文件校验
rabetbase sql validate --file .rabetbase/sql/getUserList.sql --format json

# 内联 SQL 校验
rabetbase sql validate --sql "SELECT * FROM users WHERE id = #{userId}" --format json

# 带 schema 交叉校验
rabetbase sql validate --file .rabetbase/sql/report.sql --schemas datasetCode1,datasetCode2 --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--file <path>` | string | 与 sql 二选一 | — | SQL 文件路径 |
| `--sql <content>` | string | 与 file 二选一 | — | 内联 SQL 内容 |
| `--schemas <codes>` | string | 否 | — | 逗号分隔的 Dataset code 列表，交叉校验表名 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出

| 字段 | 说明 |
|------|------|
| `valid` | 是否通过校验 |
| `sqlType` | SQL 类型（SELECT / INSERT / UPDATE / DELETE / DDL / UNKNOWN） |
| `isSelectOnly` | 是否为纯读查询 |
| `isDangerous` | 是否包含危险操作 |
| `tables` | 引用的表名列表 |
| `parameters` | 提取的 `#{param}` 参数 |
| `schemaWarnings` | 表名/Dataset 不匹配的警告（仅 `--schemas` 时） |

## 提示

- SQL 保存前建议先用此命令独立校验
- `--schemas` 可交叉检查 SQL 中引用的表是否在指定 dataset 中存在
- `sql save` 的内置校验与此命令完全共用同一个 `validateSql()` 核心，不可跳过

## 参考

- [SKILL.md](../SKILL.md)
- [sql-creation-workflow.md](../guides/sql-creation-workflow.md)
