# schema export

导出与 **`rabetbase --help` 同源**的机器可读命令元数据（全部 `service` / `command`、risk、flags 等），供 Skill、脚本、IDE 对齐当前 CLI 契约。

## 命令

```bash
rabetbase schema
# 等价于
rabetbase schema export
```

- **无需登录**、**无需 appcode**。
- 默认（未覆盖配置里的 `format`）为 **`--format json`**（缩进信封）；大 payload 时 AI 可优先 **`--format compress`** 单行省 token。

## 详细说明

见仓库内用户指南：**`docs/user-guide/12-schema命令.md`**（载荷结构、`globalFlags`、`services[].commands[].flags` 等）。

## 参考

- [SKILL.md](../SKILL.md)
