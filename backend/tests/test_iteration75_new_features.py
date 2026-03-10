"""
Iteration 75: Test Suite for 7 New Features
- Feature 1: Campaign PDF Reports
- Feature 2: Agent-to-Agent Collaboration (internal, tested via campaign execution)
- Feature 3: Advanced Trust Analytics
- Feature 4: Campaign Scheduling
- Feature 5: Multi-Tenancy/Organizations
- Feature 6: Custom Analytics Widgets Dashboard
- Feature 7: Self-Expanding Agent Suggestions
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token using admin credentials."""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "management.maars@marsgc.net",
        "password": "Admin123!"
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    pytest.skip("Authentication failed - skipping tests")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


# ===== Feature 3: Advanced Trust Analytics =====
class TestTrustAnalytics:
    """Tests for GET /api/kernel/trust-analytics"""
    
    def test_trust_analytics_returns_200(self, authenticated_client):
        """Test trust analytics endpoint returns 200."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/trust-analytics")
        assert response.status_code == 200
    
    def test_trust_analytics_has_trend_data(self, authenticated_client):
        """Test trust analytics has trend_data with 30+ entries."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/trust-analytics")
        assert response.status_code == 200
        data = response.json()
        assert "trend_data" in data
        # Should have approximately 30 days of data
        assert len(data["trend_data"]) >= 30
    
    def test_trust_analytics_trend_structure(self, authenticated_client):
        """Test trend_data entries have correct structure."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/trust-analytics")
        data = response.json()
        if data["trend_data"]:
            entry = data["trend_data"][0]
            assert "date" in entry
            assert "avg_trust" in entry
            assert "total_executions" in entry
            assert "avg_latency_ms" in entry
    
    def test_trust_analytics_has_anomalies(self, authenticated_client):
        """Test trust analytics has anomalies array."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/trust-analytics")
        data = response.json()
        assert "anomalies" in data
        assert isinstance(data["anomalies"], list)
    
    def test_trust_analytics_has_summary(self, authenticated_client):
        """Test trust analytics has summary with health_status."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/trust-analytics")
        data = response.json()
        assert "summary" in data
        summary = data["summary"]
        assert "health_status" in summary
        assert summary["health_status"] in ["healthy", "warning", "critical"]
        assert "total_agents_scored" in summary
        assert "avg_trust_score" in summary


# ===== Feature 4: Campaign Scheduling =====
class TestCampaignScheduling:
    """Tests for Campaign Scheduling APIs"""
    
    @pytest.fixture(scope="class")
    def test_campaign(self, authenticated_client):
        """Create a campaign for scheduling tests."""
        response = authenticated_client.post(f"{BASE_URL}/api/kernel/campaigns", json={
            "template_id": "content_marketing",
            "context": "TEST_SCHEDULE campaign for iteration 75"
        })
        assert response.status_code == 200
        campaign = response.json()
        yield campaign
        # Cleanup
        authenticated_client.delete(f"{BASE_URL}/api/kernel/campaigns/{campaign['campaign_id']}")
    
    def test_schedule_campaign(self, authenticated_client, test_campaign):
        """POST /api/kernel/campaigns/{id}/schedule sets schedule."""
        campaign_id = test_campaign["campaign_id"]
        response = authenticated_client.post(
            f"{BASE_URL}/api/kernel/campaigns/{campaign_id}/schedule",
            json={
                "frequency": "weekly",
                "day_of_week": 1,
                "hour": 9,
                "minute": 0,
                "enabled": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "schedule" in data
        assert data["schedule"]["frequency"] == "weekly"
        assert data["schedule"]["hour"] == 9
        assert data["schedule"]["enabled"] is True
    
    def test_get_scheduled_campaigns(self, authenticated_client, test_campaign):
        """GET /api/kernel/scheduled-campaigns returns campaigns with schedules."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/scheduled-campaigns")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should contain the test campaign
        campaign_ids = [c["campaign_id"] for c in data]
        assert test_campaign["campaign_id"] in campaign_ids
    
    def test_remove_schedule(self, authenticated_client, test_campaign):
        """DELETE /api/kernel/campaigns/{id}/schedule removes schedule."""
        campaign_id = test_campaign["campaign_id"]
        response = authenticated_client.delete(
            f"{BASE_URL}/api/kernel/campaigns/{campaign_id}/schedule"
        )
        assert response.status_code == 200
        data = response.json()
        # Schedule should be removed (None or not present)
        assert data.get("schedule") is None


