---
name: maars-llm-routing
description: MAARS multi-provider LLM routing — 33 providers, 609+ models, smart alias routing, budget-aware selection, fallback chains, and the universal maars-sk key system
---

# MAARS LLM Routing System

## Architecture Overview
```
User Request → Router Engine → Provider Selection → Model Call → Response
                    ↓
              Budget Controller
              Trust Scoring
              Circuit Breaker
              Fallback Chain
```

## Provider Registry (33 Providers)
```python
PROVIDERS = {
    # Frontier
    "openai":      {"base_url": "https://api.openai.com/v1",          "key": "OPENAI_API_KEY"},
    "anthropic":   {"base_url": "https://api.anthropic.com",           "key": "ANTHROPIC_API_KEY"},
    "google":      {"base_url": "https://generativelanguage.googleapis.com", "key": "GOOGLE_API_KEY"},
    "xai":         {"base_url": "https://api.x.ai/v1",                "key": "XAI_API_KEY"},
    # Cost-efficient
    "deepseek":    {"base_url": "https://api.deepseek.com/v1",         "key": "DEEPSEEK_API_KEY"},
    "mistral":     {"base_url": "https://api.mistral.ai/v1",           "key": "MISTRAL_API_KEY"},
    "groq":        {"base_url": "https://api.groq.com/openai/v1",      "key": "GROQ_API_KEY"},
    "cerebras":    {"base_url": "https://api.cerebras.ai/v1",          "key": "CEREBRAS_API_KEY"},
    "together":    {"base_url": "https://api.together.xyz/v1",         "key": "TOGETHER_API_KEY"},
    # Specialized
    "perplexity":  {"base_url": "https://api.perplexity.ai",           "key": "PERPLEXITY_API_KEY"},
    "cohere":      {"base_url": "https://api.cohere.com/v1",           "key": "COHERE_API_KEY"},
    "nvidia":      {"base_url": "https://integrate.api.nvidia.com/v1", "key": "NVIDIA_API_KEY"},
    "sambanova":   {"base_url": "https://api.sambanova.ai/v1",         "key": "SAMBANOVA_API_KEY"},
    "fireworks":   {"base_url": "https://api.fireworks.ai/inference/v1","key": "FIREWORKS_API_KEY"},
    "hyperbolic":  {"base_url": "https://api.hyperbolic.xyz/v1",       "key": "HYPERBOLIC_API_KEY"},
    "novita":      {"base_url": "https://api.novita.ai/v3/openai",     "key": "NOVITA_API_KEY"},
    "lepton":      {"base_url": "https://api.lepton.ai/api/v1",        "key": "LEPTON_API_KEY"},
    "lambda":      {"base_url": "https://api.lambdalabs.com/v1",       "key": "LAMBDA_API_KEY"},
    # HuggingFace
    "huggingface": {"base_url": "https://api-inference.huggingface.co/","key": "HF_API_KEY"},
    # Asian providers
    "qwen":        {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "key": "QWEN_API_KEY"},
    "moonshot":    {"base_url": "https://api.moonshot.cn/v1",          "key": "MOONSHOT_API_KEY"},
    "zhipu":       {"base_url": "https://open.bigmodel.cn/api/paas/v4","key": "ZHIPU_API_KEY"},
    "doubao":      {"base_url": "https://ark.cn-beijing.volces.com/api/v3","key": "DOUBAO_API_KEY"},
    "minimax":     {"base_url": "https://api.minimax.chat/v1",         "key": "MINIMAX_API_KEY"},
    "upstage":     {"base_url": "https://api.upstage.ai/v1",           "key": "UPSTAGE_API_KEY"},
    "inception":   {"base_url": "https://api.inceptionlabs.ai/v1",    "key": "INCEPTION_API_KEY"},
    "arcee":       {"base_url": "https://conductor.arcee.ai/v1",       "key": "ARCEE_API_KEY"},
    "ai21":        {"base_url": "https://api.ai21.com/studio/v1",      "key": "AI21_API_KEY"},
    "writer":      {"base_url": "https://api.writer.com/v1",           "key": "WRITER_API_KEY"},
    # Cloud
    "bedrock":     {"base_url": "https://bedrock-runtime.us-east-1.amazonaws.com", "key": "AWS_BEDROCK"},
    "meta":        {"base_url": "https://api.llama.com/v1",            "key": "META_API_KEY"},
    # Media
    "elevenlabs":  {"base_url": "https://api.elevenlabs.io/v1",        "key": "ELEVENLABS_API_KEY"},
    "stabilityai": {"base_url": "https://api.stability.ai/v2beta",     "key": "STABILITY_API_KEY"},
}
```

