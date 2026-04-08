---
name: inception-api
description: Inception AI Mercury — diffusion-based LLM, ultra-fast parallel inference, novel architecture for MAARS speed-critical agents
---

# Inception AI (Mercury) API — MAARS Reference

## Models
```python
INCEPTION_MODELS = {
    "mercury-coder-small": {
        "architecture": "Diffusion LLM (not autoregressive)",
        "context": "32K",
        "speed": "1000+ tokens/sec (10x faster than GPT-4o)",
        "strengths": "Ultra-fast code generation, parallel token generation",
        "best_for": "Code completion, fast coding assistant, latency-critical coding",
        "pricing": "Check api.inceptionlabs.ai for current pricing",
    },
    "mercury-small": {
        "architecture": "Diffusion LLM",
        "context": "32K",
        "strengths": "General fast inference",
        "best_for": "High-throughput text generation where speed > quality",
    },
}

# Key innovation: Diffusion LLMs generate ALL tokens in parallel
# Traditional LLMs: Generate token-by-token (sequential)
# Mercury: Generate entire response simultaneously (like diffusion images)
# Result: 10x+ speed improvement for many tasks
```

## API Integration
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.inceptionlabs.ai/v1",
    api_key=INCEPTION_API_KEY,
)

def call_mercury(prompt: str, model: str = "mercury-coder-small") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Code completion use case
def fast_code_completion(code_prefix: str, language: str = "python") -> str:
    return call_mercury(
        prompt=f"Complete this {language} code:\n```{language}\n{code_prefix}",
        model="mercury-coder-small",
    )
```

## When to Use Inception Mercury
- **Latency-critical coding**: IDEs, real-time autocomplete, live coding
- **High-throughput pipelines**: Processing thousands of code snippets
- **Code generation at scale**: When you need fast but quality matters
- **Novel architecture exploration**: Diffusion LLMs may improve rapidly

## Architecture Note
```
Autoregressive (GPT/Claude/etc.):
Token 1 → Token 2 → Token 3 → ... → Token N
Each token waits for the previous (serial)

Diffusion LLM (Mercury):
All tokens refined simultaneously from noise
Like stable diffusion for images — entire response at once
Better parallelism → massive speed gains
```
