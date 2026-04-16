# 数据库连接（db）工作流

前置知识：`auth` 已登录、当前上下文有 **appcode**（`.rabetbase.json` 或 `--appcode`）。详见 [SKILL.md](../SKILL.md)「前置条件」。

## 解决什么问题

| 场景 | 说明 |
|------|------|
| 接入已有 MySQL/PostgreSQL 等 | 在平台登记 **dblink**，供后续同步表结构、生成数据集 |
| 改连接串 / 账号 | 更新已有连接，避免在界面点来点去 |
| 验证网络与白名单 | **测连**确认研发环境能打到库 |
| 同步结构到 Lovrabet | **分析任务**把表结构同步到平台；可看进度、取消 |
| 看物理表与差异 | **tables / diff** 在写 SQL、对表前确认真实库状态 |

**与 `dataset` 的区别**：`dataset detail` 里的 `dbId` 来自数据集绑定；**`db list` 的 `id` 是 dblink 主键**，二者数值上通常一致，但 **CLI 管连接用 `db *`，管模型用 `dataset *`**。

## 前置参数从哪拿

```text
appcode     → 配置 / rabetbase app list / --appcode app-xxxx
dblink id   → rabetbase db list 返回 connections[].id（或工作台「数据库连接」列表上的 id）
trace/plan  → 见下一节（分析任务专用）
```

## traceId / planId（`db analyze-*` 用）

三者等价说法：**分析任务 id、plan id、trace id**（平台字段名多为 `latestAnalysisTraceId`）。

| 来源 | 命令 | 字段 |
|------|------|------|
| 列表快照 | `db list` | 每条连接 `latestAnalysisTraceId`、`latestAnalysisStatus` |
| 单条详情 | `db detail --id <n>` | 同上 |
| 刚启动的任务 | `db analyze-start --id <n>` | 响应 `data.planId` |

**`db analyze-status`**：必须传 **`--plan <id>`**，值来自上表之一。

**`db analyze-cancel`**：可省略 `--plan`——CLI 会先 `getOne` 用当前连接上的 **`latestAnalysisTraceId`**；若没有则必须显式 **`--plan`**。

## 推荐流程（Agent）

### A. 只读排查（已有连接）

```text
db list --format compress
  → 记下目标 connections[].id
db test --id <id>
db tables --id <id>
db diff --id <id>        # 可选：看与上次分析的 schema 差异
```

### B. 新建连接并跑分析

```text
db create --dbname … --dbtype MYSQL --dburl host:port --username … --password … [--autostart]
  → 记下返回 connection.id 或 data 中的 id
db test --id <id>        # 可选
db analyze-start --id <id>
  → 记下 data.planId
db analyze-status --id <id> --plan <planId>   # 轮询直到终态
```

### C. 改连接再测

```text
db detail --id <id>
db update --id <id> --dburl … [--username …] [--password …]   # 只传要改的字段
db test --id <id>
```

### D. 删除连接（高危）

```text
db delete --id <id> --yes    # high-risk-write，非交互必须 --yes
```

## 与其它命令的配合

- **写 SQL 前要 `dbId`**：`dataset detail --code …` 里 `db.id`；或 `db list` 的 `id` 与数据集侧 `dbId` 对应。
- **看模型关系**：仍用 `dataset links`（需要 `--db` 时，id 或名称可与 `db list` 对照）。
- **不确定 flags**：`rabetbase schema`（无需登录）查契约。

## 输出格式

db 子命令默认 **`--format compress`**（省 token）。需要人工读时用 `--format json`。

## 参考

- 各子命令单页：`../references/rabetbase-db-*.md`
- [SKILL.md](../SKILL.md)
