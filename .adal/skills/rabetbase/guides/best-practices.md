# Lovrabet 开发质量规范与最佳实践

> 目标：约束 AI 在编写 SQL 和 BFF 时的安全边界、命名风格和防御性编程习惯，避免生成高风险或难以维护的代码。
> 
> 适用场景：编写或审查 SQL 和 BFF 脚本时。

## 需求落地标准工作流

当遇到一个新业务需求时，AI **必须**按以下漏斗模型进行思考与技术选型，严禁一上来就直接写页面或堆砌复杂的自定义 SQL/BFF：

### Step 1：模型与关系推演
- **强制动作**：使用 CLI 命令（`rabetbase dataset list --format json`、`rabetbase dataset list --name "xxx" --format json`、`rabetbase dataset detail --code <数据集编码> --format json`）找出所有相关的业务模型。
- **list 与 detail**：`dataset list` 只返回精简列表（便于扫目录）；**字段、操作、关联、库表摘要**等一律以 `dataset detail` 为准——该命令默认即为完整结构化 JSON，**无需** `--verbose`。
- **分析深度**：必须分析数据集里的字段含义、系统字段、字段格式、数据规范以及多表之间的关联关系（主外键）。
- **目的**：绝不凭空捏造结构，确保后续的所有代码设计都基于平台真实的 Schema。

### Step 2：接口选型（唯一权威见 SKILL.md）

技术与实现方式优先级 **以 [SKILL.md](../SKILL.md) 的「接口选型优先级」「Agent 快速执行顺序」为准**；勿在此重复整段漏斗。

本文件仅补充执行习惯：

- **SQL**：写前先 `sql list` 查复用；统计类 SQL 主动对齐历史口径，**不一致时告知开发者**。源文件落在 **`.rabetbase/sql/`**（与 `sql save` / `sql pull` 约定一致）。
- **BFF**：写前先 `bff list` 防重复；若逻辑可复用，**建议**抽公共函数或 service 层。脚本**仅**在 **`.rabetbase/bff/<appCode>/...`** 下维护（见 `bff new`）。

### Step 3：前端页面呈现
- 只有在后端的模型和接口选型彻底理清、确认可用之后，**最后一步**才是编写前端 React 页面。
- 确保将规划好的接口数据合理、高效地绑定到页面组件上。

## 命名规范

AI 必须使用有业务语义的规范命名，严禁使用诸如 `test`、`temp`、`query1` 等无意义名称。

### SQL 查询命名
**推荐格式**: `[模块]-[功能]-[类型]`（小写，连字符分隔）

```markdown
✅ 好的命名：
- customer-active-list      # 客户-活跃列表
- order-payment-summary     # 订单-支付汇总
- product-inventory-query   # 产品-库存查询

❌ 禁止的命名：
- query1, query2            # 无意义的序号
- test, temp                # 临时性名称
- abc, xyz                  # 无含义缩写
- 数据查询                   # 不要使用中文作为 code/name 标识
```

### BFF 脚本命名
**推荐格式**: `[动词]-[模块]-[功能]`（小写或驼峰视环境而定，通常连字符风格为佳）

```markdown
✅ 好的命名：
- get-customer-list
- update-order-status
- validate-user-permission

❌ 禁止的命名：
- api1, handler2
- do-something
- test-api
```

## 安全与高危操作边界

当用户要求执行高危操作时，AI **必须主动拦截并要求二次确认**，并在生成代码时增加安全防护。

### SQL 高危操作识别

🔴 **高危特征**：
* 包含 `DELETE`、`TRUNCATE`、`DROP`
* 修改核心业务表（如订单、支付、库存）
* **无 `LIMIT` 或无 `WHERE` 限制的 `UPDATE`**

✅ **防御动作**：
* 如果用户给出了不带 `LIMIT` 或全局匹配的 `UPDATE`，AI 必须主动补充约束条件或提示风险。
* 高危 DDL/DML 不应通过 CLI 自动保存到平台，必须建议用户保存在本地 `.rabetbase/sql/` 进行 review。

### BFF 高危操作识别

🔴 **高危特征**：
* 参数未加任何验证直接传入 `delete` 或 `update` 方法
* 未做权限校验直接暴露数据

✅ **防御动作**：
AI 编写 BFF 代码时，必须养成防御性编程习惯，默认加上参数校验和错误捕获：

```javascript
// ❌ 高危：无验证，直接透传
export default async function(params: any) {
  return await client.models.customer.delete({ id: params.id });
}

// ✅ 安全：带验证和异常处理
export default async function(params: any, context: any) {
  if (!params.id) {
    return { success: false, error: '无效的 ID' };
  }
  
  // 必须捕获异常，不要让内部堆栈直接抛给前端
  try {
    return await context.client.models.customer.delete({ id: params.id });
  } catch (err) {
    return { success: false, error: '删除失败' };
  }
}
```

## 描述与版本标记

在通过 CLI 命令保存资源（如 SQL、BFF）时，应善用 `description` 字段。AI 应在描述中主动加入语义化的标签和版本说明。

**可用标记**：
* `#生产使用` - 生产环境关键资源
* `#测试中` - 仍在联调阶段
* `#待废弃` - 计划移除的旧资源

**示例**：
```markdown
查询活跃客户列表 #生产使用 

用途：客户管理主页面展示
变更记录：
- 2024-03-20: 增加状态筛选
```

## 冲突处理底线

硬性规则见 [SKILL.md](../SKILL.md)「冲突处理」；分支表、响应结构与沟通要求见 [`conflict-detection.md`](conflict-detection.md)。**禁止**捏造 `forceUpdate`、代用户强制覆盖；`blocked` 时引导平台操作或另存为新名称。
