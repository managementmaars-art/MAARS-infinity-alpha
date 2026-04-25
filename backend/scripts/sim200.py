"""200-prompt client simulation across 8 realistic categories.
Fires through services.llm_gateway.complete() with maars/auto (free-first smart
router + client-opacity). Runs concurrent batches of 6 to respect free-tier RPM.
"""
import asyncio, sys, time, random
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(str(__import__("pathlib").Path(__file__).resolve().parent.parent.parent / ".env"))

USER_ID = "user_36301191e2cb"

POOLS = {
    "general": [
        "hi", "what is 127 times 38", "define entropy in one line",
        "convert 42 degrees C to Fahrenheit", "what time is it in Tokyo",
        "name 3 capitals of South American countries",
        "translate thank you to French", "explain TCP handshake in 2 sentences",
        "give me 3 quick tips for drinking more water",
        "what does REST API stand for", "is sushi pronounced soo-shee or suh-shee",
        "summarize the plot of Hamlet in 2 sentences",
        "what year did the Berlin Wall fall", "how many time zones are there",
        "name 5 prime numbers between 30 and 60",
        "what is the difference between weather and climate",
        "define recursion in one sentence", "list 3 tips for better posture",
        "explain what a blockchain is simply", "convert 10 miles to km",
        "what is the speed of light in km per second",
        "name 5 programming languages created after 2010",
        "what is the capital of Mongolia", "explain DNS in 2 sentences",
        "give a fun fact about octopuses",
    ],
    "coding": [
        "write a Python function to check if a string is a palindrome",
        "implement bubble sort in JavaScript",
        "Go snippet: goroutine with channel example",
        "TypeScript generic function that returns the last element of an array",
        "SQL select the 3 most recent orders per customer",
        "Rust implement a simple Fibonacci function with memoization",
        "Python convert a list of dicts into a CSV string without pandas",
        "JS debounce function without lodash",
        "Python async example using httpx to fetch 3 URLs concurrently",
        "write a regex for a valid email with standard rules",
        "explain Big O of quicksort worst and average case",
        "Dockerfile for a basic Python FastAPI app",
        "bash one-liner to count unique IPs in nginx access log",
        "Python simple rate limiter decorator using token bucket",
        "React hook useDebouncedValue implementation",
        "Go implement a simple HTTP middleware for request logging",
        "Python parse an ISO 8601 datetime without dateutil",
        "SQL update prices by 10 percent for products in category electronics",
        "JavaScript deep equality check without lodash isEqual",
        "Python memoization decorator using functools",
        "write unit tests in pytest for a simple add function",
        "Kotlin data class with custom equals and hashCode",
        "PostgreSQL create a GIN index on a JSONB column",
        "Vue 3 component: controlled text input with v-model",
        "Python thread-safe counter using threading Lock",
    ],
    "webdesign": [
        "pick 5 Google Fonts good for a fintech SaaS",
        "hero section copy for an AI pricing tool: 8 word headline plus 20 word subhead",
        "CSS grid layout for a 3-column dashboard with sidebar",
        "accessible color palette WCAG AA for dark UI",
        "Tailwind classes for a gradient CTA button that pulses on hover",
        "React component structure for a pricing page with monthly/annual toggle",
        "write alt text for a generic team photo",
        "give me the CSS for a frosted glass card effect",
        "suggest a 3-tier pricing layout that emphasizes the middle plan",
        "responsive nav bar with hamburger for mobile in plain HTML+CSS",
        "dark mode color tokens for Tailwind config js",
        "skeleton loading state CSS for a card",
        "section copy for Why Us with 3 short bullets",
        "footer copy for a SaaS startup, 4 columns",
        "hero with image left, copy right: HTML structure",
        "5 micro-interaction ideas for a SaaS signup flow",
        "write meta description under 155 chars for AI gateway product page",
        "Tailwind class list for a stat card with icon number and label",
        "best UI pattern for displaying a 40-item model list",
        "button hierarchy: primary vs secondary vs tertiary styling rules",
        "checkout page flow: 3 or 4 steps",
        "write an empty-state message for a blank dashboard",
        "animation timing function for a subtle fade-in in CSS cubic-bezier",
        "section copy for testimonials carousel",
        "404 page copy that is witty but professional",
    ],
    "social": [
        "Twitter thread 5 tweets about cutting LLM costs by 90 percent",
        "LinkedIn post announcing a new AI gateway launch",
        "Instagram caption for a team photo with an inspiring quote",
        "TikTok hook script for how we saved 10k per month on AI",
        "reply template to a negative product review on Twitter",
        "5 LinkedIn headline variants for a SaaS founder",
        "Instagram carousel 5 slide outline on AI cost optimization",
        "YouTube short script 30 sec explaining what a credit-based AI plan is",
        "Facebook ad copy primary text for AI pricing tool under 125 chars",
        "tweet about a 1000 per month savings case study with a question hook",
        "reddit AMA intro post for a SaaS founder",
        "LinkedIn article hook about the hidden cost of paid LLM APIs",
        "Twitter poll idea about LLM provider preferences",
        "Instagram story text for a product drop teaser",
        "tweet announcing a Product Hunt launch",
        "LinkedIn comment reply that adds value without shilling",
        "meme caption about developer frustration with OpenAI prices",
        "Discord server welcome message for a new AI community",
        "Twitter thread outlining 7 hidden LLM pricing traps",
        "Instagram reel script: before and after AI cost in 15 sec",
        "LinkedIn post about switching from OpenAI to a router",
        "TikTok caption for a humorous tech skit",
        "cold DM opener on LinkedIn for B2B SaaS outreach",
        "Product Hunt launch description in 260 chars",
        "Twitter reply to a trending tweet about AI tools",
    ],
    "content": [
        "blog intro 120 words: why your AI bill is 10x higher than it should be",
        "5-point listicle things to check before signing an LLM contract",
        "cold email to a CTO: 50 percent LLM savings in 30 days under 150 words",
        "newsletter intro 80 words announcing product v2",
        "case study outline: how Acme Corp cut AI spend by 70 percent",
        "thought-leadership post about smart routing vs single provider",
        "blog title ideas 10 around free-tier LLM routing",
        "press release headline for Series A fundraise",
        "email subject line variants 5 for a product launch",
        "whitepaper abstract 150 words on universal AI gateways",
        "FAQ page 8 questions plus one-line answers",
        "email sequence outline 5 emails for post-signup onboarding",
        "tutorial intro: integrate our gateway in 5 minutes",
        "opinion piece hook why vendor lock-in is the real AI cost",
        "product release notes for v2.1 with 4 bullet points",
        "lead-magnet ebook title ideas 5 about AI cost control",
        "customer story quote mock-up from a CTO",
        "landing page section: social proof with 5 logos plus 2 testimonials outline",
        "in-app tooltip text one sentence each for Providers, Plans, Analytics features",
        "help doc: how to interpret your blended cost per credit",
        "changelog entry format for a new plan tier",
        "SEO meta title plus description for pricing page",
        "twitter bio variants 5 for a SaaS founder",
        "podcast talking points 5 about AI cost optimization",
        "YouTube channel trailer script 60 sec",
    ],
    "research": [
        "summarize differences between Claude Sonnet 4.6 and GPT-5 in 3 bullets",
        "what is the pricing per token for Claude Opus 4.6, Gemini 2.5 Pro, and DeepSeek R1",
        "explain how MoE models save cost vs dense models",
        "trade-offs of using rate-limited free tiers in production",
        "list major differences between OpenAI function calling and Anthropic tool use",
        "rank reasoning quality GPT-4, Claude 3.5 Sonnet, DeepSeek R1 with caveats",
        "explain Mamba-Transformer hybrid architecture Jamba in 2 sentences",
        "what is the context window of Moonshot Kimi K2 and what is it good for",
        "pros and cons of diffusion LLMs vs transformer LLMs",
        "list 5 providers that offer Llama 4 Scout and compare their prices",
        "which providers have real balance APIs and which do not",
        "what ASR providers offer whisper-large-v3 and their prices",
        "rerankers for RAG Cohere vs Voyage vs Jina quick comparison",
        "explain what LPU Groq and RDU SambaNova chips do differently",
        "why is Cerebras faster than Groq for some models and slower for others",
        "compare image-gen models FLUX.1-schnell vs DALL-E 3 vs Gemini 3 Imagen",
        "main differences between OpenRouter and a self-hosted router",
        "summarize the key features of MiniMax-M2.5 model",
        "what embedding model has best price and quality for multilingual RAG",
        "list 3 providers with 1M or more context window models",
        "compare Together vs Fireworks for llama-3.3-70b serving",
        "what is the cheapest vision model right now as of 2026",
        "explain what speculative decoding is and which providers use it",
        "list model quantization formats fp16 vs int8 vs int4 when to use each",
        "trade-offs of running inference on-device Llama 3.2 1B vs API calls",
    ],
    "heavy": [
        "draft a complete legal contract clause covering usage-based fees with per-credit tiers, liability cap at 12 months fees paid, data processing agreement, and termination for convenience with 30 days notice, enterprise-grade language",
        "diagnose root cause: API latency spiked from 180ms p50 to 3.2s p50, error rate from 0.1 percent to 7 percent over 4 minutes after deploying a Redis-backed rate limiter. Walk through 5 hypotheses, how to rule each in or out, and the most likely culprit",
        "refactor plan monolith to microservices of a billing subsystem: data model decisions, 6-stage rollout, dual-write period, shadow reads, kill-switches, rollback procedure, cost and risk analysis",
        "design a rate-limiting system for a universal AI gateway with tiered clients, per-provider quotas, burst allowance, fair-share algorithm. Include pseudocode, edge cases, operational runbook",
        "write a complete architectural decision record for choosing between event-sourcing and CRUD for a financial ledger: context, decision, consequences, alternatives considered",
        "security audit checklist for an AI gateway serving customer traffic: authentication, rate limiting, prompt injection defense, PII handling, provider key rotation, audit logging, incident response",
        "design a multi-region failover strategy for a SaaS with MongoDB, Redis, FastAPI: RPO and RTO targets, replication topology, DNS failover, data integrity checks, playbooks",
        "write a 2000-word technical post-mortem for a 4-hour outage caused by a cascading cache failure",
        "produce a complete GDPR compliance audit outline for a B2B SaaS storing user prompts and AI outputs: DPIA, ROPA, retention policies, subject rights implementation",
        "design end-to-end observability: metrics with Prometheus, traces with OpenTelemetry, logs to Loki, SLOs per service, on-call runbooks, alerting policies for 12 services",
        "write detailed migration strategy from Stripe subscriptions to a credit wallet model without breaking recurring billing: data model, Stripe webhook handling, reconciliation, customer comms",
        "complete build plan for a model router SDK in Python and TypeScript: API design, retry policies, observability hooks, error taxonomy, publishing pipeline, semantic versioning",
        "draft a technical architecture review for a proposed switch from Postgres to CockroachDB for billing data: pros, cons, migration cost, risks, operational changes",
        "design the internal abstraction for a universal model call that works across 30 providers with different auth schemes, tokenization, error codes, streaming formats",
        "write a full SRE playbook for the first on-call engineer at a new AI gateway startup: what to monitor, response to 10 common failure modes, escalation chain, writing post-mortems",
        "architect a SOC 2 Type II compliance readiness plan over 9 months for a 5-person SaaS startup",
        "design the data pipeline for ingesting 1M events per day of LLM usage logs into a time-series DB with aggregations for 10 dashboards and under 100ms query latency on hot queries",
        "write the technical RFP evaluation matrix for choosing between Pinecone, Weaviate, Milvus, Qdrant across 8 dimensions",
        "design the prompt-injection defense system for a customer-facing AI agent: input sanitization, canary prompts, output validation, monitoring, incident response",
        "full disaster recovery plan: 2 primary regions down, sub-region outage, data center fire. Expected recovery sequence, comms plan, post-incident review template",
        "write a complete FinOps plan for a Series A startup with 50k per month AI spend: budget forecasting, per-team attribution, anomaly detection, cost-optimization initiatives",
        "architect a backfill process for 500M historical records from v1 schema to v2 schema, zero-downtime, verifiable correctness, rollback",
        "design a fair-scheduling algorithm for 10k concurrent AI requests across 30 providers with varying rate limits, SLAs, costs, quality tiers",
        "write the 5-year technology strategy document for a SaaS founder: product bets, platform evolution, team structure, M&A theses",
        "produce a comprehensive risk register for a 2-year AI startup with 20 identified risks across technical, market, regulatory, operational axes",
    ],
    "image": [
        "describe an image: futuristic data center with teal plus violet neon, floating dashboards",
        "alt text for black coffee mug on walnut desk, morning light",
        "detailed visual prompt for DALL-E: minimalist SaaS hero banner with abstract geometric shapes",
        "alt text for group of 4 diverse developers in a modern office",
        "detailed prompt for cyberpunk cityscape at night with rain, neon signs, flying cars",
        "describe a single orange maple leaf floating on still pond water at dawn",
        "prompt: isometric illustration of a cloud infrastructure diagram",
        "alt text for infographic showing 5 steps of AI routing process",
        "prompt: photorealistic close-up of hands typing on a mechanical keyboard",
        "describe an abstract art piece representing speed in motion blur",
        "alt text for product box of wireless earbuds on white background",
        "prompt watercolor painting of a mountain cabin in winter",
        "describe a SaaS admin dashboard mock-up, dark theme, teal accents",
        "alt text for chart showing revenue growth over 12 months",
        "prompt surreal landscape with floating islands and giant clocks",
        "describe a happy customer holding a laptop with our product open",
        "alt text for team celebration photo after launch",
        "prompt studio product photography of a premium pen, black background",
        "describe 3D render of a transparent cube containing data streams",
        "alt text for diagram showing database replication topology",
        "prompt flat vector illustration of AI brain with connected nodes",
        "describe macro photography of a dew drop on a spider web at sunrise",
        "alt text for before and after UI screenshots of an onboarding redesign",
        "prompt 80s retro synthwave poster with a grid landscape",
        "describe a holographic data visualization hovering over a conference table",
    ],
    "video": [
        "15-second video script AI gateway saves money with VO plus visuals",
        "4-second intro clip dashboard transition from blank to 3 glowing KPIs",
        "30-second explainer storyboard how smart routing works in 4 scenes",
        "60-second YouTube short cost savings case study outline",
        "short video hook 10 sec before and after AI bill comparison",
        "storyboard for a 45-second product demo signup dashboard saving money",
        "video ad script 6 second bumper for YouTube single punchy message",
        "tutorial video outline 3 min integrating our gateway in 5 steps",
        "60-second founder intro video script",
        "15-second TikTok script developer reacts to high OpenAI bill",
        "explainer animation script 20 sec what a blended cost means",
        "3-minute walkthrough storyboard signing up and first successful request",
        "15-second reel script did you know fact about AI pricing",
        "trailer script 30 sec for an upcoming product launch",
        "customer testimonial video structure 90 seconds in 3 acts",
        "5-second animated logo intro concept and timing",
        "60-second motion graphic explaining universal gateway concept",
        "product tour video outline 8 features in 2 minutes",
        "kinetic typography script for a tagline and 3 supporting lines",
        "10-second loop animation idea for a pricing card hover state",
        "interview-style video 5 question script for founder on AI costs",
        "15-second Instagram reel 3 tips to cut AI costs",
        "2-minute webinar intro outline about AI cost management",
        "animated explainer script 40 sec what is a credit",
        "15-second ad concept side-by-side comparison of naive vs smart routing",
    ],
}


