# mixdao 专题 API（脚本实现对照）

本文与 `scripts/solo-topics.js` 行为一致；服务端若扩展字段，以实际 HTTP 响应为准。Agent 平时读 `SKILL.md` 即可，**构造 `add` 正文、排查 4xx/5xx 或字段歧义**时再打开本文。

## 安全

- **不要把 API key 写进仓库、skill 文件或提交到 git**。若在聊天/日志中泄露，请在 mixdao 侧**轮换 key** 再使用。

## 环境与 Base URL

| 变量 | 说明 |
|------|------|
| `MIXDAO_API_KEY` | 优先使用 |
| `API_KEY` | 与上一项二选一，脚本会读 |
| `BASE_URL` | 可选，默认 `https://www.mixdao.world`（末尾无 `/`） |
| `TOPIC_ID` | 仅 `articles` **省略第一个参数**时作为专题 id |

## 认证

所有请求：

- `Authorization: Bearer <API_KEY>`
- `Accept: application/json`
- `POST` 正文：`Content-Type: application/json`

## 端点一览

| 方法 | 路径 | 脚本子命令 |
|------|------|------------|
| `GET` | `/api/topics` | `topics` |
| `GET` | `/api/topics/{topicId}/articles` | `articles <TOPIC_ID>` |
| `POST` | `/api/topics/{topicId}/articles` | `add <TOPIC_ID> <file.md \| ->` |

`topicId` 为路径参数，与列表里专题对象的 **`id`** 一致（以 `topics` 返回为准）。展示名是字段 **`label`**，没有 `name` 字段。

## `GET /api/topics` 响应（实测结构）

成功时为 **JSON 数组**，元素大致为：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 专题 id，供 `articles` / `add` 路径使用 |
| `label` | string | 展示名称 |
| `description` | string | 短描述 |
| `keywords` | string[] | 检索/归类用关键词，**单条可能极长** |
| `reportPrompt` | string | 报告生成提示模板，**体积大** |
| `isRecommended` | boolean | 是否推荐 |
| `sortOrder` | number | 排序 |

向用户简报时只摘 **id + label**（可选 `description`），避免把 `keywords`、`reportPrompt` 整段打进对话（可用 `--compact` 自行解析，仍注意体积）。

## `GET /api/topics/{topicId}/articles` 响应（实测结构）

成功时为 **JSON 数组**，单篇文章对象字段示例：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 文章 id（服务端生成） |
| `topicId` | string | 所属专题 |
| `date` | string | 日期，实测形如 `YYYY-MM-DD` |
| `title` | string | 标题 |
| `content` | string | 正文，可为 Markdown |
| `url` | string | 链接 |
| `summary` | string | 摘要 |
| `source` | string | 来源，实测有 `manual` 等 |
| `sortOrder` | number | 排序 |
| `createdAt` | number | 创建时间（毫秒时间戳，服务端生成） |

## 响应与错误（脚本侧）

1. 响应体按 JSON 解析；非 JSON 会报错退出。
2. 若解析后的对象存在 **字符串** 字段 `error`，脚本视为失败并打印 `错误: …` 后退出（**不**依赖 HTTP 状态码是否 2xx，以服务端约定为准）。
3. `!res.ok` 时打印 `HTTP <status>` 及 body 字符串（若有）。

Agent 向用户解释时：401/403 → 检查 key；404 → 专题 id 或路径；5xx → 服务端问题；业务错误 → 看返回 JSON 中的 `error` 或 body。

## `POST` 投稿：`add`（Markdown）

### 命令行传 Markdown 文件或 stdin

- 输入为 **整篇 Markdown**。脚本按下列规则拼 JSON 后 POST（**不提供**手写 JSON / stdin JSON 路径）。
- **`id`**：`SHA256(UTF-8 正文)` 的十六进制字符串的 **前 12 位**（短 hash；长度由脚本常量 `SHORT_HASH_HEX_LEN` 控制）。
- **`title`**：第一个 `# 标题`；否则取**第一行非空**（至多约 500 字）。
- **`content`**：去掉 BOM 后的 Markdown **全文**。
- **`date`**：运行时刻 **本地时区** 的日历日期，格式 **`YYYY-MM-DD`**（非 UTC）。
- **`summary`**：去掉首个 `#` 标题行后对剩余做简易去 Markdown，至多约 280 字；若空则用 `title` 截断。
- **`url`**：`https://article.local/md/<id>`（与短 `id` 一致，占位用）。
- **`source`**：`markdown-cli`。
- **`sortOrder`**：`0`。

服务端仍可能返回自己的 `id` / `createdAt` 等，**以响应为准**。

### 实际 POST 的 JSON 形状（示意）

字段值由正文推导，非手写固定字面值：

```json
{
  "id": "<sha256 前 12 位 hex>",
  "title": "…",
  "content": "…",
  "date": "YYYY-MM-DD",
  "summary": "…",
  "url": "https://article.local/md/<id>",
  "source": "markdown-cli",
  "sortOrder": 0
}
```

### 与线上 `GET articles` 常见字段对照

根据 **已存文章** 反推，服务端对象常见键与脚本的对应关系（**是否必填、校验以服务端为准**）：

| 字段 | `add` 行为 |
|------|------------|
| `title` | 从 Markdown 推导 |
| `url` | 占位 URL（见上） |
| `content` | 全文 MD |
| `date` | 本地 `YYYY-MM-DD` |
| `summary` | 自动摘要 |
| `source` | `markdown-cli` |
| `sortOrder` | `0` |
| `id` | 短 hash（服务端可能覆盖） |

通常由服务端生成、**响应里才有**的字段：`topicId`、`createdAt` 等。

### stdin

`add TOPIC_ID -`：stdin 为 **Markdown**。

## 与 `SKILL.md` 的边界

- **仅支持创建**：脚本只实现 `POST` 添加；无更新、无按 id 删除。
- **不要手写 curl**：统一用脚本，避免漏头、路径错误或 key 泄露到 shell history。
