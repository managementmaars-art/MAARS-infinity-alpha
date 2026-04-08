---
name: openai-api
description: Complete OpenAI API reference for MAARS — GPT-5, GPT-4o, O3, O4-mini, Responses API, Assistants, structured outputs, tool calling, streaming, and embeddings
---

# OpenAI API — MAARS Reference

## Models Used in MAARS
| Model | Use Case | Context | Notes |
|-------|----------|---------|-------|
| `gpt-5.2` | Commander Orion, primary agents | 1M tokens | Flagship reasoning + tool use |
| `gpt-4o` | Fast agents, structured output | 128K | Best latency/quality balance |
| `o3` | Deep reasoning, verification | 200K | Extended thinking, slow |
| `o4-mini` | Budget reasoning tasks | 128K | Fast chain-of-thought |
| `text-embedding-3-large` | Semantic memory, RAG | — | 3072 dims |
| `gpt-image-1` | Image generation | — | DALL-E 4 |
| `gpt-4o-realtime` | Voice/TTS streaming | — | Real-time audio |
| `tts-1-hd` | Text-to-speech | — | HD voice output |
| `whisper-1` | STT transcription | — | Audio input |

## Chat Completions (Standard)
```python
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are..."},
        {"role": "user", "content": "..."}
    ],
    temperature=0.7,
    max_tokens=4096,
    stream=True,  # always stream in MAARS
)
async for chunk in response:
    delta = chunk.choices[0].delta.content or ""
```

## Responses API (Stateful, preferred for agents)
```python
response = await client.responses.create(
    model="gpt-4o",
    input="User message",
    instructions="System prompt",
    tools=[{"type": "web_search_preview"}],
    previous_response_id=prior_id,  # stateful threading
)
text = response.output_text
```

## Structured Outputs (Pydantic)
```python
from pydantic import BaseModel

class TaskPlan(BaseModel):
    tasks: list[str]
    priority: str
    estimated_time: int

response = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[...],
    response_format=TaskPlan,
)
plan = response.choices[0].message.parsed
```

## Tool Calling
```python
tools = [{
    "type": "function",
    "function": {
        "name": "create_task",
        "description": "Create a task in MAARS",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
            },
            "required": ["title"]
        }
    }
}]

response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)
# Handle tool call
if response.choices[0].message.tool_calls:
    for tc in response.choices[0].message.tool_calls:
        fn_name = tc.function.name
        args = json.loads(tc.function.arguments)
```

## Embeddings (for MAARS semantic memory)
```python
response = await client.embeddings.create(
    model="text-embedding-3-large",
    input=text,
    dimensions=1536,  # or 3072 for full
)
vector = response.data[0].embedding
```

## Streaming with Token Counting
```python
usage = {"prompt": 0, "completion": 0}
async for chunk in stream:
    if chunk.usage:
        usage["prompt"] = chunk.usage.prompt_tokens
        usage["completion"] = chunk.usage.completion_tokens
```

## Error Handling (MAARS pattern)
```python
from openai import RateLimitError, APIError
import asyncio

async def call_with_retry(fn, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await fn()
        except RateLimitError:
            await asyncio.sleep(2 ** attempt)
        except APIError as e:
            if e.status_code >= 500:
                await asyncio.sleep(1)
            else:
                raise
    raise Exception("Max retries exceeded")
```

## MAARS Integration Points
- **model_provider**: `"openai"` in agent config
- **model_name**: any model ID above
- **API key**: `OPENAI_API_KEY` env var
- **Base URL**: `https://api.openai.com/v1` (or MAARS proxy)
- **Cost tracking**: log `usage.total_tokens` to budget controller

## Pricing Reference (approximate)
| Model | Input $/1M | Output $/1M |
|-------|-----------|------------|
| gpt-5.2 | $15 | $60 |
| gpt-4o | $2.50 | $10 |
| o3 | $10 | $40 |
| o4-mini | $1.10 | $4.40 |
| embedding-3-large | $0.13 | — |
