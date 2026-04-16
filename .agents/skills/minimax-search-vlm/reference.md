# MiniMax 搜索与图像理解 - 参考

## 环境变量

| 变量 | 说明 |
|------|------|
| **MINIMAX_CP_API_KEY** | MiniMax Coding Plan API Key（一般为 `sk-cp-` 开头），从 [Coding Plan 订阅页](https://platform.minimaxi.com) 获取。 |
| **MINIMAX_CP_BASE_URL** | 可选。API Base URL，**未设置时默认为国内** `https://api.minimaxi.com`；国际请设为 `https://api.minimax.io`。 |

使用前：
```bash
export MINIMAX_CP_API_KEY="你的MiniMax_API_Key"
# 可选，国际环境：
# export MINIMAX_CP_BASE_URL="https://api.minimax.io"
```

**注意**：切勿在终端输出、日志或回复中打印上述环境变量的值。

## 通用 Headers

- `Authorization: Bearer $MINIMAX_CP_API_KEY`
- `Content-Type: application/json`
- `MM-API-Source: Minimax-MCP`

---

## 搜索（web_search）- 完整 curl

```bash
BASE_URL="${MINIMAX_CP_BASE_URL:-https://api.minimaxi.com}"
curl -X POST "$BASE_URL/v1/coding_plan/search" \
  -H "Authorization: Bearer $MINIMAX_CP_API_KEY" \
  -H "Content-Type: application/json" \
  -H "MM-API-Source: Minimax-MCP" \
  -d '{"q": "你的搜索关键词"}'
```

带变量、避免转义时用单引号包 JSON：
```bash
BASE_URL="${MINIMAX_CP_BASE_URL:-https://api.minimaxi.com}"
KEYWORD="Python asyncio 教程"
curl -X POST "$BASE_URL/v1/coding_plan/search" \
  -H "Authorization: Bearer $MINIMAX_CP_API_KEY" \
  -H "Content-Type: application/json" \
  -H "MM-API-Source: Minimax-MCP" \
  -d "{\"q\": \"$KEYWORD\"}"
```

---

## 图像理解（understand_image）- 完整 curl

### 图片为 URL

```bash
BASE_URL="${MINIMAX_CP_BASE_URL:-https://api.minimaxi.com}"
curl -X POST "$BASE_URL/v1/coding_plan/vlm" \
  -H "Authorization: Bearer $MINIMAX_CP_API_KEY" \
  -H "Content-Type: application/json" \
  -H "MM-API-Source: Minimax-MCP" \
  -d '{
    "prompt": "描述这张图片的内容",
    "image_url": "https://example.com/your-image.jpg"
  }'
```

### 图片为本地文件（Base64）

先转 Base64（示例文件 `image.jpg`）：
```bash
BASE_URL="${MINIMAX_CP_BASE_URL:-https://api.minimaxi.com}"
BASE64=$(base64 -i image.jpg | tr -d '\n')
curl -X POST "$BASE_URL/v1/coding_plan/vlm" \
  -H "Authorization: Bearer $MINIMAX_CP_API_KEY" \
  -H "Content-Type: application/json" \
  -H "MM-API-Source: Minimax-MCP" \
  --data-raw "{\"prompt\": \"描述这张图片\", \"image_url\": \"data:image/jpeg;base64,$BASE64\"}"
```

其他图片类型对应修改 MIME：如 PNG 为 `data:image/png;base64,$BASE64`。
