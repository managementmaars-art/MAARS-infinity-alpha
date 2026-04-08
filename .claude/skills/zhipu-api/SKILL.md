---
name: zhipu-api
description: Zhipu AI GLM models — GLM-4, CogVideo, CogView, Chinese-first LLM for MAARS Chinese market and multimodal agents
---

# Zhipu AI (GLM) API — MAARS Reference

## Models
```python
ZHIPU_MODELS = {
    "glm-4-plus": {
        "context": "128K",
        "strengths": "Best GLM, Chinese + English, strong coding",
        "pricing": "¥0.05/1K tokens (~$0.007/1K)",
        "best_for": "Chinese market AI, bilingual content",
    },
    "glm-4-air": {
        "context": "128K",
        "strengths": "Fast, cost-efficient",
        "pricing": "¥0.001/1K tokens (very cheap)",
        "best_for": "High-volume Chinese content tasks",
    },
    "glm-4v-plus": {
        "multimodal": True,
        "context": "8K",
        "strengths": "Vision + Chinese language understanding",
        "best_for": "Chinese document analysis, image description in Chinese",
    },
    "glm-4-long": {
        "context": "1M tokens",
        "best_for": "Long Chinese documents, books",
    },
    "cogvideox-5b": {
        "type": "Video generation",
        "strengths": "Open source, high quality, 6 second clips",
        "best_for": "Video gen when data privacy matters (local)",
    },
    "cogview-3-plus": {
        "type": "Image generation",
        "strengths": "SDXL quality, Chinese market optimized",
        "best_for": "Product images, illustrations for Chinese content",
    },
    "charglm-3": {
        "type": "Character roleplay",
        "strengths": "Custom AI character with persistent memory",
        "best_for": "Chatbots, virtual companions, NPCs",
    },
}
```

## API Integration
```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key=ZHIPU_API_KEY)

def call_glm(prompt: str, model: str = "glm-4-air") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Streaming
def stream_glm(messages: list):
    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=messages,
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Vision
def glm_vision(image_path: str, question: str) -> str:
    import base64
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    response = client.chat.completions.create(
        model="glm-4v-plus",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", 
                 "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                {"type": "text", "text": question},
            ]
        }],
    )
    return response.choices[0].message.content
```

## OpenAI-Compatible
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    api_key=ZHIPU_API_KEY,
)

response = client.chat.completions.create(
    model="glm-4-air",
    messages=[{"role": "user", "content": "你好，请介绍一下自己"}],
)
```

## CogVideo — Video Generation
```python
def generate_cogvideo(prompt: str, image_url: str = None) -> str:
    """Generate video with CogVideoX"""
    request_payload = {
        "model": "cogvideox-5b",
        "prompt": prompt,
        "quality": "quality",  # or "speed"
        "size": "1920x1080",
    }
    if image_url:
        request_payload["image_url"] = image_url
    
    response = client.videos.generations.create(**request_payload)
    task_id = response.id
    
    # Poll
    import time
    while True:
        result = client.videos.retrieve_videos_result(id=task_id)
        if result.task_status == "SUCCESS":
            return result.video_result[0].url
        time.sleep(5)
```

## CogView — Image Generation
```python
def generate_cogview_image(prompt: str, size: str = "1024x1024") -> str:
    response = client.images.generations.create(
        model="cogview-3-plus",
        prompt=prompt,
        size=size,  # "1024x1024", "768x1344", "1344x768"
    )
    return response.data[0].url
```

## Web Search Integration
```python
# GLM with built-in web search tool
def glm_with_search(query: str) -> str:
    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=[{"role": "user", "content": query}],
        tools=[{"type": "web_search", "web_search": {"enable": True}}],
    )
    return response.choices[0].message.content
```

## When to Use Zhipu GLM
- **Chinese market**: Best Chinese language understanding + generation
- **Cost**: GLM-4-Air at ~$0.0007/1K tokens (one of cheapest)
- **Chinese compliance**: Data stays in China if required
- **Multimodal Chinese**: CogView/CogVideo for Chinese visual content
- **Long context**: GLM-4-Long for 1M token Chinese documents
