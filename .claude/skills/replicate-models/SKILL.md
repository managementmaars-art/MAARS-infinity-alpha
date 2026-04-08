---
name: replicate-models
version: 1.0.0
description: Replicate API for running AI models, predictions, fine-tuning, deployments, streaming, and SDXL/FLUX/LLM inference
tags: [replicate, ai, ml, image-generation, llm, fine-tuning, api, python, typescript]
---

# Replicate Models

Run machine learning models in the cloud via the Replicate API. Covers predictions, streaming, fine-tuning, deployments, and popular models.

## Setup

```bash
pip install replicate
# or
npm install replicate

export REPLICATE_API_TOKEN=r8_your_token_here
```

---

## Basic Predictions

```python
import replicate
import os

client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

# Synchronous run (blocks until complete)
output = replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={
        "prompt": "A photorealistic portrait of a robot chef cooking spaghetti, studio lighting",
        "negative_prompt": "blurry, low quality, cartoon, anime",
        "width": 1024,
        "height": 1024,
        "num_inference_steps": 30,
        "guidance_scale": 7.5,
        "num_outputs": 1,
    }
)
# output is a list of FileOutput objects (URLs)
image_url = str(output[0])
print(f"Generated: {image_url}")

# Download the image
import httpx
img_bytes = httpx.get(image_url).content
with open("output.png", "wb") as f:
    f.write(img_bytes)
```

```typescript
import Replicate from "replicate";

const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN,
});

const output = await replicate.run(
  "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
  {
    input: {
      prompt: "A photorealistic portrait of a robot chef cooking spaghetti",
      width: 1024,
      height: 1024,
      num_inference_steps: 30,
    },
  }
) as string[];

console.log("Image URL:", output[0]);
```

---

## Streaming (LLM Text Generation)

```python
import replicate

# Stream tokens as they generate
for event in replicate.stream(
    "meta/meta-llama-3-70b-instruct",
    input={
        "prompt": "Explain quantum entanglement in simple terms.",
        "system_prompt": "You are a helpful physics teacher who explains complex concepts clearly.",
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop_sequences": "<|end_of_text|>",
    },
):
    print(str(event), end="", flush=True)
print()  # newline at end

# Async streaming in FastAPI
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat")
async def chat(prompt: str):
    async def generate():
        async for event in replicate.async_stream(
            "meta/meta-llama-3-70b-instruct",
            input={"prompt": prompt, "max_tokens": 1024},
        ):
            yield f"data: {str(event)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## Async Predictions (Long-Running Jobs)

```python
import replicate
import time

# Create prediction without waiting
prediction = replicate.predictions.create(
    version="39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={
        "prompt": "A vast alien landscape with twin moons, oil painting style",
        "num_outputs": 4,
        "width": 1024,
        "height": 1024,
    },
    # Webhook to call when done
    webhook="https://api.example.com/webhooks/replicate",
    webhook_events_filter=["completed", "failed"],
)

print(f"Prediction ID: {prediction.id}")
print(f"Status: {prediction.status}")  # "starting"

# Poll for completion
while prediction.status not in ("succeeded", "failed", "canceled"):
    time.sleep(1)
    prediction.reload()
    print(f"Status: {prediction.status}")

if prediction.status == "succeeded":
    for url in prediction.output:
        print(f"Output: {url}")
else:
    print(f"Failed: {prediction.error}")

# Cancel a running prediction
prediction.cancel()

# List recent predictions
for pred in replicate.predictions.list():
    print(f"{pred.id}: {pred.status} - {pred.created_at}")
```

---

## FLUX Models (Latest Image Generation)

```python
import replicate

# FLUX.1 Schnell - fast, 4 steps
output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={
        "prompt": "A serene Japanese tea garden at sunrise, cherry blossoms falling",
        "num_outputs": 1,
        "aspect_ratio": "16:9",   # "1:1", "16:9", "21:9", "3:2", "2:3", "4:5", "5:4", "3:4", "4:3", "9:16", "9:21"
        "output_format": "webp",  # "webp", "jpg", "png"
        "output_quality": 80,
        "go_fast": True,
    }
)

# FLUX.1 Dev - higher quality, 28 steps
output = replicate.run(
    "black-forest-labs/flux-dev",
    input={
        "prompt": "Ultra-realistic portrait of an elderly lighthouse keeper, dramatic lighting",
        "num_outputs": 1,
        "num_inference_steps": 28,
        "guidance": 3.5,
        "aspect_ratio": "2:3",
        "output_format": "png",
    }
)

# FLUX.1 Pro (via API)
output = replicate.run(
    "black-forest-labs/flux-pro",
    input={
        "prompt": "A detailed mechanical watch movement, macro photography",
        "steps": 25,
        "guidance": 3,
        "interval": 2,
        "aspect_ratio": "1:1",
        "safety_tolerance": 2,
    }
)

# FLUX with ControlNet (image-guided generation)
import base64

with open("reference.jpg", "rb") as f:
    control_image = base64.b64encode(f.read()).decode()

