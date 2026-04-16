# Backend Function 脚本编写规范

> 目标：约束 AI 在 Lovrabet 项目中编写 Backend Function 时的行为，避免凭空编造字段、误用 SDK 返回值、写出不可维护或高风险的脚本。
>
> 前置阅读：`data-api-guidelines.md`

## 阅读指南（按需跳转）

| 需求 | 位置 |
|------|------|
| CLI 信封、`datasetId`、`dbtableConfig` ↔ `data.dbtable`、OpenAPI 对照 | [`references/rabetbase-dataset-detail.md`](../references/rabetbase-dataset-detail.md) |
| 前后端数据访问、外键、性能 | [`data-api-guidelines.md`](data-api-guidelines.md) |
| HOOK/ENDPOINT 目录、注释模板、`context.client`、事务 | 下文 |

## 何时使用

当任务满足任一条件时，必须阅读并遵守本指南：

* 编写 HOOK 脚本
* 编写 ENDPOINT 脚本
* 在 BFF 中调用数据集 API
* 在 BFF 中调用自定义 SQL
* 在 BFF 中处理事务、权限、脱敏、聚合或多表逻辑

## 核心原则

* 先校验数据集和字段，再写脚本
* 所有脚本统一使用 `export default async function`
* 前后端单条查询统一使用 `getOne({ id })`
* BFF 中的 SQL 返回值与前端 SDK 不同，不能混用
* 平台自动维护字段不得手动设置
* 发现明显性能问题时，必须先改写再继续
* 新建与长期维护的 BFF 源文件**仅**在 **`.rabetbase/bff/<appCode>/...`**（`bff new` / `bff pull` 与 `bff status` 扫描范围）；不要写在 `src/` 等目录，详见 [`bff-creation-workflow.md`](bff-creation-workflow.md)
* BFF 脚本只写**纯 JavaScript（ESM）**，支持到 **ES2023** 特性，不支持 TypeScript

## 脚本类型

| 类型 | 作用 | 路径 / 触发方式 | 查询方式 |
|------|------|----------------|----------|
| HOOK | 挂在标准数据接口前后执行 | Before / After | 通过数据集详情 |
| ENDPOINT | 独立业务端点 | `POST /api/endpoint/{appCode}/{scriptName}` | `rabetbase bff list --format json`（默认） |
| COMMON | 公共函数，供其他脚本 import 复用 | 被其他 BFF 引用 | `rabetbase bff list --format json`（type=COMMON） |

写 BFF 前，先查一下公共函数列表（`rabetbase bff list --format json`），看是否有可复用的工具函数。

## 平台配置地址

| 类型 | 地址 |
|------|------|
| HOOK | `https://app.lovrabet.com/app/{appCode}/data/dataset/{datasetId}#api-list` |
| ENDPOINT | `https://app.lovrabet.com/app/{appCode}/data/backend-function` |

其中 `datasetId` 需要通过 `rabetbase dataset detail --code xxx --format json` 获取。

**平台 URL / OpenAPI `get-driven-data` 与 CLI `data` 的字段对应**（含 `datasetId`、`dbtable`）：见 [`references/rabetbase-dataset-detail.md`](../references/rabetbase-dataset-detail.md)。

## 本地目录约定

BFF 脚本统一存放在 `.rabetbase/bff/<appCode>/` 目录下，由 CLI 同步体系管理：

```text
.rabetbase/bff/<appCode>/
├── HOOK/
│   └── <alias>/
│       └── <operationType>/
│           └── <functionNode>/
│               └── <name>.js
├── ENDPOINT/
│   └── <scriptName>.js
└── COMMON/
    └── <scriptName>.js
```

规则：

* HOOK 放在 `.rabetbase/bff/<appCode>/HOOK/<alias>/<operationType>/<functionNode>/`
* ENDPOINT 放在 `.rabetbase/bff/<appCode>/ENDPOINT/`
* COMMON 放在 `.rabetbase/bff/<appCode>/COMMON/`
* 本地文件是可选的人类辅助物，平台是唯一 source of truth

