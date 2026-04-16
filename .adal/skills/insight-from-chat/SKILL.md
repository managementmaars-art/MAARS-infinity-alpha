---
name: insight-from-chat
description: 从聊天或用户反馈中挖掘洞察：由 Agent 传入上下文，由模型自行判断反馈类别，并产出情绪倾向、需求与痛点、业务/产品机会的结构化摘要。触发示例：「从聊天挖洞察」「用户反馈分析」「痛点挖掘」「需求洞察」「insight from chat」。
---

# 从聊天挖掘洞察（Insight from Chat）

## 何时使用

用户希望从**当前对话、历史聊天或一段用户反馈**中提炼洞察（用户需求、痛点、业务机会）时使用本 skill。由 Agent 自行将相关上下文整理后传入 LLM，不依赖固定输入格式或脚本。

## 执行方式

- **输入**：Agent 从对话中获取并传递上下文（例如用户粘贴的聊天记录、反馈汇总，或当前会话中已讨论的内容）。
- **执行**：Agent 按下方「发给 LLM 的 Prompt」组装内容并调用 LLM，不使用变量占位符；**挖掘的类别由模型根据上下文自行判断**（如功能请求、体验抱怨、竞品对比、定价敏感等）。
- **输出**：要求模型仅返回一个合法 JSON（见下方输出格式）。

## 发给 LLM 的 Prompt

将以下内容作为 **user message**（或 system + user 中 user 部分），把 Agent 整理好的**聊天/反馈原文或摘要**放在「Background Context」处，无需预先填类别或代表评论；模型需先自行从上下文中归纳类别与典型表述，再对每类做深度分析。

```text
Background Context:
[此处由 Agent 填入当前对话、用户提供的聊天记录或反馈内容]

Task: Conduct a deep-dive analysis of the user feedback/chat above.
1. Identify and name the main categories or themes by yourself (e.g. feature requests, experience complaints, competitor comparison, pricing sensitivity). Do not use variable placeholders; infer categories from the context.
2. For each category:
   - Identify the core emotional tendency.
   - Extract underlying user needs or pain points.
   - Suggest high-level business opportunities or product improvements.
3. Return a structured insight summary **in JSON only** (no markdown code fence, no other text). Use the schema below.

If the context is in Chinese, use 简体中文 for string values in the JSON; otherwise use the same language as the context.
```

## 输出格式（JSON）

要求模型**仅输出一个合法 JSON**，不要包裹在 markdown 代码块或其它说明中。结构如下：

```json
{
  "categories": [
    {
      "name": "类别名",
      "emotionalTendency": "核心情绪倾向（一句话）",
      "needsOrPainPoints": ["需求或痛点1", "需求或痛点2"],
      "opportunities": ["业务/产品机会1", "业务/产品机会2"]
    }
  ],
  "summary": "2～3 句整体洞察摘要（可选）"
}
```

| 字段 | 说明 |
| --- | --- |
| **categories** | 数组，每项为模型归纳出的一个反馈类别 |
| **categories[].name** | 类别名 |
| **categories[].emotionalTendency** | 该类核心情绪倾向，一句话 |
| **categories[].needsOrPainPoints** | 字符串数组，用户需求或痛点 |
| **categories[].opportunities** | 字符串数组，业务或产品改进机会 |
| **summary** | 可选字符串，整体洞察摘要 |
