---
name: qwen-api
description: Qwen / Alibaba Cloud API — Qwen Max, Qwen 3 235B, Qwen-VL, Qwen-Audio — used in MAARS for Asian market agents, multilingual tasks, and long-context processing
---

# Qwen API (Alibaba/DashScope) — MAARS Reference

## Models
| Model | Context | Strength |
|-------|---------|----------|
| `qwen-max` | 32K | Flagship, best quality |
| `qwen-plus` | 131K | Balanced quality/speed |
| `qwen-turbo` | 1M | Ultra-long context, fast |
| `qwen3-235b-a22b` | 32K | Open-source flagship |
| `qwen3-30b-a3b` | 32K | Efficient MoE |
| `qwen-vl-max` | 32K | Vision + language |
| `qwen-audio-turbo` | — | Audio understanding |
| `text-embedding-v3` | — | Multilingual embeddings |

## Client (OpenAI-compatible)
```python
from openai import AsyncOpenAI

qwen_client = AsyncOpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=QWEN_API_KEY,
)

response = await qwen_client.chat.completions.create(
    model="qwen-max",
    messages=messages,
    stream=True,
    max_tokens=8192,
)
```

## Thinking Mode (Qwen3)
```python
response = await qwen_client.chat.completions.create(
    model="qwen3-235b-a22b",
    messages=messages,
    extra_body={"enable_thinking": True},  # enables <think> blocks
)
thinking = response.choices[0].message.reasoning_content
answer = response.choices[0].message.content
```

## MAARS Use Cases
- Asian-language content (Chinese, Japanese, Korean)
- Ultra-long context document processing (1M tokens with qwen-turbo)
- Alibaba ecosystem integrations
- Cost-efficient multilingual workloads

## MAARS Config
```python
{
    "model_provider": "qwen",
    "model_name": "qwen-max",
    "api_key_env": "QWEN_API_KEY",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}
```
