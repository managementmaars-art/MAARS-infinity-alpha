"""MAARS — Governance: Trust Scoring Engine.

0-100 trust score per agent / tool / model, computed from four canonical
dimensions (per product catalog):

    success      — fraction of tasks that completed successfully without
                   escalation or rollback.
    latency      — normalized responsiveness. 1.0 = responses arrive at or
                   below the target latency budget; drops toward 0 as
                   responses overshoot the budget.
    quality      — verification-consensus output quality, 0.0–1.0.
    consistency  — inverse variance of recent trust scores. A stable agent
                   scores high; a swingy one scores low.

Composite score (0-100):

    0.40 * success  +  0.30 * quality  +  0.20 * latency  +  0.10 * consistency

Factors are held in the `trust_scores` collection alongside the rolling
history that powers the consistency calculation. Update events are
smoothed with exponential-moving-average so no single observation can spike
the score. The `update_trust_score` function accepts both the new
canonical fields (`success`, `latency_ms`, `quality`) and the legacy
fields (`verification_passed`, `useful`, `cost_efficient`, `had_incident`)
so callers can migrate incrementally.
"""

from datetime import datetime, timezone
from db import db

TRUST_COLLECTION = "trust_scores"

# Target latency in ms — responses at or below this score 1.0 on latency.
LATENCY_BUDGET_MS = 8000
# Exponential-moving-average decay for factor updates (higher = slower to move).
EMA_ALPHA = 0.1
# Factor weights — must sum to 1.0.
WEIGHTS = {"success": 0.40, "quality": 0.30, "latency": 0.20, "consistency": 0.10}
# How many recent score observations feed the consistency computation.
CONSISTENCY_WINDOW = 20


def _default_factors() -> dict:
    return {
        "success":     0.5,
        "latency":     0.5,
        "quality":     0.5,
        "consistency": 1.0,   # starts perfect; degrades with variance
    }


def _ema(old: float, observation: float, alpha: float = EMA_ALPHA) -> float:
    return round(old * (1 - alpha) + observation * alpha, 4)


def _latency_to_score(latency_ms: float) -> float:
    """Map a latency sample in milliseconds to a 0.0–1.0 score."""
    if latency_ms is None or latency_ms <= 0:
        return 1.0
    if latency_ms <= LATENCY_BUDGET_MS:
        return 1.0
    # Decay: every additional budget-width of latency halves the score.
    over = latency_ms / LATENCY_BUDGET_MS
    return round(max(0.0, 1.0 / over), 4)


def _consistency_from_history(history: list[dict]) -> float:
    """Low variance in recent scores → high consistency (close to 1.0)."""
    if not history:
        return 1.0
    recent = [h.get("score", 50.0) for h in history[-CONSISTENCY_WINDOW:]]
    if len(recent) < 2:
        return 1.0
    mean = sum(recent) / len(recent)
    variance = sum((s - mean) ** 2 for s in recent) / len(recent)
    # Std-dev of 0 → consistency 1.0; std-dev of 25 (half the 0–100 range)
    # → consistency 0.0. Clamped.
    stddev = variance ** 0.5
    return round(max(0.0, min(1.0, 1.0 - stddev / 25.0)), 4)


async def get_trust_score(entity_type: str, entity_id: str):
    """Fetch the trust score document for an entity, creating a default if missing."""
    doc = await db[TRUST_COLLECTION].find_one(
        {"entity_type": entity_type, "entity_id": entity_id}, {"_id": 0}
    )
    if not doc:
        doc = {
            "entity_type":  entity_type,
            "entity_id":    entity_id,
            "score":        50.0,
            "factors":      _default_factors(),
            "history":      [],
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        await db[TRUST_COLLECTION].insert_one({**doc})
    return doc


async def update_trust_score(entity_type: str, entity_id: str, event: dict):
    """Apply a new observation to an entity's trust score.

    Canonical event fields (all optional):
        success     : bool   — task succeeded end-to-end
        latency_ms  : float  — observed latency in milliseconds
        quality     : float  — verification quality score in 0.0–1.0

    Legacy event fields (mapped onto canonical factors for back-compat):
        verification_passed : bool  → success
        had_incident        : bool  → success penalty
        useful              : bool  → quality
        cost_efficient      : bool  → quality (weaker weight)
    """
    current = await get_trust_score(entity_type, entity_id)
    factors = {**_default_factors(), **current.get("factors", {})}

    # ── Canonical fields ───────────────────────────────────────────────────
    if "success" in event and event["success"] is not None:
        factors["success"] = _ema(factors["success"], 1.0 if event["success"] else 0.0)
    if "latency_ms" in event and event["latency_ms"] is not None:
        factors["latency"] = _ema(factors["latency"], _latency_to_score(event["latency_ms"]))
    if "quality" in event and event["quality"] is not None:
        q = max(0.0, min(1.0, float(event["quality"])))
        factors["quality"] = _ema(factors["quality"], q)

    # ── Legacy fields (mapped) ─────────────────────────────────────────────
    if "verification_passed" in event and event["verification_passed"] is not None:
        factors["success"] = _ema(factors["success"], 1.0 if event["verification_passed"] else 0.0)
    if "had_incident" in event and event["had_incident"]:
        factors["success"] = _ema(factors["success"], 0.0, alpha=0.2)   # bigger nudge
    if "useful" in event and event["useful"] is not None:
        factors["quality"] = _ema(factors["quality"], 1.0 if event["useful"] else 0.0)
    if "cost_efficient" in event and event["cost_efficient"] is not None:
        factors["quality"] = _ema(factors["quality"], 1.0 if event["cost_efficient"] else 0.3, alpha=0.05)

    # ── Consistency is derived from score history, not event-driven ────────
    factors["consistency"] = _consistency_from_history(current.get("history", []))

    # ── Composite ──────────────────────────────────────────────────────────
    raw = sum(factors[k] * w for k, w in WEIGHTS.items()) * 100.0
    score = round(max(0.0, min(100.0, raw)), 1)

    history_entry = {"score": score, "timestamp": datetime.now(timezone.utc).isoformat()}

    await db[TRUST_COLLECTION].update_one(
        {"entity_type": entity_type, "entity_id": entity_id},
        {
            "$set":  {"score": score, "factors": factors, "last_updated": history_entry["timestamp"]},
            "$push": {"history": {"$each": [history_entry], "$slice": -100}},
        },
        upsert=True,
    )
    return {"entity_type": entity_type, "entity_id": entity_id, "score": score, "factors": factors}


async def get_trust_leaderboard(entity_type: str = "agent", limit: int = 20):
    """Top-scoring entities of a given type."""
    cursor = (
        db[TRUST_COLLECTION]
        .find({"entity_type": entity_type}, {"_id": 0, "history": 0})
        .sort("score", -1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def get_low_trust_entities(entity_type: str = None, threshold: float = 30.0):
    """Entities below a trust threshold — flagged for operator review."""
    query: dict = {"score": {"$lt": threshold}}
    if entity_type:
        query["entity_type"] = entity_type
    cursor = db[TRUST_COLLECTION].find(query, {"_id": 0, "history": 0})
    return await cursor.to_list(length=50)
