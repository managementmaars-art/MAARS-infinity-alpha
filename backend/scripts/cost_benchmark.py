"""
MAARS Cost Benchmark — sends diverse requests through the universal router
to measure the REAL blended cost per credit.

Usage: python scripts/cost_benchmark.py
"""
import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import db

# Diverse prompts that simulate real customer usage patterns
BENCHMARK_PROMPTS = [
    # ── Simple chat (60% of typical traffic) ──
    {"category": "chat", "prompt": "Hello, how are you?"},
    {"category": "chat", "prompt": "What's the weather like today?"},
    {"category": "chat", "prompt": "Tell me a joke"},
    {"category": "chat", "prompt": "Good morning!"},
    {"category": "chat", "prompt": "Thanks for the help"},
    {"category": "chat", "prompt": "Can you help me with something?"},
    {"category": "chat", "prompt": "What time is it?"},
    {"category": "chat", "prompt": "Who are you?"},
    {"category": "chat", "prompt": "What can you do?"},
    {"category": "chat", "prompt": "Summarize your capabilities in one sentence"},
    {"category": "chat", "prompt": "Explain what AI is in simple terms"},
    {"category": "chat", "prompt": "What's the capital of France?"},
    {"category": "chat", "prompt": "How do I make coffee?"},
    {"category": "chat", "prompt": "Recommend a good book to read"},
    {"category": "chat", "prompt": "What's 25 times 17?"},
    {"category": "chat", "prompt": "Translate hello to Spanish, French, and Japanese"},
    {"category": "chat", "prompt": "Write a haiku about coding"},
    {"category": "chat", "prompt": "What are the primary colors?"},
    {"category": "chat", "prompt": "How many continents are there?"},
    {"category": "chat", "prompt": "What's the meaning of life?"},
    {"category": "chat", "prompt": "Give me 3 tips for productivity"},
    {"category": "chat", "prompt": "What's the difference between HTTP and HTTPS?"},
    {"category": "chat", "prompt": "Explain machine learning in one paragraph"},
    {"category": "chat", "prompt": "What year was Python created?"},
    {"category": "chat", "prompt": "List 5 popular programming languages"},
    {"category": "chat", "prompt": "What does API stand for?"},
    {"category": "chat", "prompt": "How do I center a div in CSS?"},
    {"category": "chat", "prompt": "What is MongoDB?"},
    {"category": "chat", "prompt": "Explain REST vs GraphQL briefly"},
    {"category": "chat", "prompt": "What is Docker used for?"},

    # ── Code generation (20% of typical traffic) ──
    {"category": "code", "prompt": "Write a Python function to reverse a string"},
    {"category": "code", "prompt": "Write a JavaScript function to find duplicates in an array"},
    {"category": "code", "prompt": "Create a simple HTML login form with CSS styling"},
    {"category": "code", "prompt": "Write a SQL query to find the top 5 customers by total orders"},
    {"category": "code", "prompt": "Write a Python function to check if a number is prime"},
    {"category": "code", "prompt": "Create a React component for a todo list item"},
    {"category": "code", "prompt": "Write a bash script to backup a directory"},
    {"category": "code", "prompt": "Write a Python class for a linked list with insert and delete methods"},
    {"category": "code", "prompt": "Create a FastAPI endpoint that accepts JSON and returns a response"},
    {"category": "code", "prompt": "Write a TypeScript interface for a User with email, name, and role"},

    # ── Reasoning / analysis (10% of typical traffic) ──
    {"category": "reasoning", "prompt": "A bat and ball cost $1.10. The bat costs $1 more than the ball. How much does the ball cost? Show your work."},
    {"category": "reasoning", "prompt": "Compare the pros and cons of microservices vs monolithic architecture"},
    {"category": "reasoning", "prompt": "If I have 3 red balls and 5 blue balls, what's the probability of picking 2 red balls in a row without replacement?"},
    {"category": "reasoning", "prompt": "Analyze the trade-offs between SQL and NoSQL databases for a social media application"},
    {"category": "reasoning", "prompt": "What are the implications of Moore's Law slowing down for the tech industry?"},

    # ── Creative writing (10% of typical traffic) ──
    {"category": "creative", "prompt": "Write a short story about a robot learning to paint, in 100 words"},
    {"category": "creative", "prompt": "Create a product description for an AI-powered coffee maker"},
    {"category": "creative", "prompt": "Write a professional email declining a meeting invitation politely"},
    {"category": "creative", "prompt": "Generate 5 creative names for a tech startup that does AI consulting"},
    {"category": "creative", "prompt": "Write a LinkedIn post announcing a new product launch"},
]


