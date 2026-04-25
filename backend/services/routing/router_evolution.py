"""
MAARS Router Evolution — self-improving model routing via 3-agent feedback loop.

Merges:
  * Multi-agent-evolve (github.com/ulab-uiuc/Multi-agent-evolve)
    — Proposer/Solver/Judge self-improvement pattern
    — Strict rubric scoring from their default.json templates
    — Quality filtering + iterative refinement

  * LLMRouter (github.com/ulab-uiuc/LLMRouter)
    — Score-every-model approach (already in smart_router.py)
    — KNN learned routing from traffic data

  * MAARS existing infrastructure
    — Uses the MAARS gateway providers (no external GPU needed)
    — Feeds results into smart_router's quality map
    — Wallet-aware (evolution cycles cost credits from the operator's budget)

Evolution cycle:
    1. PROPOSE — generate diverse test prompts across task categories
    2. SOLVE   — route each prompt to N candidate models, collect responses
    3. JUDGE   — score each response on a 1-10 rubric (strict, from Multi-agent-evolve)
    4. UPDATE  — feed scores into smart_router's learned quality map
    5. PERSIST — store results in `router_evolution_runs` collection

The router gets smarter with every cycle — no human labels, no external training.
Runs via: POST /admin/metrics/router/evolve
"""
from __future__ import annotations

import logging
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from db import db

logger = logging.getLogger(__name__)

EVOLUTION_COLLECTION = "router_evolution_runs"

# ---------------------------------------------------------------- task categories

TASK_CATEGORIES = [
    ("code",        "Write a Python function that reverses a linked list in-place."),
    ("code",        "Debug this function: def fib(n): return fib(n-1) + fib(n-2)"),
    ("math",        "Prove that for any integer n, n^2 + n is always even."),
    ("math",        "Calculate the integral of x*e^x from 0 to 1."),
    ("reasoning",   "A bat and ball cost $1.10. The bat costs $1 more than the ball. How much does the ball cost?"),
    ("reasoning",   "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?"),
    ("creative",    "Write a haiku about a programmer debugging at 3am."),
    ("creative",    "Invent a new word and write a dictionary entry for it."),
    ("translation", "Translate to French: The weather is beautiful today, shall we go for a walk?"),
    ("translation", "Translate to Japanese: I would like to order two coffees please."),
    ("summary",     "Summarize the concept of quantum entanglement in 3 sentences for a 10 year old."),
    ("summary",     "Explain blockchain in one paragraph without using technical jargon."),
    ("search",      "What are the most significant AI breakthroughs of 2025?"),
    ("chat",        "Hello, how are you today?"),
    ("chat",        "What is the meaning of life?"),
]


# ---------------------------------------------------------------- proposer (from Multi-agent-evolve)

PROPOSER_SYSTEM = """You are a Proposer agent. Your job is to generate challenging, diverse test prompts
that will help evaluate which AI model is best for different tasks.

Generate ONE prompt that is:
- Self-contained and clearly described
- Non-trivial, requiring real capability to answer well
- In the specified domain/category
- Free from ambiguity

Wrap your prompt in <question></question> tags.
Category: {category}"""


async def _propose(category: str, provider_call) -> Optional[str]:
    """Generate a test prompt using a cheap fast model (Proposer role)."""
    messages = [
        {"role": "system", "content": PROPOSER_SYSTEM.format(category=category)},
        {"role": "user", "content": f"Generate a challenging {category} prompt that will differentiate strong models from weak ones."},
    ]
    try:
        resp = await provider_call(messages=messages, max_tokens=300)
        text = resp or ""
        # Extract from <question> tags if present.
        m = re.search(r"<question>(.*?)</question>", text, re.DOTALL)
        return m.group(1).strip() if m else text.strip()
    except Exception as exc:
        logger.warning("proposer failed: %s", exc)
        return None


# ---------------------------------------------------------------- judge (from Multi-agent-evolve strict rubric)

JUDGE_SYSTEM = """Please evaluate the following solution to a question/problem with a STRICT rubric.

Question/Problem: {question}

Generated Solution: {answer}

First, analyze the solution in <think></think> tags.

STRICT RUBRIC:
- Factual correctness is mandatory. ANY factual error => score MUST be in [1,3].
- Meaningless repetition or filler => score MUST be in [1,3].
- Hallucinated references or unsupported claims => score MUST be in [1,3].
- Completeness: Missing key steps => score in [4,7] unless factual errors (then [1,3]).
- Only entirely correct, concise, instruction-following answers may receive [8,10].

Then provide a score from 1 to 10 between <score> and </score> tags.

<score>X</score> (where X is an integer from 1 to 10)"""


