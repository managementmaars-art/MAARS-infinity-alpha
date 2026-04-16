# menu update

批量更新线上菜单的 CDN 资源 URL。

> **风险等级：write** — 修改线上菜单配置。

## 命令

```bash
# 交互模式（TTY）
rabetbase menu update

# 静默批量更新
rabetbase menu update --yes

# 静默更新（指定 URL）
rabetbase menu update --params '{"jsUrl":"https://...js","cssUrl":"https://...css"}'
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--params <json>` | string | 否 | — | 预填 JS/CSS URL。JSON 格式：`{"jsUrl":"...","cssUrl":"..."}` |
| `--yes` | boolean | 否 | — | 非交互：更新所有已有资源的菜单 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 三种执行模式

1. **`--yes`** — 静默批量更新所有已有资源的菜单
2. **`--params` + 非 TTY** — 静默更新，使用传入的 URL
3. **TTY 交互式** — 展示有资源的菜单列表 → 输入 JS URL → 输入 CSS URL → 确认 → 执行更新

## 输出

- 成功：`✓ Menu update completed: N menu(s) updated`
- 无目标：`! No menus with existing resources found`
- 部分失败：`! N menu(s) failed`

## 提示

- 仅更新已配置了资源 URL 的菜单（`filterMenusWithResources` 过滤）
- 典型场景：新版本构建后批量更新 CDN 地址
- 交互模式会展示受影响菜单的摘要表

## 参考

- [SKILL.md](../SKILL.md)
- [menu sync](rabetbase-menu-sync.md)