### HOOK 目录名优先级

HOOK 的第一层子目录名（标识数据集）按以下优先级确定：

1. **alias**（优先）：来自 `api.ts`（由 `rabetbase api pull` 生成），如 `customers`、`orders`
2. **datasetCode**（兜底）：当 `api.ts` 不可用时，直接使用 32 位数据集编码

推荐始终先执行 `rabetbase api pull` 以获得可读性更好的 alias 命名。

## 文件命名与函数命名

| 类型 | 文件名 | 导出函数 |
|------|--------|---------|
| HOOK Before | `<name>.js`（位于 `HOOK/<alias>/<operationType>/before/`） | `<name>` |
| HOOK After | `<name>.js`（位于 `HOOK/<alias>/<operationType>/after/`） | `<name>` |
| ENDPOINT | `<scriptName>.js`（位于 `ENDPOINT/`） | `<scriptName>` |
| COMMON | `<scriptName>.js`（位于 `COMMON/`） | `<scriptName>` |

常见 `Operation`：

* `filter`
* `getOne`
* `create`
* `update`
* `delete`
* `aggregate`

## 强制工作流

```text
理解需求 -> 校验数据集与字段 -> 选择脚本类型 -> 生成本地脚本 -> 自检 -> status -> dry-run -> push/pull
```

### Step 1：理解需求

开始写脚本前，AI 必须确认：

* 这是 HOOK 还是 ENDPOINT
* 作用于哪个数据集或接口
* 输入参数是什么
* 返回结构是什么
* 是否涉及权限、脱敏、事务、外部依赖

### Step 2：校验数据集、字段与关系

写任何 BFF 逻辑前，必须执行 `rabetbase dataset detail --code xxx --format json`，必要时先用 `rabetbase dataset list --format json` 定位数据集。

必须确认：

* 字段真实存在
* 字段类型正确
* 必填字段已识别
* 外键或关联关系真实存在

禁止行为：

* 未读取数据集详情就直接写字段名
* 凭经验猜 `user_id`、`status`、`deleted` 等通用字段
* 把前端代码里的字段名照搬到当前 BFF

### Step 3：选择脚本类型

使用规则：

* Before：修改请求参数、补默认值、做前置校验
* After：修改返回结果、做脱敏、补充展示字段
* ENDPOINT：独立业务流程、事务、多表写入、复杂业务端点

### Step 4：生成脚本

在本地 `.rabetbase/bff/<appCode>/...` 下生成或修改完整脚本。

脚本必须包含：

* 顶部注释
* `export default async function`
* 明确的输入输出
* 数据集映射
* 必要的错误处理

本地文件是主工作副本：

* 新建时用 `rabetbase bff new`
* 修改时直接编辑 `.rabetbase/bff/<appCode>/...`
* 需要远端最新内容时先 `rabetbase bff pull`

如果 BFF 行为与预期不符，或 `push` 显示 `unchanged` 但效果没变，先确认远端实际运行的是哪份代码：

* `rabetbase bff detail --id <id> --format json`
* 必要时再 `rabetbase bff pull --format json` 同步远端到本地

先确认“远端现在是什么”，再决定是否继续改本地、查页面或查锁状态。

### Step 5：自检

至少检查：

* 函数名匹配（用于 `scriptName` 参数）
* 顶部注释占位符已替换
* 单条查询是否统一使用 `getOne({ id })`
* SQL 返回值是否按 BFF 语义处理
* 是否误设置系统字段
* 是否存在明显性能问题

### Step 6：检查状态并预览

至少执行：

* `rabetbase bff status --format json`
* `rabetbase bff push --type <type> --name <name> --dry-run --format json`

确认：

* 脚本进入 `added` / `modified`
* 预览返回的 `lockKey`、`mode`、`status` 符合预期

### Step 7：推送到平台

确认无误后执行：

* `rabetbase bff push --yes --type <type> --name <name> --format json`

如果目标是同步远端到本地，则执行：

* `rabetbase bff pull --format json`

## 顶部注释规范

顶部注释必须写清楚：

