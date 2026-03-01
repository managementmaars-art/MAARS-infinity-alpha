"""
Backend tests for iteration 28:
- Agent enable/disable toggle (is_active field)
- Brain Editor temperature and max_tokens controls
- CSV Analytics Export
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    res = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if res.status_code == 200:
        return res.json().get("token")
    pytest.skip(f"Admin login failed: {res.status_code}")


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Headers with admin auth"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestAgentToggle:
    """Tests for agent enable/disable (is_active) functionality"""
    
    def test_disable_agent_via_settings(self, admin_headers):
        """PUT /api/admin/agents/{agent_id}/settings with is_active=false disables agent"""
        res = requests.put(
            f"{BASE_URL}/api/admin/agents/agent_seo/settings",
            headers=admin_headers,
            json={"is_active": False}
        )
        assert res.status_code == 200, f"Failed to disable agent: {res.text}"
        data = res.json()
        assert data.get("success") is True
        assert "is_active" in data.get("updated", [])
        print("PASSED: Agent disabled successfully via settings endpoint")
    
    def test_disabled_agent_not_in_user_endpoint(self, admin_headers):
        """GET /api/agents (user endpoint) does NOT return disabled agents"""
        # First ensure agent_seo is disabled
        requests.put(
            f"{BASE_URL}/api/admin/agents/agent_seo/settings",
            headers=admin_headers,
            json={"is_active": False}
        )
        
        res = requests.get(f"{BASE_URL}/api/agents", headers=admin_headers)
        assert res.status_code == 200
        agents = res.json()
        agent_ids = [a.get("agent_id") for a in agents]
        assert "agent_seo" not in agent_ids, "Disabled agent should not appear in user endpoint"
        print("PASSED: Disabled agent not returned by user endpoint /api/agents")
    
    def test_disabled_agent_not_in_public_endpoint(self, admin_headers):
        """GET /api/agents/public does NOT return disabled agents"""
        # First ensure agent_seo is disabled
        requests.put(
            f"{BASE_URL}/api/admin/agents/agent_seo/settings",
            headers=admin_headers,
            json={"is_active": False}
        )
        
        res = requests.get(f"{BASE_URL}/api/agents/public")
        assert res.status_code == 200
        agents = res.json()
        agent_ids = [a.get("agent_id") for a in agents]
        assert "agent_seo" not in agent_ids, "Disabled agent should not appear in public endpoint"
        print("PASSED: Disabled agent not returned by public endpoint /api/agents/public")
    
    def test_admin_endpoint_returns_disabled_agents(self, admin_headers):
        """GET /api/admin/agents returns ALL agents including disabled ones"""
        # First ensure agent_seo is disabled
        requests.put(
            f"{BASE_URL}/api/admin/agents/agent_seo/settings",
            headers=admin_headers,
            json={"is_active": False}
        )
        
        res = requests.get(f"{BASE_URL}/api/admin/agents", headers=admin_headers)
        assert res.status_code == 200
        agents = res.json()
        agent_ids = [a.get("agent_id") for a in agents]
        assert "agent_seo" in agent_ids, "Admin endpoint should return all agents including disabled"
        
        # Verify the disabled agent has is_active=False
        seo_agent = next((a for a in agents if a.get("agent_id") == "agent_seo"), None)
        assert seo_agent is not None
        assert seo_agent.get("is_active") is False, "Disabled agent should have is_active=False"
        print("PASSED: Admin endpoint returns all agents including disabled ones with is_active=False")
    
    def test_enable_agent_via_settings(self, admin_headers):
        """PUT /api/admin/agents/{agent_id}/settings with is_active=true re-enables agent"""
        res = requests.put(
            f"{BASE_URL}/api/admin/agents/agent_seo/settings",
            headers=admin_headers,
            json={"is_active": True}
        )
        assert res.status_code == 200, f"Failed to re-enable agent: {res.text}"
        data = res.json()
        assert data.get("success") is True
        print("PASSED: Agent re-enabled successfully")
        
        # Verify agent now appears in user endpoint
        res2 = requests.get(f"{BASE_URL}/api/agents", headers=admin_headers)
        assert res2.status_code == 200
        agents = res2.json()
        agent_ids = [a.get("agent_id") for a in agents]
        assert "agent_seo" in agent_ids, "Re-enabled agent should appear in user endpoint"
        print("PASSED: Re-enabled agent appears in user endpoint")


class TestBrainEditorTemperatureMaxTokens:
    """Tests for Brain Editor temperature and max_tokens controls"""
    
    def test_save_temperature_via_brain_endpoint(self, admin_headers):
        """PUT /api/admin/agents/{agent_id}/brain with temperature saves correctly"""
        res = requests.put(
            f"{BASE_URL}/api/admin/agents/agent_marketing/brain",
            headers=admin_headers,
            json={"temperature": 0.8}
        )
        assert res.status_code == 200, f"Failed to save temperature: {res.text}"
        data = res.json()
        assert data.get("success") is True or "agent" in data
        print("PASSED: Temperature saved via brain endpoint")
        
        # Verify persistence
        res2 = requests.get(f"{BASE_URL}/api/admin/agents/agent_marketing", headers=admin_headers)
        if res2.status_code == 200:
            agent = res2.json()
            assert agent.get("temperature") == 0.8, f"Temperature not persisted: {agent.get('temperature')}"
            print("PASSED: Temperature persisted correctly: 0.8")
    
    def test_save_max_tokens_via_brain_endpoint(self, admin_headers):
        """PUT /api/admin/agents/{agent_id}/brain with max_tokens saves correctly"""
        res = requests.put(
            f"{BASE_URL}/api/admin/agents/agent_marketing/brain",
            headers=admin_headers,
            json={"max_tokens": 8192}
        )
        assert res.status_code == 200, f"Failed to save max_tokens: {res.text}"
        data = res.json()
        assert data.get("success") is True or "agent" in data
        print("PASSED: Max tokens saved via brain endpoint")
        
        # Verify persistence
        res2 = requests.get(f"{BASE_URL}/api/admin/agents/agent_marketing", headers=admin_headers)
        if res2.status_code == 200:
            agent = res2.json()
            assert agent.get("max_tokens") == 8192, f"Max tokens not persisted: {agent.get('max_tokens')}"
            print("PASSED: Max tokens persisted correctly: 8192")
    
    def test_save_both_temperature_and_max_tokens(self, admin_headers):
        """PUT /api/admin/agents/{agent_id}/brain with both temperature and max_tokens"""
        res = requests.put(
            f"{BASE_URL}/api/admin/agents/agent_strategist/brain",
            headers=admin_headers,
            json={"temperature": 0.5, "max_tokens": 4096}
        )
        assert res.status_code == 200, f"Failed to save both params: {res.text}"
        print("PASSED: Both temperature and max_tokens saved")
        
        # Verify persistence
        res2 = requests.get(f"{BASE_URL}/api/admin/agents/agent_strategist", headers=admin_headers)
        if res2.status_code == 200:
            agent = res2.json()
            assert agent.get("temperature") == 0.5
            assert agent.get("max_tokens") == 4096
            print("PASSED: Both values persisted correctly")


class TestAnalyticsExport:
    """Tests for CSV Analytics Export functionality"""
    
    def test_analytics_export_returns_csv(self, admin_headers):
        """GET /api/admin/analytics/export returns valid CSV file"""
        res = requests.get(
            f"{BASE_URL}/api/admin/analytics/export?format=csv",
            headers=admin_headers
        )
        assert res.status_code == 200, f"Export failed: {res.status_code}"
        
        # Check content type
        content_type = res.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Wrong content type: {content_type}"
        print("PASSED: Analytics export returns text/csv content type")
    
    def test_analytics_export_has_users_section(self, admin_headers):
        """CSV export contains USERS section"""
        res = requests.get(
            f"{BASE_URL}/api/admin/analytics/export?format=csv",
            headers=admin_headers
        )
        assert res.status_code == 200
        content = res.text
        assert "=== USERS ===" in content, "CSV should contain USERS section"
        assert "User ID" in content, "CSV should have User ID column"
        assert "Email" in content, "CSV should have Email column"
        print("PASSED: CSV contains USERS section with proper columns")
    
    def test_analytics_export_has_agent_usage_section(self, admin_headers):
        """CSV export contains AGENT USAGE section"""
        res = requests.get(
            f"{BASE_URL}/api/admin/analytics/export?format=csv",
            headers=admin_headers
        )
        assert res.status_code == 200
        content = res.text
        assert "=== AGENT USAGE ===" in content, "CSV should contain AGENT USAGE section"
        print("PASSED: CSV contains AGENT USAGE section")
    
    def test_analytics_export_has_payments_section(self, admin_headers):
        """CSV export contains PAYMENTS section"""
        res = requests.get(
            f"{BASE_URL}/api/admin/analytics/export?format=csv",
            headers=admin_headers
        )
        assert res.status_code == 200
        content = res.text
        assert "=== PAYMENTS ===" in content, "CSV should contain PAYMENTS section"
        print("PASSED: CSV contains PAYMENTS section")
    
    def test_analytics_export_has_summary_section(self, admin_headers):
        """CSV export contains SUMMARY section with totals"""
        res = requests.get(
            f"{BASE_URL}/api/admin/analytics/export?format=csv",
            headers=admin_headers
        )
        assert res.status_code == 200
        content = res.text
        assert "=== SUMMARY ===" in content, "CSV should contain SUMMARY section"
        assert "Total Users" in content, "CSV should have Total Users summary"
        assert "Total Revenue" in content, "CSV should have Total Revenue summary"
        print("PASSED: CSV contains SUMMARY section with totals")
    
    def test_analytics_export_has_content_disposition(self, admin_headers):
        """CSV export has proper Content-Disposition header for download"""
        res = requests.get(
            f"{BASE_URL}/api/admin/analytics/export?format=csv",
            headers=admin_headers
        )
        assert res.status_code == 200
        disposition = res.headers.get("Content-Disposition", "")
        assert "attachment" in disposition, "Should have attachment disposition"
        assert "maars_analytics" in disposition, "Filename should contain maars_analytics"
        assert ".csv" in disposition, "Filename should have .csv extension"
        print(f"PASSED: Proper Content-Disposition header: {disposition}")


class TestAnalyticsRegression:
    """Regression tests for Analytics dashboard"""
    
    def test_analytics_endpoint_works(self, admin_headers):
        """GET /api/admin/analytics returns data"""
        res = requests.get(f"{BASE_URL}/api/admin/analytics", headers=admin_headers)
        assert res.status_code == 200, f"Analytics endpoint failed: {res.status_code}"
        data = res.json()
        assert "kpis" in data, "Should have kpis"
        print("PASSED: Analytics endpoint returns KPIs")
    
    def test_activity_feed_regression(self, admin_headers):
        """GET /api/admin/activity-feed still works"""
        res = requests.get(f"{BASE_URL}/api/admin/activity-feed?limit=5", headers=admin_headers)
        assert res.status_code == 200, f"Activity feed failed: {res.status_code}"
        data = res.json()
        assert isinstance(data, list), "Should return array"
        print(f"PASSED: Activity feed returns {len(data)} events")


class TestCleanup:
    """Cleanup after tests"""
    
    def test_restore_agent_state(self, admin_headers):
        """Ensure agent_seo is re-enabled after tests"""
        res = requests.put(
            f"{BASE_URL}/api/admin/agents/agent_seo/settings",
            headers=admin_headers,
            json={"is_active": True}
        )
        assert res.status_code == 200
        print("CLEANUP: agent_seo re-enabled")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
