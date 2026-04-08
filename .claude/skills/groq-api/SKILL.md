---
name: groq-api
description: Groq and Cerebras ultra-fast inference API — Llama 4, QwQ-32B, Mixtral — used in MAARS for latency-critical agent tasks
---

# Groq + Cerebras API — MAARS Reference

## Why Groq in MAARS
Groq provides the fastest inference speeds (500–2000 tokens/sec) for open models. MAARS routes to Groq when:
- Sub-second response latency is required
- High-volume agent tasks need throughput
- Budget-sensitive workloads (lower cost than frontier models)

## Models Available
| Model | Provider | Speed | Context | Use Case |
|-------|----------|-------|---------|----------|
| `llama-4-maverick-17b-128e-instruct` | Groq | Ultra-fast | 128K | General agent tasks |
| `llama-4-scout-17b-16e-instruct` | Groq | Fast | 128K | Quick lookups |
| `llama-3.3-70b-versatile` | Groq | Fast | 128K | Versatile reasoning |
| `qwq-32b` | Groq | Fast | 128K | Chain-of-thought reasoning |
| `mixtral-8x7b-32768` | Groq | Fast | 32K | Multi-task routing |
| `llama3-8b-8192` | Groq | Fastest | 8K | Micro-tasks |
| `llama-4-maverick` | Cerebras | ~2000 t/s | 128K | Extreme throughput |

## Python Client (OpenAI-compatible)
```python
from openai import AsyncOpenAI

groq_client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)

response = await groq_client.chat.completions.create(
    model="llama-4-maverick-17b-128e-instruct",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ],
    temperature=0.7,
    max_tokens=2048,
    stream=True,
)
```

## Cerebras Client
```python
cerebras_client = AsyncOpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=CEREBRAS_API_KEY,
)
# Same interface as Groq — just different base_url
```

## MAARS Router Integration
```python
# In MAARS backend/router/engine.py
GROQ_MODELS = {
    "fast": "llama-4-scout-17b-16e-instruct",
    "balanced": "llama-4-maverick-17b-128e-instruct",
    "reasoning": "qwq-32b",
}

def should_route_to_groq(task_type: str, latency_budget_ms: int) -> bool:
    return latency_budget_ms < 500 or task_type in ("classification", "extraction", "routing")
```

## Rate Limits
| Tier | RPM | TPM |
|------|-----|-----|
| Free | 30 | 6K |
| Dev | 500 | 14.4K |
| Pro | 6000 | 200K |

## Error Codes
- `429`: Rate limit — implement exponential backoff
- `503`: Model overloaded — fallback to Anthropic/OpenAI
- `400`: Context length exceeded — truncate or summarize

## MAARS Config
```python
{
    "model_provider": "groq",
    "model_name": "llama-4-maverick-17b-128e-instruct",
    "api_key_env": "GROQ_API_KEY",
    "base_url": "https://api.groq.com/openai/v1",
    "max_tokens": 8192,
    "temperature": 0.7,
}
```