async def run_benchmark():
    """Send all benchmark prompts through the router and measure costs."""
    from services.llm_service import call_direct_llm
    from shared.utils import get_api_keys
    from services.routing import smart_router

    api_keys = await get_api_keys()

    print("=" * 70)
    print("MAARS COST BENCHMARK")
    print("=" * 70)
    print(f"Prompts: {len(BENCHMARK_PROMPTS)}")
    print(f"Categories: chat={sum(1 for p in BENCHMARK_PROMPTS if p['category']=='chat')}, "
          f"code={sum(1 for p in BENCHMARK_PROMPTS if p['category']=='code')}, "
          f"reasoning={sum(1 for p in BENCHMARK_PROMPTS if p['category']=='reasoning')}, "
          f"creative={sum(1 for p in BENCHMARK_PROMPTS if p['category']=='creative')}")
    print()

    # Tag benchmark entries so we can identify them
    benchmark_id = f"bench_{int(time.time())}"

    results = []
    errors = 0
    start_time = time.time()

    for i, bp in enumerate(BENCHMARK_PROMPTS):
        prompt = bp["prompt"]
        category = bp["category"]

        # Let smart router pick the best model
        try:
            ranked = smart_router.rank(prompt)
            if not ranked:
                print(f"  [{i+1}/{len(BENCHMARK_PROMPTS)}] SKIP - no models ranked")
                errors += 1
                continue

            top = ranked[0]
            provider = top["provider"]
            model = top["model_id"]
            key = api_keys.get(provider, "")

            if not key:
                # Try next model
                for alt in ranked[1:5]:
                    key = api_keys.get(alt["provider"], "")
                    if key:
                        provider = alt["provider"]
                        model = alt["model_id"]
                        break

            if not key:
                print(f"  [{i+1}/{len(BENCHMARK_PROMPTS)}] SKIP {category} - no key for {provider}")
                errors += 1
                continue

            # Call the model
            t0 = time.time()
            response = await call_direct_llm(provider, model, "", prompt, [], key)
            latency = time.time() - t0

            # Get the cost from the most recent usage_log
            log = await db.usage_logs.find_one(
                {"model": model},
                sort=[("created_at", -1)]
            )

            cost = float(log.get("estimated_cost_usd", 0)) if log else 0.0
            input_tokens = int(log.get("input_tokens", 0)) if log else 0
            output_tokens = int(log.get("output_tokens", 0)) if log else 0
            total_tokens = input_tokens + output_tokens

            results.append({
                "category": category,
                "provider": provider,
                "model": model,
                "cost_usd": cost,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "latency_s": round(latency, 2),
                "response_len": len(response or ""),
            })

            status = "FREE" if cost == 0 else f"${cost:.6f}"
            print(f"  [{i+1}/{len(BENCHMARK_PROMPTS)}] {category:10s} → {provider:12s} {model:35s} {total_tokens:>5d} tok  {status:>12s}  {latency:.1f}s")

        except Exception as exc:
            print(f"  [{i+1}/{len(BENCHMARK_PROMPTS)}] ERROR {category} - {exc}")
            errors += 1

    elapsed = time.time() - start_time

    # ── Analysis ──
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    if not results:
        print("No successful calls. Check API keys and provider health.")
        return

    total_cost = sum(r["cost_usd"] for r in results)
    total_tokens_all = sum(r["total_tokens"] for r in results)
    total_calls = len(results)
    free_calls = sum(1 for r in results if r["cost_usd"] == 0)
    paid_calls = total_calls - free_calls
    avg_cost_per_credit = total_cost / total_calls if total_calls > 0 else 0
    avg_tokens_per_credit = total_tokens_all / total_calls if total_calls > 0 else 0

    print(f"  Total calls:          {total_calls} ({errors} errors)")
    print(f"  Total cost:           ${total_cost:.6f}")
    print(f"  Total tokens:         {total_tokens_all:,}")
    print(f"  Elapsed:              {elapsed:.1f}s")
    print()
    print(f"  ══ BLENDED COST PER CREDIT: ${avg_cost_per_credit:.8f} ══")
    print(f"  Avg tokens per credit: {avg_tokens_per_credit:.0f}")
    print(f"  Free routing:          {free_calls}/{total_calls} ({free_calls/total_calls*100:.0f}%)")
    print(f"  Paid routing:          {paid_calls}/{total_calls} ({paid_calls/total_calls*100:.0f}%)")
    print()

    # Per-category breakdown
    print("  By category:")
    for cat in ["chat", "code", "reasoning", "creative"]:
        cat_results = [r for r in results if r["category"] == cat]
        if cat_results:
            cat_cost = sum(r["cost_usd"] for r in cat_results)
            cat_avg = cat_cost / len(cat_results)
            cat_tokens = sum(r["total_tokens"] for r in cat_results) / len(cat_results)
            cat_free = sum(1 for r in cat_results if r["cost_usd"] == 0)
            print(f"    {cat:12s}: {len(cat_results):3d} calls, avg ${cat_avg:.8f}/credit, avg {cat_tokens:.0f} tokens, {cat_free}/{len(cat_results)} free")

    # Per-provider breakdown
    print()
    print("  By provider:")
    from collections import Counter
    provider_counts = Counter(r["provider"] for r in results)
    for provider, count in provider_counts.most_common():
        prov_results = [r for r in results if r["provider"] == provider]
        prov_cost = sum(r["cost_usd"] for r in prov_results)
        print(f"    {provider:15s}: {count:3d} calls, total ${prov_cost:.6f}")

    print()
    print("=" * 70)
    print(f"USE THIS AS YOUR BASE COST: ${avg_cost_per_credit:.8f} per credit")
    print(f"At 200% margin: price = cost × 3.0 = ${avg_cost_per_credit * 3:.8f} per credit")
    print(f"At 500% margin: price = cost × 6.0 = ${avg_cost_per_credit * 6:.8f} per credit")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
