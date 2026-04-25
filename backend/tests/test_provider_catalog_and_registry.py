"""
Phase-6 tests — provider catalog integrity, model registry integrity,
setup-orchestrator detection, /v1/models/registry visibility filter.
"""
from __future__ import annotations

import os
import re

import pytest

from tests.conftest import MAARS_TEST_LOOP


def _run(coro):
    return MAARS_TEST_LOOP.run_until_complete(coro)


# ─────────────────────────────────────────── catalog integrity

URL_RE = re.compile(r"^https://[^\s/$.?#].[^\s]*$")
ENV_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def test_catalog_has_at_least_31_providers():
    from services import provider_catalog as pc
    # PDF lists ~31 providers; the catalog must include everything in the spec plus quick tier.
    assert len(pc.CATALOG) >= 31


def test_catalog_quick_tier_matches_existing_provider_classes():
    from services import provider_catalog as pc
    quick_slugs = {p.slug for p in pc.QUICK_PROVIDERS}
    assert quick_slugs == {"openai", "anthropic", "groq", "deepseek"}


def test_every_catalog_entry_has_valid_url_and_env_var():
    from services import provider_catalog as pc
    for entry in pc.CATALOG:
        assert URL_RE.match(entry.dashboard_url), f"{entry.slug}: bad dashboard URL {entry.dashboard_url!r}"
        assert ENV_RE.match(entry.env_var),       f"{entry.slug}: bad env_var {entry.env_var!r}"
        assert entry.validation_strategy in pc.VALIDATION_STRATEGIES, f"{entry.slug}: unknown strategy"
        assert entry.category in pc.CATEGORIES,   f"{entry.slug}: unknown category {entry.category}"


def test_catalog_slugs_are_unique():
    from services import provider_catalog as pc
    slugs = [p.slug for p in pc.CATALOG]
    assert len(slugs) == len(set(slugs)), "duplicate provider slug in catalog"


def test_catalog_env_vars_are_unique():
    from services import provider_catalog as pc
    env_vars = [p.env_var for p in pc.CATALOG]
    assert len(env_vars) == len(set(env_vars)), "duplicate env_var across providers"


def test_pdf_named_providers_present():
    """Every provider explicitly named in the MAARS PDF must appear."""
    from services import provider_catalog as pc
    pdf_named = {
        "openai", "anthropic", "google", "xai", "deepseek", "mistral", "perplexity",
        "cohere", "together", "fireworks", "huggingface", "sambanova", "nvidia_nim",
        "novita", "lepton", "lambda", "cerebras", "zhipu", "qwen", "moonshot",
        "ai21", "bedrock", "minimax", "upstage", "arcee", "inception", "writer",
        "yi", "doubao", "hyperbolic", "meta_llama_api", "elevenlabs", "groq",
    }
    have = {p.slug for p in pc.CATALOG}
    missing = pdf_named - have
    assert not missing, f"missing PDF-named providers: {missing}"


# ─────────────────────────────────────────── model registry integrity

def test_registry_size_and_coverage():
    from services import model_registry as mr
    assert len(mr.REGISTRY) >= 50, "expected ≥50 curated models"
    providers = set(mr.BY_PROVIDER.keys())
    # Coverage of headline families.
    must_have = {"openai", "anthropic", "google", "xai", "deepseek", "mistral",
                 "perplexity", "cohere", "qwen", "zhipu", "meta_llama_api"}
    assert must_have.issubset(providers), f"registry missing coverage for: {must_have - providers}"


def test_registry_provider_slugs_exist_in_catalog():
    from services import model_registry as mr, provider_catalog as pc
    catalog_slugs = {p.slug for p in pc.CATALOG}
    for m in mr.REGISTRY:
        assert m.provider_slug in catalog_slugs, \
            f"model {m.model_id} references unknown provider {m.provider_slug}"


def test_registry_tiers_are_well_known():
    from services import model_registry as mr
    for m in mr.REGISTRY:
        assert m.tier in mr.TIERS, f"{m.maars_id}: unknown tier {m.tier}"


def test_registry_capabilities_well_known():
    from services import model_registry as mr
    for m in mr.REGISTRY:
        for cap in m.capabilities:
            assert cap in mr.CAPABILITIES, f"{m.maars_id}: unknown capability {cap}"


def test_registry_maars_id_unique():
    from services import model_registry as mr
    ids = [m.maars_id for m in mr.REGISTRY]
    assert len(ids) == len(set(ids))


def test_registry_filter_visible_for_respects_configured_providers():
    from services import model_registry as mr
    visible = mr.filter_visible_for(configured_providers={"openai", "groq"})
    providers_in_view = {m.provider_slug for m in visible}
    assert providers_in_view <= {"openai", "groq"}
    assert visible, "expected at least one OpenAI or Groq model in the curated registry"


# ─────────────────────────────────────────── orchestrator detection

def test_detect_marks_missing_when_env_unset(monkeypatch):
    from services import setup_orchestrator as orch, provider_catalog as pc
    # Wipe env for every catalog entry so we have a known baseline.
    for p in pc.CATALOG:
        monkeypatch.delenv(p.env_var, raising=False)
    detected = orch.detect_configured_providers()
    for slug, info in detected.items():
        if info["validation_strategy"] == "coming_soon":
            assert info["status"] == "skipped"
        else:
            assert info["status"] == "missing", f"{slug} should be missing when env unset"


def test_detect_marks_detected_when_env_set(monkeypatch):
    from services import setup_orchestrator as orch
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key-1234567890")
    detected = orch.detect_configured_providers()
    assert detected["openai"]["status"] == "detected"
    assert detected["openai"]["configured"] is True
    assert detected["openai"]["masked_value"] is not None
    assert "sk-test-fake-key-1234567890" not in detected["openai"]["masked_value"]


def test_overlay_promotes_to_validated_on_success_step():
    from services import setup_orchestrator as orch
    detected = {"openai": {"slug": "openai", "configured": True, "status": "detected"}}
    steps = {"provider_openai": {"status": "success", "detail": "validated 200"}}
    overlay = orch.overlay_step_status(detected, steps)
    assert overlay["openai"]["status"] == "validated"


def test_overlay_marks_invalid_on_failed_step():
    from services import setup_orchestrator as orch
    detected = {"openai": {"slug": "openai", "configured": True, "status": "detected"}}
    steps = {"provider_openai": {"status": "failed", "detail": "401"}}
    overlay = orch.overlay_step_status(detected, steps)
    assert overlay["openai"]["status"] == "invalid"


# ─────────────────────────────────────────── catalog API roundtrip

pytestmark_db = pytest.mark.skipif(
    not os.environ.get("MONGO_URL"),
    reason="MONGO_URL not configured",
)


@pytestmark_db
def test_setup_providers_catalog_endpoint_shape():
    """The /api/setup/providers/catalog endpoint must return both quick + advanced lists."""
    from services import setup_orchestrator as orch, provider_catalog as pc

    async def scenario():
        state = await orch.get_state()
        detected = orch.detect_configured_providers()
        detected = orch.overlay_step_status(detected, state.get("steps", {}))
        return detected

    detected = _run(scenario())
    assert "openai" in detected
    assert "google" in detected
    assert "elevenlabs" in detected
    assert detected["openai"]["quick"] is True
    assert detected["google"]["quick"] is False
