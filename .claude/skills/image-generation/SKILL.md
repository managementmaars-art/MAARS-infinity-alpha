---
name: image-generation
description: AI image generation skills — DALL-E, Stable Diffusion, Flux, Midjourney prompting, style guides, batch generation, image editing for MAARS creative agents
---

# Image Generation AI — MAARS Reference

## Provider Comparison
| Provider | Best For | Quality | Speed | Cost |
|----------|---------|---------|-------|------|
| `gpt-image-1` (DALL-E 4) | Instruction-following, text in images | Highest | Medium | $$$ |
| Stability Ultra | Photorealistic, editorial | Excellent | Fast | $$ |
| Stability Core | General creative | Good | Fast | $ |
| `FLUX.1-schnell` (Together) | Fast iterations | Very Good | Very Fast | $$ |
| `FLUX.1-dev` | High quality | Excellent | Medium | $$ |
| `ideogram-v3` | Text in images, logos | Excellent for text | Fast | $$ |

## DALL-E 4 (GPT-Image-1)
```python
from openai import AsyncOpenAI

async def generate_dalle(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "high",
    n: int = 1,
) -> list[str]:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,       # "1024x1024", "1536x1024", "1024x1536"
        quality=quality, # "low", "medium", "high"
        n=n,
    )
    return [img.url for img in response.data]
```

## Flux (via Together AI)
```python
async def generate_flux(prompt: str, model: str = "FLUX.1-schnell") -> str:
    together_client = AsyncOpenAI(
        base_url="https://api.together.xyz/v1",
        api_key=TOGETHER_API_KEY,
    )
    response = await together_client.images.generate(
        model=f"black-forest-labs/{model}",
        prompt=prompt, n=1, width=1024, height=1024,
    )
    return response.data[0].url
```

## Prompt Engineering for Images

### Photorealistic Portrait
```
[Subject description], [lighting], [camera], [lens], [film/style]
"Professional headshot of a 30-year-old business executive, 
soft studio lighting with rim light, Sony A7R IV, 85mm f/1.4,
clean white background, sharp focus, editorial photography style"
```

### Marketing/Product
```
"Product photography of [product], [background], [lighting setup],
[angle], commercial photography, clean, minimalist, advertising quality"
```

### Social Media Content
```
"[Scene description], Instagram aesthetic, [color palette],
lifestyle photography, [mood], natural light, candid feel"
```

### Brand Identity
```
"Logo design for [company], [style: minimalist/bold/geometric],
[color palette], vector art, white background, professional,
suitable for scalable branding"
```

### Negative Prompts (Stability AI)
```python
NEGATIVE_PROMPTS = {
    "portrait": "blurry, distorted, extra limbs, deformed, watermark, text",
    "product": "shadows, reflections, busy background, distorted, low quality",
    "logo": "complex, detailed, photorealistic, shadows, gradients",
}
```

## Style Presets Reference
```python
STYLES = {
    "photorealistic": "hyperrealistic, 8K, professional photography, sharp focus",
    "cinematic": "movie still, dramatic lighting, widescreen, film grain, cinematic color grade",
    "illustration": "digital illustration, flat design, vector, clean lines",
    "oil_painting": "oil on canvas, painterly, textured, museum quality",
    "watercolor": "watercolor painting, soft edges, flowing colors, paper texture",
    "3d_render": "3D render, octane render, subsurface scattering, global illumination",
    "anime": "anime style, Studio Ghibli, detailed, vibrant colors",
    "minimalist": "minimalist, clean, simple, white space, geometric",
    "vintage": "retro, 1970s, film photography, grain, muted colors, nostalgic",
    "neon": "neon lights, cyberpunk, dark background, glowing, futuristic",
}
```

## Batch Generation Pattern
```python
async def batch_generate(prompts: list[str], provider: str = "stability") -> list[bytes]:
    tasks = [generate_image(p, provider=provider) for p in prompts]
    return await asyncio.gather(*tasks)
```

## Models to Use
- **Marketing visuals**: `gpt-image-1` (best instruction following)
- **Artistic/creative**: `Stability Ultra`
- **Fast iterations**: `FLUX.1-schnell` via Together
- **Logos/text in images**: `ideogram-v3`
- **Bulk generation**: `Stability Core` (cheapest at scale)
