# project create

创建新项目。

> **风险等级：write** — 创建项目文件和配置。

## 命令

```bash
# 交互模式
rabetbase project create

# 指定项目名
rabetbase project create my-project

# 通过 flag 指定
rabetbase project create --name my-project

# 非交互模式（必须传 name）
rabetbase project create my-project --appcode <code> --env production

# 别名
rabetbase create my-project --appcode <code>
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `<project-name>` | positional | 否 | — | 项目名称（也可用 `--name`） |
| `--name <name>` | string | 否 | — | 项目名称（优先于位置参数） |
| `--env <env>` | string | 否 | — | 目标环境 |
| `--appcode <code>` | string | 否 | — | 绑定的应用 code（跳过交互选择） |

## 两种模式

1. **交互模式** — 通过提示选择项目配置
2. **非交互模式**（`--ci` 或非 TTY）— 必须提供项目名称，支持 `--appcode` 跳过应用选择

## 提示

- `--name` 和位置参数二选一，`--name` 优先
- 非交互模式下缺少项目名会报错
- 旧命令 `rabetbase create` 是此命令的 deprecated alias
- 新项目中的 `.rabetbase.json` **只继承**全局中的少量偏好（如 `cookie`、`accessKey`、`locale`、`format`、`riskLevel`），**不会**把全局的 `apps` / `defaultApp` 复制进新项目

## 参考

- [SKILL.md](../SKILL.md)
- [rabetbase init](rabetbase-init.md)
