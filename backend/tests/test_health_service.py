import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.health_service import (
    build_api_health_response,
    build_readiness_response,
    get_environment_configuration,
)


def test_environment_configuration_summarizes_required_and_optional(monkeypatch):
    monkeypatch.setenv("MONGO_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("DB_NAME", "maars_test")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)

    config = get_environment_configuration()

    assert config["missing_required"] == []
    assert config["summary"]["required_configured"] == 3
    assert config["summary"]["integrations_total"] >= 1
    assert config["optional_integrations"]["openai"]["configured"] is True
    assert config["optional_integrations"]["email_smtp"]["configured"] is False
    assert config["optional_integrations"]["email_smtp"]["partial"] is True


def test_api_health_response_exposes_startup_summary(monkeypatch):
    monkeypatch.setenv("MONGO_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("DB_NAME", "maars_test")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)

    payload = build_api_health_response(
        "MAARS Command",
        {
            "ready": False,
            "started_at": "2026-04-12T00:00:00+00:00",
            "completed_at": None,
            "last_error": "RuntimeError: seed failed",
            "tasks": {"seed_default_agents": True, "seed_default_tools": False},
        },
    )

    assert payload["status"] == "ok"
    assert payload["ready"] is False
    assert payload["startup"]["completed_tasks"] == 1
    assert payload["startup"]["total_tasks"] == 2
    assert payload["configuration"]["required_total"] == 3


def test_readiness_response_fails_when_database_check_fails(monkeypatch):
    monkeypatch.setenv("MONGO_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("DB_NAME", "maars_test")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)

    async def failing_ping():
        raise RuntimeError("db offline")

    payload = asyncio.run(
        build_readiness_response(
            "MAARS Command",
            {"ready": True, "tasks": {"seed_default_agents": True}},
            db_ping_fn=failing_ping,
        )
    )

    assert payload["ready"] is False
    assert payload["checks"]["database"]["status"] == "fail"
    assert "db offline" in payload["checks"]["database"]["error"]


def test_readiness_response_passes_with_healthy_database(monkeypatch):
    monkeypatch.setenv("MONGO_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("DB_NAME", "maars_test")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)

    async def healthy_ping():
        return None

    payload = asyncio.run(
        build_readiness_response(
            "MAARS Command",
            {"ready": True, "tasks": {"seed_default_agents": True}},
            db_ping_fn=healthy_ping,
        )
    )

    assert payload["ready"] is True
    assert payload["checks"]["database"]["status"] == "pass"
    assert payload["summary"]["passed"] == payload["summary"]["total"]
