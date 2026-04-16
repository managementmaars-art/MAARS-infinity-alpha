# rabetbase app use

切换默认应用（持久写入配置文件的 `defaultApp`）。名称校验基于**全局 + 项目合并**后的 `apps`（与 `app list` 一致）。**位置参数** `<name>`，与 lovrabet-runtime-cli 一致。

**写入哪一文件**：显式 `--global` → 始终写全局 `~/.rabetbase.json`；否则若该名在**项目** `apps` 中 → 写项目；若仅出现在**全局** `apps` → 写全局。

## 命令

```bash
rabetbase app use <name> [--global]
```

## 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `<name>` | string | **必填** — 已配置的应用名（位置参数，如 `order`、`product`） |
| `--global` | boolean | 强制将 `defaultApp` 写入全局配置文件 |

## 输出

确认消息，显示切换后的默认应用名及 appcode。

## 提示

- 应用名须在合并配置中存在（可先只在全局 `app add --global`，或仅在项目里配置）
- 切换后所有不带 `--app` flag 的命令都会使用新的默认应用
- 如果只需临时切换，使用 `--app <name>` flag 而非 `app use`

## 参考

- [SKILL.md](../SKILL.md) — 总索引
- [rabetbase app list](rabetbase-app-list.md) — 查看所有应用
- [rabetbase app add](rabetbase-app-add.md) — 添加应用
