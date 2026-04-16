# 数据接口访问规范

> **目标**：统一前后端数据接口访问方式，确保性能最优、数据准确
>
> **适用范围**：前端页面开发、Backend Function 编写、SQL 查询编写

---

## 核心原则

| 原则 | 说明 |
|------|------|
| **先获取数据集详情** | 使用 CLI 命令获取字段信息和依赖关系 |
| **分析主外键关系** | 理解表间关联，正确处理下拉框数据 |
| **使用真实接口** | 不使用 mock 数据，直接调用数据集接口 |
| **避免循环访问** | 批量查询替代循环单个查询 |
| **性能优先** | 单次接口调用次数 < 50 次 |

---

## 编写前强制检查清单

在编写任何数据访问代码前，**必须先完成以下检查**：

- [ ] 使用 `rabetbase dataset detail --code <数据集编码> --format json` 获取数据集完整字段与操作信息
- [ ] 核对字段名（区分大小写）、类型、是否必填
- [ ] 分析数据集依赖关系（主外键约束）
- [ ] 识别外键字段，确定下拉框数据来源

**注意**：系统自动维护字段（id、create_time 等）的处理方式，详见 `backend-function.md`。

**CLI 信封、`data.*` 键位、平台 `get-driven-data` 与 CLI 归一化对照**：单一权威见 [`references/rabetbase-dataset-detail.md`](../references/rabetbase-dataset-detail.md)。

---

## 先判定数据访问路线

在决定写 SQL、BFF 还是直接查数据前，先看 `rabetbase dataset detail --code <数据集编码> --format json` 的 `source`：

| `source` | 建议路线 |
|----------|----------|
| `METADATA` | **不要默认走 SQL**；优先 `filter` / `getOne` / 标准数据接口 |
| `CUSTOM` / `DB` | 可继续评估 SQL、BFF 或标准数据接口 |

---

## 可选：`lovrabet` CLI 查数（`data filter` / `data getOne`）

本 skill 的**主路径**始终基于 **`rabetbase`**（`dataset detail`、`sql exec` 等），**不要求**安装其它 CLI。

若开发者本机已单独安装 **Lovrabet 运行时 CLI**（npm 包 **`@lovrabet/lovrabet-cli`**，命令名 **`lovrabet`**），可在终端用 **`lovrabet data filter`**、**`lovrabet data getOne`** 按 **与 `@lovrabet/sdk` 相同的语义** 查询数据集行数据，并直接查看 JSON 结构，便于与前端 / BFF 里的 `filter`、`getOne` 对照调试。

**版本要求：须 `lovrabet` CLI ≥ 2.0**（主版本 2 及以上）。低于 2.0 的旧包**没有**与本文一致的 `data filter` / `data getOne` 能力（或行为不同），请勿按本节操作；请升级：`npm install -g @lovrabet/lovrabet-cli@^2.0.0`（或 `latest`）。自检：`lovrabet --version`。

**注意：**

| 点 | 说明 |
|----|------|
| **非必备** | 团队未必全局安装 `lovrabet`；**不要**在文档或 Agent 流程里把 `lovrabet` 写成前置条件。 |
| **≥ 2.0** | 本节所述 `data` 子命令以 **2.0+** 为准；版本不符时先升级，勿将异常当作 skill 错误。 |
| **未安装时** | 仍用 `rabetbase dataset detail` 拿结构；要看真实数据可用 **`rabetbase sql exec`**（已有对应 `sqlCode`）、或平台控制台；勿假设用户会去装第二个 CLI。 |
| **配置与认证** | `lovrabet` 与 `rabetbase` 的配置项、鉴权方式**可能不完全相同**，需按各自 CLI 文档分别配置；勿照搬一条 `rabetbase` 的 flag 就认为 `lovrabet` 等价。 |
| **详细用法** | 以 `lovrabet data --help`、`lovrabet data filter --help` 为准（参数多为 `--code` + `--params` JSON）。 |

示例（仅作形态参考，需本机已安装且已登录/配置）：

```bash
lovrabet data filter --code <数据集code> --params '{"where":{...},"currentPage":1,"pageSize":10}' --format json
lovrabet data getOne --code <数据集code> --params '{"id":123}' --format json
```

---

## 步骤 1: 获取数据集详情

```bash
rabetbase dataset detail --code orders --format json
```

字段表、归一化规则、`dbtable`、jq 示例：**见 [`references/rabetbase-dataset-detail.md`](../references/rabetbase-dataset-detail.md)**。

做行数据验证时，补一个现实预期：

