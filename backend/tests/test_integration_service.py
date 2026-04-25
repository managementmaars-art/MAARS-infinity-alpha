from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.integration_service import (
    AVAILABLE_INTEGRATIONS_BY_ID,
    _derive_connection_status,
    canonicalize_integration_id,
)


def test_catalog_contains_core_and_expanded_connectors():
    expected = {
        "slack", "github", "sendgrid", "resend", "twilio", "google_suite",
        "whatsapp", "shopify", "hubspot", "salesforce",
        "webhooks", "notion", "jira", "confluence", "stripe",
    }
    assert expected.issubset(set(AVAILABLE_INTEGRATIONS_BY_ID))


def test_legacy_google_workspace_alias_maps_to_google_suite():
    assert canonicalize_integration_id("google_workspace") == "google_suite"


def test_incomplete_status_detects_missing_required_fields():
    template = AVAILABLE_INTEGRATIONS_BY_ID["slack"]
    status = _derive_connection_status(template, {}, system_config={})
    assert status["verification_status"] == "incomplete"
    assert status["missing_required_fields"] == ["bot_token"]
    assert status["execution_ready"] is False


def test_complete_status_marks_execution_ready():
    template = AVAILABLE_INTEGRATIONS_BY_ID["webhooks"]
    status = _derive_connection_status(
        template,
        {"webhook_url": "https://example.com/hooks/maars-test"},
        system_config={},
    )
    assert status["verification_status"] == "verified"
    assert status["missing_required_fields"] == []
    assert status["execution_ready"] is True


def test_planned_connector_stays_planned_even_when_configured():
    template = AVAILABLE_INTEGRATIONS_BY_ID["notion"]
    status = _derive_connection_status(
        template,
        {"integration_token": "secret_test_token"},
        system_config={},
    )
    assert status["verification_status"] == "planned"
    assert status["execution_ready"] is False
