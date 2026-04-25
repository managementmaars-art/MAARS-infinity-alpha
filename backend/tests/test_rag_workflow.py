"""Smoke tests for the new RAG + memory + SME pipelines.

These deliberately don't hit real providers — they exercise the
plumbing (doc_ingest → vector_store → evaluator → synthesis) with
mocked LLM calls. Run with:

    cd backend && venv/Scripts/python.exe -m pytest tests/test_rag_workflow.py -v

Real LLM-dependent behavior is validated separately in the
end-to-end smoke script (scripts/smoke.py, if present) that needs
a live backend.
"""
from __future__ import annotations
import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest


# ── Fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def test_user_id() -> str:
    return "user_test_rag_001"


@pytest.fixture
async def cleanup_mongo(test_user_id):
    """Wipe every collection row this test touches. Runs before + after."""
    from db import db
    async def _wipe():
        for coll in ("rag_docs", "rag_chunks", "memory_graph",
                     "sme_corrections", "eval_golden_set", "mcp_tokens"):
            await db[coll].delete_many({"user_id": test_user_id})
    await _wipe()
    yield
    await _wipe()


# ── Tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_doc_ingest_text_creates_chunks(cleanup_mongo, test_user_id):
    from services import doc_ingest
    from db import db
    result = await doc_ingest.ingest_text(
        user_id=test_user_id,
        text="MAARS is a universal AI gateway that routes across 22 providers.",
        title="test-doc",
    )
    assert result["ok"] is True
    assert result["chunks"] >= 1
    assert result["doc_id"].startswith("doc_")
    # Verify persistence
    doc = await db.rag_docs.find_one({"doc_id": result["doc_id"]})
    assert doc is not None
    assert doc["user_id"] == test_user_id


@pytest.mark.asyncio
async def test_memory_graph_records_and_recalls(cleanup_mongo, test_user_id):
    from services import memory_graph
    fact = await memory_graph.record_fact(
        user_id=test_user_id, subject="user",
        predicate="timezone", obj="UTC+8",
    )
    assert fact["fact_id"].startswith("mf_")
    assert fact["valid_to"] is None   # currently active
    recall = await memory_graph.recall(
        user_id=test_user_id, predicate="timezone",
    )
    assert len(recall) == 1
    assert recall[0]["object"] == "UTC+8"


@pytest.mark.asyncio
async def test_memory_graph_supersedes_on_duplicate_predicate(cleanup_mongo, test_user_id):
    from services import memory_graph
    first = await memory_graph.record_fact(
        user_id=test_user_id, subject="user",
        predicate="timezone", obj="UTC+8",
    )
    await memory_graph.record_fact(
        user_id=test_user_id, subject="user",
        predicate="timezone", obj="PST",
    )
    # Active recall returns only the newer one
    recall = await memory_graph.recall(
        user_id=test_user_id, predicate="timezone",
    )
    assert len(recall) == 1
    assert recall[0]["object"] == "PST"
    # But include_superseded returns both
    full = await memory_graph.recall(
        user_id=test_user_id, predicate="timezone",
        include_superseded=True,
    )
    assert len(full) == 2


@pytest.mark.asyncio
async def test_sme_corrections_approve_validates_answer(cleanup_mongo, test_user_id):
    from services import sme_corrections
    item = await sme_corrections.queue_for_review(
        user_id=test_user_id, query="What is MAARS?",
        response="bad placeholder response", reason="test",
    )
    assert item["status"] == "pending"
    approved = await sme_corrections.approve(
        item["correction_id"],
        corrected_answer="MAARS is a Universal AI Gateway.",
    )
    assert approved["status"] == "validated"
    # lookup_validated should find it on a similar query
    hit = await sme_corrections.lookup_validated(
        "what is maars anyway?", user_id=test_user_id,
    )
    assert hit is not None
    assert "Universal AI Gateway" in hit["answer"]


@pytest.mark.asyncio
async def test_eval_harness_golden_set_add_and_list(cleanup_mongo, test_user_id):
    from services import eval_harness
    from db import db
    g = await eval_harness.add_golden(
        prompt="What is 2+2?", task="reasoning",
        reference="4",
    )
    assert g["item_id"].startswith("ge_")
    items = await eval_harness.list_golden(task="reasoning")
    assert any(it["item_id"] == g["item_id"] for it in items)
    # cleanup
    await db.eval_golden_set.delete_one({"item_id": g["item_id"]})


@pytest.mark.asyncio
async def test_provider_scorecard_record_eval_score(cleanup_mongo, test_user_id):
    from services import provider_scorecard
    await provider_scorecard.record_eval_score(
        model="openai/gpt-4o-mini",
        mean_score=0.85, pass_rate=0.9, sample_size=10,
    )
    # Verify it's in the in-memory scorecard cache
    card = provider_scorecard.get("openai", "gpt-4o-mini")
    assert card is not None
    assert card.get("eval_mean_score") == 0.85
