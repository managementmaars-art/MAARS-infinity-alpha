# sql pull

将远端自定义 SQL 同步到本地 **`<项目根>/.rabetbase/sql/`**（与 skills 中「写入本地」路径一致）。

## 命令

```bash
rabetbase sql pull --format json
rabetbase sql pull --sqlcode <xxxxxxxx-xxxxxxxx> --format json
rabetbase sql pull --name <过滤名> --format json
rabetbase sql pull --dry-run --format json
rabetbase sql pull --force --format json
```

## 参数

| Flag | 说明 |
|------|------|
| `--sqlcode` | 仅拉取指定 SQL（格式 `xxxxxxxx-xxxxxxxx`） |
| `--name` | 按展示名过滤（与 list API 一致） |
| `--force` | 覆盖与远端不一致的本地文件 |
| `--dry-run` | 预览目标路径与状态（不写文件） |

## 输出文件

每条 SQL 写入一个 `.sql` 文件，文件名由 `sqlName` 安全化得到；同名冲突时自动追加 `__<sqlCode去横线>` 后缀。

文件头部包含：

- `-- @lovrabet.sqlName`
- `-- @lovrabet.sqlCode`
- `-- @lovrabet.description`

正文为远端 `sqlContent`。

## 行为说明

- 本地已与远端内容一致：计入 `skipped: unchanged`
- 本地存在且与远端不同、未加 `--force`：跳过并提示 `local differs from remote`
- `--force` 且存在需覆盖的本地文件时：交互模式下会先确认（非交互需显式 `--force`）

## 参考

- [sql-creation-workflow.md](../guides/sql-creation-workflow.md)
- [SKILL.md](../SKILL.md)
