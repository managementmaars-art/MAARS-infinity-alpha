# Provider Allies — Full Intel

Live per-provider identification as of 2026-04-19. **1,313 models** reachable across 26 active providers on current keys. Ordered by strategic role so the smart router can pick the right ally for the right job.

---

## Tier 1 — Free / near-free workhorses (route cheap/quota-friendly traffic here FIRST)

### Groq — 16 models · FREE tier
**Unique superpower**: sub-300ms inference on OSS models via custom LPU hardware.
- `llama-3.1-8b-instant` (current smoke model, ~420ms wall)
- `meta-llama/llama-4-scout-17b-16e-instruct`, `llama-4-maverick-17b-128e-instruct`
- `mixtral-8x7b-instruct-v0.1`, `llama-guard-3-8b` (safety)
- Audio: `whisper-large-v3`, `whisper-large-v3-turbo` (free ASR)
- TTS: `canopylabs/orpheus-v1-english`
- Kimi: `moonshotai/kimi-k2.5` (hosted on Groq infra)
- **Rate limit**: 30 RPM / 6000 TPM free. Paid tier lifts to 600+ RPM.
- **Use for**: chat, long completions, real-time voice ASR, safety filtering.

### Cerebras — 4 models · FREE tier
**Unique superpower**: ~1,800 tokens/sec — fastest inference on the planet by ~4×.
- `qwen-3-235b-a22b-instruct-2507` (flagship, reasoning)
- `zai-glm-4.7` (GLM family)
- `llama3.1-8b`, `llama-3.3-70b`
- **Rate limit**: 1 req/sec free, 30 RPM Pro
- **Use for**: real-time streaming chat where latency > model quality.

### SambaNova — 8 models · FREE tier
**Unique superpower**: RDU chip — DeepSeek R1/V3 at fastest latency of any host.
- `DeepSeek-V3.1`, `DeepSeek-V3.1-cb`, `DeepSeek-V3.2`
- `Meta-Llama-3.3-70B-Instruct` (current smoke model)
- `Meta-Llama-3.1-405B-Instruct`, `Llama-4-Maverick`
- **Use for**: highest-quality OSS reasoning without the OpenAI/Anthropic markup.

### Google Gemini — 50 models · generous FREE tier
**Unique superpower**: huge 1M-2M context + native multimodal (images, audio, video, code).
- `gemini-2.5-flash` (current smoke — fastest)
- `gemini-2.5-pro` (best quality)
- `gemini-2.0-flash`, `gemini-2.0-flash-lite` (cheapest tier)
- `gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-preview-tts` (TTS!)
- `gemma-3-1b-it` through `gemma-3-27b-it` (open weights)
- `embedding-001`, `text-embedding-004` (free embeddings)
- **Rate limit**: 15 RPM free on flash; 2 RPM on pro
- **Use for**: long-context RAG, video/image understanding, free embeddings.

### HuggingFace Router — 118 models · included with key
**Unique superpower**: meta-gateway to every open model hosted on HF Inference Endpoints + Inference Providers.
- `MiniMaxAI/MiniMax-M2.7`, `google/gemma-4-31B-it`, `google/gemma-4-26B-A4B-it`
- `Qwen/Qwen3.5-9B`, `moonshotai/Kimi-K2.5`
- Also: Zephyr, Mixtral, Llama variants, Falcon, Phi-3
- **Use for**: trying new open models the moment they're released.

### OpenRouter — 342 models · 28 are `:free`
**Unique superpower**: single-key access to every commercial + open model, with :free fallback tier.
- Free models live: `openai/gpt-oss-120b:free` (current smoke), `openai/gpt-oss-20b:free`, `google/gemma-3-27b-it:free`, `meta-llama/llama-3.3-70b-instruct:free`, `deepseek/deepseek-r1:free`, `z-ai/glm-4.5-air:free`, `nousresearch/hermes-3-llama-3.1-405b:free`, `qwen/qwen3-coder:free`, `arcee-ai/trinity-large-preview:free`, `nvidia/nemotron-*-free`
- Paid passthroughs: `anthropic/claude-opus-4.7`, `anthropic/claude-sonnet-4-6`, every xAI/Groq/Together model
- **Use for**: fallback when your direct provider is rate-limited; access to models you don't have direct keys for.

