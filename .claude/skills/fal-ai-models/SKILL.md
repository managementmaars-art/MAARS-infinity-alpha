---
name: fal-ai-models
description: fal.ai API for FLUX image generation, video synthesis, audio models, real-time streaming, lip sync, and 3D generation.
---

# fal.ai Models

## Overview

fal.ai provides serverless GPU inference for generative AI models including FLUX for images, video generation, audio synthesis, real-time streaming, lip sync, and 3D model generation.

## Installation & Setup

```bash
npm install @fal-ai/client
pip install fal-client
```

```typescript
import { fal } from "@fal-ai/client";

fal.config({ credentials: process.env.FAL_KEY });
```

```python
import fal_client
import os

# Set via env or directly
fal_client.api_key = os.getenv("FAL_KEY")
```

## FLUX Image Generation

```typescript
// FLUX.1 [schnell] - fastest, 4 steps
const result = await fal.subscribe("fal-ai/flux/schnell", {
  input: {
    prompt: "A serene mountain lake at golden hour, photorealistic, 8k",
    image_size: "landscape_16_9",   // "square", "portrait_4_3", "landscape_16_9", or {width, height}
    num_inference_steps: 4,
    num_images: 1,
    enable_safety_checker: true,
    seed: 42,                        // For reproducibility
  },
  logs: true,
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      console.log(update.logs.map((l) => l.message).join("\n"));
    }
  },
});

console.log(result.data.images[0].url);
console.log(result.data.seed); // Actual seed used

// FLUX.1 [dev] - higher quality, 28 steps
const devResult = await fal.subscribe("fal-ai/flux/dev", {
  input: {
    prompt: "Studio portrait of a professional woman, soft lighting, Canon 5D",
    image_size: { width: 1024, height: 1024 },
    num_inference_steps: 28,
    guidance_scale: 3.5,
    num_images: 4,
    output_format: "jpeg",
    output_quality: 90,
  },
});

// FLUX Pro with fine control
const proResult = await fal.subscribe("fal-ai/flux-pro/v1.1", {
  input: {
    prompt: "Architectural visualization of a modern house",
    image_size: "landscape_16_9",
    steps: 25,
    guidance: 3,
    safety_tolerance: "2",
  },
});
```

## Image-to-Image & Editing

```typescript
// FLUX with ControlNet (pose/depth/canny)
const controlResult = await fal.subscribe("fal-ai/flux-controlnet", {
  input: {
    prompt: "Fashion model wearing designer clothes",
    control_image_url: "https://example.com/pose.jpg",
    controlnet_conditioning_scale: 0.8,
    control_type: "pose",
    num_inference_steps: 28,
  },
});

// Inpainting - edit specific regions
const inpaintResult = await fal.subscribe("fal-ai/flux/dev/image-to-image", {
  input: {
    prompt: "Replace background with sunset beach",
    image_url: "https://example.com/photo.jpg",
    strength: 0.85,               // How much to change (0-1)
    num_inference_steps: 28,
  },
});

// Background removal
const bgRemoved = await fal.subscribe("fal-ai/birefnet", {
  input: {
    image_url: "https://example.com/photo.jpg",
    model: "General Use (Light)",
    operating_resolution: "1024x1024",
    output_format: "png",
  },
});
```

## Video Generation

```typescript
// Kling AI video generation
const videoResult = await fal.subscribe("fal-ai/kling-video/v1.6/pro/text-to-video", {
  input: {
    prompt: "A drone shot of a coastline at sunrise, cinematic, smooth camera movement",
    negative_prompt: "blur, low quality",
    duration: "5",               // "5" or "10" seconds
    aspect_ratio: "16:9",
    cfg_scale: 0.5,
  },
});

console.log(videoResult.data.video.url);

// Image-to-video (animate a still image)
const animResult = await fal.subscribe("fal-ai/kling-video/v1.6/pro/image-to-video", {
  input: {
    prompt: "The woman walks forward gracefully",
    image_url: "https://example.com/portrait.jpg",
    duration: "5",
    aspect_ratio: "9:16",
  },
});

// Minimax video (alternative)
const minimaxResult = await fal.subscribe("fal-ai/minimax/video-01-live", {
  input: {
    prompt: "Time-lapse of a city street",
    image_url: "https://example.com/city.jpg",
  },
});
```

## Lip Sync

