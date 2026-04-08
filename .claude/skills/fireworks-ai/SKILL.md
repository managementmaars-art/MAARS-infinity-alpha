---
name: fireworks-ai
description: Fireworks AI — fastest open model inference, Llama/Mixtral/DeepSeek/Qwen, compound AI systems, fine-tuning, FireFunction for MAARS speed-optimized agents
---

# Fireworks AI — MAARS Reference

## Models & Pricing
```python
FIREWORKS_MODELS = {
    "accounts/fireworks/models/llama-v3p3-70b-instruct": {
        "speed": "~150 tok/s", "pricing": "$0.90/1M in, $0.90/1M out",
        "best_for": "Fast high-quality 70B inference",
    },
    "accounts/fireworks/models/llama-v3p1-405b-instruct": {
        "pricing": "$3.00/1M in, $3.00/1M out",
        "best_for": "Largest Llama at competitive price",
    },
    "accounts/fireworks/models/deepseek-r1": {
        "pricing": "$3.00/1M in, $8.00/1M out",
        "best_for": "Reasoning with chain-of-thought",
    },
    "accounts/fireworks/models/mixtral-8x22b-instruct": {
        "pricing": "$0.90/1M in, $0.90/1M out",
        "best_for": "Strong MoE model, cost-effective",
    },
    "accounts/fireworks/models/firefunction-v2": {
        "special": "Optimized for function calling/tool use",
        "pricing": "$0.90/1M in, $0.90/1M out",
        "best_for": "Reliable agentic tool calls at speed",
    },
    "accounts/fireworks/models/qwen2p5-72b-instruct": {
        "pricing": "$0.90/1M in, $0.90/1M out",
        "best_for": "Multilingual + coding tasks",
    },
    "accounts/fireworks/models/flux-1-schnell-fp8": {
        "type": "Image generation",
        "pricing": "$0.002/image",
        "best_for": "Fastest image gen available",
    },
}
```

## API Integration
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=FIREWORKS_API_KEY,
)

def call_fireworks(prompt: str, 
                    model: str = "accounts/fireworks/models/llama-v3p3-70b-instruct") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Streaming
def stream_fireworks(messages: list, model: str):
    response = client.chat.completions.create(
        model=model, messages=messages, stream=True, max_tokens=2048,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# JSON mode
def fireworks_json(prompt: str) -> dict:
    import json
    response = client.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p3-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
```

## FireFunction — Tool Use
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City, State"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    }
}]

response = client.chat.completions.create(
    model="accounts/fireworks/models/firefunction-v2",
    messages=[{"role": "user", "content": "What's the weather in SF?"}],
    tools=tools,
    tool_choice="auto",
)

# Parse tool call
if response.choices[0].message.tool_calls:
    call = response.choices[0].message.tool_calls[0]
    import json
    args = json.loads(call.function.arguments)
    result = get_weather(**args)
```

## Image Generation
```python
import requests, base64

def fireworks_image(prompt: str, model: str = "accounts/fireworks/models/flux-1-schnell-fp8",
                     width: int = 1024, height: int = 1024) -> bytes:
    resp = requests.post(
        "https://api.fireworks.ai/inference/v1/image_generation/accounts/fireworks/models/flux-1-schnell-fp8",
        headers={"Authorization": f"Bearer {FIREWORKS_API_KEY}",
                 "Content-Type": "application/json"},
        json={
            "prompt": prompt, "width": width, "height": height,
            "num_inference_steps": 4, "guidance_scale": 3.5,
            "num_images": 1,
        }
    )
    image_b64 = resp.json()["images"][0]["base64"]
    return base64.b64decode(image_b64)
```

## Fine-Tuning
```python
# Fireworks supports LoRA fine-tuning on their platform
FINETUNING_WORKFLOW = {
    "supported_base_models": ["Llama 3.1 8B/70B", "Mixtral 8x7B", "Mistral 7B"],
    "method": "LoRA fine-tuning",
    "data_format": "JSONL with messages array",
    "steps": [
        "1. Prepare JSONL training data",
        "2. Upload to Fireworks dataset",
        "3. Create fine-tuning job",
        "4. Deploy fine-tuned model",
        "5. Call via API with your model ID",
    ],
    "min_examples": 50,
}
```

## When to Use Fireworks
- **Speed**: Fastest inference for open models (~150 tok/s for 70B)
- **Function calling**: FireFunction-v2 optimized for reliable tool use
- **Cost**: $0.90/1M competitive for 70B models
- **Image gen**: $0.002/image for FLUX Schnell (among cheapest)
- **405B access**: Llama 405B at competitive pricing
- **Fine-tuning**: Deploy LoRA fine-tunes on their infrastructure

## Models to Use
- **Fastest 70B**: `llama-v3p3-70b-instruct` via Fireworks
- **Best tool calling**: `firefunction-v2`
- **Reasoning**: `deepseek-r1` via Fireworks
- **Image gen**: `flux-1-schnell-fp8` at $0.002/image
