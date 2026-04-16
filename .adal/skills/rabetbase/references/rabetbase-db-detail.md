# db detail

按 **dblink id** 拉取单条连接的完整元数据（含分析相关字段）。密码在输出中脱敏。

## 何时用

- 已用 `db list` 拿到 `id`，需要比列表更全的字段
- 需要当前 **`latestAnalysisTraceId`** 做 `analyze status/cancel`

## 命令

```bash
rabetbase db detail --id 10157 --format compress
```

## 参数

| Flag | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--id` | number | **是** | `db list` / 工作台连接列表上的 dblink id |
| `--appcode` | string | 否 | 覆盖当前 app |
| `--format` | string | 否 | 默认 **compress** |

## 参考

- [database-connection-workflow.md](../guides/database-connection-workflow.md)
- [SKILL.md](../SKILL.md)
