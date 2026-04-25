"""Shadow / mirror / canary traffic.

Three related patterns we combine in one module:

  MIRROR   — fire-and-forget: for N% of production calls, duplicate
             the request to a SHADOW candidate (different provider or
             prompt). Don't return the shadow result to the user; just
             log it. Over a few thousand calls this builds ground
             truth to support routing decisions with ZERO user risk.
  CANARY   — gradually ramp a new route from 1% → 5% → 25% → 100%.
             Paired with error_budget + drift_detector: if the canary
             fires too many errors or quality regresses, auto-rollback.
  A/B TEST — two arms, each gets deterministic traffic share. Used when
             you want conclusive data on (arm_a vs arm_b).

All three sit on top of feature_flags + stable user-bucket hashing.

Usage in `llm_gateway.complete()`:

    # after real call finishes:
    await shadow_traffic.maybe_mirror(
        user_id=user_id, messages=messages, real_response=data,
        real_provider=actual_provider,
    )
"""
from __future__ import annotations
import asyncio
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


async def _should_mirror(user_id: str) -> bool:
    from services import feature_flags as ff
    enabled = await ff.is_enabled("shadow_mirror_enabled", user_id=user_id)
    return bool(enabled)


async def maybe_mirror(
    *,
    user_id: str,
    messages: list[dict],
    model: str,
    real_response: dict,
    real_provider: str,
    shadow_model: str = "maars/economy",
    complete_fn=None,
) -> None:
    """If shadow traffic is enabled and the user is in the bucket,
    fire a second call in the background with `shadow_model` and log
    the pair for later judge-based evaluation. Never raises."""
    from services import feature_flags as ff
    if not await ff.is_enabled("shadow_mirror_enabled", user_id=user_id):
        return
    if shadow_model == model:
        return  # would only duplicate traffic without signal
    if complete_fn is None:
        # Lazy-import to avoid circular dependency
        from services.llm_gateway import complete as complete_fn  # noqa: F401

    async def _run_shadow():
        try:
            shadow_resp = await complete_fn(
                user_id, messages=messages, model=shadow_model,
                source="shadow_mirror", enable_cache=True,
                verify_injection=False,
                max_tokens=512,   # bounded — shadows shouldn't be expensive
            )
            try:
                from db import db
                await db.shadow_calls.insert_one({
                    "user_id": user_id,
                    "real_provider": real_provider,
                    "shadow_model": shadow_model,
                    "real_text": (real_response.get("choices", [{}])[0]
                                  .get("message", {}).get("content", ""))[:4000],
                    "shadow_text": (shadow_resp.get("choices", [{}])[0]
                                    .get("message", {}).get("content", ""))[:4000],
                    "real_credits": real_response.get("maars", {}).get("credits_used", 0),
                    "shadow_credits": shadow_resp.get("maars", {}).get("credits_used", 0),
                    "ts": time.time(),
                })
            except Exception as exc:
                logger.info("shadow log write failed: %s", exc)
        except Exception as exc:
            logger.info("shadow call errored (ignored): %s", exc)

    # Fire-and-forget; do not await.
    try:
        asyncio.create_task(_run_shadow())
    except RuntimeError:
        # No running loop — rare, but don't blow up.
        pass


async def canary_pick(
    *, user_id: str, flag: str, default: str, canary: str,
) -> str:
    """Stable-hash the user into a canary bucket. Returns `canary` if
    the user is inside the rollout percentage, else `default`."""
    from services import feature_flags as ff
    if await ff.is_enabled(flag, user_id=user_id):
        return canary
    return default
