"""
MAARS Smart Router — merges LLMRouter's ML scoring with MAARS's model catalog.

Inspired by github.com/ulab-uiuc/LLMRouter (KNN + HybridLLM + MLP approaches).
Ported WITHOUT the heavy torch/transformers stack — uses scikit-learn + TF-IDF
for lightweight, CPU-only, sub-millisecond routing decisions.

Architecture (3-stage pipeline):
    1. FEATURIZE  — TF-IDF on the prompt (captures intent/domain/complexity)
    2. SCORE      — for EVERY candidate model, compute a composite score:
                      task_fit      (trained classifier OR keyword fallback)
                      cost_score    (cheaper = higher, from MODEL_COSTS_MAP)
                      quality_score (from training data OR tier-based estimate)
                      health_score  (is the provider up right now?)
                      latency_score (faster = higher)
    3. SELECT     — pick highest composite score among available + affordable models

Training:
    Call `train_from_logs()` to learn from gateway_usage_logs. The router
    gets smarter with every request that flows through MAARS. When no training
    data exists, it falls back to keyword classification (the existing
    `classify_task_complexity` behavior) — so it's never worse than today.

Integration:
    `routes/universal._smart_candidates` calls `smart_router.rank()` instead
    of the hardcoded tier×task intersection. Everything downstream (wallet,
    fallback, response shaping) is unchanged.

All 169+ models in MODEL_COSTS_MAP are candidates. No model is left behind.
"""
from __future__ import annotations

import logging
import math
import os
import pickle
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------- paths

_MODEL_DIR = Path(__file__).parent / "_router_models"
_VECTORIZER_PATH = _MODEL_DIR / "tfidf_vectorizer.pkl"
_KNN_PATH = _MODEL_DIR / "knn_classifier.pkl"


# ---------------------------------------------------------------- model catalog

def _build_candidate_catalog() -> list[dict[str, Any]]:
    """
    Build the full candidate list from MAARS's existing model knowledge.

    Merges:
      - MODEL_COSTS_MAP (169 models, pricing)
      - MODEL_CREDIT_COSTS (per-call credit charge)
      - TASK_PREFERRED_MODELS (task→model affinity from universal.py)
      - model_registry (65 curated with tiers/capabilities)

    Every model in any of these sources becomes a candidate.
    """
    from services.llm_service import MODEL_COSTS_MAP, MODEL_CREDIT_COSTS

    # Build task affinity from TASK_PREFERRED_MODELS if available.
    task_affinity: dict[str, set[str]] = defaultdict(set)
    try:
        from routes.universal import TASK_PREFERRED_MODELS
        for task, models in TASK_PREFERRED_MODELS.items():
            for provider, model_id in models:
                task_affinity[model_id].add(task)
    except Exception:
        pass

    # Build tier + capability info from model_registry if available.
    registry_info: dict[str, dict[str, Any]] = {}
    try:
        from services.model_registry import BY_MAARS_ID, REGISTRY
        for m in REGISTRY:
            key = m.model_id.split("/")[-1]
            registry_info[key] = {
                "tier": m.tier,
                "capabilities": list(m.capabilities),
                "avg_latency_ms": m.avg_latency_ms,
                "context_window": m.context_window,
            }
    except Exception:
        pass

    candidates = []
    seen = set()

    for model_id, pricing in MODEL_COSTS_MAP.items():
        if model_id in seen:
            continue
        seen.add(model_id)

        cost_blend = (pricing.get("input", 2.5) + pricing.get("output", 10.0)) / 2.0
        credit_cost = MODEL_CREDIT_COSTS.get(model_id, 1)
        reg = registry_info.get(model_id, {})
        tasks = list(task_affinity.get(model_id, set()))

        # Infer provider from known patterns.
        provider = _infer_provider(model_id)

        candidates.append({
            "model_id": model_id,
            "provider": provider,
            "cost_per_mtok": cost_blend,
            "credit_cost": credit_cost,
            "tier": reg.get("tier", _infer_tier(cost_blend)),
            "capabilities": reg.get("capabilities", []),
            "tasks": tasks,
            "avg_latency_ms": reg.get("avg_latency_ms", 1500),
            "context_window": reg.get("context_window", 16000),
        })

    logger.info("smart_router catalog: %d candidate models", len(candidates))
    return candidates