* 脚本功能描述
* 接口路径
* 平台配置地址
* HTTP 请求参数
* 返回数据结构

占位符必须替换为真实值，不能保留：

* `{appCode}`
* `{datasetCode}`
* `{datasetId}`
* `{operation}`
* `{scriptName}`

### HOOK 注释模板

```javascript
/**
 * 脚本功能描述
 *
 * [接口路径] POST /api/{appCode}/{datasetCode}/{operation}
 * [平台配置] https://app.lovrabet.com/app/{appCode}/data/dataset/{datasetId}#api-list
 *
 * [HTTP 请求体参数]
 * { "field1": "字段说明" }
 *
 * [返回数据结构]
 * HOOK: 返回修改后的 params
 */
```

### ENDPOINT 注释模板

```javascript
/**
 * 脚本功能描述
 *
 * [接口路径] POST /api/endpoint/{appCode}/{scriptName}
 * [平台配置] https://app.lovrabet.com/app/{appCode}/data/backend-function
 *
 * [HTTP 请求体参数]
 * { "field1": "字段说明" }
 *
 * [返回数据结构]
 * ENDPOINT: 返回业务数据对象
 */
```

## 参数与返回值

| 类型 | `params` 含义 | 返回要求 |
|------|---------------|---------|
| Before | 请求参数 | 返回修改后的 `params` |
| After | 响应结果，如 `tableData`、`tableColumns` | 返回修改后的 `params` |
| ENDPOINT | HTTP 请求体 JSON | 返回业务数据对象 |

`context` 常用字段：

* `context.userInfo`
* `context.appCode`
* `context.tenantCode`
* `context.client`

## 数据集调用规范

通过 `context.client.models.dataset_xxx` 调用数据集，推荐先定义映射表：

```javascript
const TABLES = {
  customers: "dataset_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", // 数据集: 客户 | 数据表: customers
  orders: "dataset_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", // 数据集: 订单 | 数据表: orders
};

const models = context.client.models;
const order = await models[TABLES.orders].getOne({ id: 123 });
```

规则：

* 必须使用 32 位数据集编码
* 每个映射后写 `// 数据集: ... | 数据表: ...`
* 查询单条统一使用 `getOne({ id })`
* 列表查询优先使用 `filter()`

常用方法：

| 方法 | 说明 |
|------|------|
| `getOne({ id })` | 按主键查询单条 |
| `filter(params)` | 高级过滤查询 |
| `create(data)` | 创建记录 |
| `update({ id, ...fields })` | 更新记录（id 支持数组批量，最多 1000 条） |
| `delete({ id })` | 删除记录（id 支持数组批量，最多 1000 条） |

不要再写：

```javascript
const record = await models[TABLES.orders].findOne({ id });
```

## 系统自动维护字段

以下字段由平台自动维护，代码中不要手动设置：

* `id`
* `create_time`
* `modify_time`
* `create_by`
* `modify_by`

正确做法是只设置业务字段。

## Before / After / Endpoint 规则

### Before

适合：

* 参数校验
* 默认值填充
* 权限过滤

规则：

* 普通接口可直接修改 `params.field`
* `filter` / `aggregate` 接口必须修改 `params.where`
* 追加过滤条件时要保留原条件，通常用 `$and`

```javascript
export default async function beforeFilter(params, context) {
  if (context.userInfo.role !== "admin") {
    params.where = params.where || {};
    const originalWhere = { ...params.where };
    params.where = {
      $and: [originalWhere, { created_by: { $eq: context.userInfo.id } }],
    };
  }
  return params;
}
```

### After

适合：

* 数据脱敏
* 字段补充
* 展示增强

规则：

* 主要操作 `params.tableData`
* 不要破坏既有返回结构

```javascript
export default async function afterFilter(params) {
  params.tableData?.forEach((record) => {
    if (record.phone) {
      record.phone = record.phone.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2");
    }
  });
  return params;
}
```

### ENDPOINT

适合：

* 独立业务流程
* 多表读写
* 事务处理
* 需要前端通过 `client.bff.execute()` 调用的业务接口

返回规则：

