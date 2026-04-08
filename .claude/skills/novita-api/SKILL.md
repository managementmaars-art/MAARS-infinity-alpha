---
name: novita-api
description: Novita AI — cheapest image generation, video generation, 100+ open models, LoRA training for MAARS cost-optimized creative agents
---

# Novita AI API — MAARS Reference

## Overview
```python
NOVITA_OVERVIEW = {
    "type": "AI API marketplace — image, video, LLM, audio",
    "strength": "Cheapest image generation in the market",
    "models": [
        "FLUX.1-schnell", "FLUX.1-dev", "SDXL",
        "Stable Diffusion 3.5", "SD 1.5 + 100s of LoRAs",
        "Llama 3.3 70B", "Qwen 2.5 72B", "DeepSeek V3",
        "Kling video", "Wan video", "AnimateDiff",
    ],
    "pricing_vs_others": {
        "flux_schnell_per_image": "$0.001-0.003 (vs OpenAI DALL-E: $0.04)",
        "flux_dev_per_image": "$0.02",
        "sdxl_per_image": "$0.007",
        "llm_llama3_70b": "$0.60/1M tokens",
    },
}
```

## Image Generation
```python
import requests

def generate_image_novita(prompt: str, model: str = "flux/1-schnell",
                            width: int = 1024, height: int = 1024,
                            steps: int = 4) -> str:
    """Returns URL of generated image"""
    resp = requests.post(
        "https://api.novita.ai/v3/async/txt2img",
        headers={
            "Authorization": f"Bearer {NOVITA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model_name": model,
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, watermark",
            "width": width,
            "height": height,
            "image_num": 1,
            "steps": steps,
            "guidance_scale": 3.5,  # For FLUX
            "sampler_name": "euler_a",
        }
    )
    task_id = resp.json()["task_id"]
    
    # Poll for result
    import time
    while True:
        result = requests.get(
            f"https://api.novita.ai/v3/async/task-result",
            headers={"Authorization": f"Bearer {NOVITA_API_KEY}"},
            params={"task_id": task_id}
        ).json()
        if result["task"]["status"] == "TASK_STATUS_SUCCEED":
            return result["images"][0]["image_url"]
        time.sleep(2)

# OpenAI-compatible image API
def novita_openai_image(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(
        base_url="https://api.novita.ai/v3/openai",
        api_key=NOVITA_API_KEY,
    )
    response = client.images.generate(
        model="flux/1-schnell",
        prompt=prompt,
        n=1, size="1024x1024",
    )
    return response.data[0].url
```

## LLM Inference
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.novita.ai/v3/openai",
    api_key=NOVITA_API_KEY,
)

def call_novita_llm(prompt: str, model: str = "meta-llama/llama-3.3-70b-instruct") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
    )
    return response.choices[0].message.content

NOVITA_LLM_MODELS = [
    "meta-llama/llama-3.3-70b-instruct",
    "deepseek/deepseek-v3",
    "deepseek/deepseek-r1",
    "qwen/qwen2.5-72b-instruct",
    "mistralai/mistral-large-2411",
    "google/gemma-3-27b-it",
]
```

## Image-to-Image & Inpainting
```python
def image_to_image_novita(init_image_url: str, prompt: str, 
                            strength: float = 0.7) -> str:
    """Transform existing image"""
    resp = requests.post(
        "https://api.novita.ai/v3/async/img2img",
        headers={"Authorization": f"Bearer {NOVITA_API_KEY}"},
        json={
            "model_name": "flux/1-dev",
            "image_assets": [{"image_type": "image_init", "image_url": init_image_url}],
            "prompt": prompt,
            "strength": strength,
            "steps": 20,
            "width": 1024, "height": 1024,
        }
    )
    task_id = resp.json()["task_id"]
    return _poll_novita(task_id)

def inpaint_novita(image_url: str, mask_url: str, prompt: str) -> str:
    """Fill in masked area with AI-generated content"""
    resp = requests.post(
        "https://api.novita.ai/v3/async/inpainting",
        headers={"Authorization": f"Bearer {NOVITA_API_KEY}"},
        json={
            "model_name": "sdXL_v10VAEFix.safetensors",
            "image_assets": [
                {"image_type": "image_init", "image_url": image_url},
                {"image_type": "image_mask", "image_url": mask_url},
            ],
            "prompt": prompt,
            "steps": 20,
        }
    )
    return _poll_novita(resp.json()["task_id"])

def _poll_novita(task_id: str) -> str:
    import time
    while True:
        result = requests.get("https://api.novita.ai/v3/async/task-result",
                             headers={"Authorization": f"Bearer {NOVITA_API_KEY}"},
                             params={"task_id": task_id}).json()
        if result["task"]["status"] == "TASK_STATUS_SUCCEED":
            return result["images"][0]["image_url"]
        time.sleep(2)
```

## Video Generation
```python
def generate_video_novita(prompt: str, model: str = "wan/2.1-i2v-480p",
                           image_url: str = None) -> str:
    payload = {
        "model_name": model,
        "prompt": prompt,
        "duration": 5,  # seconds
    }
    if image_url:
        payload["image_url"] = image_url
    
    resp = requests.post(
        "https://api.novita.ai/v3/async/video-generation",
        headers={"Authorization": f"Bearer {NOVITA_API_KEY}"},
        json=payload
    )
    task_id = resp.json()["task_id"]
    import time
    while True:
        result = requests.get("https://api.novita.ai/v3/async/task-result",
                             headers={"Authorization": f"Bearer {NOVITA_API_KEY}"},
                             params={"task_id": task_id}).json()
        if result["task"]["status"] == "TASK_STATUS_SUCCEED":
            return result["videos"][0]["video_url"]
        time.sleep(5)
```

## When to Use Novita
- **Cheapest image gen**: FLUX Schnell at $0.001-0.003/image (10-40x cheaper than DALL-E)
- **Custom LoRA**: Thousands of community LoRAs available
- **Bulk image processing**: Cost-effective for high-volume creative workflows
- **Video + image + LLM**: One API for multiple modalities
- **Open model variety**: Access to hundreds of SD checkpoints
