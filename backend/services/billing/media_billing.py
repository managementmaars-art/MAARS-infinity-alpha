"""Wallet reserve+settle helper for media (image/video/tts/stt) endpoints.

Mirrors the v1_gateway chat billing pattern:
 1. Estimate credits upfront via media_credit_cost()
 2. Reserve that amount (fail fast with 402 if wallet can't cover)
 3. Run the actual provider call via the caller-supplied router function
 4. Settle for the router's reported actual cost (refunds the delta or debits overage)

Returns (result, router_meta, billing_dict). The endpoint passes `billing` back
to the caller in the response so the UI can show `reserved / actual / refunded`.
"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Callable
from fastapi import HTTPException

from services.llm_service import media_credit_cost
from services.billing import wallet_service

logger = logging.getLogger(__name__)


# Modality labels used by the media router don't perfectly match canonical
# credit-bucket names (TTS bills against the `voice` pool). Map explicitly.
_MODALITY_TO_BUCKET = {
    "image":     "image",
    "video":     "video",
    "tts":       "voice",
    "voiceover": "voice",
    "stt":       "stt",
}


async def bill_and_run(
    user_id: str,
    modality: str,          # "image" | "video" | "tts" | "stt"
    model_estimate: str,    # model we expect the router to pick (cost lookup)
    units_estimate: float,  # 1 image / N seconds / N chars / N sec audio
    router_coro_factory: Callable[..., Any],
    **router_kwargs,
) -> tuple[Any, dict, dict]:
    """Reserve → run → settle. Raises HTTPException(402) if wallet can't cover
    the upfront estimate."""

    estimate = media_credit_cost(modality, model_estimate, units_estimate)
    ref_id = f"{modality}_{uuid.uuid4().hex[:12]}"
    bucket = _MODALITY_TO_BUCKET.get(modality, "general")

    reserve_result = await wallet_service.reserve(
        user_id, estimate,
        reference_id=ref_id,
        description=f"Reserve for {modality} ({model_estimate}, {units_estimate} units)",
        metadata={"modality": modality, "model_estimate": model_estimate,
                  "units_estimate": units_estimate, "bucket": bucket},
        bucket=bucket,
        source=f"media_{modality}",
    )
    if reserve_result is None:
        raise HTTPException(status_code=402, detail={
            "error": {
                "message": (f"Insufficient credits for {modality}. Requires "
                            f"~{estimate} credits. Top up your balance or choose a "
                            f"cheaper path."),
                "type": "insufficient_credits",
                "code": "insufficient_credits",
                "credits_required": estimate,
                "modality": modality,
            }
        })

    try:
        result, meta = await router_coro_factory(**router_kwargs)
    except Exception:
        # Release the reserve fully — nothing was consumed on the provider side.
        try:
            await wallet_service.settle(
                user_id,
                reserved_amount=estimate,
                actual_amount=0,
                reference_id=ref_id,
                description=f"Refund {modality} (provider call failed)",
                metadata={"modality": modality, "failed": True, "bucket": bucket},
                bucket=bucket,
            )
        except Exception as settle_err:
            logger.error(f"settle on failure failed for {ref_id}: {settle_err}")
        raise

    actual = int(meta.get("cost_credits") or estimate)
    wallet_after = await wallet_service.settle(
        user_id,
        reserved_amount=estimate,
        actual_amount=actual,
        reference_id=ref_id,
        description=f"Settle {modality} ({meta.get('provider')}/{meta.get('model')})",
        metadata={"modality": modality, "router_meta": meta, "bucket": bucket},
        bucket=bucket,
    )
    # Treasury: debit real COGS from the operator's reserve pool so the
    # operator's profit/COGS dashboard stays accurate per-call (no
    # manual reconciliation needed). Fire-and-forget.
    try:
        from services.billing import treasury
        cost_usd = float(meta.get("cost_usd") or 0.0)
        if cost_usd > 0:
            await treasury.on_api_call_billed(
                actual_cost_usd=cost_usd,
                provider=meta.get("provider") or "media",
                user_id=user_id,
                model=meta.get("model"),
                reference_id=ref_id,
            )
    except Exception as tex:
        logger.info("treasury media debit skipped for %s: %s", ref_id, tex)

    # Unified token quota — debit the CLIENT's single token pool by the
    # token-equivalent of this media call's USD cost. Keeps the user
    # experience unified (one "credits remaining" number drops regardless
    # of whether the request was chat, image, or video).
    try:
        from services.billing import token_quota
        cost_usd = float(meta.get("cost_usd") or 0.0)
        if cost_usd > 0:
            equiv_tokens = token_quota.cost_usd_to_tokens(cost_usd)
            if equiv_tokens > 0:
                await token_quota.settle_tokens(
                    user_id,
                    reserved_tokens=equiv_tokens,
                    actual_tokens=equiv_tokens,
                    reference_id=ref_id,
                    source=f"media_{modality}",
                    provider=meta.get("provider"),
                    model=meta.get("model"),
                    cost_usd=cost_usd,
                )
    except Exception as tqx:
        logger.info("token_quota media debit skipped for %s: %s", ref_id, tqx)
    billing = {
        "reference_id": ref_id,
        "reserved_credits": estimate,
        "actual_credits": actual,
        "refunded_credits": max(0, estimate - actual),
        "wallet": wallet_after,
    }
    return result, meta, billing
