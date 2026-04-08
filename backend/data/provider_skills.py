"""MAARS Provider Skills Knowledge Base.

Curated prompting best-practices, capability notes, and agent guidance for every
LLM provider available in MAARS.  Injected into agent system prompts at runtime
when a specific provider/model is selected.
"""

PROVIDER_SKILLS: dict[str, dict] = {

    # ── OpenAI ──────────────────────────────────────────────────────────────
    "openai": {
        "display_name": "OpenAI",
        "models": ["gpt-5.2", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini", "o3", "o4", "o4-mini"],
        "strengths": ["instruction following", "tool use", "structured output", "coding", "reasoning"],
        "knowledge": """
## OpenAI Model Guidance

**GPT-5 / GPT-4.1 (frontier reasoning)**
- Exceptional at multi-step planning, code generation, and complex analysis.
- Use `response_format: {"type": "json_object"}` for strict JSON output.
- System prompt: establish role + constraints up front. Be explicit about output format.
- Tool/function calling: define tools with tight schemas; GPT-5 will choose and chain tools reliably.
- Avoid vague instructions — GPT-5 follows literal instructions precisely.

**GPT-4o / GPT-4o-mini (speed + vision)**
- Best for vision tasks: attach images directly in user message.
- GPT-4o-mini: cost-efficient for classification, extraction, summarization.
- Use structured outputs with `strict: true` for guaranteed schema adherence.

**O3 / O4 / O4-mini (reasoning models)**
- Do NOT over-specify reasoning steps — these models reason autonomously.
- Provide the problem clearly; let the model figure out the approach.
- Use for math, logic, long-horizon planning, coding challenges.
- O4-mini: faster + cheaper reasoning; O3: most powerful, use for hardest tasks.
- Avoid `temperature` overrides on reasoning models.

**Universal OpenAI tips**
- Keep system prompts role-focused; avoid duplicating instructions in user turn.
- Use streaming for long outputs to avoid timeout.
- Seed for reproducibility when determinism matters.
- Token-efficient: batch multiple questions in one call rather than separate calls.
""",
    },

    # ── Anthropic ────────────────────────────────────────────────────────────
    "anthropic": {
        "display_name": "Anthropic / Claude",
        "models": ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4.5"],
        "strengths": ["nuanced writing", "long context", "following complex instructions", "safety", "tool use"],
        "knowledge": """
## Anthropic / Claude Model Guidance

**Claude Opus 4.6 (most capable)**
- Use for complex multi-step reasoning, nuanced writing, strategic analysis.
- Enable adaptive thinking: `thinking: {"type": "adaptive"}` for hard problems.
- Excellent at following long, complex system prompts with many constraints.
- XML tags dramatically improve structure: `<context>`, `<task>`, `<format>`, `<examples>`.
- Pass long documents in `<document>` tags; Claude respects them fully.

**Claude Sonnet 4.6 (balanced)**
- Best price/performance for most production tasks.
- Streaming default for all outputs > 500 tokens.
- Reliable tool use with structured `tool_choice` parameter.

**Claude Haiku 4.5 (fast + cheap)**
- Use for classification, extraction, short Q&A, routing decisions.
- Still respects XML structure; keep system prompts concise for speed.

**Universal Claude tips**
- Claude responds best to direct, explicit instructions.
- Use `<thinking>` sections to guide multi-step reasoning.
- For structured output: put schema in system prompt as XML or JSON example.
- Claude is trained to refuse harmful requests — don't fight this, work with it.
- Prefer `Human:/Assistant:` turn structure for legacy prompts.
- Extended context (200K): put reference material first, question last.
""",
    },

    # ── Google Gemini ────────────────────────────────────────────────────────
    "gemini": {
        "display_name": "Google Gemini",
        "models": ["gemini-3-pro", "gemini-3-flash", "gemini-2.5-pro", "gemini-2.5-flash"],
        "strengths": ["multimodal", "long context (1M+)", "code execution", "grounding", "structured output"],
        "knowledge": """
## Google Gemini Model Guidance

**Gemini 3 Pro / 2.5 Pro (flagship)**
- Strongest multimodal model: images, video, audio, documents natively.
- 1M+ token context: pass entire codebases, long PDFs, full conversation histories.
- Use `response_schema` for guaranteed structured JSON output.
- Grounding: enable `google_search_retrieval` for real-time web-grounded answers.
- Code execution: Gemini can run Python in a sandbox — use for data analysis tasks.

**Gemini 3 Flash / 2.5 Flash (fast)**
- Best for latency-sensitive tasks; still multimodal.
- Flash-Lite: cheapest Google option, good for simple tasks.

**Universal Gemini tips**
- System instruction + user role is the correct turn structure.
- Gemini handles interleaved multimodal inputs (text + image + text) naturally.
- For long-context tasks: put the key question at the END of the context.
- Safety settings can be adjusted per category (harassment, hate, etc.).
- Function calling: define tools as OpenAPI schemas.
- Streaming is strongly recommended for large outputs.
""",
    },

    # ── xAI / Grok ───────────────────────────────────────────────────────────
    "xai": {
        "display_name": "xAI / Grok",
        "models": ["grok-3", "grok-3-mini", "grok-2"],
        "strengths": ["real-time info", "humor", "web awareness", "coding", "less restrictive"],
        "knowledge": """
## xAI / Grok Model Guidance

**Grok 3 (flagship)**
- Strong at coding, math, and real-time information (trained on X/Twitter data).
- Less constrained on controversial topics — suitable for creative/edgy tasks.
- Use DeepSearch mode for web-augmented answers.
- Think mode for step-by-step reasoning on hard problems.

**Grok 3 Mini (fast)**
- Cost-efficient; good for quick reasoning and classification.
- Reasoning model: avoid over-specifying steps.

**Universal Grok tips**
- Grok uses an OpenAI-compatible API; function calling works identically to GPT.
- System prompt sets persona; Grok will maintain it consistently.
- Good for social media tone analysis (trained on X data).
- Avoid redundant instructions — Grok follows single clear directives well.
""",
    },

    # ── DeepSeek ─────────────────────────────────────────────────────────────
    "deepseek": {
        "display_name": "DeepSeek",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "strengths": ["coding", "math", "reasoning", "cost efficiency", "Chinese/English bilingual"],
        "knowledge": """
## DeepSeek Model Guidance

**DeepSeek-V3 Chat (general purpose)**
- Exceptional at coding tasks — rivals GPT-5 on most benchmarks.
- Cost: ~10x cheaper than GPT-5 for similar coding quality.
- Bilingual: handles Chinese and English equally well.
- OpenAI-compatible API: same function calling syntax.

**DeepSeek-R1 (reasoning)**
- Chain-of-thought reasoning model; do NOT interrupt its thinking.
- Best for: math proofs, algorithm design, complex logical reasoning.
- Let it generate its full `<think>` block before reading the answer.
- Avoid temperature=0 on R1; slight variance improves reasoning quality.

**Universal DeepSeek tips**
- System prompts work but DeepSeek is more sensitive to user-turn framing.
- For code: specify language, constraints, and expected I/O in the user message.
- JSON output: request explicitly; DeepSeek follows format instructions reliably.
- Very strong at following markdown and structured output formats.
""",
    },

    # ── Mistral ───────────────────────────────────────────────────────────────
    "mistral": {
        "display_name": "Mistral AI",
        "models": ["mistral-large", "mistral-medium", "mistral-small", "codestral", "mistral-nemo"],
        "strengths": ["European GDPR compliance", "function calling", "coding", "multilingual", "efficiency"],
        "knowledge": """
## Mistral AI Model Guidance

**Mistral Large (flagship)**
- Best Mistral model for complex reasoning, multilingual, and tool use.
- Native function calling with strict schema adherence.
- Strong European language support (French, German, Spanish, Italian).
- GDPR-compliant hosting available — ideal for EU data residency requirements.

**Codestral (code specialist)**
- State-of-the-art code completion and generation.
- Supports 80+ programming languages.
- Use for: code review, refactoring, test generation, documentation.
- Fill-in-the-middle (FIM) capability for code completion tasks.

**Mistral Small / Nemo (efficient)**
- Small: best price/quality for classification, extraction, simple Q&A.
- Nemo: Apache 2.0 licensed, deployable anywhere, 128K context.

**Universal Mistral tips**
- Use `[INST]` / `[/INST]` tags for instruct models if using raw API.
- Function calling uses the same OpenAI-compatible schema.
- Mistral responds well to concise, direct system prompts.
- Le Chat integration available for consumer-facing deployments.
""",
    },

    # ── Perplexity ────────────────────────────────────────────────────────────
    "perplexity": {
        "display_name": "Perplexity",
        "models": ["sonar-pro", "sonar", "sonar-reasoning-pro", "sonar-deep-research"],
        "strengths": ["real-time web search", "citations", "research", "current events", "fact checking"],
        "knowledge": """
## Perplexity / Sonar Model Guidance

**Sonar Pro (recommended)**
- Automatically searches the web for every query — always provides current info.
- Returns inline citations with source URLs — ideal for research tasks.
- Do NOT ask Sonar to rely on training data; let it search.
- Best for: market research, competitive analysis, news, fact-checking.

**Sonar Deep Research**
- Multi-step autonomous research agent: searches, reads, synthesizes.
- Use for comprehensive research reports that need 10+ sources.
- Slower but produces thorough, well-cited outputs.

**Sonar Reasoning Pro**
- Combines web search with chain-of-thought reasoning.
- Best for: research questions requiring analysis + synthesis.

**Universal Perplexity tips**
- Frame queries as research questions: "What are the latest developments in X?"
- Citations are returned in `[1]`, `[2]` format with source metadata.
- System prompt: specify output format (bullet points, report, etc.).
- Ideal when agents need real-time competitive or market intelligence.
- Don't use for tasks where web search is undesirable (hallucination risk reduced but adds latency).
""",
    },

    # ── Cohere ────────────────────────────────────────────────────────────────
    "cohere": {
        "display_name": "Cohere",
        "models": ["command-a", "command-r-plus", "command-r"],
        "strengths": ["RAG", "enterprise search", "tool use", "grounding", "embeddings"],
        "knowledge": """
## Cohere Model Guidance

**Command A (latest flagship)**
- Best Cohere model for complex reasoning and enterprise tasks.
- Multi-step tool use with reliable grounding.
- Excellent for RAG pipelines: pass documents as grounding context.

**Command R+ (RAG specialist)**
- Purpose-built for retrieval-augmented generation.
- Use `documents` parameter to pass retrieved chunks — model cites them inline.
- Grounded generation: model distinguishes retrieved facts from trained knowledge.
- 128K context: ideal for long-document Q&A.

**Command R (efficient)**
- Cost-efficient for search and extraction tasks.
- Good multilingual support (10+ languages).

**Universal Cohere tips**
- Use `documents` field (not system prompt) to pass knowledge base content.
- Citations are returned per-sentence with source attribution.
- Connectors API: natively integrates with enterprise search (Elasticsearch, etc.).
- Tool use follows OpenAI-compatible schema.
- Best for enterprise knowledge management and document Q&A use cases.
""",
    },

    # ── Groq ─────────────────────────────────────────────────────────────────
    "groq": {
        "display_name": "Groq",
        "models": ["llama-4-scout", "llama-4-maverick", "llama-3.3-70b"],
        "strengths": ["ultra-low latency", "high throughput", "real-time applications", "streaming"],
        "knowledge": """
## Groq Model Guidance

**Core Advantage: Speed**
- Groq uses custom LPU (Language Processing Unit) silicon — fastest inference available.
- Llama 4 Scout/Maverick on Groq: ~10x faster than same model elsewhere.
- Ideal for: real-time chat, live transcription, interactive agents, low-latency APIs.

**Llama 4 Maverick (most capable on Groq)**
- 128E mixture-of-experts architecture; strong at reasoning and coding.
- Use when you need Llama quality with sub-second response times.

**Llama 4 Scout (efficient)**
- 17B active params; excellent for classification, extraction, routing.
- Very low cost; suitable for high-volume tasks.

**Universal Groq tips**
- OpenAI-compatible API: drop-in replacement, same SDK.
- Best for streaming: first token in <100ms.
- Avoid very long system prompts — keep under 2K tokens for max throughput.
- Rate limits apply; use for interactive/real-time paths, not batch jobs.
- No native tool calling on all models — verify support per model version.
""",
    },

    # ── Cerebras ──────────────────────────────────────────────────────────────
    "cerebras": {
        "display_name": "Cerebras",
        "models": ["cerebras-llama-3.3", "cerebras-llama-3.1"],
        "strengths": ["fastest inference", "wafer-scale chip", "high throughput"],
        "knowledge": """
## Cerebras Model Guidance

**Core Advantage: Wafer-Scale Speed**
- Cerebras CS-3 wafer chip: world-record inference speeds (1800+ tokens/sec).
- Use for: real-time streaming, interactive assistants, live coding help.
- Currently runs Llama 3.x series at unprecedented speed.

**Tips**
- OpenAI-compatible API; standard system/user/assistant turn structure.
- Best suited for tasks where latency is the primary constraint.
- Llama 3.3 70B: good balance of capability and speed on Cerebras hardware.
- Keep prompts focused — high throughput means you can afford more turns.
""",
    },

    # ── Together AI ───────────────────────────────────────────────────────────
    "together": {
        "display_name": "Together AI",
        "models": ["together-llama-4", "together-deepseek-r1"],
        "strengths": ["open-source models", "fine-tuning", "custom deployment", "wide model selection"],
        "knowledge": """
## Together AI Model Guidance

**Platform Strengths**
- Hosts 200+ open-source models: Llama, Mistral, DeepSeek, Qwen, etc.
- Fine-tuning API: customize any hosted model on your data.
- Good for: open-source experimentation, custom model deployment.

**Llama 4 on Together**
- FP8 quantized: excellent quality/cost ratio.
- 128K context; strong multimodal support.

**DeepSeek R1 on Together**
- Full reasoning model with exposed `<think>` blocks.
- Cost-efficient alternative to DeepSeek's own API.

**Tips**
- OpenAI-compatible API.
- Use `repetition_penalty` for open-source models that loop.
- Together is ideal for A/B testing multiple open-source models via one API.
- Custom fine-tune endpoint available for domain-specific agents.
""",
    },

    # ── Fireworks AI ──────────────────────────────────────────────────────────
    "fireworks": {
        "display_name": "Fireworks AI",
        "models": ["fw-llama-4", "fw-deepseek-v3"],
        "strengths": ["fast open-source inference", "compound AI systems", "low cost"],
        "knowledge": """
## Fireworks AI Model Guidance

**Platform Focus**
- Optimized for production open-source model serving.
- FireFunction: fastest function-calling inference for Llama-based models.
- Compound AI: chain multiple models efficiently in one pipeline.

**Models**
- Llama 4 405B: largest Llama variant, strong at complex reasoning.
- DeepSeek V3: cost-efficient coding and analysis.

**Tips**
- OpenAI-compatible API.
- Use FireFunction-v2 for reliable tool calling on open-source models.
- Streaming recommended for all models.
- Grammar-based sampling: force specific output formats without fine-tuning.
""",
    },

    # ── AI21 ──────────────────────────────────────────────────────────────────
    "ai21": {
        "display_name": "AI21 Labs",
        "models": ["jamba-1.6-large", "jamba-1.6-mini"],
        "strengths": ["hybrid Mamba-Transformer", "long context", "document understanding", "low cost"],
        "knowledge": """
## AI21 Labs / Jamba Guidance

**Jamba 1.6 (Mamba-Transformer hybrid)**
- Unique SSM+Transformer architecture: extremely efficient at long-context tasks.
- 256K context window at lower cost than comparable transformers.
- Excellent for: document analysis, long-form summarization, context-heavy Q&A.
- KV-cache efficiency: faster for multi-turn conversations than standard transformers.

**Tips**
- OpenAI-compatible API.
- Best utilized when context length is the bottleneck.
- Jamba Mini: 80% cheaper than Large; good for long-doc extraction tasks.
- Function calling supported.
""",
    },

    # ── SambaNova ─────────────────────────────────────────────────────────────
    "sambanova": {
        "display_name": "SambaNova",
        "models": ["samba-llama-4", "samba-deepseek-r1"],
        "strengths": ["ultra-fast enterprise inference", "reconfigurable dataflow", "on-premise option"],
        "knowledge": """
## SambaNova Model Guidance

**Enterprise Speed Platform**
- SambaNova RDU (Reconfigurable Dataflow Unit): enterprise-grade speed.
- Llama 4 and DeepSeek R1 at production throughput.
- On-premise deployment available for air-gapped environments.

**Tips**
- OpenAI-compatible API.
- Best for enterprise use cases requiring speed + data privacy.
- DeepSeek R1 on SambaNova: reasoning model without data leaving your environment.
- Use streaming for interactive applications.
""",
    },

    # ── NVIDIA ────────────────────────────────────────────────────────────────
    "nvidia": {
        "display_name": "NVIDIA NIM",
        "models": ["nemotron-253b", "nemotron-49b"],
        "strengths": ["enterprise GPU cloud", "NVIDIA-optimized models", "RAG", "agentic AI"],
        "knowledge": """
## NVIDIA NIM Model Guidance

**Nemotron Models**
- NVIDIA-fine-tuned Llama variants optimized for enterprise tasks.
- 253B: most capable; suitable for complex reasoning and knowledge work.
- 49B: efficient; good for structured extraction and classification.
- Optimized for NVIDIA GPU infrastructure: lowest latency on H100/H200.

**NIM Platform**
- Deploy any NIM model on your own NVIDIA GPU infrastructure.
- Supports RAG pipelines via NVIDIA NeMo Retriever.
- Function calling and structured output supported.

**Tips**
- Use for workloads that stay on NVIDIA cloud/on-prem.
- Nemotron is fine-tuned for helpfulness — very instruction-following.
- Context window: 128K tokens.
""",
    },

    # ── Qwen ─────────────────────────────────────────────────────────────────
    "qwen": {
        "display_name": "Alibaba Qwen",
        "models": ["qwen-max", "qwen-3-235b"],
        "strengths": ["Chinese/English bilingual", "coding", "long context", "multimodal", "tool use"],
        "knowledge": """
## Alibaba Qwen Model Guidance

**Qwen 3 235B (flagship)**
- Mixture-of-experts; exceptional at coding and math.
- 128K context; strong Chinese-English bilingual capability.
- Thinking mode: enable for step-by-step reasoning.
- Competitive with GPT-5 on coding benchmarks.

**Qwen Max**
- Best balance of speed and quality in the Qwen family.
- Good at tool use and structured output.

**Tips**
- OpenAI-compatible API.
- For Chinese language tasks: Qwen outperforms most Western models.
- Enable thinking mode (`enable_thinking: true`) for hard problems.
- Strong at code generation across Python, JavaScript, Java, C++.
- Long-context: pass full documents for summarization/extraction.
""",
    },

    # ── Moonshot / Kimi ───────────────────────────────────────────────────────
    "moonshot": {
        "display_name": "Moonshot AI / Kimi",
        "models": ["kimi-latest"],
        "strengths": ["long context (128K)", "Chinese bilingual", "document understanding"],
        "knowledge": """
## Moonshot / Kimi Model Guidance

**Kimi**
- 128K context: pass entire books, codebases, legal documents.
- Strong Chinese-English bilingual.
- Best for: long document Q&A, contract review, research synthesis.

**Tips**
- OpenAI-compatible API.
- Ideal for Chinese-market document tasks.
- Strong at extracting structured data from unstructured long documents.
""",
    },

    # ── Minimax ───────────────────────────────────────────────────────────────
    "minimax": {
        "display_name": "Minimax",
        "models": ["minimax-text-01"],
        "strengths": ["long context (1M tokens)", "Chinese bilingual", "multimodal"],
        "knowledge": """
## Minimax Model Guidance

**MiniMax Text-01**
- 1M token context window — one of the largest available.
- Strong at full-document analysis and very long conversations.
- Chinese-English bilingual.

**Tips**
- Use for tasks requiring extreme context length (full codebase, entire books).
- OpenAI-compatible API.
- Cost-efficient for long-context tasks compared to GPT-5/Claude.
""",
    },

    # ── Hugging Face ──────────────────────────────────────────────────────────
    "huggingface": {
        "display_name": "Hugging Face",
        "models": ["175,000+ open-source models"],
        "strengths": ["open-source", "fine-tuning", "specialized models", "full control", "privacy"],
        "knowledge": """
## Hugging Face Model Guidance

**Platform Overview**
- 175,000+ models covering every task: NLP, vision, audio, multimodal.
- Inference API: run any model via simple HTTP call.
- Serverless inference: no infra management for standard models.

**Best Practices**
- Match model to task: use task-specific fine-tuned models for best results.
  - Summarization: `facebook/bart-large-cnn`, `philschmid/bart-large-cnn-samsum`
  - Classification: `cardiffnlp/twitter-roberta-base-sentiment`
  - Code: `bigcode/starcoder2-15b`, `Salesforce/codegen-16B-mono`
  - Embeddings: `BAAI/bge-large-en-v1.5`, `sentence-transformers/*`

**Tips**
- Use Inference Endpoints for production (dedicated compute).
- Transformers pipeline API for local fine-tuned models.
- For MAARS: use HF as fallback for specialized tasks (sentiment, NER, classification).
- Privacy: run sensitive data on self-hosted HF models.
""",
    },

    # ── Hyperbolic ────────────────────────────────────────────────────────────
    "hyperbolic": {
        "display_name": "Hyperbolic",
        "models": ["hyperbolic-llama", "hyperbolic-deepseek"],
        "strengths": ["decentralized GPU", "low cost", "open-source models"],
        "knowledge": """
## Hyperbolic Model Guidance

**Decentralized GPU Marketplace**
- Aggregates GPU compute from distributed providers.
- Runs Llama, DeepSeek, and other open-source models.
- Often cheapest option for open-source inference.

**Tips**
- OpenAI-compatible API.
- Good for: budget-conscious, high-volume open-source tasks.
- Variable latency (decentralized); not ideal for real-time interactive use.
""",
    },

    # ── Inception / Mercury ───────────────────────────────────────────────────
    "inception": {
        "display_name": "Inception AI",
        "models": ["mercury"],
        "strengths": ["diffusion LLM", "parallel decoding", "fast generation"],
        "knowledge": """
## Inception AI / Mercury Guidance

**Mercury (Diffusion LLM)**
- Novel architecture: diffusion-based language model, not autoregressive.
- Parallel token generation: extremely fast for fixed-length outputs.
- Best for: structured generation, form filling, template completion.

**Tips**
- Specify output length explicitly; Mercury optimizes for fixed-size outputs.
- Good for classification and structured extraction tasks.
- OpenAI-compatible API.
""",
    },

    # ── Lambda Labs ───────────────────────────────────────────────────────────
    "lambda": {
        "display_name": "Lambda Labs",
        "models": ["lambda-llama-3.3"],
        "strengths": ["research GPU cloud", "Llama models", "academic use"],
        "knowledge": """
## Lambda Labs Guidance

**Platform**
- GPU cloud focused on ML researchers and AI developers.
- Runs Llama 3.3 and other open-source models.
- OpenAI-compatible API.

**Tips**
- Good for: development, testing, research workloads.
- Cost-competitive for A100/H100 compute.
""",
    },

    # ── Lepton AI ─────────────────────────────────────────────────────────────
    "lepton": {
        "display_name": "Lepton AI",
        "models": ["lepton-llama", "lepton-mistral"],
        "strengths": ["serverless AI", "fast deployment", "Python SDK"],
        "knowledge": """
## Lepton AI Guidance

**Serverless AI Platform**
- Deploy open-source models serverlessly in seconds.
- Strong Python SDK; easy integration.
- Good for: prototyping, production APIs, custom model serving.

**Tips**
- OpenAI-compatible API.
- Use for quickly deploying fine-tuned models to production.
""",
    },

    # ── Novita AI ─────────────────────────────────────────────────────────────
    "novita": {
        "display_name": "Novita AI",
        "models": ["novita-llama", "novita-mistral"],
        "strengths": ["affordable open-source", "image generation", "multi-modal"],
        "knowledge": """
## Novita AI Guidance

**Platform**
- Aggregates open-source LLM and image generation models.
- Very cost-competitive for bulk/batch processing.
- OpenAI-compatible API.

**Tips**
- Best for: high-volume, cost-sensitive batch tasks.
- Combine LLM + image generation in one platform.
""",
    },

    # ── Upstage ───────────────────────────────────────────────────────────────
    "upstage": {
        "display_name": "Upstage",
        "models": ["solar-pro"],
        "strengths": ["document AI", "OCR", "Korean/English bilingual", "enterprise"],
        "knowledge": """
## Upstage / Solar Guidance

**Solar Pro**
- Enterprise document AI: OCR, layout analysis, document parsing.
- Strong Korean-English bilingual capability.
- Document Parse: extract structured data from PDFs, scanned docs.

**Tips**
- Best for: document processing pipelines, Korean-language tasks.
- Document API: pass raw documents for structured extraction.
- OpenAI-compatible chat API for Solar LLM.
""",
    },

    # ── Writer ────────────────────────────────────────────────────────────────
    "writer": {
        "display_name": "Writer",
        "models": ["palmyra-x5", "palmyra-x4"],
        "strengths": ["enterprise writing", "brand voice", "compliance", "no hallucination"],
        "knowledge": """
## Writer / Palmyra Guidance

**Palmyra X5 (flagship)**
- Purpose-built for enterprise writing: marketing, legal, finance.
- Strong at maintaining brand voice and style guides.
- No hallucination mode: grounded generation from provided documents.
- HIPAA, SOC 2 compliant.

**Tips**
- Best for: B2B content, marketing copy, legal drafting, compliance docs.
- Pass brand guidelines in system prompt for consistent voice.
- Use no-hallucination mode for regulated content.
- Integrate style guide directly into system prompt for brand consistency.
""",
    },

    # ── Arcee AI ──────────────────────────────────────────────────────────────
    "arcee": {
        "display_name": "Arcee AI",
        "models": ["arcee-agent", "arcee-nova"],
        "strengths": ["small efficient models", "fine-tuning", "on-device", "merging"],
        "knowledge": """
## Arcee AI Guidance

**Specialized Efficient Models**
- Arcee specializes in small, highly capable models via model merging.
- Arcee Agent: purpose-built for agentic tasks and tool use.
- SuperNova: merged model combining multiple open-source models.

**Tips**
- Use Arcee Agent for reliable tool calling at low cost.
- Model merging: Arcee can combine multiple fine-tuned models into one.
- Good for: on-device deployment, cost-sensitive agentic pipelines.
""",
    },

    # ── Amazon Bedrock ────────────────────────────────────────────────────────
    "amazon": {
        "display_name": "Amazon Bedrock",
        "models": ["nova-pro", "nova-lite", "titan"],
        "strengths": ["AWS integration", "enterprise compliance", "multi-model", "VPC deployment"],
        "knowledge": """
## Amazon Bedrock Guidance

**Amazon Nova Pro / Lite**
- Nova Pro: strong at multimodal reasoning and agentic tasks.
- Nova Lite: cost-optimized for text and light multimodal tasks.
- Native AWS integration: IAM, VPC, CloudWatch, S3.

**Bedrock Advantages**
- SOC 2, HIPAA, PCI-DSS compliant by default.
- Model access: Claude, Llama, Mistral, Cohere all via single Bedrock API.
- Agents for Bedrock: native agent orchestration with Lambda tools.
- Knowledge Bases: managed RAG with S3, OpenSearch.

**Tips**
- Use for AWS-native architectures requiring compliance.
- Bedrock Agents: orchestrate multi-step tasks with Lambda function tools.
- Pass context via Knowledge Base rather than long system prompts.
""",
    },

    # ── Yi ────────────────────────────────────────────────────────────────────
    "yi": {
        "display_name": "01.AI / Yi",
        "models": ["yi-large", "yi-medium"],
        "strengths": ["Chinese bilingual", "long context", "efficient"],
        "knowledge": """
## 01.AI / Yi Guidance

**Yi Models**
- Yi Large: 200K context; strong bilingual Chinese-English.
- Yi Medium: efficient, good for everyday tasks.

**Tips**
- OpenAI-compatible API.
- Best for Chinese-language enterprise tasks requiring long context.
""",
    },

    # ── Zhipu AI ──────────────────────────────────────────────────────────────
    "zhipu": {
        "display_name": "Zhipu AI / GLM",
        "models": ["glm-4", "glm-4v"],
        "strengths": ["Chinese enterprise", "multimodal", "code", "tool use"],
        "knowledge": """
## Zhipu AI / GLM Guidance

**GLM-4**
- Leading Chinese enterprise LLM; strong tool use and code generation.
- GLM-4V: multimodal variant with image understanding.
- Native Chinese-language optimization for business tasks.

**Tips**
- OpenAI-compatible API.
- Best for: Chinese-market enterprise, customer service, document tasks.
- Function calling supported; use for structured agentic workflows.
""",
    },

    # ── Doubao ────────────────────────────────────────────────────────────────
    "doubao": {
        "display_name": "ByteDance / Doubao",
        "models": ["doubao-pro", "doubao-lite"],
        "strengths": ["Chinese social content", "creative writing", "cost efficiency"],
        "knowledge": """
## ByteDance Doubao Guidance

**Doubao Pro**
- ByteDance's enterprise LLM; trained on vast Chinese internet data.
- Strong at social media content, creative writing, marketing copy.
- Very cost-efficient for high-volume Chinese-language tasks.

**Tips**
- Best for: Chinese content generation, social media, marketing.
- OpenAI-compatible API.
""",
    },

    # ── Llama API ─────────────────────────────────────────────────────────────
    "llama": {
        "display_name": "Meta Llama API",
        "models": ["llama-4-scout", "llama-4-maverick"],
        "strengths": ["open weights", "Meta-official API", "multimodal", "tool use"],
        "knowledge": """
## Meta Llama API Guidance

**Official Meta API**
- Direct from Meta; uses official Llama 4 weights.
- Llama 4 Maverick: 128E MoE; strong multimodal and reasoning.
- Llama 4 Scout: efficient 17B active params; fast for most tasks.

**Tips**
- OpenAI-compatible API.
- Llama 4 has native image understanding.
- Best for: open-source-aligned workloads, no vendor lock-in.
- Tool calling supported in Llama 4 series.
""",
    },
}


def get_provider_knowledge(provider: str) -> str:
    """Return the knowledge block for a given provider name."""
    entry = PROVIDER_SKILLS.get(provider.lower())
    if not entry:
        return ""
    return entry["knowledge"].strip()


def get_provider_recommendations(agent: dict) -> list[str]:
    """Return dynamically matched providers for any agent dict.

    Uses keyword matching on role/description/capabilities — works for all
    458 default agents and any custom agent regardless of agent_id.
    Delegates to services.skills_service to avoid circular imports.
    """
    from services.skills_service import match_providers_for_agent
    return match_providers_for_agent(agent)
