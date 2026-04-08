---
name: doubao-api
description: ByteDance Doubao (Volcano Engine) — Doubao Pro, MoE models, Chinese-first enterprise LLM, video/image generation for MAARS Chinese market agents
---

# Doubao (ByteDance/Volcano Engine) API — MAARS Reference

## Models
```python
DOUBAO_MODELS = {
    "doubao-1.5-pro-256k": {
        "context": "256K tokens",
        "strengths": "ByteDance's best, long context, strong reasoning",
        "pricing": "¥0.003-0.009/1K tokens (cheap)",
        "best_for": "Long Chinese documents, enterprise tasks",
    },
    "doubao-1.5-pro-32k": {
        "context": "32K tokens",
        "strengths": "Fast, strong performance",
        "best_for": "Standard Chinese content tasks",
    },
    "doubao-1.5-lite-32k": {
        "context": "32K tokens",
        "strengths": "Very cheap, fast",
        "pricing": "¥0.0003/1K tokens (cheapest tier)",
        "best_for": "Ultra-high volume classification",
    },
    "doubao-pro-4k": {
        "context": "4K",
        "strengths": "Lowest cost per simple task",
        "best_for": "Short content generation, simple Q&A",
    },
    "doubao-embedding-large": {
        "type": "Embedding model",
        "dims": 4096,
        "best_for": "Chinese text embeddings for RAG",
    },
}
```

## API Integration (Volcano Engine / ARK)
```python
from openai import OpenAI

# ByteDance uses Volcano Engine (ARK) infrastructure
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=DOUBAO_API_KEY,
)

def call_doubao(prompt: str, model_endpoint: str = "doubao-1.5-pro-32k") -> str:
    """
    Note: Doubao requires creating endpoint IDs in Volcano Engine console
    model_endpoint is the endpoint ID you create (ep-xxxxx-xxxx)
    """
    response = client.chat.completions.create(
        model=model_endpoint,  # Your configured endpoint ID
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Streaming
def stream_doubao(messages: list, endpoint_id: str):
    response = client.chat.completions.create(
        model=endpoint_id,
        messages=messages,
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Embeddings
def get_doubao_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="ep-your-embedding-endpoint",
        input=text,
    )
    return response.data[0].embedding
```

## Doubao Bot API (Agent Framework)
```python
import requests

def chat_with_doubao_bot(bot_id: str, user_message: str, 
                          conversation_id: str = None) -> dict:
    """Doubao Bot API — pre-configured AI assistants"""
    headers = {
        "Authorization": f"Bearer {DOUBAO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "bot_id": bot_id,
        "user_id": "user_001",
        "stream": False,
        "additional_messages": [{
            "role": "user",
            "content": user_message,
            "content_type": "text",
        }],
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    resp = requests.post(
        "https://api.coze.cn/v3/chat",
        headers=headers,
        json=payload,
    )
    return resp.json()
```

## Image Generation (Doubao / FLUX via ByteDance)
```python
def generate_doubao_image(prompt: str, model: str = "doubao-seedream-3-0") -> str:
    """Bytedance image generation via VolcEngine"""
    resp = requests.post(
        "https://visual.volcengineapi.com/?Action=CVProcess&Version=2022-08-31",
        headers={
            "Authorization": f"HMAC-SHA256 ...",  # VolcEngine signature
            "Content-Type": "application/json",
        },
        json={
            "req_key": "img2img_sr",
            "prompt": prompt,
            "model_version": "general_v1.4",
        }
    )
    return resp.json()["data"]["binary_data_base64"]
```

## When to Use Doubao
- **Chinese market**: ByteDance trained on Chinese web — superior Chinese understanding
- **Ultra-low cost**: Doubao Lite at ¥0.0003/1K (~$0.00004/1K) — cheapest available
- **256K context**: Competitive long-context at fraction of cost
- **ByteDance ecosystem**: Integration with TikTok/Lark/Feishu workflows
- **Chinese compliance**: Deployed in China, ICP licensed

## Coze Platform (ByteDance No-Code Agents)
```python
COZE_PLATFORM = {
    "url": "https://www.coze.com (global) / https://www.coze.cn (China)",
    "features": [
        "No-code bot builder with Doubao models",
        "Plugin marketplace (100+ tools)",
        "Knowledge base upload (RAG)",
        "Workflow automation",
        "Multi-platform deployment (Discord, Telegram, WeChat)",
    ],
    "api": "Coze API for programmatic bot creation",
    "use_case": "Quick agent prototyping for Chinese market",
}
```
