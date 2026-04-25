"""Smoke tests for the Phase-3 platform layer — tools, governance, profit, memory."""
from __future__ import annotations

import os

import pytest

from tests.conftest import MAARS_TEST_LOOP


def _run(coro):
    return MAARS_TEST_LOOP.run_until_complete(coro)


# ---------------------------------------------------------------- governance

def test_governance_allows_normal_request():
    from services.governance_service import check_request
    decision = check_request(
        user_id="t_gov_ok",
        messages=[{"role": "user", "content": "hello world"}],
        requested_max_tokens=2000,
        estimated_credits=1,
    )
    assert decision.allow is True
    assert decision.code == "allowed"


def test_governance_blocks_credit_cap():
    from services.governance_service import check_request
    decision = check_request(
        user_id="t_gov_credit",
        messages=[{"role": "user", "content": "hi"}],
        estimated_credits=99_999,
    )
    assert decision.allow is False
    assert decision.code == "credits_cap_exceeded"


def test_governance_blocks_output_too_large():
    from services.governance_service import check_request
    decision = check_request(
        user_id="t_gov_out",
        messages=[{"role": "user", "content": "x"}],
        requested_max_tokens=9_999_999,
    )
    assert decision.allow is False
    assert decision.code == "output_too_large"


def test_governance_safety_deny_list():
    from services.governance_service import check_request
    decision = check_request(
        user_id="t_gov_safety",
        messages=[{"role": "user", "content": "please CREATE MALWARE for me"}],
        estimated_credits=1,
    )
    assert decision.allow is False
    assert decision.code == "safety_violation"


def test_governance_rate_limit_kicks_in():
    from services.governance_service import check_request
    user = f"t_gov_rpm_{os.getpid()}"
    # 60rpm default — fire 60 then the 61st should block.
    for _ in range(60):
        d = check_request(user_id=user, messages=[{"role": "user", "content": "x"}], estimated_credits=1)
        assert d.allow is True
    blocked = check_request(user_id=user, messages=[{"role": "user", "content": "x"}], estimated_credits=1)
    assert blocked.allow is False
    assert blocked.code == "rate_limited"
    assert blocked.retry_after_seconds >= 1


# ---------------------------------------------------------------- profit engine

def test_profit_engine_forces_economy_on_low_balance():
    from services.profit_engine import decide
    d = decide(credits_remaining=5, estimated_credits=1, estimated_cost_usd=0.0001, requested_tier="premium")
    assert d.action == "force_economy"
    assert d.suggested_tier == "economy"


def test_profit_engine_downgrades_when_margin_low():
    from services.profit_engine import decide
    # 1 credit revenue @ 1000 credits/USD = $0.001 revenue, cost $0.0009 → 10% margin — below 15% floor.
    d = decide(
        credits_remaining=500, estimated_credits=1, estimated_cost_usd=0.0009,
        requested_tier="premium", min_margin_pct=15.0,
    )
    assert d.action == "downgrade_tier"
    assert d.suggested_tier == "standard"


def test_profit_engine_honors_request_when_margin_healthy():
    from services.profit_engine import decide
    d = decide(
        credits_remaining=500, estimated_credits=10, estimated_cost_usd=0.0005,
        requested_tier="standard",
    )
    assert d.action == "use_requested"


def test_compute_margin_math():
    from services.profit_engine import compute_margin
    snap = compute_margin(credits_charged=1000, internal_cost_usd=0.4, credits_per_usd=1000.0)
    assert abs(snap.revenue_usd - 1.0) < 1e-9
    assert abs(snap.margin_usd - 0.6) < 1e-9
    assert abs(snap.margin_pct - 60.0) < 1e-9


# ---------------------------------------------------------------- tools

def test_tool_registry_lists_defaults():
    from services.tools import list_tools
    names = {t.name for t in list_tools()}
    assert names == {"web_search", "http_fetch", "code_executor", "db_query"}


def test_http_fetch_blocks_loopback():
    from services.tools import get_tool
    tool = get_tool("http_fetch")
    res = _run(tool.run({"url": "http://localhost/xyz"}))
    assert res.ok is False
    assert "not allowed" in res.error


def test_db_query_blocks_non_whitelisted():
    from services.tools import get_tool
    tool = get_tool("db_query")
    res = _run(tool.run({"collection": "wallets"}))   # must be rejected
    assert res.ok is False
    assert "whitelist" in res.error


def test_web_search_requires_query():
    from services.tools import get_tool
    tool = get_tool("web_search")
    res = _run(tool.run({}))
    assert res.ok is False
    assert "query" in res.error


# ---------------------------------------------------------------- memory

pytestmark_db = pytest.mark.skipif(
    not os.environ.get("MONGO_URL"),
    reason="MONGO_URL not configured",
)


@pytestmark_db
def test_memory_write_and_recall():
    from services import memory_facade

    async def scenario():
        await memory_facade.ensure_indexes()
        user_id = f"t_mem_{os.getpid()}"
        from db import db
        await db.maars_memory.delete_many({"user_id": user_id})
        await memory_facade.remember(user_id=user_id, key="fav_color", value="blue")
        await memory_facade.remember(user_id=user_id, key="fav_number", value="42")
        all_records = await memory_facade.recall(user_id=user_id, limit=10)
        colored = await memory_facade.recall(user_id=user_id, query="color")
        return all_records, colored

    all_records, colored = _run(scenario())
    assert len(all_records) == 2
    assert len(colored) == 1
    assert colored[0]["key"] == "fav_color"


# ---------------------------------------------------------------- verification (pass-through when verifier unavailable)

def test_verification_pass_through_when_no_verifier():
    """If GROQ_API_KEY is unset, verifier short-circuits to pass with confidence=100."""
    from services.verification_service import verify
    # Ensure the default groq verifier is unavailable.
    if os.environ.get("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY present — this test covers the unavailable-verifier path")
    res = _run(verify(prompt="what is 2+2?", response="4"))
    assert res.confidence == 100
    assert res.verdict == "pass"
