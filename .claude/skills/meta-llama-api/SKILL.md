---
name: meta-llama-api
description: Meta Llama 4 and Llama 3.x API — open-source models via Meta AI, Together AI, Groq, Replicate, AWS Bedrock, Fireworks for MAARS LLM routing
---

# Meta Llama API — MAARS Reference

## Available Models
```python
LLAMA_MODELS = {
    "llama-4-maverick": {
        "context": "1M tokens",
        "multimodal": True,
        "params": "17B active (MoE)",
        "strengths": "Speed + quality balance, multimodal",
        "best_for": "General assistant, vision tasks",
    },
    "llama-4-scout": {
        "context": "10M tokens",  # Longest context available
        "multimodal": True,
        "params": "17B active (MoE)",
        "strengths": "World's longest context window",
        "best_for": "Document analysis, long context RAG",
    },
    "llama-3.3-70b": {
        "context": "128K",
        "strengths": "Best open-source 70B, strong reasoning",
        "best_for": "High quality without frontier model cost",
    },
    "llama-3.1-405b": {
        "context": "128K",
        "strengths": "Largest open Llama, frontier-class",
        "best_for": "Complex reasoning, code generation",
    },
    "llama-3.2-11b-vision": {
        "context": "128K",
        "multimodal": True,
        "best_for": "Image analysis at lower cost",
    },
    "llama-3.2-1b": {
        "params": "1B",
        "best_for": "Edge deployment, ultra-cheap batch",
    },
    "llama-guard-3": {
        "purpose": "Content moderation + safety",
        "best_for": "Filter harmful content in pipelines",
    },
    "code-llama-70b": {
        "purpose": "Code generation specialist",
        "best_for": "Code completion, debugging (self-hosted)",
    },
}
```

## Integration via Together AI (Recommended)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=TOGETHER_API_KEY,
)

def call_llama(prompt: str, model: str = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Llama 4 with vision
def llama_vision(image_url: str, question: str):
    return client.chat.completions.create(
        model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": question},
            ]
        }],
        max_tokens=512,
    ).choices[0].message.content
```

## Integration via Groq (Fastest)
```python
from groq import Groq

groq_client = Groq(api_key=GROQ_API_KEY)

def llama_groq(prompt: str, model: str = "llama-3.3-70b-versatile"):
    # 300+ tokens/sec — fastest inference available
    return groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8192,
    ).choices[0].message.content

# Available Groq Llama models:
GROQ_LLAMA_MODELS = [
    "llama-4-scout-17b-16e-instruct",
    "llama-4-maverick-17b-128e-instruct-fp8",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-guard-3-8b",
]
```

## Self-Hosted via Ollama
```python
import requests

def ollama_llama(prompt: str, model: str = "llama3.3"):
    """Run Llama locally with Ollama"""
    resp = requests.post("http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
    )
    return resp.json()["response"]

# Pull model: ollama pull llama3.3
# Available: llama3.3, llama3.2, llama3.1, codellama, llama-guard3
```

## Meta AI API (Direct)
```python
# Direct Meta access via llama-api
client = OpenAI(
    base_url="https://api.llama.com/compat/v1",
    api_key=META_LLAMA_API_KEY,
)

response = client.chat.completions.create(
    model="Llama-4-Maverick-17B-128E-Instruct",
    messages=[{"role": "user", "content": "Hello"}],
)
```

## Llama Guard — Safety Moderation
```python
def moderate_content(text: str) -> dict:
    """Use Llama Guard to check content safety"""
    response = groq_client.chat.completions.create(
        model="llama-guard-3-8b",
        messages=[{
            "role": "user",
            "content": f"<|start_header_id|>user<|end_header_id|>\n{text}<|eot_id|>"
        }],
        max_tokens=100,
    )
    result = response.choices[0].message.content
    is_safe = result.startswith("safe")
    return {
        "is_safe": is_safe,
        "verdict": result,
        "categories": result.split("\n") if not is_safe else [],
    }
```

## Routing Logic
```python
LLAMA_ROUTING = {
    "ultra_fast_simple": "llama-3.1-8b-instant via Groq",
    "fast_quality": "llama-3.3-70b-versatile via Groq",
    "best_quality": "llama-3.1-405b via Together AI or Fireworks",
    "multimodal": "llama-4-maverick via Together AI",
    "long_context": "llama-4-scout via Together AI (10M context)",
    "code": "llama-3.1-405b via Fireworks (code-optimized)",
    "safety_filter": "llama-guard-3 via Groq",
    "local_private": "ollama (any model, no data leaves machine)",
}

PRICING_ESTIMATE = {
    "groq_llama_3.3_70b": "$0.59/1M input, $0.79/1M output",
    "together_llama_4_maverick_fp8": "$0.27/1M input, $0.27/1M output",
    "fireworks_llama_3.1_405b": "$3.00/1M input, $3.00/1M output",
    "ollama_local": "Free (hardware cost only)",
}
```

## When to Choose Llama
- **Privacy/on-premise**: Self-host with Ollama or vLLM — data never leaves
- **Cost at scale**: Llama 3.3-70B at <$1/M tokens vs. GPT-4o at $5/M
- **Fine-tuning**: Open weights → customize for domain
- **Long context**: Llama 4 Scout has 10M token context (unique)
- **Speed**: Groq inference at 300+ tok/s (fastest available)
