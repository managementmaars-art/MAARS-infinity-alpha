---
name: mistral-api
description: Mistral AI API reference — Mistral Large, Small, Codestral, Pixtral — used in MAARS for European-hosted, code-focused, and cost-efficient agent tasks
---

# Mistral AI API — MAARS Reference

## Models Used in MAARS
| Model | Context | Strength | Cost |
|-------|---------|----------|------|
| `mistral-large-latest` | 128K | Best reasoning, multilingual | $$$ |
| `mistral-small-latest` | 32K | Fast, cost-efficient | $ |
| `codestral-latest` | 32K | Code generation, fill-in-middle | $$ |
| `pixtral-large-latest` | 128K | Vision + text multimodal | $$$ |
| `mistral-embed` | — | Embeddings 1024d | $ |
| `ministral-8b-latest` | 128K | Edge deployment, ultra-fast | $ |

## Python Client (Official SDK)
```python
from mistralai import Mistral

mistral = Mistral(api_key=MISTRAL_API_KEY)

# Async chat
response = await mistral.chat.complete_async(
    model="mistral-large-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ],
    temperature=0.7,
    max_tokens=4096,
)
content = response.choices[0].message.content
```

## Streaming
```python
stream = await mistral.chat.stream_async(
    model="mistral-large-latest",
    messages=messages,
)
async for event in stream:
    chunk = event.data.choices[0].delta.content or ""
    yield chunk
```

## OpenAI-Compatible Client (MAARS standard)
```python
from openai import AsyncOpenAI

mistral_client = AsyncOpenAI(
    base_url="https://api.mistral.ai/v1",
    api_key=MISTRAL_API_KEY,
)
# Then use standard openai interface
```

## Function Calling
```python
response = await mistral.chat.complete_async(
    model="mistral-large-latest",
    messages=messages,
    tools=[{
        "type": "function",
        "function": {
            "name": "tool_name",
            "description": "...",
            "parameters": {...}
        }
    }],
    tool_choice="auto",
)
```

## Code Completion (Codestral FIM)
```python
response = await mistral.fim.complete_async(
    model="codestral-latest",
    prompt="def fibonacci(n):\n    ",
    suffix="\n    return result",
)
code = response.choices[0].message.content
```

## MAARS Use Cases
- **Mistral Large**: Legal, compliance, multilingual agents
- **Codestral**: Code generation agent (Kai Nakamoto)
- **Mistral Small**: High-volume classification, routing
- **Pixtral**: Image analysis, document processing

## MAARS Config
```python
{
    "model_provider": "mistral",
    "model_name": "mistral-large-latest",
    "api_key_env": "MISTRAL_API_KEY",
    "base_url": "https://api.mistral.ai/v1",
}
```