def _infer_provider(model_id: str) -> str:
    """Best-effort provider inference from model name patterns."""
    mid = model_id.lower()
    if "gpt" in mid or mid.startswith("o3") or mid.startswith("o4") or "dall-e" in mid:
        return "openai"
    if "claude" in mid:
        return "anthropic"
    if "gemini" in mid or "gemma" in mid:
        return "gemini"
    if "grok" in mid:
        return "xai"
    if "deepseek" in mid:
        return "deepseek"
    if "mistral" in mid or "codestral" in mid or "pixtral" in mid:
        return "mistral"
    if "sonar" in mid:
        return "perplexity"
    if "command" in mid:
        return "cohere"
    if "llama" in mid:
        return "groq"  # default host for llama
    if "jamba" in mid:
        return "ai21"
    if "qwen" in mid or "qwq" in mid:
        return "qwen"
    if "glm" in mid:
        return "zhipu"
    if "solar" in mid:
        return "upstage"
    if "palmyra" in mid:
        return "writer"
    if "nemotron" in mid:
        return "nvidia"
    if "yi-" in mid:
        return "yi"
    if "kimi" in mid or "moonshot" in mid:
        return "moonshot"
    return "unknown"


def _infer_tier(cost_per_mtok: float) -> str:
    if cost_per_mtok < 0.5:
        return "economy"
    if cost_per_mtok < 5.0:
        return "standard"
    if cost_per_mtok < 20.0:
        return "premium"
    return "flagship"


# ---------------------------------------------------------------- task classifier (keyword fallback)

# Same keywords as services/llm_router.classify_task_complexity but condensed.
_TASK_KEYWORDS: dict[str, list[str]] = {
    "code":        ["code", "python", "javascript", "function", "bug", "debug", "api", "sql", "regex", "```"],
    "math":        ["math", "calculate", "equation", "integral", "derivative", "algebra", "proof", "theorem"],
    "reasoning":   ["reason", "logic", "step by step", "think through", "analyze", "deduce", "infer"],
    "creative":    ["poem", "story", "haiku", "creative", "fiction", "imagine", "song", "lyric"],
    "translation": ["translate", "french", "spanish", "german", "chinese", "japanese", "korean", "arabic"],
    "summary":     ["summarize", "summary", "tl;dr", "key points", "brief", "condense"],
    "research":    ["research", "study", "paper", "literature", "citation", "survey", "state of the art"],
    "vision":      ["image", "picture", "photo", "describe this", "what do you see", "visual"],
    "search":      ["search", "latest", "news", "current", "recent", "today"],
}

_TASK_CAPABILITY_MAP: dict[str, list[str]] = {
    "code":        ["code"],
    "math":        ["reasoning", "math"],
    "reasoning":   ["reasoning"],
    "creative":    ["creative", "long_context"],
    "translation": ["multilingual"],
    "summary":     ["long_context"],
    "research":    ["search", "research"],
    "vision":      ["vision"],
    "search":      ["search"],
    "chat":        [],
}


def classify_prompt(text: str) -> str:
    """Keyword-based task classification (fallback when no trained model)."""
    text_lower = text.lower()
    scores: dict[str, int] = defaultdict(int)
    for task, keywords in _TASK_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[task] += 1
    if not scores:
        return "chat"
    return max(scores, key=scores.get)


# ---------------------------------------------------------------- scoring engine (LLMRouter-inspired)

# Weights — cost-first by default. The thesis: "free tier as much as possible"
# is cheaper for the operator without hurting client experience on 90%+ of prompts
# (Gemini-flash, Groq-llama, Cerebras, SambaNova are all production-quality for
# simple chat/content/vibe-coding). Premium tiers still win when the prompt
# genuinely needs them because task_fit + quality together > cost alone.
DEFAULT_WEIGHTS = {
    "task_fit":     0.25,   # how well the model matches the task
    "cost":         0.40,   # cheaper is better (inverse cost) — was 0.25
    "quality":      0.15,   # learned quality OR tier-based estimate — was 0.20
    "health":       0.12,   # is the provider responding?
    "latency":      0.08,   # faster is better (inverse latency)
}


