"""MAARS — Intelligence: Search Engine with Source Ranking & Freshness Detection."""

import hashlib
from datetime import datetime, timezone
from db import db

SEARCH_CACHE = "search_cache"
SEARCH_RESULTS = "search_results"


def _hash(q: str):
    return hashlib.md5(q.encode()).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat()


async def plan_query(goal: str, context: dict = None):
    """Plan search queries from a goal description. Returns structured query plan."""
    context = context or {}
    queries = []
    keywords = goal.lower().split()

    # Primary query
    queries.append({"query": goal, "purpose": "primary", "priority": 1})

    # Generate sub-queries for better coverage
    if any(w in goal.lower() for w in ["competitor", "market", "industry"]):
        queries.append({"query": f"{goal} market share 2026", "purpose": "market_data", "priority": 2})
        queries.append({"query": f"{goal} latest news", "purpose": "freshness", "priority": 3})

    if any(w in goal.lower() for w in ["regulation", "compliance", "legal"]):
        queries.append({"query": f"{goal} regulatory update 2026", "purpose": "regulatory", "priority": 2})

    if any(w in goal.lower() for w in ["price", "cost", "pricing"]):
        queries.append({"query": f"{goal} pricing comparison", "purpose": "pricing", "priority": 2})

    return {"goal": goal, "queries": queries, "created_at": _now()}


async def execute_search(query: str, freshness_required: str = "standard"):
    """Execute a search query. Checks cache first, returns structured results."""
    qhash = _hash(query)

    # Check cache
    cached = await db[SEARCH_CACHE].find_one({"query_hash": qhash}, {"_id": 0})
    if cached and freshness_required != "real_time":
        return {"source": "cache", "results": cached["results"], "freshness": cached.get("freshness_score", 0.5)}

    # Simulated search results (will integrate real web search in production)
    results = [
        {"title": f"Result for: {query}", "snippet": f"Relevant information about {query}...", "url": f"https://source.example.com/{qhash[:8]}", "relevance": 0.85, "source_type": "web"},
    ]

    # Cache results
    await db[SEARCH_CACHE].update_one(
        {"query_hash": qhash},
        {"$set": {"query": query, "results": results, "freshness_score": 0.7, "created_at": _now(), "expires_at": _now()}},
        upsert=True,
    )

    return {"source": "live", "results": results, "freshness": 0.7}


def rank_sources(results: list):
    """Rank search results by credibility, relevance, and freshness."""
    tier_scores = {
        "official": 1.0, "academic": 0.9, "news_major": 0.85,
        "industry": 0.8, "news_minor": 0.6, "blog": 0.4, "social": 0.3, "web": 0.5,
    }
    for r in results:
        base = tier_scores.get(r.get("source_type", "web"), 0.5)
        r["credibility_score"] = round(base * r.get("relevance", 0.5), 3)
    return sorted(results, key=lambda x: x["credibility_score"], reverse=True)


def detect_freshness(result: dict):
    """Assess freshness of a search result."""
    # In production, parse dates from result metadata
    return {"fresh": True, "confidence": 0.7, "assessment": "standard"}


async def verify_across_sources(claim: str, results: list):
    """Cross-reference a claim across multiple sources."""
    supporting = []
    conflicting = []
    for r in results:
        snippet = r.get("snippet", "").lower()
        if any(word in snippet for word in claim.lower().split()[:3]):
            supporting.append(r.get("url", "unknown"))
        else:
            conflicting.append(r.get("url", "unknown"))

    total = len(supporting) + len(conflicting)
    confidence = len(supporting) / max(total, 1)

    status = "verified" if confidence > 0.7 else "likely" if confidence > 0.4 else "unconfirmed"
    if conflicting and supporting:
        status = "conflicting"

    return {
        "claim": claim, "status": status, "confidence": round(confidence, 2),
        "supporting_sources": supporting, "conflicting_sources": conflicting,
    }


async def search_and_rank(query: str, freshness: str = "standard"):
    """Full pipeline: search → rank → freshness check."""
    raw = await execute_search(query, freshness)
    ranked = rank_sources(raw["results"])
    for r in ranked:
        r["freshness"] = detect_freshness(r)
    return {"query": query, "results": ranked, "total": len(ranked), "source": raw["source"]}
