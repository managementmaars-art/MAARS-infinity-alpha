---
name: nvidia-api
description: NVIDIA NIM API — Nemotron Ultra 253B, Nemotron Super 49B, Llama Nemotron — enterprise-grade inference with NVIDIA's optimized models
---

# NVIDIA NIM API — MAARS Reference

## Models
| Model | Context | Strength |
|-------|---------|----------|
| `nvidia/llama-3.1-nemotron-ultra-253b-v1` | 128K | Flagship, best open model |
| `nvidia/llama-3.3-nemotron-super-49b-v1` | 128K | Fast, high quality |
| `nvidia/llama-3.1-nemotron-70b-instruct` | 128K | Balanced |
| `nvidia/mistral-nemo-minitron-8b-8k-instruct` | 8K | Ultra-fast |
| `meta/llama-4-maverick-17b-128e-instruct` | 128K | Llama 4 on NVIDIA |

## Client (OpenAI-compatible)
```python
from openai import AsyncOpenAI

nvidia_client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
)

response = await nvidia_client.chat.completions.create(
    model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
    messages=messages,
    temperature=0.7,
    max_tokens=4096,
    stream=True,
)
```

## Thinking Mode (Nemotron Ultra)
```python
# Toggle reasoning with system prompt
response = await nvidia_client.chat.completions.create(
    model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
    messages=[
        {"role": "system", "content": "detailed thinking on"},  # enables CoT
        {"role": "user", "content": "Solve this complex problem..."}
    ],
)
```

## MAARS Use Cases
- High-quality open-source alternative to frontier models
- Enterprise deployments requiring on-prem-like compliance
- Fallback chain for OpenAI/Anthropic outages
- Nemotron Ultra for complex reasoning tasks

## MAARS Config
```python
{
    "model_provider": "nvidia",
    "model_name": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
    "api_key_env": "NVIDIA_API_KEY",
    "base_url": "https://integrate.api.nvidia.com/v1",
}
```
