---
name: moonshot-api
description: Moonshot AI (Kimi) API — 1M context window, long document processing — used in MAARS for processing entire books, codebases, and long-form research
---

# Moonshot AI (Kimi) — MAARS Reference

## Models
| Model | Context | Strength |
|-------|---------|----------|
| `moonshot-v1-8k` | 8K | Fast, cheapest |
| `moonshot-v1-32k` | 32K | Standard |
| `moonshot-v1-128k` | 128K | Long documents |
| `kimi-latest` | 1M | Ultra-long context, flagship |

## Client (OpenAI-compatible)
```python
from openai import AsyncOpenAI

kimi_client = AsyncOpenAI(
    base_url="https://api.moonshot.cn/v1",
    api_key=MOONSHOT_API_KEY,
)

# Process an entire long document
response = await kimi_client.chat.completions.create(
    model="kimi-latest",
    messages=[
        {"role": "system", "content": "You are an expert analyst."},
        {"role": "user", "content": f"Analyze this entire document:\n\n{long_document}"}
    ],
    stream=True,
)
```

## File Upload (for long docs)
```python
# Upload file for context
with open("large_report.pdf", "rb") as f:
    file = kimi_client.files.create(file=f, purpose="assistants")

# Reference in message
response = await kimi_client.chat.completions.create(
    model="kimi-latest",
    messages=[{
        "role": "user",
        "content": [
            {"type": "file", "file_id": file.id},
            {"type": "text", "text": "Summarize this report"}
        ]
    }],
)
```

## MAARS Use Cases
- Processing entire legal contracts, financial reports, codebases
- Dr. Eleanor Shaw (Knowledge Architect): full corpus ingestion
- Legal agents: entire case file analysis in one prompt
- Research agents: multi-paper synthesis

## MAARS Config
```python
{
    "model_provider": "moonshot",
    "model_name": "kimi-latest",
    "api_key_env": "MOONSHOT_API_KEY",
    "base_url": "https://api.moonshot.cn/v1",
}
```
