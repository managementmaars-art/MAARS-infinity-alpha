"""Phase-2 smoke tests — provider adapters, router scoring, stripe idempotency.

The async tests use plain asyncio.run() so this file doesn't depend on
pytest-asyncio being installed.
"""
from __future__ import annotations

import asyncio
import os

import pytest

from services.routing import router_scoring
from services.providers import AnthropicProvider, DeepSeekProvider, GroqProvider, OpenAIProvider


from tests.conftest import MAARS_TEST_LOOP  # shared across the whole test session


def _run(coro):
    return MAARS_TEST_LOOP.run_until_complete(coro)


# ----------------------------------------------------------------- providers

@pytest.mark.parametrize("cls,slug", [
    (OpenAIProvider, "openai"),
    (AnthropicProvider, "anthropic"),
    (GroqProvider, "groq"),
    (DeepSeekProvider, "deepseek"),
])
def test_provider_metadata(cls, slug):
    p = cls(api_key="")
    assert p.slug == slug
    assert not p.available
    # With a key, adapter is considered available.
    p2 = cls(api_key="sk-fake")
    assert p2.available


@pytest.mark.parametrize("cls", [OpenAIProvider, AnthropicProvider, GroqProvider, DeepSeekProvider])
def test_provider_health_returns_structured_result_when_key_missing(cls):
    """No api_key → HealthStatus(healthy=False, detail='no api_key configured'). Never raises."""
    p = cls(api_key="")
    status = _run(p.health_check())
    assert status.healthy is False
    assert "no api_key" in status.detail


@pytest.mark.parametrize("cls", [OpenAIProvider, AnthropicProvider, GroqProvider, DeepSeekProvider])
def test_provider_estimate_usage(cls):
    p = cls(api_key="sk-x")
    est = _run(p.estimate_usage(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "hello " * 50}],
        max_output_tokens=100,
    ))
    assert est.prompt_tokens > 0
    assert est.completion_tokens == 100
    assert est.estimated_cost_usd >= 0.0


# ----------------------------------------------------------------- router scoring

def _cands():
    return [
        router_scoring.Candidate("openai",    "gpt-4o-mini",  "economy",  0.5,  avg_latency_ms=900,  capabilities=["code", "fast"]),
        router_scoring.Candidate("openai",    "gpt-4o",       "standard", 5.0,  avg_latency_ms=1700, capabilities=["code", "reasoning", "vision"]),
        router_scoring.Candidate("anthropic", "claude-opus",  "premium", 15.0,  avg_latency_ms=2500, capabilities=["reasoning", "long_context"]),
        router_scoring.Candidate("groq",      "llama-3.3-70b","economy",  0.3,  avg_latency_ms=300,  capabilities=["fast"]),
    ]


def test_rank_respects_cost_for_quick_task():
    ranked = router_scoring.rank_candidates(_cands(), task_type="quick")
    # Cheap + fast should win.
    assert ranked[0].candidate.provider == "groq"


def test_rank_respects_capability_for_code_task():
    ranked = router_scoring.rank_candidates(_cands(), task_type="code", tier_preference="economy")
    # gpt-4o-mini has code+fast AND matches economy tier; groq has only fast (no code).
    assert ranked[0].candidate.model == "gpt-4o-mini"


def test_unhealthy_provider_excluded():
    ranked = router_scoring.rank_candidates(
        _cands(),
        task_type="reasoning",
        health_map={"anthropic": 0.0, "openai": 1.0, "groq": 1.0, "deepseek": 1.0},
    )
    providers = [s.candidate.provider for s in ranked]
    # anthropic still appears in ranked output but with zero health — pick_best filters it.
    best = router_scoring.pick_best(
        _cands(),
        task_type="reasoning",
        health_map={"anthropic": 0.0, "openai": 1.0, "groq": 1.0, "deepseek": 1.0},
    )
    assert best is not None
    assert best.candidate.provider != "anthropic"


def test_score_breakdown_exposes_all_components():
    scored = router_scoring.score_candidate(_cands()[0], task_type="code")
    for key in ("capability_raw", "cost_raw", "latency_raw", "health_raw", "tier_raw"):
        assert key in scored.breakdown


# ----------------------------------------------------------------- stripe

pytestmark_db = pytest.mark.skipif(
    not os.environ.get("MONGO_URL"),
    reason="MONGO_URL not configured — skipping DB-backed stripe tests",
)


@pytestmark_db
def test_stripe_event_idempotency():
    """Re-delivering the same checkout.session.completed event must not double-credit."""
    from services.billing import stripe_service, wallet_service

    from services.billing import ledger_service

    async def scenario():
        # Clean any prior test data BEFORE building unique indexes, otherwise
        # orphan duplicates from older test runs would block index creation.
        from db import db
        await db.ledger_entries.delete_many({"user_id": {"$regex": "^test_user_stripe_"}})
        await db.wallets.delete_many({"user_id": {"$regex": "^test_user_stripe_"}})

        await ledger_service.ensure_indexes()
        await wallet_service.ensure_indexes()

        user_id = f"test_user_stripe_{os.getpid()}"
        session_id = f"cs_test_{os.getpid()}_{int(asyncio.get_event_loop().time()*1000)}"
        await wallet_service.ensure_wallet(user_id, initial_credits=0)

        event = {
            "type": "checkout.session.completed",
            "data": {"object": {
                "id": session_id,
                "amount_total": 1000,
                "currency": "usd",
                "metadata": {
                    "maars_billing": "v1",
                    "user_id": user_id,
                    "package_id": "starter",
                    "credits": "1000",
                },
            }},
        }  # noqa: E501
        r1 = await stripe_service.handle_event(event)
        await stripe_service.handle_event(event)
        summary = await wallet_service.get_summary(user_id)
        return r1, summary

    r1, summary = _run(scenario())
    assert r1["status"] == "credited"
    # Second call must not double-count — grant() short-circuits on the ledger unique index.
    # Credits are derived from user_backing_usd × CREDITS_PER_USD now:
    #   amount_total = $10, starter operator_share_pct = 0.30
    #   user_backing = $7  →  7 × 1000 = 7000 credits.
    from shared.constants import CREDITS_PER_USD
    expected = round(10.0 * (1.0 - 0.30) * CREDITS_PER_USD)
    assert summary["balance_credits"] == expected
