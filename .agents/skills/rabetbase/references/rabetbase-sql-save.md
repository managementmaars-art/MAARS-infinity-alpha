# sql save

创建或更新自定义 SQL 查询。保存前自动执行 SQL 校验，不可跳过。

> **风险等级：write** — 建议先 `--dry-run` 预览。

## 本地路径约定

团队约定：`--file` 指向项目根下 **`.rabetbase/sql/<sqlName>.sql`**（与 `sql pull` 落盘、`guides/sql-creation-workflow.md` 一致）。示例路径如下；勿默认长期使用 `queries/` 等随意目录。

## 命令

```bash
# 新建
rabetbase sql save --file .rabetbase/sql/getUserList.sql --sqlname getUserList --format json

# 更新
rabetbase sql save --file .rabetbase/sql/getUserList.sql --sqlcode 2305f915-dd48cd4c --format json

# 先预览
rabetbase sql save --file .rabetbase/sql/getUserList.sql --sqlcode 2305f915-dd48cd4c --dry-run --format json

# CI 模式
rabetbase sql save --file .rabetbase/sql/getUserList.sql --sqlcode 2305f915-dd48cd4c --non-interactive --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--file <path>` | string | 是 | — | SQL 文件路径 |
| `--sqlcode <code>` | string | 否 | — | 更新时指定 SQL code（不传为新建） |
| `--sqlname <name>` | string | 否 | — | 查询显示名称 |
| `--db <name\|id>` | string | 否 | — | 目标数据库，支持名称或 ID |
| `--description <desc>` | string | 否 | — | 查询描述 |
| `--dry-run` | boolean | 否 | — | 预览校验结果，不实际保存 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## SQL 校验规则

保存前自动执行以下校验（与 `sql validate` 共用核心，**不可跳过**）：

- 检测 SQL 类型（SELECT / INSERT / UPDATE / DELETE / DDL）
- 阻止 DELETE / DDL（`DROP TABLE`、`TRUNCATE` 等破坏性操作）
- 提取 `#{param}` 格式的参数

## 冲突处理

返回 `blocked: true` 时，表示平台检测到冲突：
- 告知用户手动在平台操作
- 将内容写入 `.draft.sql` 草稿文件
- 禁止重试或绕过

## 提示

- 新建时推荐传 `--sqlname` 和 `--description`
- `--db` 支持按名称匹配（如 `ecommerce_db`），应用只有一个数据库时可不传
- 非 SELECT / blocked 的 SQL → 写草稿 `<sqlName>.draft.sql`，告知用户手动处理
- `--dry-run` 展示校验结果和请求预览，不实际调用保存 API

## 参考

- [SKILL.md](../SKILL.md)
- [sql-creation-workflow.md](../guides/sql-creation-workflow.md)
- [conflict-detection.md](../guides/conflict-detection.md)
