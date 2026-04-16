# dataset detail

获取指定 Dataset 的完整详情：字段定义（含 v1/v2 归一化）、操作端点（含解析后的 request/response schema）、关联页面、dbtable 摘要等。默认即为「完整视图」，无需额外开关。

## 命令

```bash
rabetbase dataset detail --code 097b7361b76c42bcb12b923fa5a08861 --format json
rabetbase dataset detail --alias order --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--code <code>` | string | 与 alias 二选一 | — | Dataset code（32 位 hex UUID） |
| `--alias <name>` | string | 与 code 二选一 | — | `api.ts` 中定义的别名 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出（要点）

- **fields**：归一化字段（`name` / `displayName` / `type` / `pk` / `required` / `options` 等）
- **operations**：每项含 `method`、`path`、`host`（若有）、**已解析 JSON 的** `requestBody` / `responseBody`（原 API 为字符串）
- **dbtable**：`dbtableConfig` 关键信息（含 `allFieldNames` 由 `allFields` 拆分）
- **relatedPages**：来自 `relatedPageInfoList`（`id` / `type` / `code` / `title` / `deleted`）
- **relations**、**indexes**、**formatRules**、**validateRules** 等与平台返回一致

## CLI 标准信封与 `data` 指代

声明式命令（含本命令）在 `--format json` 或 `compress` 下，顶层为：

`{ ok, command, risk, data }`（失败时可能含 `error` 等，以实际输出为准）。

下文及 **`references/`、`guides/`** 中凡写「`data.*`」，均指该 **`data` 对象**（不是 HTTP 原始体里其它层级的同名键）。

## 平台 `get-driven-data` 与 CLI 输出的对应

阅读 OpenAPI 或对照 `rabetbase-cli/mock/get-driven-data.json` 时，需与 CLI 归一化结果区分：

| 概念 | 平台原始（`get-driven-data` 业务负载内） | CLI `dataset detail` 的 `data` |
|------|------------------------------------------|-------------------------------|
| 数据集数字 ID | `modelId` 或 `dataset.datasetId` | `data.id` |
| 数据集 32 位 hex | `modelCode` / `dataset.datasetCode` | `data.code` |
| 库表级配置 | `dbtableConfig`（与 `fields`、`operations` 等并列） | `data.dbtable`（子字段键名与 `dbtableConfig` **一致**；`allFields` 为逗号串时衍生 **`allFieldNames`**） |
| 字段列表 | `fields[]`（原始字段名可能与归一化不一致） | `data.fields[]`（v1/v2 统一为 `name` / `type` / `pk` 等） |

**日常以 CLI 的 `data.fields[]` 为准。** 完整原始形状见仓库 **`rabetbase-cli/mock/get-driven-data.json`**。勿与 HTTP 最外层的 `success`/`msg` 混淆——平台文档里的「`data`」指业务负载；CLI 文档里的「`data`」指信封内的 `data` 对象。

**平台 URL**（如 `.../data/dataset/{datasetId}#api-list`）中的 **`datasetId`** 与 OpenAPI 中的 **`data.modelId`**（或 **`data.dataset.datasetId`**）一致；CLI 中为 **`data.id`**（数字），与 **`data.code`**（32 位 hex）描述同一数据集。

### `data` 内常用键（速查）

| 信息项 | 路径（`data` 内） | 说明 |
|--------|------------------|------|
| 数据集标识 | `id`, `code`, `name`, `doVersion` | 数字 id、32 位 code、展示名 |
| 字段列表 | `fields[]` | 归一化字段（表单、查询、SQL 列名均以 `name` 为准） |
| 操作端点 | `operations[]` | 含 `method`/`path` 及解析后的 `requestBody`/`responseBody` |
| 依赖关系 | `relations[]` | 主外键（无关联时为空数组） |
| 库与表 | `db`, `dbtable`, `table` | `db` 为 `{ id, name }`；`dbtable` 为表级配置摘要 |

### 字段归一化（`data.fields[]`）

| 字段 | 含义 | 用途 |
|------|------|------|
| `name` | **列名**（接口参数中的字段名） | 查询 / 写入 / SQL |
| `displayName` | 人类可读展示名 | 表单 label |
| `type` | API 层类型（对应平台 `doType`） | 接口约束 |
| `dbType` | 数据库存储类型 | SQL 编写 |
| `pk` | 是否主键 | create 策略 |
| `required` | 是否必填 | 校验 |
| `options` | SELECT/ENUM 的 `{label, value, children}[]` | 下拉枚举 |

平台原始 JSON 中的 `systemRetain` / `autoIncrement` 等 **不会逐字段完整体现在归一化 `fields[]`**；系统时间列请结合 **`data.dbtable.createTimeField` / `updateTimeField`** 与 [`guides/backend-function.md`](../guides/backend-function.md) 约定判断。

### 数据库配置（`data.dbtable`）关键字段

| 路径 | 含义 | 用途 |
|------|------|------|
| `dbId` | 数据库 ID | SQL、跨库 |
| `tableName` | 物理表名 | SQL 表名 |
| `pkField` | 主键列名 | JOIN、条件 |
| `createTimeField.fieldName` | 创建时间列 | 筛选、排序 |
| `updateTimeField.fieldName` | 更新时间列 | 筛选、排序 |
| `creatorIdField.fieldName` | 创建人 ID 列（可能为 `null`） | 权限过滤 |

需要再缩小 JSON 时，用全局 **`--jq`**（在 `--format json` 或 `compress` 之后对信封做投影），例如：

```bash
# 仅 data 里的字段与操作名（envelope 含 ok/command/data）
rabetbase dataset detail --code <数据集编码> --format json --jq '.data | {fields, opNames: [.operations[].name]}'

# 仅查看 filter 操作的请求体 schema
rabetbase dataset detail --code <数据集编码> --format json --jq '.data.operations[] | select(.name=="filter") | .requestBody'
```

## 提示

- 写 SQL / BFF 前先调用此命令确认真实字段名、类型与枚举；关联关系可看 **relations** 或 **`dataset links`**
- `--alias` 需要先执行 `rabetbase api pull` 生成 `api.ts`
- 横切数据访问流程、外键与性能：见 [`guides/data-api-guidelines.md`](../guides/data-api-guidelines.md)

## 参考

- [SKILL.md](../SKILL.md)
- 响应形状示例：`rabetbase-cli/mock/get-driven-data.json`
