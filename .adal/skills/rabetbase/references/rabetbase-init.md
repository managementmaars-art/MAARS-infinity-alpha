# rabetbase init

智能初始化 `.rabetbase.json` 配置。

> **风险等级：write** — 创建或修改配置文件。

## 命令

```bash
# 交互模式（从平台拉取应用列表选择）
rabetbase init

# 指定 appcode 直接写入（非交互）
rabetbase init --appcode <code>

# 指定环境
rabetbase init --appcode <code> --env daily

# 写入全局配置
rabetbase init --appcode <code> --global

# 委托给旧 Ink 初始化流程
rabetbase init --project
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--appcode <code>` | string | 否 | — | 直接写入配置，跳过交互选择 |
| `--env <env>` | string | 否 | `production` | 目标环境：`production` / `daily` |
| `--global` | boolean | 否 | `false` | 写入全局配置而非项目配置 |
| `--project` | boolean | 否 | `false` | 委托给旧 Ink 初始化流程 |

## 执行逻辑

按优先级自动路由：

1. **`--project`** → 委托给旧版 Ink init 流程
2. **老项目检测**（仅 project scope）→ 若检测到旧配置文件（如 `.lovrabet.json`）且无 `.rabetbase.json`，自动触发 `project upgrade`
3. **`--appcode`** → 直接写入配置（单应用或 CI 模式）
4. **CI 无 `--appcode`** → 报错 `flag_missing`
5. **TTY 交互** → 从平台拉取应用列表，用户多选后写入配置

## 输出

- 成功：`✓ Successfully initialized project config` 并显示 AppCode、Env、Config 路径
- 已有配置：报错 `.rabetbase.json already exists`
- 旧项目：自动进入 `project upgrade` 流程

## 多应用

交互模式支持选择多个应用，生成多应用配置：

```json
{
  "apps": {
    "app1": { "appcode": "code1", "env": "production" },
    "app2": { "appcode": "code2", "env": "production" }
  },
  "defaultApp": "app1"
}
```

## 提示

- 这是新用户首次使用的推荐入口命令
- CI/CD 场景必须传 `--appcode`
- 已有配置时先删除，或用 `config set env ...` / `app add` / `app use` 修改；`config set appcode` 仅适合单应用场景，会写成 `apps + defaultApp`

## 参考

- [SKILL.md](../SKILL.md)
- [配置参考](rabetbase-config.md)
- [project upgrade](rabetbase-project-upgrade.md)
