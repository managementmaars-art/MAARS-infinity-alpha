# SQL 工作流规则

前置知识：`data-api-guidelines.md`

## 核心原则

平台是唯一 source of truth。修改已有 SQL 时，从平台拉取最新内容。

## 工作流

```
确认需求 → [按需]查现有 SQL → 校验字段 → 编写 SQL → 验证 → 保存到平台 → 测试 → 写入本地
```

### 1. 确认需求
写 SQL 前必须明确：查询目标、字段、筛选条件、排序分页、是否 JOIN、新建还是修改。缺失则先问用户。

### 2. 查现有 SQL（按需）
* 新建 → 可跳过
* 修改已有 → 执行 `rabetbase sql list --format json` 找到目标，确认 sqlCode，拉取内容
* 不确定 → 查一下

命中同名或同语义 SQL 时，停下问用户：沿用还是另建。

### 3. 校验字段
执行 `rabetbase dataset detail --code <数据集编码> --format json` 确认表名、字段名、字段类型。禁止凭经验猜。

### 4. 编写 SQL（规范路径）
在项目根 **`.rabetbase/sql/<sqlName>.sql`** 创建或编辑文件（与 `sql pull` 落盘、`sql save --file` 约定一致）。**不要**默认把长期源文件放在 `queries/`、`src/` 等目录；临时文件若在其他路径编写，纳入 Git 前应迁入 `.rabetbase/sql/`。

编写完整 SQL，带 `@lovrabet` 头注释：
```sql
-- @lovrabet.sqlName: <领域>-<用途>
-- @lovrabet.description: <一句话说明>
```

### 5. 验证
执行 `rabetbase sql validate --file <sql文件路径> --format json` 传入 SQL 文件。未通过则修正后重新验证。

### 6. 保存到平台
执行 `rabetbase sql save --file <sql文件路径> --format json`：
* 新建需传 `dbId`（从 `rabetbase dataset detail` 获取）
* SQL 文件中包含完整 SQL 原文及 `@lovrabet` 头注释

### 7. 测试
保存成功后执行 `rabetbase sql exec --sqlcode <sqlCode> --format json` 验证。失败则修正 → validate → save → execute。

### 8. 纳入版本管理
若全流程已在 **`.rabetbase/sql/<sqlName>.sql`** 中编辑，测试通过后只需确认头注释完整并提交 Git。头注释须含 `@lovrabet.sqlName`、`@lovrabet.sqlCode`（从保存响应获取）、`@lovrabet.description`。
若曾在临时路径编写，须将最终内容迁入 `.rabetbase/sql/` 再纳入版本管理。

## 非 SELECT 语句

DELETE / DDL（DROP / ALTER / CREATE / TRUNCATE）属高风险，不走自动保存。
将 SQL 写入本地草稿文件，告知用户手动在平台操作。
草稿路径：`.rabetbase/sql/<sqlName>.draft.sql`

## 冲突处理

返回 `blocked: true` → 将当前 SQL 写入本地草稿文件，告知用户手动处理，不重试。
草稿路径：`.rabetbase/sql/<sqlName>.draft.sql`

## 本地文件

正常流程：保存平台 + 测试通过后写入本地，路径及格式同 Step 8。
例外场景：
* 保存被 blocked 或属于 DELETE/DDL → 写草稿（`.draft.sql`），供人工处理
* 用户主动要求"同步平台最新到本地" → 执行 `rabetbase sql pull`（或 `sql detail` 查看后手工写入）→ 覆盖/生成 `.rabetbase/sql/` 下文件

修改已有 SQL 时，从平台拉取最新内容（`sql pull` 或 `sql list` + `sql detail`）。

## SQL 调用差异

| 场景 | 前端 SDK | BFF (context.client) |
|------|---------|---------------------|
| 返回值 | `{ execSuccess, execResult }` | 直接返回数组 |
| 调用 | `client.sql.execute({ sqlCode, params })` | `context.client.sql.execute({ sqlCode, params })` |
