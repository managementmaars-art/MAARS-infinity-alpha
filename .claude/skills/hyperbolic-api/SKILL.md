---
name: hyperbolic-api
description: Hyperbolic AI — affordable AI inference, GPU marketplace, open models at competitive pricing for MAARS cost-optimized inference
---

# Hyperbolic API — MAARS Reference

## Overview
```python
HYPERBOLIC_OVERVIEW = {
    "type": "AI API + GPU marketplace",
    "mission": "Democratize AI compute through shared GPU resources",
    "strengths": [
        "Competitive pricing on open models",
        "GPU rental marketplace",
        "Image generation (FLUX, SDXL)",
        "Text-to-speech",
        "On-demand scalable inference",
    ],
}
```

## LLM Models Available
```python
HYPERBOLIC_LLM_MODELS = {
    "meta-llama/Llama-3.3-70B-Instruct": "$0.40/1M in, $0.40/1M out",
    "deepseek-ai/DeepSeek-V3": "$0.50/1M in, $0.50/1M out",
    "deepseek-ai/DeepSeek-R1": "$0.50/1M in, $1.50/1M out",
    "Qwen/Qwen2.5-72B-Instruct": "$0.40/1M in, $0.40/1M out",
    "NovaSky-Berkeley/Sky-T1-32B-Preview": "$0.40/1M in, $0.40/1M out",
    "mistralai/Mixtral-8x7B-Instruct-v0.1": "$0.20/1M in, $0.20/1M out",
    "meta-llama/Llama-3.1-8B-Instruct": "$0.10/1M in, $0.10/1M out",
}
```

## API Integration
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.hyperbolic.xyz/v1",
    api_key=HYPERBOLIC_API_KEY,
)

def call_hyperbolic(prompt: str, 
                     model: str = "meta-llama/Llama-3.3-70B-Instruct") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Image generation
def generate_image_hyperbolic(prompt: str, model: str = "FLUX.1-schnell") -> str:
    response = client.images.generate(
        model=model,
        prompt=prompt,
        n=1,
        size="1024x1024",
    )
    return response.data[0].url

# Audio TTS
def hyperbolic_tts(text: str, speed: float = 1.0) -> bytes:
    response = client.audio.speech.create(
        model="11labs",  # ElevenLabs backend
        voice="en-US-1",
        input=text,
        speed=speed,
    )
    return response.content
```

## GPU Marketplace
```python
import requests

def list_available_gpus():
    """Browse available GPU instances on Hyperbolic marketplace"""
    resp = requests.get(
        "https://api.hyperbolic.xyz/v1/marketplace",
        headers={"Authorization": f"Bearer {HYPERBOLIC_API_KEY}"}
    )
    return resp.json()

def rent_gpu(cluster_name: str, node_name: str, gpu_count: int,
              image: str = "nvidia/cuda:12.2.0-devel-ubuntu20.04"):
    """Rent GPU from marketplace"""
    resp = requests.post(
        "https://api.hyperbolic.xyz/v1/marketplace/instances/create",
        headers={"Authorization": f"Bearer {HYPERBOLIC_API_KEY}"},
        json={
            "cluster_name": cluster_name,
            "node_name": node_name,
            "gpu_count": gpu_count,
            "image": image,
        }
    )
    return resp.json()
```

## When to Use Hyperbolic
- **Budget inference**: Competitive pricing on Llama/DeepSeek
- **GPU marketplace**: Rent peer-to-peer GPU resources
- **Image + TTS + LLM**: One account for multiple AI services
- **DeepSeek R1**: Good pricing on reasoning model
- **Community GPUs**: Lower prices from shared GPU network
