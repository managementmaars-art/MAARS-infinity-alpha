"""Runtime feature flags — toggle gateway behavior without redeploy.

All the optimizations we just built have on/off semantics at runtime:
  - semantic_cache: on by default, off for a specific user (debug)
  - hedged_requests: on for interactive, off for batch
  - verify (CoV): opt-in per call
  - moa: opt-in per call
  - output_guard: on; can be bypassed for trusted internal callers
  - structured_output schema enforcement: per-route

We keep a simple JSON-doc store in Mongo (`feature_flags` collection)
with one doc per flag. Each doc supports:
  - default_value     : bool / string
  - user_overrides    : {user_id: value}
  - percentage        : int 0-100 for stable-hash gradual rollout
  - updated_at, updated_by (audit)

Read path is lru_cached with a 30-second TTL so high-frequency lookups
don't hammer Mongo.

Write path is via admin endpoints (to be added under `routes/admin.py`).
"""
from __future__ import annotations
import hashlib
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

_cache: dict[str, tuple[Any, float]] = {}
_CACHE_TTL = 30  # seconds


DEFAULTS: dict[str, Any] = {
    "semantic_cache_enabled":     True,
    "hedged_requests_enabled":    True,
    "cov_verify_opt_in":          True,
    "moa_enabled":                True,
    "output_guard_enabled":       True,
    "pii_scrub_enabled":          True,
    "injection_detect_enabled":   True,
    "conversation_summarize":     True,
    "context_packing":            True,
    "dual_classifier_enabled":    False,  # opt-in; adds cost
    "bandit_routing_enabled":     False,  # opt-in while we build up samples
    "drift_detector_enabled":     True,
    "batch_api_opt_in":           True,
}


async def _load_from_db(name: str) -> dict[str, Any]:
    try:
        from db import db
        doc = await db.feature_flags.find_one({"_id": name})
    except Exception:
        return {}
    return doc or {}


def _stable_bucket(user_id: str, flag: str) -> int:
    """0-99. Stable — same user+flag always maps to the same bucket.
    Used for percentage rollouts."""
    h = hashlib.md5(f"{flag}:{user_id}".encode()).digest()
    return h[0] % 100


async def is_enabled(flag: str, *, user_id: str | None = None) -> bool:
    """Main read API. Returns True/False, respects overrides + percentage."""
    now = time.time()
    cached = _cache.get(flag)
    if cached and now - cached[1] < _CACHE_TTL:
        doc = cached[0]
    else:
        doc = await _load_from_db(flag)
        _cache[flag] = (doc, now)

    default = DEFAULTS.get(flag, False)

    if not doc:
        return bool(default)

    # Per-user override takes highest precedence.
    if user_id and "user_overrides" in doc:
        overrides = doc.get("user_overrides") or {}
        if user_id in overrides:
            return bool(overrides[user_id])

    # Percentage rollout.
    pct = doc.get("percentage")
    if isinstance(pct, (int, float)) and user_id:
        return _stable_bucket(user_id, flag) < pct

    return bool(doc.get("default_value", default))


async def get_value(flag: str, *, user_id: str | None = None, default: Any = None) -> Any:
    """For non-boolean flags (strings, ints). Returns the configured value or `default`."""
    doc = (await _load_from_db(flag)) or {}
    if user_id and "user_overrides" in doc:
        ov = doc["user_overrides"].get(user_id)
        if ov is not None:
            return ov
    return doc.get("default_value", default if default is not None else DEFAULTS.get(flag))


async def set_flag(
    name: str, *,
    default_value: Any = None,
    user_overrides: dict | None = None,
    percentage: int | None = None,
    updated_by: str = "admin",
) -> dict[str, Any]:
    """Write a flag. Partial updates supported via non-None fields."""
    from db import db
    from datetime import datetime, timezone
    update: dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat(), "updated_by": updated_by}
    if default_value is not None:
        update["default_value"] = default_value
    if user_overrides is not None:
        update["user_overrides"] = user_overrides
    if percentage is not None:
        update["percentage"] = max(0, min(100, int(percentage)))
    await db.feature_flags.update_one({"_id": name}, {"$set": update}, upsert=True)
    _cache.pop(name, None)
    return update