### Bytez — free tier `sm` models
**Unique superpower**: proxies to 5,000+ HuggingFace models with unified auth. Free on small variants.
- Currently working: `microsoft/DialoGPT-small` (smoke OK)
- Upgrade path: paid tier unlocks `lg`, `xl` variants of same model families
- Custom auth: `Authorization: Key <key>` (not Bearer)
- URL pattern: `/models/v2/{model_id}` (unusual — not OpenAI-compatible)
- **Use for**: experimentation, obscure HF models, cheap dev/test.

---

## Tier 2 — Premium paid with broad catalogs

### OpenAI — 120 models · $20 balance
**Unique superpower**: state-of-the-art across every modality + ecosystem standard.
- Text: GPT-4.1 family, GPT-5 (if available), O-series (o3, o4-mini = reasoning)
- Vision: GPT-4 Vision, GPT-5 Vision
- Image: DALL-E 3, GPT-Image 1
- Audio: Whisper (ASR), TTS-1/TTS-1-HD
- Embeddings: text-embedding-3-small / -large
- Tools: code-interpreter, function calling
- **Use for**: default fallback, function-calling-heavy agents, embeddings.

### Anthropic — 9 models · $20 balance
**Unique superpower**: best-in-class instruction following + safety + long-context tool use.
- **Claude Opus 4.7** (latest flagship, highest quality)
- Claude Sonnet 4.6, Claude Opus 4.6
- Claude Opus 4.5 / Sonnet 4.5 / Haiku 4.5 (current smoke model)
- Claude Opus 4.1 / Opus 4 / Sonnet 4
- 200K context, vision, tool use, computer-use API
- **Use for**: code generation, complex multi-step agents, computer-use automation.

### Together AI — 234 models · $5 balance
**Unique superpower**: largest OSS catalog — every significant open model is hosted here.
- Text: Llama 3.3 70B/8B, Llama 4 Scout/Maverick, DeepSeek V3/R1, Qwen 2.5 / 3 / 3.5, GLM-5.1, Gemma 4
- Image: FLUX.1 family (schnell, pro, max, kontext), FLUX.2 family, Seedream 3/4, Juggernaut
- Video: Veo 3.0 (Google), Kling 1.6 Pro / 2.1 Master, Vidu Q1, Wan2.6
- Audio/ASR: Parakeet (NVIDIA)
- Image LLM: GPT-Image-1.5 (OpenAI-hosted here)
- **77 zero-priced chat models** — free once balance > $0 (free models still need account in good standing)
- **Use for**: any OSS model not directly hosted elsewhere; image/video generation pipelines.

### NVIDIA NIM — 133 models · FREE tier
**Unique superpower**: NVIDIA's curated best-of-OSS + their own Nemotron family.
- `meta/llama-3.1-8b-instruct` (current smoke model), Llama 3.3 70B / 405B
- `nvidia/nemotron-3-super-120b` (flagship reasoner), `nemotron-ultra-253b`
- Vision: `adept/fuyu-8b`, `nvidia/vila-13b`
- Code: `nvidia/code-sage-gpu`, `abacusai/dracarys-llama-3.1-70b`
- Also: `01-ai/yi-large` (Chinese flagship), `mistralai/mixtral-8x22b`
- **Use for**: diverse model access with free-tier generosity; vision-language tasks.

---

## Tier 3 — Specialized excellence

