---
name: xai-grok-api
description: xAI Grok API — Grok-4, Grok-3, Grok-3 Mini — real-time web search, vision, and reasoning used in MAARS web intelligence and research agents
---

# xAI Grok API — MAARS Reference

## Models
| Model | Context | Strength |
|-------|---------|----------|
| `grok-4` | 256K | Frontier reasoning, agents |
| `grok-3` | 131K | General flagship |
| `grok-3-mini` | 131K | Fast, budget reasoning |
| `grok-3-fast` | 131K | Low-latency production |
| `grok-2-vision-1212` | 32K | Image + text |
| `grok-2-image` | — | Image generation |

## Why Grok in MAARS
- Real-time X/Twitter data access
- Live web search built into the model
- Strong at current events, news, and trending topics
- Used by MAARS **Web Intelligence Network** (20 agents)

## Python Client (OpenAI-compatible)
```python
from openai import AsyncOpenAI

xai_client = AsyncOpenAI(
    base_url="https://api.x.ai/v1",
    api_key=XAI_API_KEY,
)

response = await xai_client.chat.completions.create(
    model="grok-3",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ],
    stream=True,
    temperature=0.7,
)
```

## Live Search Integration
```python
# Grok has built-in real-time search — just prompt it
response = await xai_client.chat.completions.create(
    model="grok-3",
    messages=[{
        "role": "user",
        "content": "What's the latest news about AI regulation today?"
    }],
)
# Grok automatically fetches real-time data
```

## Vision (Grok-2-vision)
```python
response = await xai_client.chat.completions.create(
    model="grok-2-vision-1212",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_url}},
            {"type": "text", "text": "Analyze this image"}
        ]
    }],
)
```

## Reasoning with Grok-3-mini
```python
response = await xai_client.chat.completions.create(
    model="grok-3-mini",
    messages=messages,
    reasoning_effort="high",  # "low", "medium", "high"
)
# Access reasoning
thinking = response.choices[0].message.reasoning_content
```

## MAARS Use Cases
- **Grok-4**: Commander deep research, strategic analysis
- **Grok-3**: Web Intelligence Network agents (trending, news, social)
- **Grok-3-mini**: Fast research queries, fact-checking
- **Grok-2-vision**: Document and image analysis agents

## MAARS Config
```python
{
    "model_provider": "xai",
    "model_name": "grok-3",
    "api_key_env": "XAI_API_KEY",
    "base_url": "https://api.x.ai/v1",
}
```
