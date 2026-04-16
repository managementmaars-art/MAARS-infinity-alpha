# db tables

列出指定 dblink 下**物理表**及平台打上的分析标签（如是否已分析、是否新增表等）。只读。

## 何时用

- 写自定义 SQL / 对表前确认真实表名
- 与 `dataset list` 对照：哪些表尚未建成数据集

## 命令

```bash
rabetbase db tables --id 10157 --format compress
```

## 参数

| Flag | 必填 | 说明 |
|------|------|------|
| `--id` | **是** | dblink id（`db list`） |

## 参考

- [database-connection-workflow.md](../guides/database-connection-workflow.md)
- [SKILL.md](../SKILL.md)
