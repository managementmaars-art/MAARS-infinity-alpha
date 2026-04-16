# AI 故障诊断手册 (Troubleshooting)

> 目标：当执行代码报错，或用户向 AI 抛出"报错日志 / 没数据 / 查不到"时，约束 AI 的第一排查反应，避免顺着错误方向盲目改代码。
> 
> 前置阅读：`data-api-guidelines.md`

## 何时使用

当遇到以下情况时，AI 必须进入本指南定义的诊断模式：
* 用户说"查询没有结果"、"空数组"
* 控制台报错"参数格式不正确"、"字段不存在"、"表不存在"
* 用户说"BFF 返回结构不对"、"SQL 报错"
* CLI 命令执行失败，提示"Dataset not found"

---

## 诊断肌肉记忆（强制）

### 1. 听到"查不到数据"、"空数组"
**AI 的第一反应**：检查是否漏写了操作符。

* ❌ 错误排查方向：怀疑数据库没连上、怀疑数据集配错
* ✅ **强制动作**：检查 `where` 对象里是否直接写了值（如 `status: "active"`）。必须补上操作符（如 `status: { $eq: "active" }`）。

### 2. 听到"参数格式不正确"
**AI 的第一反应**：检查分页、排序、字段选择的参数名是否写成了老旧格式。

* ❌ 错误排查方向：怀疑后端 API 坏了
* ✅ **强制动作**：
  * 检查是否误用了 `fields`，必须改为 `select`
  * 检查是否误用了 `sort`，必须改为 `orderBy`
  * 检查是否误用了 `page` / `limit`，必须改为 `currentPage` / `pageSize`

### 3. 听到"SQL 报错：表不存在/字段不存在"
**AI 的第一反应**：立刻执行 `rabetbase dataset detail --code xxx --format json` 核对 Schema。

* ❌ 错误排查方向：按自己的猜测随便换一个字段名重试
* ✅ **强制动作**：
  1. 执行 `rabetbase dataset detail --code xxx --format json` 获取真实数据集信息
  2. 提取 `basic.tableName` 作为表名
  3. 逐一核查报错字段是否存在于 `fields` 列表中，注意大小写
  4. 确认无误后再重新生成 SQL 并通过 `rabetbase sql validate --file xxx --format json` 验证

### 4. 听到"BFF 查不到数据 / 字段是 undefined"
**AI 的第一反应**：检查 BFF 中的 API 调用方式和 SQL 结果提取。

* ❌ 错误排查方向：给 BFF 增加前端 SDK 包装结构
* ✅ **强制动作**：
  * 检查单条查询是否误用了 `findOne`，必须改为 `getOne`
  * 检查 SQL 执行是否用了 `result.execResult`，在 BFF 中，`context.client.sql.execute` **直接返回数组**，没有 `execResult` 这一层

### 5. 听到"CLI 报错 / Dataset not found"
**AI 的第一反应**：检查基础连通性，指导用户确认环境。

* ❌ 错误排查方向：建议用户重装各种库
* ✅ **强制动作**：
  * 建议用户检查 `.lovrabetrc`（或其他配置）中的 `appcode` 是否正确
  * 建议用户在终端执行 `rabetbase auth` 检查是否未登录或 Cookie 过期
  * 帮用户执行 `rabetbase dataset list --format json` 确认该环境到底有哪些可用数据集

---

## 核心原则

* **不要猜**：只要涉及"不存在"、"不匹配"，第一步永远是通过 CLI 命令（如 `rabetbase dataset detail`）拉取最新真实数据。
* **不要盲试**：在没有分析出具体根因前，不要试图通过微调参数名盲目重试。
* **分清端环境**：报错若是发生在前/后端交互边界，第一时间弄清是前端 SDK 的事，还是 BFF 脚本里的事，两者的返回值和对象结构不同。