- **不要默认 `filter()` 返回完整字段**。列表接口常为展示做裁剪，某些字段可能缺失。
- 需要确认“某条记录的完整字段”或依赖关键字段时，优先 `getOne({ id })`。
- 遇到 `USER` 类型字段时，留意同名的 `_label` 扩展对象（如 `creator_id_label`、`assignee_id_label`），很多展示信息已在其中，无需立刻反查 SQL 或额外写 BFF。

### 错误处理

**CLI 命令执行失败时**：

检查以下常见问题：
1. 数据集编码是否正确
2. 是否有权限访问该数据集
3. CLI 是否已正确认证（`rabetbase auth`）

**Backend Function 中的错误处理**：

```javascript
export default async function createOrder(params, context) {
  const customerResult = await context.client.models.customers.filter({
    where: { id: { $eq: params.customer_id } },
    select: ['id', 'customer_name']
  });

  if (!customerResult.tableData || customerResult.tableData.length === 0) {
    throw new Error(`客户 ${params.customer_id} 不存在`);
  }

  // 继续业务逻辑...
}
```

---

## 步骤 2: 分析字段依赖关系

### 主外键关系分析

**从数据集详情中获取依赖关系**，重点关注：

```
订单数据集依赖关系示例：
1. customer_id → customers.id (外键)
   - 创建订单时 customer_id 必须存在
   - 下拉框数据来自 customers 表
   - 需要显示 customer_name，存储 customer_id

2. product_id → products.id (外键)
   - 下拉框数据来自 products 表
   - 需要显示 product_name，存储 product_id

3. status (无外键，`type` 为 SELECT)
   - 枚举字段，直接使用 `fields[].options` 数组
   - 不需要额外接口请求
```

### 下拉框数据来源推理

| 字段类型 | 识别方式 | 数据来源 | 处理方式 |
|---------|---------|---------|---------|
| **外键字段** | `relations[]` 中有对应记录 | 关联的数据集 | 调用关联数据集的 filter 接口 |
| **枚举字段** | `type === "SELECT"` 且 `options` 非空 | `fields[].options` | 直接使用，无需额外请求 |
| **级联选择** | 父字段决定子字段 | 父字段变化时动态加载 | 监听父字段变化，动态加载子选项 |

**前端示例**：

```tsx
// 分析：status 字段 type === "SELECT"，options 已有枚举值
// 直接从字段定义取，不需要接口请求
const statusOptions = field.options.map(o => ({ label: o.label, value: o.value }));

// 分析：customer_id 是外键，关联 customers 表
// 需要获取客户列表作为下拉框数据
const [customers, setCustomers] = useState([]);

useEffect(() => {
  client.models.customers.filter({
    select: ['id', 'customer_name'],
    where: { status: { $eq: 'active' } }
  }).then(result => {
    setCustomers(result.tableData || []);
  });
}, []);

// 下拉框配置
const customerOptions = customers.map(c => ({
  label: c.customer_name,
  value: c.id,
}));
```

**Backend Function 示例**：

```javascript
// 分析：订单表 customer_id 是外键
// 创建订单前需要校验客户是否存在

const customer = await customerDS.getOne({ id: params.customer_id });
if (!customer) {
  throw new Error(`客户 ${params.customer_id} 不存在`);
}
```

---

## 步骤 3: 使用真实接口

### 禁止使用 Mock 数据

```tsx
// ❌ 错误：使用 mock 数据
const CUSTOMER_OPTIONS = [
  { label: '客户A', value: 1 },
  { label: '客户B', value: 2 },
];

// ✅ 正确：使用真实接口
const [customers, setCustomers] = useState([]);
useEffect(() => {
  client.models.customers.filter({
    select: ['id', 'customer_name'],
  }).then(result => {
    setCustomers(result.tableData || []);
  });
}, []);
```

### 标准接口调用方式

**前端**：

```tsx
import { createClient } from '@lovrabet/sdk';

const client = createClient({ appCode: 'your-app-code' });

// 查询列表
const result = await client.models.dataset_XXXXXXXXXX.filter({
  where: { status: { $eq: 'active' } },
  select: ['id', 'name'],
  pageSize: 100,
});

const data = result.tableData || [];
```

**Backend Function**：

```javascript
// 使用 context.client 访问数据集
const models = context.client.models;
const TABLES = {
  customers: 'dataset_XXXXXXXXXX', // 数据集: 客户 | 数据表: customers
};

const result = await models[TABLES.customers].filter({
  where: { status: { $eq: 'active' } },
  select: ['id', 'customer_name'],
});
```

---

## 步骤 4: 性能优化（避免循环访问）

### 场景识别

代码中出现**循环内调用接口**时，必须优化：

```tsx
// ❌ 性能灾难：N 次接口调用
for (const order of orders) {
  const customer = await getCustomer(order.customer_id);
}
```

