"""MAARS — Intelligence: Search Engine with Source Ranking & Freshness Detection.
Uses DuckDuckGo for real web search, with cache layer and source ranking."""

import hashlib
import asyncio
import logging
from datetime import datetime, timezone
from db import db

logger = logging.getLogger(__name__)

SEARCH_CACHE = "search_cache"
SEARCH_RESULTS = "search_results"
CACHE_TTL_SECONDS = 3600  # 1 hour


def _hash(q: str):
    return hashlib.md5(q.encode()).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat()


async def plan_query(goal: str, context: dict = None):
    """Plan search queries from a goal description. Returns structured query plan."""
    context = context or {}
    queries = []

    queries.append({"query": goal, "purpose": "primary", "priority": 1})

    if any(w in goal.lower() for w in ["competitor", "market", "industry"]):
        queries.append({"query": f"{goal} market share 2026", "purpose": "market_data", "priority": 2})
        queries.append({"query": f"{goal} latest news", "purpose": "freshness", "priority": 3})

    if any(w in goal.lower() for w in ["regulation", "compliance", "legal"]):
        queries.append({"query": f"{goal} regulatory update 2026", "purpose": "regulatory", "priority": 2})

    if any(w in goal.lower() for w in ["price", "cost", "pricing"]):
        queries.append({"query": f"{goal} pricing comparison", "purpose": "pricing", "priority": 2})

    return {"goal": goal, "queries": queries, "created_at": _now()}


async def _ddg_search(query: str, max_results: int = 5):
    """Execute real DuckDuckGo search."""
    try:
        from ddgs import DDGS

        def _search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=max_results))

        raw = await asyncio.to_thread(_search)
        results = []
        for r in raw:
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", r.get("snippet", "")),
                "url": r.get("href", r.get("link", "")),
                "relevance": 0.8,
                "source_type": _classify_source(r.get("href", "")),
            })
        return results
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed for '{query[:60]}': {e}")
        return []


def _classify_source(url: str) -> str:
    """Classify a URL into a source tier."""
    url_lower = url.lower()
    if any(d in url_lower for d in [".gov", ".edu", "who.int", "un.org"]):
        return "official"
    if any(d in url_lower for d in ["scholar.google", "arxiv.org", "pubmed", "ieee.org", "springer.com"]):
        return "academic"
    if any(d in url_lower for d in ["reuters.com", "bbc.com", "nytimes.com", "wsj.com", "bloomberg.com", "apnews.com"]):
        return "news_major"
    if any(d in url_lower for d in ["techcrunch.com", "wired.com", "arstechnica.com", "theverge.com", "forbes.com"]):
        return "industry"
    if any(d in url_lower for d in ["medium.com", "substack.com", "dev.to", "hashnode.dev"]):
        return "blog"
    if any(d in url_lower for d in ["twitter.com", "x.com", "reddit.com", "facebook.com"]):
        return "social"
    if any(d in url_lower for d in ["wikipedia.org"]):
        return "encyclopedia"
    return "web"


async def execute_search(query: str, freshness_required: str = "standard"):
    """Execute a search query. Checks cache first, uses DuckDuckGo for live results."""
    qhash = _hash(query)

    # Check cache (skip for real_time freshness)
    if freshness_required != "real_time":
        cached = await db[SEARCH_CACHE].find_one({"query_hash": qhash}, {"_id": 0})
        if cached:
            return {"source": "cache", "results": cached["results"], "freshness": cached.get("freshness_score", 0.5)}

    # Real DuckDuckGo search
    results = await _ddg_search(query, max_results=6)
    freshness_score = 0.85 if results else 0.0

    if not results:
        # Fallback: return empty with note
        return {"source": "live", "results": [], "freshness": 0.0, "note": "No results found"}

    # Cache results
    await db[SEARCH_CACHE].update_one(
        {"query_hash": qhash},
        {"$set": {"query": query, "results": results, "freshness_score": freshness_score, "created_at": _now()}},
        upsert=True,
    )

    return {"source": "live", "results": results, "freshness": freshness_score}


def rank_sources(results: list):
    """Rank search results by credibility, relevance, and freshness."""
    tier_scores = {
        "official": 1.0, "academic": 0.95, "news_major": 0.9, "encyclopedia": 0.85,
        "industry": 0.8, "news_minor": 0.65, "blog": 0.45, "social": 0.3, "web": 0.5,
    }
    for r in results:
        base = tier_scores.get(r.get("source_type", "web"), 0.5)
        relevance = r.get("relevance", 0.5)
        snippet_len = len(r.get("snippet", ""))
        length_bonus = min(snippet_len / 500, 0.15)
        r["credibility_score"] = round(base * relevance + length_bonus, 3)
    return sorted(results, key=lambda x: x["credibility_score"], reverse=True)


def detect_freshness(result: dict):
    """Assess freshness of a search result based on content signals."""
    snippet = result.get("snippet", "").lower()
    import re
    year_matches = re.findall(r'202[4-9]', snippet)
    has_recent_year = bool(year_matches)
    time_signals = any(w in snippet for w in ["today", "yesterday", "this week", "this month", "latest", "new", "just", "announced", "breaking"])
    if has_recent_year and time_signals:
        return {"fresh": True, "confidence": 0.9, "assessment": "very_fresh"}
    if has_recent_year or time_signals:
        return {"fresh": True, "confidence": 0.7, "assessment": "recent"}
    return {"fresh": False, "confidence": 0.4, "assessment": "unknown_age"}


async def verify_across_sources(claim: str, results: list):
    """Cross-reference a claim across multiple sources."""
    claim_words = [w for w in claim.lower().split() if len(w) > 3][:5]
    supporting = []
    conflicting = []
    for r in results:
        snippet = r.get("snippet", "").lower()
        title = r.get("title", "").lower()
        combined = snippet + " " + title
        matches = sum(1 for w in claim_words if w in combined)
        threshold = max(len(claim_words) // 2, 1)
        if matches >= threshold:
            supporting.append({"url": r.get("url", "unknown"), "title": r.get("title", ""), "match_score": matches / max(len(claim_words), 1)})
        else:
            conflicting.append({"url": r.get("url", "unknown"), "title": r.get("title", "")})

    total = len(supporting) + len(conflicting)
    confidence = len(supporting) / max(total, 1)

    if confidence >= 0.7:
        status = "verified"
    elif confidence >= 0.4:
        status = "likely"
    elif supporting and conflicting:
        status = "conflicting"
    else:
        status = "unconfirmed"

    return {
        "claim": claim, "status": status, "confidence": round(confidence, 2),
        "supporting_sources": supporting, "conflicting_sources": conflicting,
        "total_sources_checked": total,
    }


async def search_and_rank(query: str, freshness: str = "standard"):
    """Full pipeline: search → rank → freshness check."""
    raw = await execute_search(query, freshness)
    ranked = rank_sources(raw["results"])
    for r in ranked:
        r["freshness"] = detect_freshness(r)
    return {"query": query, "results": ranked, "total": len(ranked), "source": raw["source"]}
