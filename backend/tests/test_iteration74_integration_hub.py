"""
Iteration 74 Tests: Integration Hub + Custom Agent Creation LLM Providers

Tests:
1. Integration Hub Backend APIs:
   - GET /api/kernel/integrations/available - returns the unified catalog with summary metadata
   - POST /api/kernel/integrations/connect - creates user integration connection
   - DELETE /api/kernel/integrations/{id} - disconnects an integration
   - PUT /api/kernel/integrations/{id}/toggle - toggles integration enabled/disabled
   - POST /api/kernel/integrations/{id}/verify - returns readiness/verification state

2. CreateAgent page new providers verification (Groq, Together AI, Fireworks AI, AI21)
   - Validated via code review (no backend endpoint needed)

3. Regression tests for Campaign Builder and Workflow Builder
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")

# Test credentials
TEST_EMAIL = "management.maars@marsgc.net"
TEST_PASSWORD = "Admin123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "token" in data, f"No token in response: {data}"
    return data["token"]


@pytest.fixture
def auth_headers(auth_token):
    """Headers with authentication."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


class TestIntegrationHubAvailable:
    """Tests for GET /api/kernel/integrations/available endpoint."""

    def test_get_available_integrations_requires_auth(self):
        """401 without authentication."""
        response = requests.get(f"{BASE_URL}/api/kernel/integrations/available")
        assert response.status_code == 401

    def test_get_available_integrations_returns_catalog(self, auth_headers):
        """Returns the unified integration catalog."""
        response = requests.get(
            f"{BASE_URL}/api/kernel/integrations/available",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "available" in data
        assert "connected" in data
        assert "connected_ids" in data
        assert "summary" in data
        
        available = data["available"]
        assert len(available) >= 15, f"Expected a broad catalog, got {len(available)}"
        assert data["summary"]["total_available"] == len(available)

    def test_integrations_have_correct_ids(self, auth_headers):
        """Core integration IDs are present."""
        response = requests.get(
            f"{BASE_URL}/api/kernel/integrations/available",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        
        integration_ids = {i["integration_id"] for i in data["available"]}
        expected_ids = {
            "whatsapp", "slack", "github", "sendgrid", "resend", "twilio", "google_suite",
            "shopify", "hubspot", "salesforce", "webhooks", "notion", "jira", "confluence", "stripe",
        }
        
        assert expected_ids.issubset(integration_ids), f"Missing integrations: {expected_ids - integration_ids}"

    def test_integrations_grouped_by_category(self, auth_headers):
        """Integrations have correct categories."""
        response = requests.get(
            f"{BASE_URL}/api/kernel/integrations/available",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        
        categories = {i["integration_id"]: i["category"] for i in data["available"]}
        
        expected_categories = {
            "whatsapp": "social_media",
            "shopify": "commerce",
            "hubspot": "crm",
            "salesforce": "crm",
            "slack": "productivity",
            "webhooks": "automation",
        }
        
        for int_id, expected_cat in expected_categories.items():
            assert categories.get(int_id) == expected_cat, f"{int_id} should be {expected_cat}, got {categories.get(int_id)}"

    def test_integration_has_config_fields(self, auth_headers):
        """Each integration has config_fields defined."""
        response = requests.get(
            f"{BASE_URL}/api/kernel/integrations/available",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        
        for integ in data["available"]:
            assert "config_fields" in integ, f"{integ['integration_id']} missing config_fields"
            assert isinstance(integ["config_fields"], list)
            assert len(integ["config_fields"]) > 0, f"{integ['integration_id']} has no config_fields"
            
            for field in integ["config_fields"]:
                assert "key" in field
                assert "label" in field
                assert "type" in field

    def test_whatsapp_config_fields(self, auth_headers):
        """WhatsApp has correct config fields."""
        response = requests.get(
            f"{BASE_URL}/api/kernel/integrations/available",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        
        whatsapp = next((i for i in data["available"] if i["integration_id"] == "whatsapp"), None)
        assert whatsapp is not None
        
        field_keys = {f["key"] for f in whatsapp["config_fields"]}
        expected_keys = {"phone_number_id", "access_token", "waba_id"}
        
        assert expected_keys.issubset(field_keys), f"WhatsApp missing fields: {expected_keys - field_keys}"

    def test_summary_tracks_connection_counts(self, auth_headers):
        response = requests.get(
            f"{BASE_URL}/api/kernel/integrations/available",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["connected"] == len(data["connected"])
        assert set(data["connected_ids"]) == {item["integration_id"] for item in data["connected"]}


class TestIntegrationConnect:
    """Tests for POST /api/kernel/integrations/connect endpoint."""

    def test_connect_integration_requires_auth(self):
        """401 without authentication."""
        response = requests.post(
            f"{BASE_URL}/api/kernel/integrations/connect",
            json={"integration_id": "slack", "config": {}},
        )
        assert response.status_code == 401

    def test_connect_integration_success(self, auth_headers):
        """Successfully connect an integration."""
        response = requests.post(
            f"{BASE_URL}/api/kernel/integrations/connect",
            headers=auth_headers,
            json={
                "integration_id": "slack",
                "config": {
                    "bot_token": "xoxb-test-token-12345",
                    "signing_secret": "test-secret-abc123",
                },
                "enabled": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["integration_id"] == "slack"
        assert data["name"] == "Slack"
        assert data["status"] == "connected"
        assert data["enabled"] is True
        assert "connected_at" in data

    def test_connect_invalid_integration(self, auth_headers):
        """400 for invalid integration_id."""
        response = requests.post(
            f"{BASE_URL}/api/kernel/integrations/connect",
            headers=auth_headers,
            json={
                "integration_id": "nonexistent_integration",
                "config": {},
            },
        )
        assert response.status_code == 400

    def test_integration_appears_in_connected_list(self, auth_headers):
        """Connected integration appears in connected list."""
        # First connect
        requests.post(
            f"{BASE_URL}/api/kernel/integrations/connect",
            headers=auth_headers,
            json={"integration_id": "hubspot", "config": {"api_key": "test-key"}},
        )
        
        # Check available returns it in connected
        response = requests.get(
            f"{BASE_URL}/api/kernel/integrations/available",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "hubspot" in data["connected_ids"]
        assert any(c["integration_id"] == "hubspot" for c in data["connected"])


class TestIntegrationDisconnect:
    """Tests for DELETE /api/kernel/integrations/{id} endpoint."""

    def test_disconnect_integration_requires_auth(self):
        """401 without authentication."""
        response = requests.delete(f"{BASE_URL}/api/kernel/integrations/slack")
        assert response.status_code == 401

    def test_disconnect_integration_success(self, auth_headers):
        """Successfully disconnect an integration."""
        # First connect
        requests.post(
            f"{BASE_URL}/api/kernel/integrations/connect",
            headers=auth_headers,
            json={"integration_id": "webhooks", "config": {"webhook_url": "https://example.com/hooks/maars-test"}},
        )

        # Then disconnect
        response = requests.delete(
            f"{BASE_URL}/api/kernel/integrations/webhooks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "disconnected"

    def test_disconnect_removes_from_connected(self, auth_headers):
        """Disconnected integration is removed from connected list."""
        # Connect
        requests.post(
            f"{BASE_URL}/api/kernel/integrations/connect",
            headers=auth_headers,
            json={"integration_id": "shopify", "config": {"shop_domain": "test.myshopify.com", "access_token": "test"}},
        )
        
        # Disconnect
        requests.delete(f"{BASE_URL}/api/kernel/integrations/shopify", headers=auth_headers)
        
        # Verify not in connected
        response = requests.get(
            f"{BASE_URL}/api/kernel/integrations/available",
            headers=auth_headers,
        )
        data = response.json()
        assert "shopify" not in data["connected_ids"]


class TestIntegrationToggle:
    """Tests for PUT /api/kernel/integrations/{id}/toggle endpoint."""

    def test_toggle_integration_requires_auth(self):
        """401 without authentication."""
        response = requests.put(
            f"{BASE_URL}/api/kernel/integrations/slack/toggle",
            json={"enabled": False},
        )
        assert response.status_code == 401

    def test_toggle_integration_disable(self, auth_headers):
        """Successfully disable an integration."""
        # First connect
        requests.post(
            f"{BASE_URL}/api/kernel/integrations/connect",
            headers=auth_headers,
            json={"integration_id": "whatsapp", "config": {"phone_number_id": "123", "access_token": "test", "verify_token": "test"}},
        )
        
        # Toggle to disabled
        response = requests.put(
            f"{BASE_URL}/api/kernel/integrations/whatsapp/toggle",
            headers=auth_headers,
            json={"enabled": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False

    def test_toggle_integration_enable(self, auth_headers):
        """Successfully enable an integration."""
        # Connect and disable
        requests.post(
            f"{BASE_URL}/api/kernel/integrations/connect",
            headers=auth_headers,
            json={"integration_id": "salesforce", "config": {"instance_url": "https://test.salesforce.com", "client_id": "id", "client_secret": "secret", "refresh_token": "token"}},
        )
        requests.put(
            f"{BASE_URL}/api/kernel/integrations/salesforce/toggle",
            headers=auth_headers,
            json={"enabled": False},
        )
        
        # Toggle to enabled
        response = requests.put(
            f"{BASE_URL}/api/kernel/integrations/salesforce/toggle",
            headers=auth_headers,
            json={"enabled": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True

    def test_toggle_nonexistent_integration(self, auth_headers):
        """404 for toggling non-connected integration."""
        response = requests.put(
            f"{BASE_URL}/api/kernel/integrations/nonexistent/toggle",
            headers=auth_headers,
            json={"enabled": False},
        )
        assert response.status_code == 404

    def test_verify_connected_integration(self, auth_headers):
        requests.post(
            f"{BASE_URL}/api/kernel/integrations/connect",
            headers=auth_headers,
            json={
                "integration_id": "slack",
                "config": {
                    "bot_token": "xoxb-test-token-12345",
                },
            },
        )
        response = requests.post(
            f"{BASE_URL}/api/kernel/integrations/slack/verify",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["integration_id"] == "slack"
        assert data["verification_status"] in {"verified", "incomplete", "configured"}


class TestCampaignBuilderRegression:
    """Regression tests for Campaign Builder from iteration 73."""

    def test_campaign_templates_still_returns_6(self, auth_headers):
        """Campaign templates endpoint still works."""
        response = requests.get(
            f"{BASE_URL}/api/kernel/campaign-templates",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 6

    def test_campaigns_crud_works(self, auth_headers):
        """Campaign CRUD operations still work."""
        # List
        response = requests.get(f"{BASE_URL}/api/kernel/campaigns", headers=auth_headers)
        assert response.status_code == 200
        
        # Create
        response = requests.post(
            f"{BASE_URL}/api/kernel/campaigns",
            headers=auth_headers,
            json={"template_id": "content_marketing", "context": "Test context"},
        )
        assert response.status_code == 200
        campaign = response.json()
        campaign_id = campaign["campaign_id"]
        
        # Get
        response = requests.get(f"{BASE_URL}/api/kernel/campaigns/{campaign_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/kernel/campaigns/{campaign_id}", headers=auth_headers)
        assert response.status_code == 200


class TestWorkflowBuilderRegression:
    """Regression tests for Workflow Builder from iteration 73."""

    def test_workflows_crud_works(self, auth_headers):
        """Workflow CRUD operations still work."""
        # List
        response = requests.get(f"{BASE_URL}/api/kernel/workflows", headers=auth_headers)
        assert response.status_code == 200
        
        # Create
        response = requests.post(
            f"{BASE_URL}/api/kernel/workflows",
            headers=auth_headers,
            json={"name": "Test Workflow", "description": "Regression test"},
        )
        assert response.status_code == 200
        workflow = response.json()
        workflow_id = workflow["workflow_id"]
        
        # Get
        response = requests.get(f"{BASE_URL}/api/kernel/workflows/{workflow_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/kernel/workflows/{workflow_id}", headers=auth_headers)
        assert response.status_code == 200


class TestCleanup:
    """Cleanup test-created integrations."""

    def test_cleanup_test_integrations(self, auth_headers):
        """Clean up any integrations created during testing."""
        test_integrations = ["slack", "hubspot", "webhooks", "shopify", "whatsapp", "salesforce"]
        for int_id in test_integrations:
            requests.delete(f"{BASE_URL}/api/kernel/integrations/{int_id}", headers=auth_headers)
        
        # Verify cleanup
        response = requests.get(
            f"{BASE_URL}/api/kernel/integrations/available",
            headers=auth_headers,
        )
        data = response.json()
        for int_id in test_integrations:
            assert int_id not in data["connected_ids"], f"{int_id} should be disconnected"