```typescript
// Sync audio to video with lip sync
const lipSyncResult = await fal.subscribe("fal-ai/sync-lipsync", {
  input: {
    video_url: "https://example.com/talking-head.mp4",
    audio_url: "https://example.com/speech.mp3",
    model: "sync-1.9.0-beta",
    sync_mode: "bounce",         // "bounce" | "loop" | "cut_off"
  },
});

// Generate speech then lip sync
const ttsResult = await fal.subscribe("fal-ai/playht/tts/v3", {
  input: {
    input: "Welcome to our platform! Let me show you around.",
    voice: "s3://voice-cloning-zero-shot/...",
    output_format: "mp3",
    speed: 1.0,
  },
});

// Chain: text -> speech -> lip sync
const pipeline = async (text: string, videoUrl: string) => {
  const speech = await fal.subscribe("fal-ai/playht/tts/v3", {
    input: { input: text, output_format: "mp3" },
  });

  return await fal.subscribe("fal-ai/sync-lipsync", {
    input: {
      video_url: videoUrl,
      audio_url: speech.data.audio.url,
    },
  });
};
```

## Audio Generation

```typescript
// Music generation with Stable Audio
const musicResult = await fal.subscribe("fal-ai/stable-audio", {
  input: {
    prompt: "Upbeat electronic music, 120 BPM, synthesizers, energetic",
    negative_prompt: "vocals, lyrics",
    seconds_total: 30,
    seconds_start: 0,
    steps: 100,
  },
});

// Voice cloning and TTS
const voiceResult = await fal.subscribe("fal-ai/f5-tts", {
  input: {
    gen_text: "This is a test of voice cloning technology.",
    ref_audio_url: "https://example.com/voice-sample.mp3",
    ref_text: "This is the reference text spoken in the audio sample.",
    model_type: "F5-TTS",
    remove_silence: true,
  },
});
```

## 3D Generation

```typescript
// Image to 3D model
const model3d = await fal.subscribe("fal-ai/trellis", {
  input: {
    image_url: "https://example.com/object.jpg",
    ss_guidance_strength: 7.5,
    ss_sampling_steps: 12,
    slat_guidance_strength: 3,
    slat_sampling_steps: 12,
    mesh_simplify: 0.95,
    texture_size: 1024,
  },
});

console.log(model3d.data.model_url);  // .glb file URL
console.log(model3d.data.video_url);  // Preview video

// Text to 3D
const text3d = await fal.subscribe("fal-ai/triposg", {
  input: {
    prompt: "A sleek sports car, detailed, game-ready",
    num_views: 6,
    texture_size: 2048,
  },
});
```

## Real-time Streaming

```typescript
// Real-time image generation (Turbo mode)
const stream = fal.stream("fal-ai/flux/schnell", {
  input: {
    prompt: "A beautiful landscape",
    num_inference_steps: 4,
  },
});

for await (const event of stream) {
  if (event.type === "output") {
    updatePreview(event.output.images[0].url);
  }
}

const finalResult = await stream.done();
```

## Python Async Usage

```python
import fal_client
import asyncio

async def generate_image(prompt: str) -> str:
    result = await fal_client.run_async(
        "fal-ai/flux/schnell",
        arguments={
            "prompt": prompt,
            "image_size": "landscape_16_9",
            "num_inference_steps": 4,
        },
    )
    return result["images"][0]["url"]

async def batch_generate(prompts: list[str]) -> list[str]:
    tasks = [generate_image(p) for p in prompts]
    return await asyncio.gather(*tasks)

# With queue and webhook
def on_queue_update(update):
    if hasattr(update, "logs"):
        for log in update.logs:
            print(log["message"])

result = fal_client.subscribe(
    "fal-ai/flux/dev",
    arguments={"prompt": "...", "num_images": 4},
    with_logs=True,
    on_queue_update=on_queue_update,
)
```

## Upload Files to fal Storage

```typescript
// Upload local files to fal's CDN
import { fal } from "@fal-ai/client";
import fs from "fs";

const file = new File([fs.readFileSync("./image.jpg")], "image.jpg", {
  type: "image/jpeg",
});

const url = await fal.storage.upload(file);
// Use url in subsequent API calls
```

## Key Patterns

- **`fal.subscribe`** handles queue management automatically — use for most cases
- **`fal.stream`** for real-time progressive output
- **Chain models**: generate image -> upscale -> remove background -> lip sync
- **Seed parameter** for reproducible results
- **`onQueueUpdate` callback** shows progress logs in your UI
- **Upload to fal storage** before referencing local files in model inputs

## Models to Use

- **claude-opus-4-5**: Complex multi-model pipelines, video production workflows
- **claude-sonnet-4-5**: Standard image/video generation, lip sync pipelines
- **claude-haiku-3-5**: Simple image generation calls, prompt variations
