# sql list

列出当前 App 下的自定义 SQL 查询。

## 命令

```bash
rabetbase sql list --format json
rabetbase sql list --name getUserList --format json
rabetbase sql list --sqlcode 2305f915-dd48cd4c --format json
rabetbase sql list --page 2 --pagesize 20 --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--app <name>` | string | 否 | — | 多应用模式下指定应用名称 |
| `--appcode <code>` | string | 否 | — | 直接指定 appcode |
| `--sqlcode <code>` | string | 否 | — | 按 SQL code 过滤（格式：`xxxxxxxx-xxxxxxxx`） |
| `--name <name>` | string | 否 | — | 按名称过滤 |
| `--page <n>` | number | 否 | `1` | 页码 |
| `--pagesize <n>` | number | 否 | `50` | 每页数量 |
| `--verbose` | boolean | 否 | — | 返回完整 SQL 对象（含 SQL 内容和参数） |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 多应用过滤

多应用模式下：
- 不加 `--app` / `--appcode`：遍历所有已配置应用，依次列出各应用的 SQL
- 加 `--app <name>`：仅列出指定应用的 SQL
- 加 `--appcode <code>`：反查到对应 app profile，使用其 cookie/env

```bash
# 仅列出 order 应用的 SQL
rabetbase sql list --app order

# 指定 appcode
rabetbase sql list --appcode app-8b7d35a1
```

## 输出

默认返回精简列表（sqlCode, sqlName, description, db）。`--verbose` 返回完整对象含 SQL 内容。

## 提示

- `--name` 是服务端过滤，`--sqlcode` 也是服务端过滤
- 修改已有 SQL 前先用此命令找到 sqlCode
- SQL Code 格式为 `{8位hex}-{8位hex}`，如 `2305f915-dd48cd4c`

## 参考

- [SKILL.md](../SKILL.md)
- [sql-creation-workflow.md](../guides/sql-creation-workflow.md)