### Mistral — 62 models · $5 balance
**Unique superpower**: European sovereignty + best small-model quality.
- Flagship: `mistral-large-latest`, `mistral-medium-2505/2508`, `mistral-small-latest` (current smoke)
- Code specialist: `codestral-latest` (Mistral's Copilot-class)
- Embeddings: `mistral-embed`
- Vision: `pixtral-12b-2409`, `pixtral-large-latest`
- Audio: `voxtral-small-2507`, `voxtral-mini-2507`
- Moderation: `mistral-moderation-latest`
- **Use for**: EU-compliant routing, code-specific tasks (Codestral), cheap small-model workloads.

### DeepSeek — 2 models · $19.99 balance (live API)
**Unique superpower**: best cost/quality ratio in AI right now. $0.27/$1.10 per M tokens.
- `deepseek-chat` (V3.2 — general chat, current smoke)
- `deepseek-reasoner` (R1 — chain-of-thought, matches O1)
- 128K context, tool use, JSON mode
- Live balance API (Tier-1 — real $ visible)
- **Use for**: high-volume reasoning on a budget. Near-frontier quality at 1/20th the price.

### Cohere — 20 models · $5 balance
**Unique superpower**: best multilingual + enterprise RAG infrastructure.
- `command-r-plus-08-2024` (current smoke — RAG-tuned)
- `command-a-03-2025` (latest flagship)
- `c4ai-aya-expanse-32b` + `aya-vision-32b` (101-language model)
- `cohere-transcribe-03-2026` (ASR)
- Embed: `embed-v4.0` (multilingual, best-in-class)
- Rerank: `rerank-v3.5` (the reranker that beat everyone in MTEB)
- **Use for**: multilingual apps (Aya), RAG reranking pipelines, multilingual embeddings.

### xAI (Grok) — 14 models · $25 free credit (live)
**Unique superpower**: real-time X/Twitter integration + willingness to answer edgy questions.
- `grok-4-0709` (latest, reasoning)
- `grok-3` (general), `grok-3-mini` (current smoke)
- `grok-2-vision-1212`, `grok-vision-beta` (vision)
- `grok-2-image-1212` (image gen)
- **Use for**: queries that need live web/X data, multimodal with current events.

### Perplexity Sonar — 5 models · $5 balance
**Unique superpower**: search-native LLMs with citation tracking.
- `sonar` (current smoke — base search)
- `sonar-pro` (longer answers, 200K context)
- `sonar-reasoning` (chain-of-thought + search)
- `sonar-reasoning-pro`
- `sonar-deep-research` (autonomous multi-step research)
- **Use for**: any query that needs fresh web data with citations.

### Upstage Solar — 22 models · $10 balance
**Unique superpower**: best-in-class Korean + OCR + document extraction.
- `solar-pro` (current smoke — flagship chat)
- `solar-mini`, `solar-mini-250422`
- Document AI: `document-parse`, `information-extraction`, `layout-analysis`
- **Use for**: Korean-language apps, PDF/document extraction pipelines.

### AI21 Jamba — 2 models · $10 balance
**Unique superpower**: Mamba-Transformer hybrid — 256K context at lower cost than Transformer-only.
- `jamba-large-1.7-2025-07` (flagship)
- `jamba-mini-2-2026-01` (current smoke — budget-friendly)
- **Use for**: long-document tasks where OpenAI/Anthropic are too pricey.

### Zhipu GLM (Z.ai) — 7 models · $0 (free tier)
**Unique superpower**: Chinese frontier + cheapest GLM-4.6-level quality.
- `glm-4.5-flash` (current smoke — free tier, ~1800ms)
- `glm-4.5`, `glm-4.5-air`, `glm-4.6`
- **Use for**: Chinese-language tasks, cheap reasoning (GLM-4.6 ~= GPT-4-mini quality).

### Moonshot Kimi — 13 models · $15 balance (live API via Tier-1)
**Unique superpower**: 128K-2M context window leader + thinking mode.
- `kimi-k2-thinking-turbo` (flagship reasoning)
- `kimi-k2-turbo-preview` (current smoke — fast)
- `kimi-k2-0711-preview`
- **Use for**: ultra-long-context analysis (full codebases, book-length documents).

### MiniMax — $5 balance
**Unique superpower**: multimodal (text + video + voice) at low cost.
- `MiniMax-Text-01` (current smoke)
- `MiniMax-VL-01` (vision-language)
- Video: `MiniMax-Video-01` (ready)
- Voice: `MiniMax-Voice` (cloning, TTS)
- **Use for**: unified text+video+voice pipelines without gluing 3 vendors.

---

## Tier 4 — Ultra-specialized

### Writer Palmyra — 8 models · $0 (trial credits)
**Unique superpower**: enterprise-tuned for marketing/content + vertical specialists.
- `palmyra-x5` (current smoke — flagship)
- `palmyra-x4`, `palmyra-creative` (marketing copy)
- `palmyra-med` (medical — compliance-aware)
- `palmyra-fin` (finance)
- **Use for**: enterprise content gen with compliance/industry constraints.

### Arcee — 3 models · $5 balance
**Unique superpower**: distillation specialist — Trinity models are small but punch above weight.
- `trinity-mini` (current smoke — $0.045/M tokens, super cheap)
- `trinity-large-preview`, `trinity-large-thinking`
- **Use for**: ultra-cheap high-volume tasks where GPT-3.5 was overkill.

### Inception Mercury — 5 models · $0 (free trial)
**Unique superpower**: **diffusion LLMs** — fundamentally different architecture, 5-10× faster than Transformers.
- `mercury-2` (current smoke — flagship text)
- `mercury-edit-2` (code editing)
- `mercury-coder` (code completion)
- **Use for**: latency-critical code completion, any task where even Cerebras isn't fast enough.

### Hyperbolic — 5 models · $5 balance
**Unique superpower**: GPU rental + cheap serverless. Same model, half the Together price.
- `deepseek-ai/DeepSeek-V3-0324`, `DeepSeek-R1`, `DeepSeek-R1-0528`
- `meta-llama/Llama-3.3-70B-Instruct` (current smoke)
- `Qwen/Qwen3-Coder-480B-A35B-Instruct` (huge coder model)
- **Use for**: heavy OSS models at cheaper price than Together/Fireworks.

### Fireworks AI — 12 models · $6 balance
**Unique superpower**: fastest serverless OSS (fireworks-v1 optimized inference).
- `accounts/fireworks/models/deepseek-v3p2` (current smoke)
- `accounts/fireworks/models/kimi-k2p5`
- `accounts/fireworks/models/minimax-m2p7`
- Fine-tune support, function calling, JSON mode
- **Use for**: serverless OSS with fine-tuning + speed.

### ElevenLabs — 10 models (media-only)
**Unique superpower**: best-in-class TTS — voice cloning, multilingual, emotional range.
- `eleven_v3` (newest — dialog & emotion)
- `eleven_multilingual_v2`, `eleven_flash_v2_5` (speed)
- 10,000-character free tier
- **Use for**: any voice-out in the product.

---

## Strategic routing cheat sheet

| Task | 1st choice | Fallback | Why |
|---|---|---|---|
| **Chat — cheap volume** | DeepSeek `chat` | Zhipu `glm-4.5-flash` | $0.27/M vs $0.60/M |
| **Chat — frontier quality** | Anthropic `opus-4.7` | OpenAI `gpt-5` | Best instruction following |
| **Chat — fastest** | Cerebras `qwen-3-235b` | Groq `llama-3.1-8b` | 1800 tok/sec |
| **Chat — longest context** | Moonshot `kimi-k2-thinking` | Gemini `2.5-pro` | 2M tokens |
| **Reasoning / math** | DeepSeek `reasoner` | OpenAI `o3` / Grok `grok-4` | R1 quality at 5% of o-series cost |
| **Code generation** | Anthropic `opus-4.7` | Mistral `codestral` | Claude still leads on code |
| **Code completion (latency)** | Inception `mercury-coder` | Cerebras `llama-3.1-8b` | Diffusion LLM = 5× faster |
| **Vision — image Q&A** | Gemini `2.5-flash` | Anthropic `claude-opus` | Gemini's vision is free tier |
| **Multilingual** | Cohere `aya-expanse-32b` | Gemini `2.5-pro` | 101 languages native |
| **Web search** | Perplexity `sonar-pro` | xAI `grok-4` + web tool | Native citations |
| **Image gen** | Together `FLUX.1-schnell` | OpenAI `dall-e-3` | FLUX free-priced |
| **Video gen** | Together `veo-3.0-fast-audio` | MiniMax `MiniMax-Video-01` | Veo 3 + audio included |
| **TTS** | ElevenLabs `eleven_flash` | OpenAI `tts-1-hd` | Quality leader |
| **ASR / transcription** | Groq `whisper-large-v3-turbo` | Cohere `transcribe-03-2026` | Free + fast |
| **Embeddings** | Cohere `embed-v4.0` (multilingual) | OpenAI `text-embedding-3-small` | Embed v4 tops MTEB |
| **Rerank (RAG)** | Cohere `rerank-v3.5` | — | Nobody else is close |
| **Free fallback** | OpenRouter `gpt-oss-120b:free` | Groq `llama-3.1-8b` | Zero-cost spillover |

---

## Action items the router isn't yet exploiting

1. **OpenRouter `:free` models** — 28 models available. Router should prefer these over paid calls for non-critical tasks.
2. **Together zero-priced chat** — 77 models at $0 input/output with balance > 0. Pair with smart_router cost weight.
3. **Cohere rerank** — not integrated yet. Huge RAG quality upgrade at negligible cost.
4. **Perplexity Sonar for web tasks** — chats that need fresh info should auto-route to Sonar instead of augmenting another model with web-search tools.
5. **Inception Mercury for code** — latency-gated tasks (live editor, completions) should try mercury-coder first.
6. **Gemini embeddings (free)** — replace paid OpenAI embedding calls where Gemini's quality is sufficient.
7. **Groq/Cerebras whisper** — free ASR across 99 languages, currently unused.