* ENDPOINT 返回业务对象本身
* 平台最终会包装成 `{ success, data }`
* 前端 SDK 调用 `client.bff.execute()` 时，拿到的是业务数据，不是 `{ success, data }`

## 公共函数（COMMON）

### 命名建议

公共函数建议统一加 `common` 前缀（如 `commonGetUserInfo`），便于与普通 ENDPOINT 区分，也方便人和 AI 识别。

### 在其他 BFF 中调用公共函数

通过 `context.client.bff.execute` 调用：

```javascript
const userInfo = await context.client.bff.execute({
  scriptName: 'commonGetUserInfo',
  params: { userId: params.userId }
});
```

参数说明：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `scriptName` | string | 是 | 公共函数名称（与 COMMON 脚本的 scriptName 一致） |
| `params` | object | 否 | 传递的参数，默认 `{}` |

### 注意事项

* `scriptName` 必须与公共函数名称精确匹配（大小写敏感）
* 调用必须使用 `await`
* `params` 会被深拷贝，调用方的原始对象不会被修改
* 公共函数不可循环调用（A 调 B，B 又调 A）
* 公共函数抛出的异常会向上传播到调用方，需在调用方做 try-catch
* 修改公共函数的出入参会影响所有引用方；如需改动，建议新建 V2 版本逐步切换

### 组合调用示例

```javascript
export default async function createOrder(params, context) {
  const orderNo = await context.client.bff.execute({
    scriptName: 'commonGenerateOrderNo',
    params: {}
  });

  const result = await context.client.bff.execute({
    scriptName: 'commonCreateOrderWithTransaction',
    params: { ...params, orderNo }
  });

  return result;
}
```

## SQL 调用规则

在 BFF 中使用：

```javascript
const rows = await context.client.sql.execute({
  sqlCode: "customer-active-list",
  params,
});
```

关键差异：

* 前端 SDK：返回 `{ execSuccess, execResult }`
* Backend Function：直接返回数组 `T[]`

不要写成：

```javascript
const result = await context.client.sql.execute({ sqlCode: "xxx" });
const rows = result.execResult;
```

## 事务规则

事务使用方式：

```javascript
await context.client.db.transaction(async (tx) => {
  // 成功自动提交
  // 抛错自动回滚
});
```

必须遵守：

* 外层必须 `await`
* 回调函数必须是 `async`
* 不要在事务中调用外部慢接口
* 异常要向上抛出，不能吞掉

## 性能约束

编写 BFF 前，必须阅读 `data-api-guidelines.md` 中的性能优化部分。

重点避免：

* 循环查询单条
* 循环写入
* 嵌套循环查询

性能要求：

* 单次脚本数据库调用尽量控制在 `50` 次以内
* 可批量查询时，用 `filter + $in`
* 可批量写入时，优先考虑自定义 SQL

## 禁止事项

* 不要使用 `findOne`
* 不要使用 `getList()` 代替 `filter()`
* 不要手动设置系统字段
* 不要保留顶部注释占位符
* 不要把前端 SQL 返回值语义套到 BFF
* 不要忽略权限、脱敏和错误处理
* 不要在事务里做高延迟外部调用

## 自检清单

* [ ] 已确认脚本类型是 Before / After / Endpoint / Common
* [ ] 已执行 `rabetbase dataset detail` 获取数据集信息
* [ ] 字段名、类型、关系已核对
* [ ] 函数名正确（将作为 `scriptName` 参数传入）
* [ ] 顶部注释完整且占位符已替换
* [ ] 数据集映射使用 32 位编码
* [ ] 单条查询统一使用 `getOne`
* [ ] 列表查询使用 `filter`
* [ ] SQL 返回值按 BFF 语义处理
* [ ] 未设置系统自动维护字段
* [ ] 无明显 N+1 或循环写入问题
* [ ] HOOK 返回 `params`，ENDPOINT 返回业务对象

## 相关指南

* `data-api-guidelines.md`
* `sql-creation-workflow.md`
* `bff-creation-workflow.md`
* `conflict-detection.md`