### 优化方案选择

```
循环访问接口（N 次调用）
    │
    ├─ 关联类型是 1:1 或 N:1？
    │   │
    │   ├─ 是 → 使用 filter 多表关联查询（推荐）
    │   │        一次查询，自动 JOIN
    │   │
    │   └─ 否 → 使用批量查询（$in）
    │        一次查询，手动映射
```

### 方案 1：多表关联查询（推荐）

<span style={{fontSize: '0.9em', color: '#888'}}>v1.2.0+</span>

**适用于**：1:1 或 N:1 关联（订单→客户、员工→部门）

```tsx
// ✅ 一次查询，自动 JOIN
const result = await client.models.orders.filter({
  select: [
    "id", "order_no",
    "customer.name",     // 关联表字段
    "customer.level"     // 关联表字段
  ],
  where: {
    status: { $eq: "pending" },
    "customer.level": { $eq: "VIP" }
  },
});

// result.tableData[0].customer.name ← 直接可用
```

### 方案 2：批量查询

**适用于**：复杂场景或不支持多表关联时

```tsx
// ✅ 一次查询，$in 批量获取
const customerIds = [...new Set(orders.map(o => o.customer_id))];
const customers = await client.models.customers.filter({
  where: { id: { $in: customerIds } },
  select: ['id', 'name']
});
const customerMap = Object.fromEntries(
  customers.tableData?.map(c => [c.id, c.name]) || []
);
orders.forEach(o => o.customerName = customerMap[o.customer_id]);
```

### 性能对比

| 方案 | 调用次数 | 耗时 |
|------|---------|------|
| 循环单条（100 条） | 100 次 | ~10 秒 |
| 多表关联 | 1 次 | ~0.1 秒 |
| 批量查询 | 1 次 | ~0.1 秒 |

---

## 步骤 5: 批量操作优化

### 大量数据写入场景

**场景**：批量复制 100 条订单记录

```javascript
// ❌ 错误：循环创建（100 次接口调用）
for (const order of orders) {
  await orderDS.create(order);
}

// ✅ 正确：使用自定义 SQL（1 次接口调用）
await context.client.sql.execute({
  sqlCode: "batch-copy-orders",
  params: { sourceOrderId: sourceId, targetOrderId: targetId }
});
```

**自定义 SQL 创建流程**：

1. 使用 CLI 命令 `rabetbase sql save --file <sql文件路径> --format json` 创建 SQL
2. 获得返回的 `sqlCode`
3. 在代码中调用 `context.client.sql.execute({ sqlCode, params })`

详见：`sql-creation-workflow.md`

---

## 检查清单

### 前端页面开发

- [ ] **已获取数据集详情**：使用 CLI 命令获取字段和依赖关系
- [ ] **外键字段已识别**：下拉框数据来自关联数据集接口
- [ ] **枚举字段已处理**：直接使用 `fields[].options`，`type === "SELECT"` 的字段无需额外接口
- [ ] **未使用 mock 数据**：所有下拉框数据来自真实接口
- [ ] **无循环访问**：优先使用多表关联查询，或使用批量查询
- [ ] **字段名正确**：使用 `fields[].name`（列名），区分大小写，与数据集定义一致
- [ ] **系统字段已识别**：结合 `data.dbtable` 与 `backend-function.md`，创建/更新时间等按平台约定不传
- [ ] **关联表使用表名**：多表关联时使用 `tableName.fieldName` 格式

### Backend Function 开发

- [ ] **已获取数据集详情**：使用 CLI 命令获取字段和依赖关系
- [ ] **主外键关系已分析**：理解表间关联关系
- [ ] **外键校验已处理**：创建/更新前校验外键有效性
- [ ] **系统字段未设置**：主键自增、系统时间等按平台约定不手工传入，详见 `backend-function.md`
- [ ] **无循环访问**：使用 filter + $in 批量查询
- [ ] **批量操作已优化**：大量数据操作使用自定义 SQL

### SQL 开发

- [ ] **已获取数据集详情**：通过 `data.dbtable.tableName` 确认表名，通过 `data.dbtable.dbId` 确认数据库
- [ ] **必填字段已确认**：INSERT 包含所有业务必填字段（`fields[].required === true` 中需由调用方传入的列）
- [ ] **主外键关系已分析**：JOIN 条件使用 `data.dbtable.pkField` 等
- [ ] **SQL 已验证**：使用 `rabetbase sql validate` 验证
- [ ] **SELECT 已测试**：使用 `rabetbase sql exec` 测试

---

## 相关指南

- **前端页面开发**：`frontend-development.md`
- **SQL 创建工作流**：`sql-creation-workflow.md`
- **Backend Function 规范**：`backend-function.md`