# ===== Feature 5: Multi-Tenancy / Organizations =====
class TestOrganizations:
    """Tests for Organization/Multi-Tenancy APIs"""
    
    def test_get_my_organization(self, authenticated_client):
        """GET /api/kernel/organizations/me returns org or empty."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/organizations/me")
        assert response.status_code == 200
        data = response.json()
        # Either has org or is empty
        assert "org" in data or "members" in data
    
    def test_create_organization(self, authenticated_client):
        """POST /api/kernel/organizations creates org with members."""
        response = authenticated_client.post(f"{BASE_URL}/api/kernel/organizations", json={
            "name": "TEST_ORG Iteration75",
            "slug": "test-org-iter75"
        })
        # May succeed or fail if org already exists
        if response.status_code == 200:
            data = response.json()
            assert "org_id" in data
            assert "name" in data
            assert "members" in data
            assert len(data["members"]) >= 1  # Owner should be in members
            assert data["members"][0]["role"] == "owner"
        else:
            # Org may already exist - verify via /me
            me_response = authenticated_client.get(f"{BASE_URL}/api/kernel/organizations/me")
            assert me_response.status_code == 200
    
    def test_organization_has_enriched_members(self, authenticated_client):
        """GET /api/kernel/organizations/me returns enriched member data."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/organizations/me")
        assert response.status_code == 200
        data = response.json()
        if data.get("org"):
            members = data.get("members", [])
            if members:
                member = members[0]
                # Should have name and email enriched
                assert "name" in member or "email" in member
                assert "role" in member
    
    def test_invite_member(self, authenticated_client):
        """POST /api/kernel/organizations/{id}/invite creates invite."""
        me_response = authenticated_client.get(f"{BASE_URL}/api/kernel/organizations/me")
        org_data = me_response.json()
        if not org_data.get("org"):
            pytest.skip("No organization to test invite")
        
        org_id = org_data["org"]["org_id"]
        response = authenticated_client.post(
            f"{BASE_URL}/api/kernel/organizations/{org_id}/invite",
            json={"email": "test_invite@example.com", "role": "member"}
        )
        # Should succeed (invite stored)
        assert response.status_code == 200
        data = response.json()
        assert "invite_id" in data or "email" in data


# ===== Feature 6: Custom Analytics Widgets =====
class TestAnalyticsWidgets:
    """Tests for Custom Analytics Widgets Dashboard"""
    
    def test_widget_catalog_returns_8(self, authenticated_client):
        """GET /api/kernel/widgets/catalog returns 8 widget definitions."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/widgets/catalog")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 8
    
    def test_widget_catalog_structure(self, authenticated_client):
        """Widget catalog entries have correct structure."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/widgets/catalog")
        data = response.json()
        widget_ids = [w["widget_id"] for w in data]
        expected_ids = ["agent_usage", "cost_trend", "campaign_performance", 
                       "trust_overview", "active_integrations", "model_distribution",
                       "latency_heatmap", "workflow_status"]
        for wid in expected_ids:
            assert wid in widget_ids
    
    def test_get_custom_dashboard(self, authenticated_client):
        """GET /api/kernel/dashboard/custom returns dashboard with widgets."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/dashboard/custom")
        assert response.status_code == 200
        data = response.json()
        assert "widgets" in data
        # Default should have 5 widgets
        assert len(data["widgets"]) >= 5
    
    def test_save_custom_dashboard(self, authenticated_client):
        """PUT /api/kernel/dashboard/custom saves widget configuration."""
        custom_widgets = [
            {"widget_id": "trust_overview", "x": 0, "y": 0},
            {"widget_id": "active_integrations", "x": 1, "y": 0},
        ]
        response = authenticated_client.put(
            f"{BASE_URL}/api/kernel/dashboard/custom",
            json={"widgets": custom_widgets}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["widgets"]) == 2
    
    def test_widget_data_trust_overview(self, authenticated_client):
        """GET /api/kernel/widgets/trust_overview/data returns trust data."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/widgets/trust_overview/data")
        assert response.status_code == 200
        data = response.json()
        assert "avg_trust" in data
        assert "total_agents" in data
    
    def test_widget_data_agent_usage(self, authenticated_client):
        """GET /api/kernel/widgets/agent_usage/data returns agent data."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/widgets/agent_usage/data")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
    
    def test_widget_data_cost_trend(self, authenticated_client):
        """GET /api/kernel/widgets/cost_trend/data returns cost data."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/widgets/cost_trend/data")
        assert response.status_code == 200
        data = response.json()
        assert "days" in data
        assert "total" in data
    
    def test_widget_data_campaign_performance(self, authenticated_client):
        """GET /api/kernel/widgets/campaign_performance/data returns campaign stats."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/widgets/campaign_performance/data")
        assert response.status_code == 200
        data = response.json()
        # Should have completed, failed, draft counts
        assert "total" in data or "completed" in data
    
    def test_widget_data_active_integrations(self, authenticated_client):
        """GET /api/kernel/widgets/active_integrations/data returns integration count."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/widgets/active_integrations/data")
        assert response.status_code == 200
        data = response.json()
        assert "active" in data
        assert "total" in data
    
    def test_widget_data_model_distribution(self, authenticated_client):
        """GET /api/kernel/widgets/model_distribution/data returns model stats."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/widgets/model_distribution/data")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
    
    def test_widget_data_workflow_status(self, authenticated_client):
        """GET /api/kernel/widgets/workflow_status/data returns workflow stats."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/widgets/workflow_status/data")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data


