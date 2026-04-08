---
name: deepseek-api
description: DeepSeek API — DeepSeek-V3, DeepSeek-R1 reasoner — used in MAARS for cost-efficient reasoning, coding, and math-heavy agent tasks
---

# DeepSeek API — MAARS Reference

## Models
| Model | Context | Strength | Cost |
|-------|---------|----------|------|
| `deepseek-chat` (V3) | 64K | General chat, coding | Very low |
| `deepseek-reasoner` (R1) | 64K | Chain-of-thought, math, logic | Low |

## Why DeepSeek in MAARS
- **~95% cheaper** than GPT-4o for equivalent quality on many tasks
- R1 rivals o1 on STEM reasoning benchmarks
- V3 is SOTA open-weights for coding tasks
- Used as cost-efficient fallback in the MAARS budget controller

## Python Client (OpenAI-compatible)
```python
from openai import AsyncOpenAI

deepseek_client = AsyncOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=DEEPSEEK_API_KEY,
)

# Standard chat
response = await deepseek_client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ],
    stream=True,
)

# Reasoning model
response = await deepseek_client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    # Note: temperature not supported for reasoner
)
# Access reasoning chain
reasoning = response.choices[0].message.reasoning_content
answer = response.choices[0].message.content
```

## Streaming Reasoning
```python
async for chunk in stream:
    delta = chunk.choices[0].delta
    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
        yield {"type": "thinking", "content": delta.reasoning_content}
    elif delta.content:
        yield {"type": "text", "content": delta.content}
```

## Pricing (2026)
| Model | Input $/1M | Output $/1M | Cache Hit |
|-------|-----------|------------|-----------|
| deepseek-chat | $0.27 | $1.10 | $0.07 |
| deepseek-reasoner | $0.55 | $2.19 | $0.14 |

## MAARS Budget Router
```python
# Use DeepSeek when budget per task < $0.01
def get_budget_model(task_complexity: str, budget_usd: float):
    if budget_usd < 0.005:
        return "deepseek", "deepseek-chat"
    elif task_complexity == "reasoning" and budget_usd < 0.02:
        return "deepseek", "deepseek-reasoner"
    return "openai", "gpt-4o"
```

## Via SambaNova (faster DeepSeek)
```python
sambanova_client = AsyncOpenAI(
    base_url="https://api.sambanova.ai/v1",
    api_key=SAMBANOVA_API_KEY,
)
# models: "DeepSeek-R1-0528", "DeepSeek-V3-0324"
```

## MAARS Config
```python
{
    "model_provider": "deepseek",
    "model_name": "deepseek-chat",
    "api_key_env": "DEEPSEEK_API_KEY",
    "base_url": "https://api.deepseek.com/v1",
}
```
