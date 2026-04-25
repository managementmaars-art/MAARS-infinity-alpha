"""MAARS Universal AI Gateway — the single router for every LLM chat call.

Use this from any internal caller that needs a chat-completion. It does
exactly what POST /api/v1/chat/completions does, minus the HTTP-facade
concerns (API-key auth, rate limits, budget envelope). Internal callers
already have a user_id from JWT; the wallet + router + usage-log path is
identical.

Before this module existed, internal code used `services.llm_service.call_direct_llm`
which dropped every call into a provider request with ZERO billing or logging.
That made /admin/gateway show "Total Calls: 0" even while the system was
serving real client traffic (Audit 014).

Public surface:
    complete(user_id, messages, model="maars/auto", *, ...) -> OpenAI-compat dict

Response shape matches /v1/chat/completions:
    {
      "id": "chatcmpl-maars-...",
      "model": "maars/auto",
      "provider": "gemini",
      "choices": [{"index": 0, "message": {"role": "assistant", "content": "..."},
                   "finish_reason": "stop"}],
      "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
      "maars": {
        "credits_used": N, "credits_remaining": M,
        "routing_mode": "alias" | "manual",
        "routing_reason": "maars/auto routed to gemini/gemini-2.5-flash",
        "model": "maars/auto", "provider": "gemini",
        "source": "chats.send_message"  # tags who initiated internally
      }
    }
"""
from __future__ import annotations
import asyncio
import logging
import math
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from db import db
from shared.utils import get_api_keys
from shared.constants import CREDITS_PER_USD
from services.billing import wallet_service
from services.routing import router as bandit_router
from services import (
    token_counter,
    prompt_cache_helper,
    semantic_cache,
    circuit_breaker,
    rate_limit_headers,
    request_coalesce,
    pii_scrubber,
    prompt_injection_detector,
    prompt_formatter,
    sampling_tuner,
    dedup_idempotency,
    prometheus_metrics as pm,
    output_guard,
    daily_budget,
    feature_flags,
    conversation_summarizer,
    llmlingua_compress,
    shadow_traffic,
    otel_tracing,
)

logger = logging.getLogger(__name__)