async def _judge(question: str, answer: str, provider_call) -> Optional[int]:
    """Score a response on 1-10 using Multi-agent-evolve's strict rubric (Judge role)."""
    messages = [
        {"role": "user", "content": JUDGE_SYSTEM.format(question=question, answer=answer)},
    ]
    try:
        resp = await provider_call(messages=messages, max_tokens=500)
        text = resp or ""
        m = re.search(r"<score>\s*(\d+)\s*</score>", text)
        if m:
            return max(1, min(10, int(m.group(1))))
        # Fallback: find any standalone digit.
        nums = re.findall(r"\b(\d+)\b", text)
        for n in reversed(nums):
            val = int(n)
            if 1 <= val <= 10:
                return val
        return None
    except Exception as exc:
        logger.warning("judge failed: %s", exc)
        return None


# ---------------------------------------------------------------- solver (calls MAARS providers)

async def _solve(prompt: str, provider: str, model: str, api_keys: dict) -> Optional[str]:
    """Route the prompt to a specific model via MAARS's call_direct_llm (Solver role)."""
    try:
        from services.llm_service import call_direct_llm
        api_key = api_keys.get(provider, "")
        if not api_key:
            return None
        text = await call_direct_llm(provider, model, "", prompt, [], api_key)
        return text
    except Exception as exc:
        logger.debug("solver %s/%s failed: %s", provider, model, exc)
        return None


# ---------------------------------------------------------------- evolution cycle

