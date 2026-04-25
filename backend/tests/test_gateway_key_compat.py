"""
Cross-system key-format compatibility for v1_gateway.

Confirms _get_key_doc accepts both:
  - new wizard-issued keys (maars_sk_live_*  → api_keys collection, hashed)
  - legacy keys              (maars-sk-*      → client_gateway_keys collection, plaintext)

Without this fix, every wizard-seeded key was rejected by the gateway with
"Invalid key format. MAARS keys begin with 'maars-sk-'" — breaking the
end-to-end story the setup wizard advertises.
"""
from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from tests.conftest import MAARS_TEST_LOOP


def _run(coro):
    return MAARS_TEST_LOOP.run_until_complete(coro)


pytestmark_db = pytest.mark.skipif(
    not os.environ.get("MONGO_URL"),
    reason="MONGO_URL not configured",
)


def _fake_request(auth_value: str):
    """Tiny stub — _get_key_doc only reads request.headers.get('Authorization')."""
    return SimpleNamespace(headers={"Authorization": auth_value})


@pytestmark_db
def test_new_format_key_accepted_by_gateway():
    from db import db
    from routes.v1_gateway import _get_key_doc
    from services import api_key_service

    async def scenario():
        await api_key_service.ensure_indexes()
        user_id = f"t_kc_{os.getpid()}"
        await db.api_keys.delete_many({"user_id": user_id})
        result = await api_key_service.create_key(user_id, name="gateway-compat-test")
        raw = result["raw_key"]
        doc = await _get_key_doc(_fake_request(f"Bearer {raw}"))
        return raw, doc

    raw, doc = _run(scenario())
    assert raw.startswith("maars_sk_live_")
    assert doc["user_id"].startswith("t_kc_")
    assert doc["_source"] == "api_keys"
    # USD-budget defaults are permissive — credit wallet enforces actual spend.
    assert doc["monthly_budget_usd"] >= 999_999.0
    assert doc["billing_mode"] == "subscription"
    assert doc["status"] == "active"


@pytestmark_db
def test_revoked_new_key_is_rejected():
    from db import db
    from fastapi import HTTPException
    from routes.v1_gateway import _get_key_doc
    from services import api_key_service

    async def scenario():
        await api_key_service.ensure_indexes()
        user_id = f"t_kr_{os.getpid()}"
        await db.api_keys.delete_many({"user_id": user_id})
        result = await api_key_service.create_key(user_id, name="will-be-revoked")
        raw = result["raw_key"]
        await api_key_service.revoke(result["api_key_id"], user_id)
        try:
            await _get_key_doc(_fake_request(f"Bearer {raw}"))
            return None
        except HTTPException as exc:
            return exc

    err = _run(scenario())
    # Revoke flips status; find_by_raw_key only matches active rows, so this
    # surfaces as the "Invalid API key" 401, not 403.
    assert err is not None
    assert err.status_code in (401, 403)


def test_unknown_prefix_rejected_with_clear_message():
    from fastapi import HTTPException
    from routes.v1_gateway import _get_key_doc
    try:
        _run(_get_key_doc(_fake_request("Bearer sk-not-a-maars-key-1234567890")))
    except HTTPException as exc:
        assert exc.status_code == 401
        msg = exc.detail["error"]["message"]
        assert "maars_sk_live_" in msg and "maars-sk-" in msg
        return
    raise AssertionError("expected HTTPException for non-MAARS key prefix")


def test_missing_authorization_header_rejected():
    from fastapi import HTTPException
    from routes.v1_gateway import _get_key_doc
    try:
        _run(_get_key_doc(SimpleNamespace(headers={})))
    except HTTPException as exc:
        assert exc.status_code == 401
        return
    raise AssertionError("expected HTTPException when Authorization header missing")


@pytestmark_db
def test_legacy_format_still_works():
    """The pre-existing client_gateway_keys path must remain functional for any deployment that still has legacy keys in the DB."""
    from datetime import datetime, timezone
    from db import db
    from routes.v1_gateway import _get_key_doc

    async def scenario():
        legacy = "maars-sk-legacycompat0000000000000000"
        await db.client_gateway_keys.delete_one({"key": legacy})
        await db.client_gateway_keys.insert_one({
            "user_id": "t_legacy_compat",
            "key": legacy,
            "plan_id": "free",
            "monthly_budget_usd": 0.0,
            "used_usd": 0.0,
            "cycle_start": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return await _get_key_doc(_fake_request(f"Bearer {legacy}"))

    doc = _run(scenario())
    assert doc["user_id"] == "t_legacy_compat"
    assert doc["_source"] == "client_gateway_keys"
