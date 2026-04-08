---
name: yi-api
description: 01.AI Yi models — Yi-Large, Yi-Vision, Yi-Lightning, long context Chinese-English bilingual models for MAARS LLM routing
---

# 01.AI Yi API — MAARS Reference

## Models
```python
YI_MODELS = {
    "yi-large": {
        "context": "32K",
        "strengths": "Strong reasoning, bilingual Chinese-English",
        "pricing": "$3.00/1M input, $3.00/1M output",
        "best_for": "Complex reasoning, bilingual tasks",
    },
    "yi-medium": {
        "context": "200K",
        "strengths": "Long context, good quality",
        "pricing": "$0.30/1M input, $0.30/1M output",
        "best_for": "Long document processing, cost-effective 200K",
    },
    "yi-lightning": {
        "context": "16K",
        "strengths": "Ultra-fast, very cheap",
        "pricing": "$0.14/1M input, $0.14/1M output",
        "best_for": "High-volume simple tasks",
    },
    "yi-vision": {
        "multimodal": True,
        "context": "4K",
        "best_for": "Image analysis, Chinese visual content",
    },
    "yi-large-turbo": {
        "context": "16K",
        "strengths": "Speed + quality balance",
        "pricing": "$0.12/1M input, $0.12/1M output",
        "best_for": "Fast Chinese/English content generation",
    },
    "yi-large-rag": {
        "special": "Built-in web search + RAG",
        "best_for": "Real-time information retrieval tasks",
    },
}
```

## API Integration
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.lingyiwanwu.com/v1",
    api_key=YI_API_KEY,
)

def call_yi(prompt: str, model: str = "yi-large-turbo") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Long context (200K)
def analyze_long_doc(document: str, question: str) -> str:
    return call_yi(
        prompt=f"Document:\n{document}\n\nQuestion: {question}",
        model="yi-medium"  # 200K context
    )

# Vision
def analyze_image_yi(image_url: str, question: str) -> str:
    response = client.chat.completions.create(
        model="yi-vision",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": question},
            ]
        }],
    )
    return response.choices[0].message.content
```

## Streaming
```python
def stream_yi(messages: list, model: str = "yi-large"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        max_tokens=4096,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

## When to Use Yi
- **200K context at low cost**: Yi-Medium at $0.30/1M with 200K context
- **Chinese market**: Strong Chinese-English bilingual models
- **Ultra-cheap bulk**: Yi-Lightning at $0.14/1M for simple tasks
- **Built-in search**: Yi-Large-RAG for real-time web retrieval
- **Vision + Chinese**: Yi-Vision for Chinese document images

## Pricing Comparison
```python
YI_VS_ALTERNATIVES = {
    "200K context": {
        "yi-medium": "$0.30/1M",
        "claude-3-haiku-200k": "$0.25/1M (but limited availability)",
        "gpt-4-turbo-128k": "$10/1M",
        "verdict": "Yi-Medium excellent value for 200K",
    },
    "fast cheap": {
        "yi-lightning": "$0.14/1M",
        "gemini-1.5-flash": "$0.075/1M",
        "deepseek-v3": "$0.27/1M",
        "verdict": "Gemini Flash slightly cheaper but Yi Lightning is competitive",
    },
}
```
