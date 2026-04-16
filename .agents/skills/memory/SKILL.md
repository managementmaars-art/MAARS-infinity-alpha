---
name: memory
description: 从 mixlab 检索记忆（按 tag 表达式、生成关键词/tagExpr）或向 mixlab 记录/提交记忆（整理 source/category/content/tags 并 POST）。需 MEMORY_API_KEY、MEMORY_API_BASE_URL。触发：从 mixlab 查记忆、mixlab 检索记忆、记到 mixlab、向 mixlab 提交记忆、memory、mixlab 记忆。
---

# Memory（记忆）

从 **mixlab** 检索记忆（类似 grep，按 tag 查）或向 **mixlab** 记录/提交记忆（整理字段后 POST）。所有读写均针对 mixlab Memory API，Base URL 与鉴权从环境变量读取。

## 脚本

| 脚本 | 作用 |
|------|------|
| `scripts/query.js` | 按 tagExpr 检索：入参为 tag 表达式与可选 `--limit`，输出 JSON。 |
| `scripts/submit.js` | 提交一条记忆：`--source/--category/--content/--tags`，或 `--stdin` 读一行 JSON。 |

## 环境变量

| 变量 | 说明 |
|------|------|
| **MEMORY_API_KEY** | 必填。Bearer token（如 mix_xxx）。 |
| **MEMORY_API_BASE_URL** | 必填。如 `https://www.mixlab.top`。 |

## 从 mixlab 检索记忆（GET）

根据用户意图生成可能的**关键词/tag**，再组合成 **tagExpr** 调用 mixlab API。

### tagExpr 规则（类 SQL）

- 单 tag：`tagExpr=work`
- 多 tag 且：`tagExpr=work+AND+important` 或 `work%20AND%20important`
- 或 + 且：`tagExpr=(work+OR+personal)+AND+important`
- URL 中空格用 `%20` 或 `+` 编码

### 检索流程

1. **理解意图**：从用户问题里提取「要查什么」——主题、项目名、类型（工作/生活/笔记等）。
2. **生成候选 tag**：列出 2～5 个可能用到的 tag（如：`work`、`important`、`会议`、`项目A`），优先用用户原词或近义。
3. **构建 tagExpr**：  
   - 只用一个 tag 时：`tagExpr=<tag>`  
   - 要同时满足多 tag：`tagExpr=tag1+AND+tag2`  
   - 有「或」与「且」：用括号，如 `(tag1+OR+tag2)+AND+important`
4. **请求**：`GET {MEMORY_API_BASE_URL}/api/agent/v1/memories?tagExpr=<编码后的表达式>&limit=10`，Header：`Authorization: Bearer {MEMORY_API_KEY}`，`Content-Type: application/json`。
5. **结果**：把返回的记忆列表整理成可读摘要（如标题/摘要 + 来源/时间若有），便于用户快速扫一眼。

### 检索示例

- 用户：「查一下和工作且重要的」→ tag 如 `work`, `important` → `tagExpr=work+AND+important`
- 用户：「找跟项目X或会议有关的」→ tag 如 `项目X`, `会议` → `tagExpr=(项目X+OR+会议)`

## 向 mixlab 提交/记录记忆（POST）

把用户口述或文本**整理成规范字段**，再向 mixlab POST 记录，避免缺字段或格式混乱。

### 请求体字段

| 字段 | 说明 | 整理建议 |
|------|------|----------|
| **source** | 来源（谁/哪来的） | 简短标识：如「用户口述」「Slack」「邮件」；可默认「Agent」 |
| **category** | 分类 | 固定若干类更利检索，如：笔记、待办、会议、想法、摘抄、工作、生活 |
| **content** | 正文 | 用户原意压缩成一段清晰叙述，可保留关键人名/时间/链接 |
| **tags** | 标签数组 | 2～6 个：主题词、项目名、类型等，便于后续用 tagExpr 检索 |

### 提交流程

1. **抓要点**：从用户输入里提取「谁/什么事/何时/何地/为什么/结果」等，去掉口水话。
2. **定 category**：在「笔记、待办、会议、想法、摘抄、工作、生活」等中选最贴的一个；必要时新增一致命名。
3. **写 content**：一段话概括，约 50～200 字，保留关键信息（人名、日期、链接、结论）。
4. **打 tags**：从内容里抽 2～6 个 tag，兼顾「主题」和「类型」，如 `["work","项目A","会议"]`。
5. **填 source**：若用户未说明来源，用「用户口述」或「Agent」。
6. **请求**：`POST {MEMORY_API_BASE_URL}/api/agent/v1/memories`，Header：`Authorization: Bearer {MEMORY_API_KEY}`，`Content-Type: application/json`，Body：`{"source":"...","category":"...","content":"...","tags":["..."]}`。

### 提交示例

用户：「刚才会上说下周三前把需求文档给产品，记得提醒我。」

整理后：

```json
{
  "source": "用户口述",
  "category": "待办",
  "content": "下周三前将需求文档交给产品；来源：会议。",
  "tags": ["工作", "会议", "待办", "需求文档"]
}
```

## 调用示例（curl）

**检索（单 tag）：**

```bash
curl -X GET "${MEMORY_API_BASE_URL}/api/agent/v1/memories?tagExpr=work&limit=10" \
  -H "Authorization: Bearer ${MEMORY_API_KEY}" \
  -H "Content-Type: application/json"
```

**检索（多 tag AND）：**

```bash
curl -X GET "${MEMORY_API_BASE_URL}/api/agent/v1/memories?tagExpr=work%20AND%20important&limit=10" \
  -H "Authorization: Bearer ${MEMORY_API_KEY}" \
  -H "Content-Type: application/json"
```

**提交：**

```bash
curl -X POST "${MEMORY_API_BASE_URL}/api/agent/v1/memories" \
  -H "Authorization: Bearer ${MEMORY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"source":"用户口述","category":"笔记","content":"内容摘要","tags":["tag1","tag2"]}'
```

## 小结

- **从 mixlab 检索**：意图 → 候选 tag → 构建 tagExpr（AND/OR/括号）→ GET mixlab memories。
- **向 mixlab 记录**：口述/文本 → 整理 source、category、content、tags → POST 到 mixlab。
- 所有请求均针对 mixlab，使用环境变量 `MEMORY_API_KEY` 与 `MEMORY_API_BASE_URL`，不在技能中写死密钥。
