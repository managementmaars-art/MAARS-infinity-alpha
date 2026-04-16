# db update

**增量更新**已有 dblink：只传需要改的 flag，未传的字段保持服务端原值。`write`。

## 何时用

- 换库地址、改账号、轮换密码
- 改描述便于他人识别

## 命令

```bash
rabetbase db update --id 10157 --dburl new-host:3306 --format compress
rabetbase db update --id 10157 --password '***' --format compress
```

## 参数

| Flag | 必填 | 说明 |
|------|------|------|
| `--id` | **是** | dblink id（`db list`） |
| `--dbname` / `--dburl` / `--username` / `--password` / `--dbparam` / `--dbdesc` | 否 | 仅传要覆盖的项；**不传 `--password` 则不修改密码**（空字符串行为以后端为准） |

写操作支持 **`--dry-run`**：合并当前服务端记录与 CLI 覆盖项后预览（密码脱敏）。

## 参考

- [database-connection-workflow.md](../guides/database-connection-workflow.md)
- [SKILL.md](../SKILL.md)