output = replicate.run(
    "xlabs-ai/flux-dev-controlnet",
    input={
        "prompt": "A robot in the same pose as the reference image",
        "control_image": f"data:image/jpeg;base64,{control_image}",
        "controlnet_conditioning_scale": 0.7,
        "num_inference_steps": 28,
    }
)
```

---

## Fine-Tuning (FLUX LoRA Training)

```python
import replicate

# Upload training images (must be a zip of images)
with open("training_images.zip", "rb") as f:
    training_data = replicate.files.create(f, filename="training_images.zip")

# Start training
training = replicate.trainings.create(
    model="ostris/flux-dev-lora-trainer",
    version="885394e6a31c6f349d358afbf2e8c8b17a7f8b60a9ef1fbc2628c02a5b59c0e",
    input={
        "input_images": training_data.urls["get"],
        "steps": 1000,
        "lora_rank": 16,
        "optimizer": "adamw8bit",
        "batch_size": 1,
        "resolution": "512,768,1024",
        "autocaption": True,
        "trigger_word": "TOK",  # the word that activates your style
        "learning_rate": 0.0004,
    },
    destination="your-username/my-lora-model",
)

print(f"Training ID: {training.id}")
print(f"Status: {training.status}")

# Wait for training
import time
while training.status not in ("succeeded", "failed", "canceled"):
    time.sleep(30)
    training.reload()
    print(f"Training status: {training.status}")

if training.status == "succeeded":
    print(f"Model ready at: {training.output['version']}")

# Use the fine-tuned model
output = replicate.run(
    "your-username/my-lora-model",
    input={
        "prompt": "TOK in a futuristic cityscape",  # use trigger word
        "num_inference_steps": 28,
    }
)
```

---

## Deployments (Persistent Endpoints)

```python
import replicate

# Create a deployment for consistent, low-latency access
# Deployments keep hardware warm and provide a stable URL

# Run a prediction via deployment (no version pinning needed)
prediction = replicate.deployments.predictions.create(
    deployment_name="your-username/my-sdxl-deployment",
    input={
        "prompt": "A cozy coffee shop interior, warm lighting, watercolor style",
        "width": 1024,
        "height": 1024,
    },
    webhook="https://api.example.com/webhooks/replicate",
)

# Check deployment info
deployment = replicate.deployments.get("your-username/my-sdxl-deployment")
print(f"Min instances: {deployment.current_release.configuration.min_instances}")
print(f"Max instances: {deployment.current_release.configuration.max_instances}")
print(f"Hardware: {deployment.current_release.configuration.hardware}")
```

---

## Model Discovery and Versioning

```python
import replicate

# Search for models
models = replicate.models.search("image segmentation")
for model in models:
    print(f"{model.owner}/{model.name}: {model.description}")

# Get a specific model and its versions
model = replicate.models.get("stability-ai/stable-diffusion")
for version in model.versions.list():
    print(f"Version: {version.id} - Created: {version.created_at}")

# Get latest version
latest = model.versions.list()[0]
print(f"Latest: {latest.id}")
print(f"Schema: {latest.openapi_schema['components']['schemas']['Input']}")

# Pin to exact version (recommended for production)
SDXL_VERSION = "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
LLAMA_VERSION = "meta/meta-llama-3-70b-instruct"   # some models use owner/name without version

# Webhook verification
import hmac
import hashlib

def verify_webhook(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## Common Models Reference

| Model | ID | Use Case |
|-------|-----|----------|
| FLUX Schnell | `black-forest-labs/flux-schnell` | Fast image generation |
| FLUX Dev | `black-forest-labs/flux-dev` | Quality image generation |
| SDXL | `stability-ai/sdxl` | Stable Diffusion XL |
| Llama 3.1 70B | `meta/meta-llama-3.1-70b-instruct` | LLM text generation |
| Llama 3.1 8B | `meta/meta-llama-3.1-8b-instruct` | Fast/cheap LLM |
| Whisper | `openai/whisper` | Speech to text |
| MusicGen | `meta/musicgen` | Music generation |
| Real-ESRGAN | `nightmareai/real-esrgan` | Image upscaling |
| Remove BG | `cjwbw/rembg` | Background removal |
| CodeLlama | `meta/codellama-70b-instruct` | Code generation |
| Mistral | `mistralai/mistral-7b-instruct-v0.2` | Efficient LLM |

---

## Best Practices

- **Pin model versions** in production: `model:sha256hash` not just `model/name`
- **Use webhooks** for long-running predictions; polling is wasteful and fragile
- **Cache outputs**: Replicate URLs expire; download and store results in your own storage (S3/R2)
- **Handle errors gracefully**: check `prediction.status == "failed"` and `prediction.error`
- **Use deployments** for consistent latency in user-facing features
- **Set `webhook_events_filter`**: only subscribe to events you need (reduces noise)
- **Rate limiting**: Replicate has API rate limits; implement retry with exponential backoff
- **Cost estimation**: check model pricing page; use `num_outputs=1` and test before scaling
- **Streaming for LLMs**: always stream text; users expect it and it feels faster

## Models to Use

- **claude-opus-4-5**: Designing fine-tuning pipelines, complex multi-model workflows, architecture decisions
- **claude-sonnet-4-5**: Implementing prediction handlers, webhook endpoints, async job management
- **claude-haiku-3-5**: Simple model calls, quick prototyping, fetching output URLs
