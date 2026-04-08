---
name: lepton-api
description: Lepton AI — serverless GPU inference, open model hosting, Llama/Mistral/FLUX at scale for MAARS cost-optimized inference
---

# Lepton AI API — MAARS Reference

## Overview
```python
LEPTON_OVERVIEW = {
    "type": "Serverless GPU cloud + managed inference",
    "strengths": [
        "Cheapest serverless GPU compute",
        "Hosts all major open models (Llama, Mistral, FLUX, etc.)",
        "Deploy custom models without infrastructure",
        "Auto-scaling to zero (no idle cost)",
    ],
    "models_available": [
        "llama-3.3-70b", "llama-3.1-405b",
        "mistral-7b-instruct", "mixtral-8x7b",
        "flux-1-schnell", "flux-1-dev",
        "whisper-large-v3", "stable-diffusion-xl",
        "deepseek-r1-distill-llama-70b",
        "qwen2.5-72b-instruct",
    ],
}
```

## API Integration
```python
from openai import OpenAI

# LLM inference
client = OpenAI(
    base_url="https://llama3-3-70b.lepton.run/api/v1/",
    api_key=LEPTON_API_KEY,
)

def call_lepton_llm(prompt: str, model_url_base: str) -> str:
    """
    model_url_base examples:
    - "llama3-3-70b"
    - "mistral-7b"  
    - "mixtral-8x7b"
    - "deepseek-r1-distill-llama-70b"
    """
    endpoint_client = OpenAI(
        base_url=f"https://{model_url_base}.lepton.run/api/v1/",
        api_key=LEPTON_API_KEY,
    )
    response = endpoint_client.chat.completions.create(
        model=model_url_base,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
    )
    return response.choices[0].message.content

# Image generation (FLUX)
import requests

def lepton_flux(prompt: str, model: str = "flux-1-schnell") -> bytes:
    resp = requests.post(
        f"https://{model}.lepton.run/api/v1/run",
        headers={"Authorization": f"Bearer {LEPTON_API_KEY}"},
        json={
            "prompt": prompt,
            "width": 1024, "height": 1024,
            "num_steps": 4,  # schnell = 4 steps
        }
    )
    output = resp.json()["output"][0]
    # output is base64 encoded image
    import base64
    return base64.b64decode(output)
```

## Deploy Custom Model
```python
LEPTON_CUSTOM_DEPLOY = """
# Deploy any Hugging Face model serverlessly

pip install leptonai

# Login
lep login

# Deploy a model
lep photon create -n my-model -m hf:meta-llama/Llama-3.1-8B-Instruct
lep photon push -n my-model
lep photon run -n my-model --resource-shape gpu.a10g

# Your model is now accessible at:
# https://my-model-{workspace}.lepton.run/api/v1
"""

import leptonai
from leptonai.client import Client

def call_custom_model(workspace_url: str, prompt: str):
    c = Client(workspace_url, token=LEPTON_API_KEY)
    return c.run(prompt=prompt)
```

## Pricing Reference
```python
LEPTON_PRICING = {
    "A10G (24GB)": "$0.75/hour (auto-scale to zero)",
    "A100 (80GB)": "$2.50/hour",
    "H100 (80GB)": "$4.50/hour",
    "llama3-3-70b_hosted": "$0.60/1M tokens",
    "flux-1-schnell": "$0.003/image",
    "whisper": "$0.006/minute",
    "vs_together_ai": "Similar pricing, more model variety",
    "vs_runpod": "Lepton serverless (no idle), RunPod more control",
}
```

## When to Use Lepton
- **Serverless GPU**: Don't want to manage infrastructure
- **Custom model hosting**: Deploy fine-tuned models without DevOps
- **FLUX image generation**: Cheap FLUX inference
- **Multi-model routing**: Access many open models via single provider
- **Cost optimization**: Scale to zero when not in use