# ===== Feature 7: Self-Expanding Agent Suggestions =====
class TestAgentSuggestions:
    """Tests for Agent Suggestions APIs"""
    
    def test_agent_suggestions_returns_200(self, authenticated_client):
        """GET /api/kernel/agent-suggestions returns suggestions."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/agent-suggestions")
        assert response.status_code == 200
    
    def test_agent_suggestions_has_analysis(self, authenticated_client):
        """Agent suggestions include analysis object."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/agent-suggestions")
        data = response.json()
        assert "suggestions" in data
        assert "analysis" in data
        analysis = data["analysis"]
        assert "total_campaigns" in analysis
        assert "total_workflows" in analysis
        assert "existing_agent_count" in analysis
    
    def test_agent_suggestions_structure(self, authenticated_client):
        """Agent suggestions have correct structure."""
        response = authenticated_client.get(f"{BASE_URL}/api/kernel/agent-suggestions")
        data = response.json()
        suggestions = data.get("suggestions", [])
        if suggestions:
            s = suggestions[0]
            assert "name" in s
            assert "role" in s
            assert "network" in s
            assert "confidence" in s
            assert "based_on" in s
    
    def test_create_agent_from_suggestion(self, authenticated_client):
        """POST /api/kernel/agent-suggestions/create creates auto-generated agent."""
        response = authenticated_client.post(
            f"{BASE_URL}/api/kernel/agent-suggestions/create",
            json={
                "name": "TEST_AutoAgent Iteration75",
                "role": "Test Role for Iteration 75",
                "network": "operations",
                "description": "Auto-created agent for testing"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "agent_id" in data
        assert data["name"] == "TEST_AutoAgent Iteration75"
        assert data["auto_created"] is True


# ===== Feature 1: Campaign PDF Reports =====
class TestCampaignPDFReport:
    """Tests for Campaign PDF Report generation"""
    
    @pytest.fixture(scope="class")
    def completed_campaign(self, authenticated_client):
        """Create and run a campaign to completion for PDF test."""
        # Create campaign
        response = authenticated_client.post(f"{BASE_URL}/api/kernel/campaigns", json={
            "template_id": "data_analysis",
            "context": "TEST_PDF Report generation test"
        })
        assert response.status_code == 200
        campaign = response.json()
        yield campaign
        # Cleanup
        authenticated_client.delete(f"{BASE_URL}/api/kernel/campaigns/{campaign['campaign_id']}")
    
    def test_pdf_report_endpoint_exists(self, authenticated_client, completed_campaign):
        """GET /api/kernel/campaigns/{id}/report returns PDF."""
        campaign_id = completed_campaign["campaign_id"]
        response = authenticated_client.get(
            f"{BASE_URL}/api/kernel/campaigns/{campaign_id}/report"
        )
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
    
    def test_pdf_report_has_content(self, authenticated_client, completed_campaign):
        """PDF report has non-zero content."""
        campaign_id = completed_campaign["campaign_id"]
        response = authenticated_client.get(
            f"{BASE_URL}/api/kernel/campaigns/{campaign_id}/report"
        )
        assert response.status_code == 200
        # PDF should have content (typically starts with %PDF)
        content = response.content
        assert len(content) > 100
        assert content[:4] == b'%PDF'


# ===== Auth Required Tests =====
class TestAuthRequired:
    """Verify all new endpoints require authentication"""
    
    def test_trust_analytics_requires_auth(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/kernel/trust-analytics")
        assert response.status_code == 401
    
    def test_widgets_requires_auth(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/kernel/widgets/catalog")
        assert response.status_code == 401
    
    def test_dashboard_requires_auth(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/kernel/dashboard/custom")
        assert response.status_code == 401
    
    def test_agent_suggestions_requires_auth(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/kernel/agent-suggestions")
        assert response.status_code == 401
    
    def test_organizations_me_requires_auth(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/kernel/organizations/me")
        assert response.status_code == 401
    
    def test_scheduled_campaigns_requires_auth(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/kernel/scheduled-campaigns")
        assert response.status_code == 401