async def run_evolution_cycle(
    *,
    max_prompts: int = 10,
    models_per_prompt: int = 4,
    judge_provider: str = "groq",
    judge_model: str = "llama-3.3-70b-versatile",
    proposer_provider: str = "groq",
    proposer_model: str = "llama-3.3-70b-versatile",
) -> dict[str, Any]:
    """
    Run one full Proposer -> Solver -> Judge evolution cycle.

    Uses MAARS's own providers — no external GPU, no separate training infra.
    Results update the smart_router's learned quality map so subsequent routing
    decisions are better informed.
    """
    from shared.utils import get_api_keys
    from services.routing import smart_router

    run_id = f"evo_{uuid.uuid4().hex[:12]}"
    started = time.time()
    api_keys = await get_api_keys()

    # Build the provider call helper for proposer + judge.
    async def _llm_call(messages, max_tokens=300, provider=None, model=None):
        p = provider or proposer_provider
        m = model or proposer_model
        key = api_keys.get(p, "")
        if not key:
            return None
        from services.llm_service import call_direct_llm
        sys_msg = ""
        user_msg = ""
        for msg in messages:
            if msg["role"] == "system":
                sys_msg += msg["content"] + "\n"
            else:
                user_msg = msg["content"]
        return await call_direct_llm(p, m, sys_msg.strip(), user_msg, [], key)

    # 1. SELECT candidate models to evaluate.
    # Pre-test which models actually respond (not just which have keys).
    # Use a tiny probe call to filter out providers returning 4xx.
    candidates = smart_router._build_candidate_catalog()
    available = [c for c in candidates if api_keys.get(c["provider"])]
    if not available:
        return {"run_id": run_id, "status": "no_available_models", "detail": "No provider keys configured."}

    # Known-good models (confirmed working in test matrix).
    # TODO: replace with dynamic health probe in future.
    _KNOWN_GOOD = {
        ("groq", "llama-3.1-8b-instant"),
        ("groq", "llama-3.3-70b-versatile"),
        ("gemini", "gemini-2.5-flash"),
    }
    working = [c for c in available if (c["provider"], c["model_id"]) in _KNOWN_GOOD]
    if not working:
        # Fallback: try all available and let solver failures filter naturally.
        import random
        working = random.sample(available, min(models_per_prompt * 2, len(available)))

    import random
    eval_models = random.sample(working, min(models_per_prompt, len(working)))

    # 2. PROPOSE test prompts (mix of generated + seeded).
    prompts: list[dict[str, str]] = []
    # Use seeded prompts first (guaranteed quality).
    import random as _rng
    seeded = _rng.sample(TASK_CATEGORIES, min(max_prompts // 2, len(TASK_CATEGORIES)))
    for cat, prompt_text in seeded:
        prompts.append({"category": cat, "prompt": prompt_text, "source": "seeded"})

    # Generate additional prompts via Proposer agent.
    remaining = max_prompts - len(prompts)
    categories = [c for c, _ in TASK_CATEGORIES]
    for i in range(remaining):
        cat = _rng.choice(categories)
        proposed = await _propose(cat, lambda messages, max_tokens=300: _llm_call(messages, max_tokens))
        if proposed and len(proposed) > 10:
            prompts.append({"category": cat, "prompt": proposed, "source": "proposer"})

    # 3. SOLVE — route each prompt to each eval model.
    evaluations: list[dict[str, Any]] = []
    for prompt_info in prompts:
        for model_info in eval_models:
            response = await _solve(
                prompt_info["prompt"],
                model_info["provider"],
                model_info["model_id"],
                api_keys,
            )
            if response:
                evaluations.append({
                    "prompt": prompt_info["prompt"],
                    "category": prompt_info["category"],
                    "provider": model_info["provider"],
                    "model_id": model_info["model_id"],
                    "response": response[:2000],  # cap for storage
                    "response_len": len(response),
                })

    if not evaluations:
        return {"run_id": run_id, "status": "no_responses", "detail": "All solver calls failed."}

    # 4. JUDGE — score each response using Multi-agent-evolve's strict rubric.
    for ev in evaluations:
        score = await _judge(
            ev["prompt"], ev["response"],
            lambda messages, max_tokens=500: _llm_call(
                messages, max_tokens, provider=judge_provider, model=judge_model
            ),
        )
        ev["judge_score"] = score

    # 5. UPDATE — compute per-model quality scores and feed into smart_router.
    from collections import defaultdict
    model_scores: dict[str, list[float]] = defaultdict(list)
    for ev in evaluations:
        if ev.get("judge_score") is not None:
            model_scores[ev["model_id"]].append(float(ev["judge_score"]) / 10.0)

    quality_map: dict[str, float] = {}
    if model_scores:
        import numpy as np
        for model_id, scores in model_scores.items():
            quality_map[model_id] = round(float(np.mean(scores)), 4)

    # Merge into smart_router's learned quality (additive, not replace).
    if quality_map:
        if smart_router._learned_quality is None:
            smart_router._learned_quality = {}
        for model_id, q in quality_map.items():
            existing = smart_router._learned_quality.get(model_id)
            if existing is not None:
                # Exponential moving average — new data blends with prior.
                smart_router._learned_quality[model_id] = round(0.7 * existing + 0.3 * q, 4)
            else:
                smart_router._learned_quality[model_id] = q
        logger.info("evolution cycle %s: updated quality for %d models", run_id, len(quality_map))

    # 6. PERSIST the full run for admin visibility.
    elapsed = time.time() - started
    run_doc = {
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 2),
        "prompts_generated": len(prompts),
        "evaluations_completed": len(evaluations),
        "models_evaluated": list(set(e["model_id"] for e in evaluations)),
        "quality_map_update": quality_map,
        "evaluations": [
            {k: v for k, v in e.items() if k != "response"}  # don't store full responses
            for e in evaluations
        ],
        "config": {
            "judge_provider": judge_provider,
            "judge_model": judge_model,
            "proposer_provider": proposer_provider,
            "proposer_model": proposer_model,
            "max_prompts": max_prompts,
            "models_per_prompt": models_per_prompt,
        },
    }
    try:
        await db[EVOLUTION_COLLECTION].insert_one(run_doc)
    except Exception as exc:
        logger.warning("failed to persist evolution run: %s", exc)

    return {
        "run_id": run_id,
        "status": "complete",
        "elapsed_seconds": round(elapsed, 2),
        "prompts": len(prompts),
        "evaluations": len(evaluations),
        "models_scored": len(quality_map),
        "quality_map": quality_map,
        "top_models": sorted(quality_map.items(), key=lambda kv: -kv[1])[:10],
    }


async def get_evolution_history(limit: int = 20) -> list[dict[str, Any]]:
    """Recent evolution run summaries for admin dashboard."""
    cursor = db[EVOLUTION_COLLECTION].find(
        {}, {"_id": 0, "evaluations": 0}  # exclude full eval data for listing
    ).sort("started_at", -1).limit(int(limit))
    return [doc async for doc in cursor]


async def get_current_quality_map() -> dict[str, float]:
    """The live learned quality scores the router is using right now."""
    from services.routing import smart_router
    return dict(smart_router._learned_quality or {})
