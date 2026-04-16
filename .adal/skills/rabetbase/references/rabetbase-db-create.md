# db create

在平台**新建**一条数据库连接（dblink）。写操作（`write`），成功后可用返回的 **`id`** 做测连、分析。

## 何时用

- 新项目要把业务库接到 Lovrabet
- 与「工作台 → 连接数据库」等价，适合脚本/Agent 自动化

## 命令

```bash
rabetbase db create \
  --dbname myapp \
  --dbtype MYSQL \
  --dburl db.example.com:3306 \
  --username app \
  --password '***' \
  --dbversion 8.0 \
  --format compress
```

可选：`--dbparam` 连接串附加参数、`--dbdesc` 描述、`--autostart` 创建成功后自动发起 schema 分析（等同再执行一次 `db analyze-start`）。若分析启动失败，连接仍已创建，响应中会含 `data.analysisStartWarning`。写操作支持 **`--dry-run`** 预览请求体（密码不落盘）。

## 参数（节选）

| Flag | 必填 | 说明 |
|------|------|------|
| `--dbname` | 是 | 库名/Schema 名 |
| `--dbtype` | 是 | 如 `MYSQL`、`POSTGRESQL` |
| `--dburl` | 是 | `host:port` |
| `--username` / `--password` | 是 | 凭据 |
| `--dbversion` | 否 | 默认 `8.0` |
| `--autostart` | 否 | 创建后是否自动启动分析 |

## 校验

`--dburl` 须为可解析的 `host:port` 形式（见 CLI 报错提示）。

## 参考

- [database-connection-workflow.md](../guides/database-connection-workflow.md)
- [SKILL.md](../SKILL.md)
