# menu sync

将本地页面同步为平台菜单。

> **风险等级：write** — 修改平台菜单配置。

## 命令

```bash
# 交互模式（TTY）
rabetbase menu sync

# 静默全量同步
rabetbase menu sync --yes

# 静默部分同步（预填 URL 和指定页面）
rabetbase menu sync --params '{"jsUrl":"https://...js","cssUrl":"https://...css","pages":["Page1","Page2"]}'

# 非 TTY + stdin 传入页面名
echo '["Page1","Page2"]' | rabetbase menu sync
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--params <json>` | string | 否 | — | 预填 JS/CSS URL 和/或指定页面。JSON 格式：`{"jsUrl":"...","cssUrl":"...","pages":["Page1"]}` |
| `--yes` | boolean | 否 | — | 非交互：自动创建所有本地未上线页面 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 三种执行模式

1. **`--yes`** — 静默全量同步，自动创建所有本地未在平台上的页面
2. **`--params` + 非 TTY** — 静默部分同步，按传入参数执行
3. **TTY 交互式** — 展示本地页面与线上菜单对比表 → checkbox 选择页面 → 输入 JS/CSS URL → 确认 → 执行创建

## 输出

- 成功：`✓ Menu sync completed: N menu(s) created`
- 无需同步：`✓ All local pages are already on platform` 或 `! No local pages found in src/pages`

## 提示

- 本地页面扫描 `src/pages` 目录
- 同步前会获取线上菜单列表做 diff
- 交互模式下会展示 compare table（本地 vs 线上状态）
- 页面创建需要 JS 和 CSS 资源 URL（通常指向 CDN 构建产物）

## 参考

- [SKILL.md](../SKILL.md)
