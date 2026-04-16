# rabetbase app remove

从配置中移除一个应用。**位置参数** `<name>`；**风险等级 `high-risk-write`**，非交互环境需加 **`--yes`** 确认（或与运行时交互确认）。

名称须在合并后的 `apps` 中存在；删除落盘规则与 `app use` 相同（`--global` 或按项目/全局中该名的定义位置）。

## 命令

```bash
rabetbase app remove <name> [--global] [--yes]
```

## 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `<name>` | string | **必填** — 要移除的应用名（位置参数） |
| `--global` | boolean | 从全局配置中移除（与默认落盘规则二选一；显式 `--global` 时操作全局文件） |
| `--yes` | boolean | 跳过高风险交互确认（CI / 脚本必填） |

## 输出

确认消息。如果移除的是 `defaultApp`，还会显示新的默认应用。

## 提示

- 如果移除的是 `defaultApp`，自动切换到下一个可用应用
- 如果移除后没有剩余应用，`apps` 和 `defaultApp` 字段会被清理，退回单应用模式
- 移除操作不可撤销，谨慎执行

## 参考

- [SKILL.md](../SKILL.md) — 总索引
- [rabetbase app list](rabetbase-app-list.md) — 查看所有应用
- [rabetbase app add](rabetbase-app-add.md) — 添加应用