async def complete(
    user_id: str,
    messages: list[dict],
    model: str = "maars/auto",
    *,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    task: Optional[str] = None,
    source: str = "internal",
    agent_id: Optional[str] = None,
    request_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
    tools: Optional[list[dict]] = None,
    stream: bool = False,
    enable_cache: bool = True,
    scrub_pii: bool = True,
    verify_injection: bool = True,
    speculative: bool = False,
    moa: bool = False,
    verify: bool = False,
    trust_score: str = "none",   # "none" | "auto" | "logprob" | "self_consistency"
    _quality_retry_depth: int = 0,
) -> dict[str, Any]:
    """Single entry point for every LLM chat call. See module docstring for shape.

    user_id      MAARS user that owns this request (for wallet + logging).
    messages     OpenAI-style [{"role":"system"|"user"|"assistant","content":"..."}].
    model        "maars/auto" (smart router) OR "provider/model" (manual pick).
    task         Optional task label for sampling defaults ("code_generation",
                 "reasoning_math", "summarization", etc.). Looked up only when
                 temperature is left as None.
    source       Free-form tag stored in gateway_usage_logs for attribution
                 (e.g. "chats.send_message", "vibe.create", "content.generate").
    idempotency_key  Optional — if sent, a replay with the same key for the same
                 user returns the cached response from the first call (24h TTL).
    enable_cache Set False to bypass the semantic cache (useful for tool calls,
                 chat sessions where each reply should be fresh).
    scrub_pii    If True (default), strips emails/phones/SSNs/cards from prompts
                 before sending to providers.
    verify_injection If True, prompts are scanned for jailbreak attempts; a
                 confirmed injection raises ValueError("injection_blocked").
    """
    req_id = request_id or f"chatcmpl-maars-{uuid.uuid4().hex[:16]}"
    start = time.time()
    has_tools = bool(tools)

    # ── 0. Idempotency replay — short-circuits the whole pipeline.
    if idempotency_key:
        cached = await dedup_idempotency.get_cached(idempotency_key, user_id)
        if cached is not None:
            pm.inc_cache_hit("idempotent")
            return cached

    # ── 0.5 Ensemble / speculative opt-ins.
    # These fan out to multiple complete() calls internally; each nested
    # call takes the normal pipeline. We dispatch and return here so the
    # rest of the pipeline (billing, cache) runs per-sub-call, not once.
    if moa:
        from services import mixture_of_agents
        return await mixture_of_agents.run(
            complete_fn=complete, user_id=user_id,
            messages=messages, source=source, max_tokens=max_tokens,
        )
    # Auto-enable cascade for the smart-router aliases (maars/auto, maars/smart).
    # For explicit tier picks (maars/premium, maars/economy, etc.) the caller
    # wants that tier, so don't second-guess with a cascade. Env override to
    # disable entirely: CASCADE_AUTO=0.
    import os
    _auto_cascade = (
        model in ("maars/auto", "maars/smart")
        and os.environ.get("CASCADE_AUTO", "1") != "0"
    )
    if speculative or _auto_cascade:
        from services import speculative as spec
        # Resolve user's plan tier for the escalation threshold. Premium
        # plans escalate aggressively (deliver quality); economy/free
        # plans prefer staying on the cheap arm (preserve margin). The
        # plan-keyword → tier mapping lives in shared/tier_config.py.
        tier = "standard"
        try:
            from db import db
            from shared.tier_config import resolve_tier_from_plan
            udoc = await db.users.find_one(
                {"user_id": user_id},
                {"_id": 0, "subscription_plan": 1, "plan_tier": 1},
            )
            plan_name = ((udoc or {}).get("plan_tier")
                         or (udoc or {}).get("subscription_plan")
                         or "")
            tier = resolve_tier_from_plan(plan_name)
        except Exception:
            pass
        return await spec.run(
            complete_fn=complete, user_id=user_id,
            messages=messages, source=source, max_tokens=max_tokens,
            tier=tier,
        )

    # ── 0a. Daily budget — hard cap independent of wallet balance.
    try:
        ok, spent, cap = await daily_budget.check(user_id)
        if not ok:
            pm.inc_errors("gateway", model, "daily_budget_exceeded")
            raise RuntimeError(
                f"daily_budget_exceeded: ${spent:.2f} of ${cap:.2f} spent today. Resets at 00:00 UTC."
            )
    except RuntimeError:
        raise
    except Exception as exc:
        logger.info("daily_budget check skipped: %s", exc)

    # ── 0a2. Per-agent monthly budget — reject when the agent's own cap is hit.
    # Runs before wallet reserve so a runaway agent can't drain the parent
    # wallet even if the daily budget has headroom. `agent_id=None` (legacy
    # callers) short-circuits to allow.
    agent_budget_state: dict[str, Any] = {}
    if agent_id:
        try:
            from services.agents import agent_budget as _ab
            agent_budget_state = await _ab.check(agent_id)
            if not agent_budget_state.get("allow", True):
                pm.inc_errors("gateway", model, "agent_budget_exceeded")
                raise RuntimeError(agent_budget_state.get("reason") or "agent_budget_exceeded")
        except RuntimeError:
            raise
        except Exception as exc:
            logger.info("agent_budget check skipped: %s", exc)

    # ── 0b. Prompt-injection scan — block malicious prompts up-front.
    if verify_injection and await feature_flags.is_enabled("injection_detect_enabled", user_id=user_id):
        ij = prompt_injection_detector.scan_messages(messages)
        if prompt_injection_detector.should_block(ij):
            pm.inc_errors("gateway", model, "injection_blocked")
            raise ValueError(f"injection_blocked: {ij.matched[:3]}")

    # ── 0c. PII scrub — keep emails / cards / SSNs out of provider logs.
    redacted_count = 0
    if scrub_pii and await feature_flags.is_enabled("pii_scrub_enabled", user_id=user_id):
        messages, redacted_count = pii_scrubber.scrub_messages(messages)

    # ── 0c1. Smart max_tokens cap — if the caller didn't set one, cap
    # to an appropriate value based on detected task complexity. A
    # two-word "hi" doesn't need a 4096-token response budget burning
    # credits for nothing. Easy prompts cap low; hard prompts keep
    # the original None (let the model decide).
    if max_tokens is None:
        try:
            from services.routing.task_classifier import classify
            _last_user = next((m.get("content", "") for m in reversed(messages)
                               if m.get("role") == "user"), "")
            if isinstance(_last_user, str):
                _cx = classify(_last_user, messages=messages)
                max_tokens = int(_cx["suggested_max_tokens"])
        except Exception as exc:
            logger.info("smart max_tokens cap skipped: %s", exc)

    # ── 0c2. Long-conversation compaction — summarize older turns.
    if await feature_flags.is_enabled("conversation_summarize", user_id=user_id):
        try:
            messages, _compact_info = await conversation_summarizer.maybe_compact(
                messages, complete_fn=complete, user_id=user_id,
            )
        except Exception as exc:
            logger.info("conversation compact skipped: %s", exc)

    # ── 0c3. Prompt compression — shrink long system/tool context.
    if await feature_flags.is_enabled("context_packing", user_id=user_id):
        try:
            messages, chars_saved = llmlingua_compress.compress_messages(messages)
            if chars_saved > 0:
                pm.inc_cache_hit("prompt_compressed")
        except Exception as exc:
            logger.info("compression skipped: %s", exc)

    # ── 0d. Sampling defaults — fill temperature/top_p based on task label.
    if task is None:
        # Cheap keyword inference from the user message.
        user_text = " ".join((m.get("content") or "") for m in messages if m.get("role") == "user")
        task = sampling_tuner.infer_task(user_text)
    temperature, top_p = sampling_tuner.resolve(
        task=task, user_temperature=temperature, user_top_p=top_p,
    )

    # ── 0e. Semantic cache lookup (exact + embedding) — only for deterministic calls.
    if enable_cache and await feature_flags.is_enabled("semantic_cache_enabled", user_id=user_id):
        cached_resp = await semantic_cache.lookup(
            model=model, messages=messages,
            temperature=temperature, has_tools=has_tools, stream=stream,
        )
        if cached_resp is not None:
            pm.inc_cache_hit(cached_resp.get("maars", {}).get("cache", "semantic"))
            if idempotency_key:
                await dedup_idempotency.store_cached(idempotency_key, user_id, cached_resp, credits_charged=0)
            # Log the cache hit so the Cost Health dashboard sees it. We
            # write a zero-cost row with `from_cache=True` so the
            # cache_hit_pct metric reflects reality.
            try:
                from db import db
                await db.gateway_usage_logs.insert_one({
                    "log_id":       f"gw_{str(user_id)[:8]}_{int(time.time()*1000)}",
                    "user_id":      user_id,
                    "agent_id":     agent_id,
                    "key_prefix":   "cache",
                    "maars_model":  model,
                    "provider":     "cache",
                    "native_model": cached_resp.get("maars", {}).get("cache", "semantic"),
                    "cost_usd":     0.0,
                    "billed_usd":   0.0,
                    "markup_pct":   0.0,
                    "billing_mode": "internal",
                    "latency_ms":   int((time.time() - start) * 1000),
                    "streamed":     False,
                    "prompt_words": 0,
                    "source":       source,
                    "timestamp":    datetime.now(timezone.utc).isoformat(),
                    "credits_charged": 0,
                    "from_cache":   True,
                })
            except Exception as log_exc:
                logger.info("cache-hit log skipped: %s", log_exc)
            return cached_resp

    # ── 0e2. Skill-reuse cache — per-agent replay of successful responses.
    # Narrower than the semantic cache: scoped to a single agent and keyed
    # on canonical prompt shape, so repetitive agent flows (same template,
    # new inputs) cut token spend to zero on a hit. Only fires when the
    # caller supplied agent_id and the call is deterministic.
    if enable_cache and agent_id and not has_tools and not stream:
        try:
            from services import skill_cache
            cached_skill = await skill_cache.lookup(
                agent_id=agent_id, model=model, messages=messages,
                temperature=temperature,
            )
            if cached_skill is not None:
                pm.inc_cache_hit("skill")
                if idempotency_key:
                    await dedup_idempotency.store_cached(
                        idempotency_key, user_id, cached_skill, credits_charged=0,
                    )
                return cached_skill
        except Exception as exc:
            logger.info("skill_cache lookup skipped: %s", exc)

    # ── Content moderation — fast keyword scan + OpenAI classifier.
    # Runs BEFORE any provider call so unsafe prompts never leave our
    # infrastructure. Fail-open on network errors (the keyword layer
    # already caught the obvious). Internal/system callers bypass.
    if source not in ("prompt_enhancer", "campaign_personalize", "internal_system"):
        prompt_for_mod = " ".join(
            (m.get("content") or "") for m in messages if m.get("role") in ("user", "system")
        )
        try:
            from services.content_moderation import moderate_text
            ok, reason = await moderate_text(prompt_for_mod)
            if not ok:
                raise ValueError(f"content_blocked: {reason}")
        except ValueError:
            raise
        except Exception:
            pass  # fail-open; never block on moderation infra failure

    # ── Resolve model → (provider, native_model_id) via the v1 gateway's own logic.
    # This guarantees one code path owns routing decisions.
    from routes.v1_gateway import (
        _MAARS_ALIASES, _resolve_maars_alias, _parse_model_id,
        _provider_has_key, _api_key_for_provider, _call_with_fallback,
        _get_pricing, _estimate_cost,
    )

    api_keys = await get_api_keys()

    # Extract the user-visible prompt text for token estimation + routing.
    prompt_text = " ".join(
        (m.get("content") or "") for m in messages if m.get("role") == "user"
    ) or (messages[-1].get("content") if messages else "")

    # Estimate wallet budget. Same formula as v1 gateway.
    credits_budget = 0  # gateway routing uses this only for alias tier selection
    try:
        wallet = await wallet_service.get_summary(user_id)
        credits_budget = int(wallet.get("balance_credits", 0))
    except Exception:
        credits_budget = 0

    if model in _MAARS_ALIASES:
        provider, native_model_id = await _resolve_maars_alias(
            model, prompt_text, credits_budget, api_keys, user_id=user_id,
        )
        maars_model = model
    else:
        entry = _parse_model_id(model)
        if not entry:
            raise ValueError(f"Unknown model '{model}'. Use maars/auto or provider/model.")
        _, provider, native_model_id, _, _ = entry
        maars_model = entry[0]
        if not _provider_has_key(api_keys, provider):
            raise RuntimeError(f"Provider '{provider}' is not configured on this gateway.")

    api_key = _api_key_for_provider(api_keys, provider)

    # ── Wallet reserve — token-aware estimate.
    native_key = (native_model_id or "").split("/")[-1]
    pricing = _get_pricing(native_key)
    # Accurate token count via tiktoken (was: len(text.split()) * 1.3).
    try:
        est_input_tokens = max(
            token_counter.count_messages(messages, provider=provider, model=native_key),
            10,
        )
    except Exception:
        est_input_tokens = max(int(len((prompt_text or "").split()) * 1.3), 10)
    est_output_tokens = int(max_tokens or 4096)
    est_cost_usd = (
        pricing["input"] * est_input_tokens +
        pricing["output"] * est_output_tokens
    ) / 1_000_000
    credits_estimate = max(1, math.ceil(est_cost_usd * CREDITS_PER_USD))

    # Route the reserve into the right bucket based on the source tag
    # (e.g. "vibe.create" → vibe, "office_sop:*" → agent_sop). Falls
    # through to general if the source is unrecognized.
    reserve_result = await wallet_service.reserve(
        user_id, credits_estimate,
        reference_id=req_id,
        description=f"Reserve for {maars_model} via {provider}/{native_model_id} ({source})",
        metadata={
            "provider": provider, "native_model": native_model_id,
            "maars_model": maars_model, "source": source,
            "agent_id": agent_id,
        },
        source=source,
    )
    if reserve_result is None:
        raise RuntimeError(
            f"Insufficient credits. Requires {credits_estimate} credit(s). "
            f"Top up your balance or choose maars/economy."
        )

    # Unified token quota — the HARD CAP on client spend across all
    # providers. Estimate total tokens (input + expected output) and
    # reserve them. If the user would exceed their plan token quota,
    # we refund the credit reserve and fail the request with 402.
    _est_total_tokens = int(est_input_tokens) + int(est_output_tokens)
    try:
        from services.billing import token_quota
        _tq_reserved = await token_quota.reserve_tokens(
            user_id, _est_total_tokens,
            reference_id=req_id, source=source,
        )
        if _tq_reserved is None:
            # Hard cap hit — roll back the credit reserve so we don't leak.
            try:
                await wallet_service.refund(
                    user_id, reserved_amount=credits_estimate,
                    reference_id=req_id,
                    description="Token quota exceeded — auto-refund",
                )
            except Exception:
                pass
            raise RuntimeError(
                f"You've used this period's credit quota. "
                f"Wait for renewal or upgrade your plan."
            )
    except RuntimeError:
        raise
    except Exception as tqrx:
        # Token quota service failed — log but don't block the call.
        # (We still have the bucket-based credit reserve above as the floor.)
        logger.info("token_quota reserve skipped for %s: %s", req_id, tqrx)

    routing_mode = "alias" if model in _MAARS_ALIASES else "manual"
    routing_reason = (
        f"{model} routed to {provider}/{native_model_id}"
        if routing_mode == "alias"
        else f"caller-selected {provider}/{native_model_id}"
    )

    # ── Circuit breaker — fail fast if this provider is tripped.
    if not circuit_breaker.allow(provider):
        await wallet_service.settle(
            user_id, reserved_amount=credits_estimate, actual_amount=0,
            reference_id=req_id,
            description=f"Circuit breaker open for {provider}",
            metadata={"provider": provider, "source": source},
        )
        pm.inc_errors(provider, native_model_id, "circuit_open")
        raise RuntimeError(f"Provider '{provider}' circuit breaker is open — retry in a moment.")

    # ── Rate-limit header check — don't hit a provider we know is throttled.
    ok, reason = rate_limit_headers.budget_ok(provider, required_tokens=est_input_tokens + est_output_tokens)
    if not ok:
        logger.info("rate_limit preflight skip %s: %s", provider, reason)
        pm.inc_errors(provider, native_model_id, "rl_preflight")

    # ── LLMLingua-style compression on paid providers with long prompts.
    # Free providers (Gemini, Groq, etc.) don't need compression — token
    # cost is zero. For paid providers, compress system/tool messages
    # >= 2000 chars at 2x ratio. Quality loss <3% per LLMLingua paper.
    from shared.free_providers import FREE_PROVIDERS as _FREE_PROVIDERS
    if provider not in _FREE_PROVIDERS:
        try:
            compressed, chars_saved = llmlingua_compress.compress_messages(
                messages, min_chars=2000, ratio_target=2.0,
            )
            if chars_saved > 0:
                messages = compressed
                logger.info("llmlingua compressed %d chars for %s", chars_saved, provider)
        except Exception as exc:
            logger.info("llmlingua compression skipped: %s", exc)

    # ── Provider-specific prompt shaping + cache-control markers.
    shaped = prompt_formatter.shape(messages, provider=provider, model=native_model_id)
    shaped = prompt_cache_helper.annotate(shaped, provider=provider, model=native_model_id)

    # ── Build params + provider call.
    params: dict[str, Any] = {}
    if max_tokens is not None:
        params["max_tokens"] = max_tokens
    if temperature is not None:
        params["temperature"] = temperature
    if top_p is not None and top_p < 1.0:
        params["top_p"] = top_p
    if tools:
        params["tools"] = tools

    # Request logprobs on the FIRST attempt so confidence_router.assess()
    # has a real signal (not just hedge-phrase heuristics). Only set on
    # providers that expose logprobs + only for cheap-tier calls where
    # escalation is possible — skipping for premium-tier to save tokens.
    # The quality gate at line ~683 reads these and decides whether to
    # silently re-run on a stronger model.
    if _quality_retry_depth == 0 and routing_mode == "auto":
        try:
            from services.routing.confidence_router import enable_logprobs_for_params
            params = enable_logprobs_for_params(params, provider=provider)
        except Exception:
            pass  # never block the call over a logprobs flag

    async def _producer():
        with otel_tracing.span(
            "provider.call", provider=provider, model=native_model_id,
            has_tools=has_tools, stream=stream,
        ):
            return await _call_with_fallback(
                provider, native_model_id, shaped, api_key, params, api_keys
            )

    try:
        (data, actual_provider, actual_model, _warning), was_coalesced = await request_coalesce.coalesce(
            model=f"{provider}/{native_model_id}",
            messages=shaped,
            temperature=temperature,
            max_tokens=max_tokens,
            producer=_producer,
            has_tools=has_tools,
            stream=stream,
        )
        circuit_breaker.record_success(provider)
        if was_coalesced:
            pm.inc_cache_hit("coalesced")
    except Exception as exc:
        circuit_breaker.record_failure(provider, error=str(exc))
        pm.inc_errors(provider, native_model_id, type(exc).__name__)
        bandit_router.record(
            f"{provider}/{native_model_id}", success=False,
            latency_ms=(time.time() - start) * 1000, credits=0,
        )
        # Feed aggregator-level failures into the warm-pool breaker so
        # persistent outages exclude that aggregator from routing for a
        # cool-off window (default 2 min) without waiting for the bandit
        # posterior to drift.
        try:
            from services.routing.aggregator_candidates import record_aggregator_error
            if provider in ("huggingface", "openrouter", "bytez",
                            "together", "fireworks", "novita"):
                record_aggregator_error(provider)
        except Exception:
            pass
        try:
            await wallet_service.settle(
                user_id, reserved_amount=credits_estimate, actual_amount=0,
                reference_id=req_id,
                description=f"Provider error refund: {type(exc).__name__}",
                metadata={"provider": provider, "native_model": native_model_id,
                          "error": str(exc)[:500], "source": source},
            )
        except Exception as refund_exc:
            logger.warning("wallet refund failed for %s: %s", req_id, refund_exc)
        raise

    latency_ms = int((time.time() - start) * 1000)

    # ── Compute actual cost from real tokens (or estimate if provider didn't report).
    usage = data.get("usage", {}) or {}
    pt = usage.get("prompt_tokens") or est_input_tokens
    ct = usage.get("completion_tokens") or 0
    cost_info = _get_pricing(actual_model)
    cost_usd = round(
        (cost_info.get("input", 0.003) * pt + cost_info.get("output", 0.003) * ct)
        / 1_000_000, 8
    )

    # ── Wallet settle with real cost.
    act_cost_usd = (
        pricing["input"] * pt + pricing["output"] * ct
    ) / 1_000_000
    credits_actual = max(1, math.ceil(act_cost_usd * CREDITS_PER_USD))
    credits_actual = min(credits_actual, credits_estimate)

    credits_remaining = 0
    try:
        settle_result = await wallet_service.settle(
            user_id, reserved_amount=credits_estimate, actual_amount=credits_actual,
            reference_id=req_id,
            description=f"Inference via {actual_provider}/{actual_model} ({source})",
            metadata={
                "provider": actual_provider, "native_model": actual_model,
                "maars_model": maars_model, "latency_ms": latency_ms,
                "internal_cost_usd": cost_usd, "source": source,
                "fallback_used": actual_provider != provider,
            },
        )
        credits_remaining = settle_result.get("balance_credits", 0)
    except Exception as wallet_exc:
        logger.warning("wallet settle failed for %s: %s", req_id, wallet_exc)
        credits_remaining = reserve_result.get("balance_credits", 0) if reserve_result else 0

    # Treasury: debit real COGS from the operator's reserve pool. Fire-and-
    # forget (never blocks the user's response on our bookkeeping).
    try:
        from services.billing import treasury
        await treasury.on_api_call_billed(
            actual_cost_usd=float(act_cost_usd),
            provider=actual_provider,
            user_id=user_id, model=actual_model,
            reference_id=req_id,
        )
    except Exception as tex:
        logger.info("treasury debit skipped for %s: %s", req_id, tex)

    # Unified token quota: debit the CLIENT's single token pool by the
    # actual token count the provider reported. This is what the client
    # sees as "credits remaining" — one number, spendable anywhere across
    # the 33 providers. Fire-and-forget; never blocks the response.
    try:
        from services.billing import token_quota
        # Usage total from the provider response (standard OpenAI shape)
        usage_total = 0
        try:
            u = (data or {}).get("usage") or {}
            usage_total = int(u.get("total_tokens") or 0)
            if usage_total <= 0:
                pt = int(u.get("prompt_tokens") or u.get("input_tokens") or 0)
                ct = int(u.get("completion_tokens") or u.get("output_tokens") or 0)
                usage_total = pt + ct
        except Exception:
            usage_total = 0
        if usage_total <= 0:
            # Fallback: estimate via our cost model
            usage_total = max(1, int(act_cost_usd / token_quota.COST_USD_PER_TOKEN)) if act_cost_usd > 0 else 0
        if usage_total > 0:
            # Simple settle (no separate reserve — LLMs return usage AFTER call).
            # reserve==actual means: zero release, zero overage, pure debit.
            await token_quota.settle_tokens(
                user_id,
                reserved_tokens=usage_total,
                actual_tokens=usage_total,
                reference_id=req_id,
                source=source,
                provider=actual_provider,
                model=actual_model,
                cost_usd=float(act_cost_usd),
            )
    except Exception as tqx:
        logger.info("token_quota debit skipped for %s: %s", req_id, tqx)

    # ── Usage log — same collection the /admin/gateway dashboard reads from.
    # agent_id is required for per-agent budget aggregation
    # (services.agent_budget reads this collection as its counter).
    try:
        # Tag cascade outcome if this call came via speculative.run() so the
        # Cost Health dashboard escalation_pct metric is accurate.
        from db import db
        _spec = (data or {}).get("maars", {}).get("speculative") or {}
        await db.gateway_usage_logs.insert_one({
            "log_id":       f"gw_{str(user_id)[:8]}_{int(time.time()*1000)}",
            "user_id":      user_id,
            "agent_id":     agent_id,
            "key_prefix":   "internal",
            "maars_model":  maars_model,
            "provider":     actual_provider,
            "native_model": actual_model,
            "cost_usd":     cost_usd,
            "billed_usd":   cost_usd,
            "markup_pct":   0.0,
            "billing_mode": "internal",
            "latency_ms":   latency_ms,
            "streamed":     False,
            "prompt_words": len(prompt_text.split()) if prompt_text else 0,
            "source":       source,
            "timestamp":    datetime.now(timezone.utc).isoformat(),
            "credits_charged":     credits_actual,
            "fallback_used":       actual_provider != provider,
            "from_cache":          False,
            "cascade_outcome":     _spec.get("outcome"),
            "cascade_escalated":   _spec.get("outcome") in ("escalated", "premium_won"),
            # Non-zero when this call was itself a quality-gate retry
            # of an earlier lower-tier call. Lets the dashboard count
            # how often the gate fires.
            "quality_retry_depth": _quality_retry_depth,
        })
    except Exception as log_exc:
        logger.warning("usage log failed for %s: %s", req_id, log_exc)

    # ── Post-call quality gate — retry on a premium model if the
    # response is below this tier's acceptable quality floor. Fires at
    # most once per user-facing call so cost doesn't explode. Free tier
    # never triggers (no point — free customers don't pay for quality).
    # Economy/standard customers get a silent retry on Opus if their
    # cheap-model answer scored low confidence. The client sees only
    # the final (better) response; cost of the first attempt is eaten.
    if _quality_retry_depth == 0 and routing_mode == "auto":
        try:
            from services.routing.confidence_router import assess
            from shared.tier_config import min_quality as _tier_min_q
            # Re-resolve tier (cheaper than threading it through every code path).
            _user = await db.users.find_one({"user_id": user_id},
                                            {"_id": 0, "subscription_plan": 1, "plan_tier": 1})
            from shared.tier_config import resolve_tier_from_plan
            _tier_name = resolve_tier_from_plan(
                ((_user or {}).get("plan_tier") or (_user or {}).get("subscription_plan") or "")
            )
            # Only retry for economy/standard/premium — not free (cost) and not
            # already-premium (no higher to escalate to).
            if _tier_name in ("economy", "standard"):
                verdict = assess(data, tier=_tier_name)
                # Log EVERY assessment (not just escalations) so operator
                # can see gate-firing rate, score distribution, and tune
                # the escalation threshold based on real traffic.
                try:
                    await db.quality_gate_events.insert_one({
                        "ts":              time.time(),
                        "user_id":         user_id,
                        "tier":            _tier_name,
                        "score":           verdict.score,
                        "method":          verdict.method,
                        "should_escalate": verdict.should_escalate,
                        "reason":          verdict.reason,
                        "source":          source,
                        "model":           f"{provider}/{native_model_id}",
                    })
                except Exception:
                    pass  # never let telemetry block the hot path
                if verdict.should_escalate:
                    logger.info("quality gate escalating for %s: %s",
                                _tier_name, verdict.reason)
                    try:
                        better = await complete(
                            user_id, messages, model="maars/premium",
                            max_tokens=max_tokens, temperature=temperature,
                            top_p=top_p, task=task,
                            source=f"{source}__quality_retry",
                            agent_id=agent_id, request_id=None,
                            tools=tools, stream=False,
                            enable_cache=False, scrub_pii=False,
                            verify_injection=False, speculative=False,
                            moa=False, verify=False, trust_score="none",
                            _quality_retry_depth=1,
                        )
                        better.setdefault("maars", {})["quality_retry"] = {
                            "original_tier": _tier_name,
                            "reason":        verdict.reason,
                            "score":         verdict.score,
                        }
                        return better
                    except Exception as retry_exc:
                        logger.info("quality retry failed, returning original: %s", retry_exc)
        except Exception as gate_exc:
            logger.info("quality gate skipped: %s", gate_exc)

    # ── Normalize + inject MAARS metadata (same shape as /v1/chat/completions).
    # Client-opacity: when the caller requested a maars/* alias, we hide which
    # underlying provider actually served the request — lets the free-first
    # router silently route light/medium work to free tiers without revealing
    # the hop. When the caller specified a provider explicitly (manual mode),
    # we echo it back since they already know.
    data["id"] = req_id
    data["model"] = maars_model
    if routing_mode == "manual":
        data["provider"] = actual_provider
    else:
        data.pop("provider", None)
    data["maars"] = {
        "credits_used": credits_actual,
        "credits_remaining": credits_remaining,
        "routing_mode": routing_mode,
        "model": maars_model,
        "source": source,
        "latency_ms": latency_ms,
    }
    if routing_mode == "manual":
        data["maars"]["provider"] = actual_provider
        data["maars"]["routing_reason"] = routing_reason
    if agent_id:
        data["maars"]["agent_id"] = agent_id
        if agent_budget_state.get("throttled"):
            data["maars"]["agent_budget"] = {
                "throttled": True,
                "month_to_date": agent_budget_state.get("month_to_date"),
                "budget": agent_budget_state.get("budget"),
                "pct_used": round(float(agent_budget_state.get("pct_used") or 0), 3),
            }
    # Privacy-strip — match the v1 gateway's client-facing shape.
    data.pop("x_maars", None)
    data["usage"] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    # ── Trust score — opt-in response-level confidence signal.
    # Default "none" keeps the hot path untouched; "auto" uses logprobs
    # when the provider exposes them (free), falls back to a cheap
    # self-consistency sample otherwise.
    if trust_score != "none":
        try:
            from services import trust_scorer
            sys_prompt = next((m.get("content","") for m in messages if m.get("role")=="system"), "")
            usr_prompt = " ".join((m.get("content","") for m in messages if m.get("role")=="user"))
            ts = await trust_scorer.score(
                user_id=user_id, response=data,
                system_prompt=sys_prompt, user_prompt=usr_prompt,
                mode=trust_score,
            )
            if ts and ts.get("score") is not None:
                data.setdefault("maars", {})["trust"] = ts
        except Exception as exc:
            logger.info("trust_score skipped: %s", exc)

    # ── Output guard — scan response for leaks / unsafe content.
    if await feature_flags.is_enabled("output_guard_enabled", user_id=user_id):
        data = output_guard.guard_response(data)

    # ── Observability counters.
    pm.inc_requests(actual_provider, actual_model, source, "ok")
    pm.inc_credits(actual_provider, actual_model, source, credits_actual)
    pm.observe_latency(actual_provider, actual_model, latency_ms)
    pm.set_circuit_state(provider, circuit_breaker._get(provider).state)

    # ── Free-quota tracker: tick the provider's daily counter so the router
    # knows when to stop sending traffic here and pick the next free provider.
    try:
        from services import free_quota_tracker
        total_toks = int((usage.get("prompt_tokens") or 0) + (usage.get("completion_tokens") or 0))
        await free_quota_tracker.record(provider, tokens=total_toks)
    except Exception:
        pass

    # ── Bandit feedback — update posterior for this arm.
    bandit_router.record(
        f"{actual_provider}/{actual_model}", success=True,
        latency_ms=latency_ms, credits=credits_actual,
    )

    # ── Daily budget counter.
    try:
        await daily_budget.record(user_id, cost_usd)
    except Exception:
        pass

    # ── Persist response for cache + idempotency replays.
    try:
        await semantic_cache.store(
            model=model, messages=messages, response=data,
            temperature=temperature, has_tools=has_tools, stream=stream,
        )
    except Exception as cache_exc:
        logger.info("semantic_cache store failed: %s", cache_exc)
    if agent_id and not has_tools and not stream:
        try:
            from services import skill_cache
            await skill_cache.store(
                agent_id=agent_id, model=model, messages=messages,
                temperature=temperature, response=data,
            )
        except Exception as cache_exc:
            logger.info("skill_cache store failed: %s", cache_exc)
    if idempotency_key:
        await dedup_idempotency.store_cached(
            idempotency_key, user_id, data, credits_charged=credits_actual,
        )

    # ── Shadow/canary mirror — fire-and-forget, never blocks user.
    try:
        await shadow_traffic.maybe_mirror(
            user_id=user_id, messages=messages, model=model,
            real_response=data, real_provider=actual_provider,
            complete_fn=complete,
        )
    except Exception:
        pass

    # ── Chain-of-Verification opt-in — cut hallucinations via 2nd pass.
    if verify:
        try:
            from services import cov_verifier
            original = data["choices"][0]["message"]["content"]
            revised = await cov_verifier.verify(
                original_answer=original,
                complete_fn=complete, user_id=user_id,
                source=f"{source}_cov",
            )
            if revised and revised != original:
                data["choices"][0]["message"]["content"] = revised
                data.setdefault("maars", {})["verified"] = True
        except Exception as vexc:
            logger.info("cov verify soft-fail: %s", vexc)

    return data


async def complete_text(
    user_id: str,
    system_prompt: str,
    user_prompt: str,
    model: str = "maars/auto",
    *,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    source: str = "internal",
    agent_id: Optional[str] = None,
    enable_cache: bool = True,
) -> str:
    """Convenience wrapper — the common case of 'I have a system prompt + user
    prompt, give me back a string.' Used by every call site that was previously
    calling call_direct_llm.

    enable_cache=False bypasses the semantic cache. Use it for calls that
    should always fresh-roll — workflow generation, one-off diagnostics,
    etc. — to prevent a stale cached response from being replayed.
    """
    r = await complete(
        user_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        source=source,
        agent_id=agent_id,
        enable_cache=enable_cache,
    )
    try:
        return r["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        logger.warning("complete_text: bad response shape: %s — %s", exc, str(r)[:300])
        return ""
