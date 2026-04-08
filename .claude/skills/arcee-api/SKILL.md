---
name: arcee-api
description: Arcee AI — specialized small language models, SuperNova, Blaze, Caller, domain-specific fine-tuned models for MAARS efficient LLM routing
---

# Arcee API — MAARS Reference

## Models
```python
ARCEE_MODELS = {
    "arcee-nova": {
        "context": "128K",
        "strengths": "Best Arcee model, enterprise general purpose",
        "pricing": "$0.50/1M input, $1.50/1M output",
        "best_for": "General tasks where cost matters",
    },
    "arcee-blaze": {
        "context": "128K",
        "strengths": "Fast, cost-efficient, good reasoning",
        "pricing": "$0.15/1M input, $0.45/1M output",
        "best_for": "High-volume classification, extraction",
    },
    "arcee-maestro": {
        "context": "128K",
        "strengths": "Strong at reasoning and coding",
        "pricing": "$1.00/1M input, $3.00/1M output",
        "best_for": "Complex tasks, code generation",
    },
    "arcee-caller": {
        "speciality": "Function calling + tool use",
        "strengths": "Optimized for agent tool use",
        "best_for": "Agentic workflows requiring reliable tool calls",
    },
    "arcee-lite": {
        "strengths": "Ultra-fast, very cheap",
        "pricing": "$0.05/1M input, $0.15/1M output",
        "best_for": "Bulk processing, simple tasks",
    },
    "supernova-medius": {
        "strengths": "MergeKit ensemble, beats much larger models",
        "best_for": "Reasoning, instruction following",
    },
}
```

## API Integration
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://conductor.arcee.ai/v1",
    api_key=ARCEE_API_KEY,
)

def call_arcee(prompt: str, model: str = "arcee-nova") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Tool calling with arcee-caller
def arcee_with_tools(messages: list, tools: list):
    return client.chat.completions.create(
        model="arcee-caller",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=1024,
    )
```

## Arcee Distillation Platform
```python
# Arcee specializes in model distillation and fine-tuning
DISTILLATION_WORKFLOW = {
    "concept": "Train small efficient model from larger teacher model",
    "use_case": "Domain-specific tasks at 10x lower cost",
    "steps": [
        "1. Define your task (classification, extraction, Q&A)",
        "2. Generate training data with Claude/GPT-4o (teacher)",
        "3. Fine-tune Arcee base model on your data",
        "4. Deploy specialized model for your exact use case",
    ],
    "roi": "7B specialized model can match 70B general model on target task",
}

ARCEE_MERGEKIT = {
    "description": "Model merging — combine capabilities of multiple models",
    "techniques": ["SLERP", "DARE", "TIES", "Task Arithmetic"],
    "use_case": "Merge a coding model + reasoning model for code-reasoning tasks",
}
```

## When to Use Arcee
- **Cost optimization**: Arcee Lite at $0.05/1M vs. frontier models at $5-15/1M
- **Tool calling**: Arcee Caller optimized for reliable function calls
- **Domain fine-tuning**: Arcee platform for custom model training
- **Model merging**: SuperNova approach for specialized capabilities
- **High-volume pipelines**: Arcee Blaze for bulk processing