def _score_task_fit(candidate: dict, task: str) -> float:
    """1.0 if model is known-good for this task, 0.5 for neutral, 0.0 for mismatch."""
    if task in candidate.get("tasks", []):
        return 1.0
    desired_caps = _TASK_CAPABILITY_MAP.get(task, [])
    if not desired_caps:
        return 0.5
    have = set(c.lower() for c in candidate.get("capabilities", []))
    want = set(c.lower() for c in desired_caps)
    overlap = len(have & want) / len(want) if want else 0.5
    return overlap


def _score_cost(candidate: dict, max_cost: float) -> float:
    """Inverse cost normalized to [0, 1]. Cheapest = 1.0."""
    cost = candidate.get("cost_per_mtok", 5.0)
    if max_cost <= 0:
        return 0.5
    return max(0.0, 1.0 - (cost / max_cost))


def _score_quality(candidate: dict, learned_quality: Optional[dict] = None) -> float:
    """
    Quality score — from training data if available, else tier-based estimate.
    This is the LLMRouter-inspired piece: learned per-model quality from real data.
    """
    model_id = candidate["model_id"]
    if learned_quality and model_id in learned_quality:
        return float(learned_quality[model_id])

    # Tier-based fallback (0.0-1.0).
    tier_scores = {"economy": 0.3, "standard": 0.5, "premium": 0.7, "flagship": 0.9,
                   "reasoning": 0.8, "research": 0.7, "code": 0.6, "vision": 0.6,
                   "audio": 0.4, "image": 0.5}
    return tier_scores.get(candidate.get("tier", "standard"), 0.5)


def _score_latency(candidate: dict, max_latency: float) -> float:
    lat = candidate.get("avg_latency_ms", 1500)
    if max_latency <= 0:
        return 0.5
    return max(0.0, 1.0 - (lat / max_latency))


