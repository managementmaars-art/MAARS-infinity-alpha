# 冲突检测与保存规则

**文档版本**: v3.1
**适用于**: SQL 和 BFF 资源保存

> **与 SKILL.md 的关系**：[SKILL.md](../SKILL.md)「冲突处理」只保留硬性规则；**三分支表、响应 JSON 样例、沟通语气与 AI 职责** 以本文为准。

---

## 保存规则（三分支）

`rabetbase sql save` 和 `rabetbase bff save` 均通过服务端执行保存，规则如下：

| 场景 | 行为 | AI 提示 |
|------|------|---------|
| 无同名资源 | 直接创建 | 告知创建成功 |
| 有同名资源，上次提交是本人 | 直接更新 | 告知更新成功 |
| 有同名资源，上次提交非本人 | **阻断，返回 `blocked: true`** | 告知用户手动操作 |

---

## 未保存成功时的沟通义务（强制）

只要 CLI 命令返回结果表明**未在平台完成保存**（例如 `success: false`、`blocked: true`、`action` 为 `blocked`、业务错误、校验未通过等），AI **必须**向用户明确说明，不得含糊带过：

* **必须说清楚**：本次**没有**保存到 Lovrabet 平台（或仅保存到本地草稿，若你们有本地落盘约定），并引用返回中的 `message` 或关键原因。
* **禁止**：用「好了」「已处理」「帮你弄好了」等表述，让用户误以为已保存到平台。
* **区分状态**：若同时存在「本地草稿已更新」与「平台未保存」，需分开写清，避免混为一谈。

---

## blocked 场景处理

当 CLI 命令返回 `blocked: true` 时，表示同名资源上次由其他人提交，AI 禁止自行绕过，必须告知用户：

```
该 SQL/BFF 上次由其他人提交。
如需更新，请前往 Lovrabet 平台手动操作，或联系上次提交人。
```

**禁止的行为**：
* 重试保存
* 尝试用其他参数绕过
* 替用户做决定

---

## 响应结构

### 成功（创建/更新）

```json
{ "success": true, "action": "created" | "updated", "data": { "id": 1234, "sqlName": "..." } }
```

### 阻断（非本人资源）

```json
{
  "success": false,
  "action": "blocked",
  "blocked": true,
  "message": "SQL「xxx」上次由其他人提交，请手动操作"
}
```

### 非 SELECT SQL（CLI 层拦截）

```json
{
  "success": false,
  "action": "blocked",
  "message": "SQL \"xxx\" save blocked: Detected INSERT statement ..."
}
```

---

## AI 的职责

**根据返回结果调整回复**：

| 结果 | 语气 | 行动 |
|------|------|------|
| `action: created` | 简洁直接 | 告知创建成功，给出 sqlCode |
| `action: updated` | 友好说明 | 告知更新成功 |
| `blocked: true` | 清楚说明原因 | **明确告知未保存到平台**，展示 message，引导用户手动操作，不重试 |
| `success: false` 或其他错误（未保存） | 清楚、不粉饰 | **明确告知未保存到平台**，说明原因与下一步（改内容、重试条件、或走平台/人工），不假装成功 |
| 非 SELECT | 中性解释 | 说明无法自动保存，建议保存到本地文件 |

---

## 相关文档

* **SQL 工作流**: `sql-creation-workflow.md`
* **BFF 工作流**: `bff-creation-workflow.md`
* **最佳实践**: `best-practices.md`
