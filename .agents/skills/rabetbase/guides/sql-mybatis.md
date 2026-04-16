# SQL CLI 命令与 MyBatis 语法指南

> 目标：指导 AI 如何正确使用 CLI 命令来完成 SQL 的查询、验证、保存与测试，并提供平台支持的 MyBatis 动态 SQL 语法参考。
>
> 前置阅读：`sql-creation-workflow.md`（整体流程）、`data-api-guidelines.md`（字段约束）

## 何时使用

当任务满足任一条件时，必须阅读并遵守本指南：

* 需要使用 CLI 命令处理自定义 SQL
* 编写需要动态条件的复杂 SQL（如可选参数、范围过滤）
* SQL 验证报错，需要排查语法或字段问题

## CLI 命令调用规范

在执行 `sql-creation-workflow.md` 规定的流程时，AI 必须严格按以下方式使用 CLI 命令。

### 1. `rabetbase sql list --format json`
* **用途**：创建或修改前，搜索同名或相似语义的 SQL。
* **动作**：若发现相似项，必须与开发者确认是否复用或另起新名，避免冗余创建。

### 2. `rabetbase dataset detail --code xxx --format json`
* **用途**：写 SQL 前获取表结构，**绝对禁止凭空编造表名或字段名**。
* **提取项**：
  * 真实表名：`basic.tableName`
  * 真实字段列表：`fields` 下的 `code`、`type`、`required`
  * 数据库 ID：`basic.database.dbId`（验证与保存时需要）

### 3. `rabetbase sql validate --file xxx --format json`
* **用途**：保存前的强制卡点。
* **参数**：传入 SQL 内容文件和 `dbId`。
* **动作**：如果 `valid: false`，必须根据 `errors` 提示修改 SQL 内容，然后重新执行此命令，直到通过。

### 4. `rabetbase sql save --file xxx --format json`
* **用途**：将验证通过的 SELECT 语句保存到平台。
* **限制**：INSERT / UPDATE / DELETE / DDL 等会引发异常或被拦截，应将 SQL 内容写入本地草稿文件（`.draft.sql`）并告知用户。
* **冲突处理**：如果返回 `blocked: true`，说明有作者冲突，将 SQL 内容写入本地草稿文件，**严禁重试**，直接告知开发者手动操作。

### 5. `rabetbase sql exec --sqlcode xxx --format json`
* **用途**：保存成功后的功能测试。
* **动作**：测试失败（如语法错、数据不符合预期）时，必须在内存中修改 SQL -> 重新 validate -> 重新 save -> 重新 execute，形成闭环。

---

## 📚 MyBatis 动态 SQL 语法参考（核心）

平台支持 MyBatis 语法。在自定义 SQL 中处理动态参数时，必须遵守以下规范。

### 简单参数 vs 动态参数

| 类型 | 语法 | `jdbcType` | 适用场景 |
|---|---|---|---|
| **简单参数** | `#{param}` | ❌ 不加 | 必定传入的固定条件 |
| **动态参数** | `#{param, jdbcType=TYPE}` | ✅ 必须加 | `<if>` 标签内的可选条件 |

### 动态 SQL 示例（推荐）

```sql
SELECT id, name, status_code 
FROM company
<where>
    <if test="statusCode != null and statusCode != ''">
        AND status_code = #{statusCode, jdbcType=VARCHAR}
    </if>
    <if test="name != null and name != ''">
        AND name LIKE CONCAT('%', #{name, jdbcType=VARCHAR}, '%')
    </if>
    <if test="startDate != null">
        AND created_at &gt;= #{startDate, jdbcType=DATE}
    </if>
</where>
ORDER BY id DESC
```

### 常用标签说明

* `<where>`：自动处理内部的 `AND` / `OR` 前缀，当内部没有条件成立时，整个 `WHERE` 关键字也不会出现。
* `<if test="条件">`：用于判空。注意：字符串应同时判断 `!= null` 和 `!= ''`，数字/布尔只需判断 `!= null`。
* `<foreach>`：常用于 `IN` 语句的数组遍历。

### `jdbcType` 对照表

在 `<if>` 标签内使用参数时，必须带上对应的 `jdbcType`：

| 数据类型 | `jdbcType` |
|---|---|
| 字符串 | `VARCHAR` |
| 整数 | `INTEGER` |
| 小数 | `DECIMAL` |
| 日期 | `DATE` |
| 时间戳 | `TIMESTAMP` |

### XML 转义规则

由于 SQL 内容会被解析为 XML，符号需要正确转义：

* **SQL 文本中**：必须转义！
  * 大于号 `>` 写作 `&gt;`
  * 小于号 `<` 写作 `&lt;`
  * 示例：`AND created_at &gt;= #{startDate, jdbcType=DATE}`
* **`<if test="...">` 属性内**：不需要转义！
  * 示例：`<if test="amount > 100">`

## 禁止事项

* ❌ 禁止在未执行 `rabetbase sql validate` 通过前，直接执行 `rabetbase sql save`
* ❌ 禁止在 `<if>` 标签的参数绑定中漏写 `jdbcType`
* ❌ 禁止在简单固定参数（不在标签内）里加 `jdbcType`
* ❌ 禁止把 `<` 或 `>` 直接写在 SQL 正文中（必须用 `&lt;` / `&gt;`）