## Smart Aliases (maars/ prefix)
```python
MAARS_ALIASES = {
    "maars/auto":       ("openai",   "gpt-4o"),           # best general
    "maars/fast":       ("groq",     "llama-4-scout-17b-16e-instruct"),  # lowest latency
    "maars/smart":      ("openai",   "gpt-5.2"),           # best quality
    "maars/code":       ("anthropic","claude-sonnet-4-6"), # best coding
    "maars/reason":     ("openai",   "o3"),                # deep reasoning
    "maars/cheap":      ("deepseek", "deepseek-chat"),     # lowest cost
    "maars/search":     ("xai",      "grok-3"),            # real-time web
    "maars/vision":     ("openai",   "gpt-4o"),            # image understanding
    "maars/long":       ("anthropic","claude-opus-4-6"),   # longest context
    "maars/creative":   ("anthropic","claude-sonnet-4-6"), # creative tasks
    "maars/research":   ("perplexity","sonar-pro"),        # research + citations
}
```

## Router Engine Logic
```python
# backend/router/engine.py
async def route_request(
    model: str,
    messages: list,
    agent_id: str,
    budget_remaining: float,
    task_type: str,
) -> tuple[str, str]:  # (provider, model_name)
    
    # 1. Resolve alias
    if model.startswith("maars/"):
        provider, model_name = MAARS_ALIASES[model]
        return provider, model_name
    
    # 2. Budget enforcement
    if budget_remaining < 0.001:
        return "deepseek", "deepseek-chat"  # cheapest fallback
    
    # 3. Task-based routing
    if task_type == "voice":
        return "elevenlabs", "eleven_turbo_v2_5"
    if task_type == "search":
        return "xai", "grok-3"
    if task_type == "code":
        return "anthropic", "claude-sonnet-4-6"
    
    # 4. Default
    return "openai", "gpt-4o"
```

## Fallback Chain
```python
FALLBACK_CHAINS = {
    "openai":    ["anthropic", "google", "deepseek"],
    "anthropic": ["openai",    "google", "deepseek"],
    "google":    ["openai",    "anthropic", "groq"],
    "groq":      ["together",  "fireworks", "deepseek"],
    "xai":       ["perplexity","openai", "google"],
}

async def call_with_fallback(provider, model, messages, **kwargs):
    try:
        return await call_provider(provider, model, messages, **kwargs)
    except (RateLimitError, ServiceUnavailableError):
        for fallback in FALLBACK_CHAINS.get(provider, []):
            try:
                fallback_model = get_default_model(fallback)
                return await call_provider(fallback, fallback_model, messages, **kwargs)
            except Exception:
                continue
        raise Exception("All providers failed")
```

## Universal Client (for OpenAI-compatible providers)
```python
from openai import AsyncOpenAI

def get_client(provider: str) -> AsyncOpenAI:
    cfg = PROVIDERS[provider]
    return AsyncOpenAI(
        base_url=cfg["base_url"],
        api_key=os.getenv(cfg["key"], ""),
    )

async def universal_chat(provider, model, messages, **kwargs):
    client = get_client(provider)
    return await client.chat.completions.create(
        model=model, messages=messages, **kwargs
    )
```

## Cost Tracking
```python
# After every LLM call
await budget_controller.record_usage(
    agent_id=agent_id,
    provider=provider,
    model=model,
    input_tokens=usage.prompt_tokens,
    output_tokens=usage.completion_tokens,
    cost_usd=calculate_cost(provider, model, usage),
)
```
