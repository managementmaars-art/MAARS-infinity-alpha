# db list

列出当前应用下所有 **数据库连接（dblink）** 及最近一次**分析状态**。**先执行本命令拿到 `id`**，再调用 `db detail` / `db test` / `db tables` 等。

## 何时用

- 刚接手项目，需要知道有哪些库、分析是否跑完
- 为其它 `db` 子命令准备 **`--id`**
- 查看 **`latestAnalysisTraceId`**（供 `db analyze-status` / `db analyze-cancel`）

## 命令

```bash
rabetbase db list --format compress
rabetbase db list --page 1 --pagesize 100 --format compress
rabetbase db list --appcode app-xxxx --format compress
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--appcode` | string | 否 | 配置文件 | 覆盖当前 app |
| `--page` | number | 否 | `1` | 页码（1-based） |
| `--pagesize` | number | 否 | `100` | 每页条数 |
| `--format` | string | 否 | **compress** | `json` / `compress` / `pretty` |

## 输出要点

- `connections[]`：每条含 `id`、`dbName`、`dbType`、`latestAnalysisStatus`、`latestAnalysisTraceId` 等
- 返回中密码已脱敏
- 若接口未返回分页元数据，`paging.totalCount` 为 `null` 并带 `note`，**勿将本页条数当作全量总数**

## 参考

- [database-connection-workflow.md](../guides/database-connection-workflow.md)
- [SKILL.md](../SKILL.md)
