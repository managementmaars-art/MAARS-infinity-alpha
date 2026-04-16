# rabetbase app list

列出已配置应用。默认与 CLI 运行时一致：**合并**全局 `~/.rabetbase.json`（或同目录下首个匹配的旧名）与**项目**当前目录下的配置文件。

- **不加 flag**：合并视图（global + project）。
- **`--global`**：仅列出**全局**文件中的应用。
- **`--project`**：仅列出**项目**文件中的应用（与 `--global` 互斥）。

`app add` 默认写项目（`--global` 写全局）。`app use` / `app remove` 的落盘规则见各子命令 reference。

## 命令

```bash
rabetbase app list
rabetbase app list --global
rabetbase app list --project
```

> **说明：** `rabetbase app` 本身只显示 `app` 服务帮助；查看本地配置中的应用请显式执行 `rabetbase app list`。查询平台可访问应用请执行 `rabetbase app remote`。

## 参数

| Flag | 说明 |
|------|------|
| `--global` | 仅全局配置中的应用 |
| `--project` | 仅项目配置中的应用 |

## 结构化输出（`--format json` / `compress`）

`data` 为对象（**不是**顶层数组），包含 `items` 与 `meta`：

| 字段 | 说明 |
|------|------|
| `items` | 应用条目数组 |
| `meta` | **合并视图**：`globalPath`、`projectPath`、`defaultApp`（无命名默认时为**有效 appcode**）、`defaultAppSource`（`project` \| `global` \| `null`）。**`--global` / `--project`**：`scope`、`configPath` |

每个 `items[]` 元素除 `name`、`appcode`、`env` 等外，另有：

| 字段 | 说明 |
|------|------|
| `named` | `true` — 来自 `apps` 中的命名应用；`false` — 仅顶层 `appcode`/`app` 的**旧版单应用**行（`name` 可能为 `null`） |
| `definedIn` | `global` / `project` / `both`（合并视图下；单边视图下为对应侧） |
| `isDefault` | 是否为当前解析出的默认应用 |
| `isCurrent` | 是否为当前激活应用（合并视图） |

**jq 示例**（只取命名应用名）：`--format json --jq '.data.items[] | select(.named) | .name'`

无任何应用时：`data` 可能为空数组 `[]`（见命令 `message`）。

## 人类可读（`pretty` / `table`）

合并视图：先打印全局/项目配置文件路径、当前 **Default app**（及来源），再列出各应用。`--global` / `--project` 时元信息对应该单层。

## 提示

- 若列表与预期不符，先检查项目或全局 JSON **是否为合法 JSON**（例如尾随逗号会导致该侧配置被忽略）；`rabetbase doctor` 的 **Config JSON** 段可检测语法。
- 无 `apps` 时显示单应用信息，并提示可用 `app add` 迁移到多应用模式。
- 如果你想知道“当前登录账号在平台上还能访问哪些应用”，不要看 `app list`，而应执行 `rabetbase app remote`。

## 参考

- [SKILL.md](../SKILL.md) — 总索引
- [`.rabetbase.json` 配置参考](rabetbase-config.md) — 合并策略与路径
- [rabetbase doctor](rabetbase-doctor.md) — 配置与 JSON 诊断
- [rabetbase app add](rabetbase-app-add.md) — 添加应用
- [rabetbase app use](rabetbase-app-use.md) — 切换默认应用
