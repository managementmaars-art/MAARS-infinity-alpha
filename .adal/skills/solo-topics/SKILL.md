---
name: solo-topics
description: mixdao 专题 Topics：列专题、看文章、投稿。用本 skill 内脚本，勿手写 curl。触发：solo-topics、专题、topic articles、往专题加文章、mixdao 专题 API、列出 mixdao 专题、查看专题文章。
---

# Solo Topics

- **脚本**：与本 `SKILL.md` 同目录下的 `scripts/solo-topics.js`（Node 18+，`fetch`，无额外依赖）
- **环境**：`MIXDAO_API_KEY`（必填；脚本亦接受 `API_KEY`）；`BASE_URL` 可选；`articles` 可省略参数时用 `TOPIC_ID`
- **命令**（在 skill 根 `cd` 后，或 `node` 指向脚本绝对路径）：
  - `node scripts/solo-topics.js topics`
  - `node scripts/solo-topics.js articles <TOPIC_ID>`
  - `node scripts/solo-topics.js add <TOPIC_ID> <文件.md|->`（stdin 为整篇 Markdown；路径相对**当前工作目录**）
- **省 token**：可加 `--compact`（单行 JSON 输出）
- **`add`（Markdown）**：脚本根据正文自动生成 `id`（SHA-256 的**短 hex**，默认前 12 位）、`title`（首行 `#` 或第一行非空）、`content`（全文）、`date`（**本地时区** `YYYY-MM-DD`）、`summary`、`url`、`source`、`sortOrder`。细节见 `references/api-details.md`。
- **`topics` 输出**：每条含 `label`（展示名，**不是** `name`）、`description`、`keywords`（常很长）、`reportPrompt` 等；向用户呈现时只摘 **id + label**（可加一句 description），勿默认整段贴 `keywords` / `reportPrompt`。

## 详细参考

端点、认证、错误处理、`add` 请求体与示例见 `references/api-details.md`（按需读取；该目录便于后续扩展长文档而不撑满主上下文）。

## Agent 约定

- **读**：解析脚本输出，用列表/摘要呈现给用户，勿默认整段粘贴 raw JSON（用户要求除外）。`topics`：**id + `label`**（必要时一行 `description`）；`articles`：**`title`、`url`、`date`**（需要时再带 `summary` / `source`）；列表空要说明。
- **写**：仅用户明确要求时投稿；`add` 仅接受 **Markdown**（标题/日期等由脚本从正文推导并拼 JSON）。事前确认专题 id；成功回报返回 id/对象；失败原样说明、**不重试**。
- **错**：非零退出 / stderr；用自然语言解释（如 401 → 检查 `MIXDAO_API_KEY`）。
- **API**：仅支持 POST 创建文章，不能按 id 更新或删除。
