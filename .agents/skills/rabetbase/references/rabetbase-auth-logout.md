# auth logout

退出登录，删除本地认证 cookie。

> **风险等级：write** — 删除认证文件。

## 命令

```bash
rabetbase auth logout

# deprecated alias
rabetbase logout
```

## 参数

无。

## 输出

- 已登录：`✓ Logged out`
- 未登录：`! Not logged in`

## 提示

- 删除的是本地 cookie 文件，不影响其他设备
- 退出后需重新 `rabetbase auth` 才能使用 API 命令
- `rabetbase logout` 是 deprecated alias，建议使用 `rabetbase auth logout`

## 参考

- [SKILL.md](../SKILL.md)
