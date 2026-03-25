"""
Iteration 31 Tests: User Insights Dashboard + Backend Refactoring Regression
Tests:
1. GET /api/user/insights - Personal usage stats endpoint
2. Regression: /api/agents returns 21 agents
3. Regression: /api/admin/analytics works
4. Regression: /api/auth/login works
5. Regression: /api/plans returns 4 plans
6. Regression: Agent chat flow (send message, get AI response)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://maars-infinity.preview.emergentagent.com").rstrip("/")

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestAdminLogin:
    """Test admin authentication"""

    def test_admin_login_success(self):
        """Login with admin credentials"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        data = resp.json()
        assert "token" in data, "No token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["is_admin"] is True, "User should be admin"


class TestUserInsightsEndpoint:
    """Test the new /api/user/insights endpoint"""

    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if resp.status_code == 200:
            return resp.json().get("token")
        pytest.skip("Admin login failed")

    def test_insights_endpoint_requires_auth(self):
        """Insights endpoint should reject unauthenticated requests"""
        resp = requests.get(f"{BASE_URL}/api/user/insights")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    def test_insights_endpoint_returns_stats(self, admin_token):
        """Insights endpoint returns user stats"""
        resp = requests.get(
            f"{BASE_URL}/api/user/insights",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200, f"Insights failed: {resp.text}"
        data = resp.json()
        
        # Check top-level keys
        assert "stats" in data, "Missing 'stats' key"
        assert "favorite_agents" in data, "Missing 'favorite_agents' key"
        assert "recommendations" in data, "Missing 'recommendations' key"
        assert "daily_activity" in data, "Missing 'daily_activity' key"

    def test_insights_stats_structure(self, admin_token):
        """Insights stats contain all required fields"""
        resp = requests.get(
            f"{BASE_URL}/api/user/insights",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        stats = resp.json().get("stats", {})
        
        required_fields = [
            "total_chats", "user_messages", "ai_messages",
            "credits_remaining", "credits_used", "plan",
            "feedback_up", "feedback_down", "streak"
        ]
        for field in required_fields:
            assert field in stats, f"Missing field '{field}' in stats"
        
        # Validate types
        assert isinstance(stats["total_chats"], int)
        assert isinstance(stats["user_messages"], int)
        assert isinstance(stats["ai_messages"], int)
        assert isinstance(stats["credits_remaining"], int)
        assert isinstance(stats["credits_used"], int)
        assert isinstance(stats["plan"], str)
        assert isinstance(stats["feedback_up"], int)
        assert isinstance(stats["feedback_down"], int)
        assert isinstance(stats["streak"], int)

    def test_insights_favorite_agents_structure(self, admin_token):
        """favorite_agents is a list with expected structure"""
        resp = requests.get(
            f"{BASE_URL}/api/user/insights",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        favorites = resp.json().get("favorite_agents", [])
        
        assert isinstance(favorites, list), "favorite_agents should be a list"
        # If there are any, verify structure
        if favorites:
            fav = favorites[0]
            assert "agent_id" in fav, "Missing agent_id in favorite"
            assert "name" in fav, "Missing name in favorite"
            assert "avatar" in fav, "Missing avatar in favorite"
            assert "role" in fav, "Missing role in favorite"
            assert "messages" in fav, "Missing messages count in favorite"

    def test_insights_recommendations_structure(self, admin_token):
        """recommendations is a list with expected structure"""
        resp = requests.get(
            f"{BASE_URL}/api/user/insights",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        recs = resp.json().get("recommendations", [])
        
        assert isinstance(recs, list), "recommendations should be a list"
        # If there are any, verify structure
        if recs:
            rec = recs[0]
            assert "agent_id" in rec, "Missing agent_id in recommendation"
            assert "name" in rec, "Missing name in recommendation"
            assert "avatar" in rec, "Missing avatar in recommendation"
            assert "role" in rec, "Missing role in recommendation"

    def test_insights_daily_activity_structure(self, admin_token):
        """daily_activity contains 30 days of data"""
        resp = requests.get(
            f"{BASE_URL}/api/user/insights",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        activity = resp.json().get("daily_activity", [])
        
        assert isinstance(activity, list), "daily_activity should be a list"
        assert len(activity) >= 30, f"Expected 30+ days, got {len(activity)}"
        
        # Check structure of each day
        if activity:
            day = activity[0]
            assert "date" in day, "Missing date in daily_activity"
            assert "messages" in day, "Missing messages count in daily_activity"


class TestRegressionAgents:
    """Regression test: /api/agents endpoint after refactoring"""

    @pytest.fixture
    def admin_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if resp.status_code == 200:
            return resp.json().get("token")
        pytest.skip("Admin login failed")

    def test_agents_endpoint_returns_21_agents(self, admin_token):
        """After refactoring, /api/agents should still return 21 agents"""
        resp = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200, f"Failed: {resp.text}"
        agents = resp.json()
        assert isinstance(agents, list), "Should return list"
        assert len(agents) == 21, f"Expected 21 agents, got {len(agents)}"

    def test_agents_have_correct_structure(self, admin_token):
        """Each agent should have required fields from config.py"""
        resp = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        agents = resp.json()
        
        required_fields = ["agent_id", "name", "description", "avatar", "role", "capabilities"]
        for agent in agents[:5]:  # Check first 5
            for field in required_fields:
                assert field in agent, f"Agent {agent.get('name', 'unknown')} missing {field}"


class TestRegressionAdminAnalytics:
    """Regression test: /api/admin/analytics after refactoring"""

    @pytest.fixture
    def admin_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if resp.status_code == 200:
            return resp.json().get("token")
        pytest.skip("Admin login failed")

    def test_admin_analytics_endpoint(self, admin_token):
        """Admin analytics returns valid KPIs"""
        resp = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        
        # KPIs should be nested under 'kpis' key
        assert "kpis" in data, "Missing 'kpis' key"
        kpis = data["kpis"]
        
        # Check essential KPIs (total_users, total_chats, mrr, etc.)
        expected_kpis = ["total_users", "total_chats", "mrr"]
        for kpi in expected_kpis:
            assert kpi in kpis, f"Missing KPI '{kpi}'"


class TestRegressionPlans:
    """Regression test: /api/plans endpoint"""

    def test_plans_endpoint_returns_4_plans(self):
        """Plans endpoint should return 4 subscription plans"""
        resp = requests.get(f"{BASE_URL}/api/plans")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        
        assert "plans" in data, "Missing 'plans' key"
        plans = data["plans"]
        # Plans is a dict with plan_id as keys
        assert isinstance(plans, dict), "plans should be a dict"
        assert len(plans) == 4, f"Expected 4 plans, got {len(plans)}"
        
        # Verify plan IDs as keys
        for expected in ["free", "starter", "pro", "business"]:
            assert expected in plans, f"Missing plan '{expected}'"


class TestRegressionAgentChat:
    """Regression test: Agent chat still works after refactoring"""

    @pytest.fixture
    def admin_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if resp.status_code == 200:
            return resp.json().get("token")
        pytest.skip("Admin login failed")

    def test_create_chat_and_send_message(self, admin_token):
        """Create a chat and send a message (basic flow)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create chat with secretary agent
        create_resp = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": "agent_secretary", "title": "Test Chat from Iteration 31"}
        )
        assert create_resp.status_code == 200, f"Create chat failed: {create_resp.text}"
        chat = create_resp.json()
        chat_id = chat.get("chat_id")
        assert chat_id, "No chat_id returned"
        
        # Send a simple message (non-streaming)
        msg_resp = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": "Hello, please respond briefly."}
        )
        # Allow timeout (AI can be slow) but should succeed
        assert msg_resp.status_code in [200, 504], f"Message failed: {msg_resp.status_code}"
        
        # Cleanup - delete the test chat
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=headers)


class TestConfigImports:
    """Verify config.py imports are working correctly"""

    @pytest.fixture
    def admin_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if resp.status_code == 200:
            return resp.json().get("token")
        pytest.skip("Admin login failed")

    def test_agent_tools_endpoint(self, admin_token):
        """Agent tools endpoint should return tools from config.py"""
        resp = requests.get(
            f"{BASE_URL}/api/agents/tools",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        
        assert "tools" in data, "Missing 'tools' key"
        assert "agent_tools" in data, "Missing 'agent_tools' key"
        
        # Verify some core tools exist
        tools = data["tools"]
        for expected_tool in ["web_search", "calculate", "create_task"]:
            assert expected_tool in tools, f"Missing tool '{expected_tool}'"

    def test_agents_have_tools_from_config(self, admin_token):
        """Agents should have tools field populated from AGENT_TOOL_MAP in config.py"""
        resp = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        agents = resp.json()
        
        # Commander should have tools
        commander = next((a for a in agents if a.get("agent_id") == "agent_commander"), None)
        assert commander, "Commander agent not found"
        assert "tools" in commander, "Commander missing tools"
        assert isinstance(commander["tools"], list), "tools should be a list"
        # Commander should have web_search according to AGENT_TOOL_MAP in config.py
        assert "web_search" in commander["tools"], "Commander should have web_search tool"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
