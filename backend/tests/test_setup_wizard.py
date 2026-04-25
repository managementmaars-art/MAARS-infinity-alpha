"""Tests for env_writer + setup_orchestrator step logic."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from tests.conftest import MAARS_TEST_LOOP


def _run(coro):
    return MAARS_TEST_LOOP.run_until_complete(coro)


# ────────────────────────────────────────────── env_writer

def test_env_writer_round_trip(tmp_path, monkeypatch):
    from services import env_writer
    target = tmp_path / ".env"
    monkeypatch.setattr(env_writer, "ENV_PATH", target)

    env_writer.upsert({"FOO": "bar", "BAZ": "value with spaces"})
    loaded = env_writer.load()
    assert loaded["FOO"] == "bar"
    assert loaded["BAZ"] == "value with spaces"


def test_env_writer_preserves_unrelated_keys_and_comments(tmp_path, monkeypatch):
    from services import env_writer
    target = tmp_path / ".env"
    target.write_text(
        "# header comment\nKEEP_ME=untouched\nALSO_KEEP=42\n# inline comment\nWILL_UPDATE=old\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(env_writer, "ENV_PATH", target)

    env_writer.upsert({"WILL_UPDATE": "new", "BRAND_NEW": "added"})
    text = target.read_text(encoding="utf-8")

    assert "KEEP_ME=untouched" in text
    assert "ALSO_KEEP=42" in text
    assert "# header comment" in text
    assert "# inline comment" in text
    assert "WILL_UPDATE=new" in text
    assert "WILL_UPDATE=old" not in text
    assert "BRAND_NEW=added" in text


def test_mask_short_and_long():
    from services.env_writer import mask
    assert mask("") == ""
    assert mask("abc") == "•••"
    assert mask("abcdefghijklmnop") == "abcd…mnop"


def test_sync_os_in_process(monkeypatch):
    from services import env_writer
    monkeypatch.setenv("MAARS_PROBE", "before")
    env_writer.sync_os({"MAARS_PROBE": "after"})
    assert os.environ["MAARS_PROBE"] == "after"


# ────────────────────────────────────────────── orchestrator (no DB)

def test_provider_links_have_required_fields():
    from services.setup_orchestrator import PROVIDER_LINKS
    for slug, info in PROVIDER_LINKS.items():
        assert info["url"].startswith("https://")
        assert info["env"].endswith("_API_KEY")
        assert info["name"]


def test_step_order_includes_all_providers():
    from services.setup_orchestrator import PROVIDER_LINKS, STEP_ORDER
    for slug in PROVIDER_LINKS:
        assert f"provider_{slug}" in STEP_ORDER


# ────────────────────────────────────────────── orchestrator (with DB)

pytestmark_db = pytest.mark.skipif(
    not os.environ.get("MONGO_URL"),
    reason="MONGO_URL not configured",
)


@pytestmark_db
def test_get_state_creates_singleton():
    from services import setup_orchestrator as orch

    async def scenario():
        # Wipe so the test starts clean.
        from db import db
        await db[orch.SETUP_COLLECTION].delete_many({})
        s = await orch.get_state()
        return s

    state = _run(scenario())
    assert state["setup_id"] == "default"
    for sid in ("system_check", "migrate", "seed"):
        assert sid in state["steps"]


@pytestmark_db
def test_step_provider_save_rejects_bad_key():
    from services import setup_orchestrator as orch

    async def scenario():
        return await orch.step_provider_save_and_test("openai", "sk-DEFINITELY-INVALID-zzzzzzzz")

    ok, detail, meta = _run(scenario())
    assert ok is False
    assert "rejected" in detail or "no api_key" in detail or "401" in detail or "HTTP 4" in detail


@pytestmark_db
def test_set_step_writes_back():
    from services import setup_orchestrator as orch

    async def scenario():
        await orch.set_step("system_check", status="success", detail="hand-set in test")
        s = await orch.get_state()
        return s

    state = _run(scenario())
    assert state["steps"]["system_check"]["status"] == "success"
    assert "hand-set" in state["steps"]["system_check"]["detail"]


@pytestmark_db
def test_build_report_reflects_step_status():
    from services import setup_orchestrator as orch

    async def scenario():
        from db import db
        await db[orch.SETUP_COLLECTION].delete_many({})
        await orch.set_step("system_check", status="success")
        await orch.set_step("migrate", status="success")
        await orch.set_step("seed", status="success")
        return await orch.build_report()

    report = _run(scenario())
    assert report["backend_ready"] is True
    assert report["database_ready"] is True
    assert report["wallet_ready"] is False        # test_wallet still pending
    assert report["launch_ready"] is False        # nothing tested yet