async def fire(sem, complete_fn, user_id, category, prompt, idx, total):
    async with sem:
        t0 = time.time()
        try:
            import os as _os3
            resp = await complete_fn(
                user_id=user_id,
                messages=[{"role": "user", "content": prompt}],
                model="maars/auto",
                source=_os3.environ.get("SIM_TAG", "client_sim_v3"),
            )
            wall = round((time.time() - t0) * 1000)
            has_leak = "provider" in resp
            preview = resp.get("choices", [{}])[0].get("message", {}).get("content", "")[:30]
            opacity = "LEAK" if has_leak else "OK"
            if idx % 10 == 0 or idx == total or idx <= 5:
                print(f"  [{idx:>3}/{total}] {category:10s} {wall:>5}ms [{opacity}] {preview}")
        except Exception as exc:
            print(f"  [{idx:>3}/{total}] {category:10s} FAIL: {str(exc)[:50]}")


async def main():
    from db import db
    import os as _os2
    source_tag = _os2.environ.get("SIM_TAG", "client_sim_v3")
    await db.gateway_usage_logs.delete_many({"source": source_tag})

    # Repeat pool to hit target size (default 225; set TARGET=1000 for wider CI).
    import os as _os
    target = int(_os.environ.get("SIM_TARGET", "225"))
    prompts = []
    for cat, pool in POOLS.items():
        for p in pool:
            prompts.append((cat, p))
    random.seed(42)
    random.shuffle(prompts)
    # If target > pool size, sample with replacement from shuffled order
    if target > len(prompts):
        extra = target - len(prompts)
        prompts = prompts + [random.choice(prompts) for _ in range(extra)]
    total = len(prompts)
    print(f"Firing {total} prompts (~25 per 8 categories), concurrency 6...\n")

    from services.llm_gateway import complete
    # Concurrency cap of 3 respects the tightest free-tier cap (Gemini Flash
    # at 15 RPM / 60 = 4 req/sec, and Cerebras 30 RPM). Rate-limit-aware
    # router handles spillover automatically.
    sem = asyncio.Semaphore(3)
    tasks = [fire(sem, complete, USER_ID, cat, p, i, total)
             for i, (cat, p) in enumerate(prompts, 1)]
    t0 = time.time()
    await asyncio.gather(*tasks)
    elapsed = round(time.time() - t0)
    print(f"\nAll {total} done in {elapsed}s. Invalidating blended_cost cache now.")
    from services.costing.blended_cost import invalidate_cache
    invalidate_cache()
    print("Cache invalidated. UI will pick up fresh figure on next 60s poll.")


if __name__ == "__main__":
    asyncio.run(main())
