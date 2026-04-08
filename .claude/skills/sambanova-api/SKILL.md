---
name: sambanova-api
description: SambaNova Cloud API — fastest DeepSeek R1, Llama 4 — ultra-high throughput inference used in MAARS for speed-critical reasoning tasks
---

# SambaNova API — MAARS Reference

## Models
| Model | Speed | Context | Strength |
|-------|-------|---------|----------|
| `DeepSeek-R1-0528` | Very Fast | 64K | Best reasoning on SambaNova |
| `DeepSeek-V3-0324` | Very Fast | 64K | Best chat on SambaNova |
| `Meta-Llama-4-Maverick-17B-128E-Instruct` | Fastest | 128K | Speed champion |
| `Meta-Llama-3.3-70B-Instruct` | Fast | 128K | Reliable workhorse |
| `Qwen3-32B` | Fast | 40K | Strong reasoning |

## Client (OpenAI-compatible)
```python
from openai import AsyncOpenAI

sambanova_client = AsyncOpenAI(
    base_url="https://api.sambanova.ai/v1",
    api_key=SAMBANOVA_API_KEY,
)

response = await sambanova_client.chat.completions.create(
    model="DeepSeek-R1-0528",
    messages=messages,
    stream=True,
    max_tokens=8192,
)

# For DeepSeek R1 — access thinking chain
async for chunk in response:
    delta = chunk.choices[0].delta
    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
        print("Thinking:", delta.reasoning_content)
    elif delta.content:
        print("Answer:", delta.content)
```

## MAARS Use Cases
- Fastest DeepSeek R1 inference available
- High-throughput batch processing
- Cost-efficient reasoning at scale
- Primary choice when needing R1 quality at speed

## MAARS Config
```python
{
    "model_provider": "sambanova",
    "model_name": "DeepSeek-R1-0528",
    "api_key_env": "SAMBANOVA_API_KEY",
    "base_url": "https://api.sambanova.ai/v1",
}
```