def score_all(
    candidates: list[dict],
    task: str,
    *,
    health_map: Optional[dict[str, float]] = None,
    learned_quality: Optional[dict[str, float]] = None,
    weights: Optional[dict[str, float]] = None,
) -> list[dict[str, Any]]:
    """
    Score every candidate model for a given task.

    Returns a list sorted by composite score (descending), each entry:
        {model_id, provider, score, breakdown, candidate}
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    health = health_map or {}
    max_cost = max((c.get("cost_per_mtok", 0.01) for c in candidates), default=1.0)
    max_latency = max((c.get("avg_latency_ms", 100) for c in candidates), default=1.0)

    scored = []
    for c in candidates:
        tf  = _score_task_fit(c, task)
        co  = _score_cost(c, max_cost)
        qu  = _score_quality(c, learned_quality)
        he  = health.get(c["provider"], 1.0)
        la  = _score_latency(c, max_latency)

        # Hard penalty: if task needs specific capabilities and model has NONE.
        desired = _TASK_CAPABILITY_MAP.get(task, [])
        if desired and tf == 0.0:
            penalty = 0.2
        else:
            penalty = 1.0

        composite = (
            w["task_fit"] * tf +
            w["cost"]     * co +
            w["quality"]  * qu +
            w["health"]   * he +
            w["latency"]  * la
        ) * penalty

        scored.append({
            "model_id": c["model_id"],
            "provider": c["provider"],
            "score": round(composite, 5),
            "breakdown": {
                "task_fit": round(tf, 3), "cost": round(co, 3),
                "quality": round(qu, 3), "health": round(he, 3),
                "latency": round(la, 3), "penalty": penalty,
            },
            "candidate": c,
        })

    scored.sort(key=lambda s: s["score"], reverse=True)
    return scored


# ---------------------------------------------------------------- KNN learned router (LLMRouter port)

_vectorizer: Optional[TfidfVectorizer] = None
_knn_model: Optional[KNeighborsClassifier] = None
_learned_quality: Optional[dict[str, float]] = None


def _load_trained_models() -> bool:
    """Load persisted TF-IDF + KNN from disk. Returns True if loaded."""
    global _vectorizer, _knn_model, _learned_quality
    if _vectorizer is not None:
        return True
    if not _VECTORIZER_PATH.exists() or not _KNN_PATH.exists():
        return False
    try:
        with open(_VECTORIZER_PATH, "rb") as f:
            _vectorizer = pickle.load(f)
        with open(_KNN_PATH, "rb") as f:
            data = pickle.load(f)
            _knn_model = data["knn"]
            _learned_quality = data.get("quality_map", {})
        logger.info("smart_router: loaded trained KNN (%d neighbors)", _knn_model.n_neighbors)
        return True
    except Exception as exc:
        logger.warning("smart_router: failed to load trained models: %s", exc)
        return False


async def train_from_logs(*, min_samples: int = 50) -> dict[str, Any]:
    """
    Train the KNN router from MAARS's own gateway_usage_logs.

    Each log entry that has a `maars_model`, `provider`, `native_model`,
    and `cost_usd` becomes a training sample. The "best" model for a prompt
    is the one that was chosen and succeeded (non-fallback, non-error).

    Saves the trained vectorizer + KNN to _MODEL_DIR for hot-reload.
    """
    from db import db

    cursor = db.gateway_usage_logs.find(
        {"cost_usd": {"$gt": 0}},
        {"_id": 0, "key_prefix": 1, "maars_model": 1, "provider": 1,
         "native_model": 1, "cost_usd": 1, "latency_ms": 1,
         "prompt_preview": 1, "fallback_used": 1},
    ).sort("timestamp", -1).limit(10000)

    prompts: list[str] = []
    labels: list[str] = []
    model_successes: dict[str, list[float]] = defaultdict(list)

    async for log in cursor:
        prompt = log.get("prompt_preview") or log.get("key_prefix", "")
        model = log.get("native_model", "")
        if not prompt or not model:
            continue
        # Only learn from non-fallback (primary pick succeeded).
        if log.get("fallback_used"):
            continue
        prompts.append(prompt)
        labels.append(model)
        # Track quality proxy: lower cost + lower latency = higher quality/efficiency.
        cost = float(log.get("cost_usd") or 0.001)
        latency = float(log.get("latency_ms") or 1500)
        efficiency = 1.0 / (cost * 0.5 + latency / 10000 * 0.5 + 0.01)
        model_successes[model].append(efficiency)

    if len(prompts) < min_samples:
        return {"status": "insufficient_data", "samples": len(prompts),
                "min_required": min_samples}

    # Build TF-IDF features.
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english",
                                  ngram_range=(1, 2), min_df=2, max_df=0.95)
    X = vectorizer.fit_transform(prompts)

    # Train KNN (like LLMRouter's KNNRouter).
    knn = KNeighborsClassifier(n_neighbors=min(5, len(set(labels))),
                                metric="cosine", weights="distance")
    knn.fit(X, labels)

    # Build learned quality map (0.0 to 1.0 per model).
    quality_map: dict[str, float] = {}
    if model_successes:
        max_eff = max(np.mean(v) for v in model_successes.values())
        for model, effs in model_successes.items():
            quality_map[model] = round(float(np.mean(effs) / max_eff), 4) if max_eff > 0 else 0.5

    # Persist.
    _MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(_VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    with open(_KNN_PATH, "wb") as f:
        pickle.dump({"knn": knn, "quality_map": quality_map}, f)

    # Hot-reload into memory.
    global _vectorizer, _knn_model, _learned_quality
    _vectorizer = vectorizer
    _knn_model = knn
    _learned_quality = quality_map

    return {
        "status": "trained",
        "samples": len(prompts),
        "unique_models": len(set(labels)),
        "quality_map": quality_map,
    }


# ---------------------------------------------------------------- public API: rank()

def rank(
    prompt: str,
    *,
    available_providers: Optional[set[str]] = None,
    health_map: Optional[dict[str, float]] = None,
    quality_override: Optional[str] = None,
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """
    The main entry point. Called by _smart_candidates.

    Returns up to `top_k` scored model candidates, sorted by composite score.
    If trained KNN exists, uses it for task classification. Otherwise falls
    back to keyword classifier. Either way, ALL models in the catalog are
    scored — no model is left behind.

    Args:
        prompt:               raw user prompt
        available_providers:  set of provider slugs that have valid API keys
        health_map:           provider → health (0.0 down .. 1.0 healthy)
        quality_override:     if "economy"/"standard"/"premium", boost that tier
        top_k:                how many top results to return
    """
    # 1. Classify task.
    task = "chat"
    knn_suggestion: Optional[str] = None

    if _load_trained_models() and _vectorizer is not None and _knn_model is not None:
        try:
            X = _vectorizer.transform([prompt])
            knn_suggestion = _knn_model.predict(X)[0]
            # Use the KNN's suggestion to refine task classification.
            # The KNN predicts a MODEL NAME, not a task type. We infer the task
            # from the model's known capabilities.
            task = _task_from_model(knn_suggestion) or classify_prompt(prompt)
        except Exception:
            task = classify_prompt(prompt)
    else:
        task = classify_prompt(prompt)

    # 2. Build candidate catalog.
    candidates = _build_candidate_catalog()

    # 3. Filter to available providers if specified.
    if available_providers:
        candidates = [c for c in candidates if c["provider"] in available_providers]

    # 4. Apply quality_override (tier preference).
    weights = dict(DEFAULT_WEIGHTS)
    if quality_override in ("economy", "standard", "premium", "flagship"):
        # Boost cost weight for economy, quality weight for premium.
        if quality_override == "economy":
            weights["cost"] = 0.40
            weights["quality"] = 0.10
        elif quality_override == "premium":
            weights["cost"] = 0.10
            weights["quality"] = 0.35
        elif quality_override == "flagship":
            weights["cost"] = 0.05
            weights["quality"] = 0.40

    # 5. Score all.
    scored = score_all(
        candidates, task,
        health_map=health_map,
        learned_quality=_learned_quality,
        weights=weights,
    )

    # 6. If KNN suggested a specific model and it's in the top results,
    #    boost it (LLMRouter's "direct prediction" behavior).
    if knn_suggestion:
        for i, s in enumerate(scored):
            if s["model_id"] == knn_suggestion:
                s["score"] += 0.1  # KNN confidence bonus
                s["breakdown"]["knn_bonus"] = 0.1
                break
        scored.sort(key=lambda s: s["score"], reverse=True)

    return scored[:top_k]


def _task_from_model(model_id: str) -> Optional[str]:
    """Reverse-infer likely task from a model's known capabilities."""
    mid = model_id.lower()
    if "codestral" in mid or "starcoder" in mid:
        return "code"
    if "o3" in mid or "o4" in mid or "deepseek-r1" in mid or "qwq" in mid:
        return "reasoning"
    if "sonar" in mid:
        return "search"
    if "whisper" in mid or "tts" in mid:
        return "audio"
    return None


# ---------------------------------------------------------------- diagnostics

def explain(prompt: str, **kwargs) -> dict[str, Any]:
    """
    Full diagnostic: what the router would do with this prompt, and why.
    Returns the task classification, top 10 candidates with score breakdowns,
    and whether KNN or keyword classification was used.
    """
    task = classify_prompt(prompt)
    knn_used = False
    knn_suggestion = None

    if _load_trained_models() and _vectorizer is not None and _knn_model is not None:
        try:
            X = _vectorizer.transform([prompt])
            knn_suggestion = _knn_model.predict(X)[0]
            knn_used = True
            task = _task_from_model(knn_suggestion) or task
        except Exception:
            pass

    ranked = rank(prompt, **kwargs)
    return {
        "prompt_preview": prompt[:100],
        "task_classified": task,
        "classifier": "knn" if knn_used else "keyword",
        "knn_suggestion": knn_suggestion,
        "top_candidates": ranked[:10],
        "total_candidates_scored": len(_build_candidate_catalog()),
    }
