# db delete

**永久删除**一条 dblink 配置。**high-risk-write**：非交互环境必须带 **`--yes`**。

## 何时用

- 下线环境、误建连接需清理（确认无数据集仍依赖该连接）

## 命令

```bash
rabetbase db delete --id 10157 --yes --format compress
```

## 参数

| Flag | 必填 | 说明 |
|------|------|------|
| `--id` | **是** | dblink id |
| `--yes` | CI/脚本必填 | 跳过高危确认 |
| `--appcode` | 否 | 覆盖 app |

## 参考

- [database-connection-workflow.md](../guides/database-connection-workflow.md)
- [SKILL.md](../SKILL.md)「风险控制」
