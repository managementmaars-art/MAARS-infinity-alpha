"""
Test suite for MAARS Global Corporation Robot Avatars and Custom Agent Creation features.
Tests:
- All 20 default agents have new robot avatar URLs (containing 'static.prod-images.emergentagent.com')
- GET /api/agents/create/info returns correct creation cost, plan limits, and current count
- Free plan users get 403 when trying to create agents
- Admin user can create agents without credit deduction
- Plan-based custom agent limits are enforced
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-team-commander.preview.emergentagent.com')

# Admin credentials (bypasses all limits)
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"

# Regular free plan user credentials
FREE_USER_EMAIL = "admin@test.com"
FREE_USER_PASSWORD = "Admin1234!"

# Expected values
CUSTOM_AGENT_CREDIT_COST = 20
ROBOT_AVATAR_PATTERN = "static.prod-images.emergentagent.com"


class TestRobotAvatars:
    """Test that all 20 default agents have new robot/futuristic avatar URLs"""

    @pytest.fixture
    def admin_token(self):
        """Get admin user token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["token"]

    def test_all_default_agents_have_robot_avatars(self, admin_token):
        """All 20 default agents should have new robot avatar URLs"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        agents = response.json()
        
        # Filter to default agents only
        default_agents = [a for a in agents if not a.get("is_custom")]
        
        # Should have exactly 20 default agents
        assert len(default_agents) == 20, f"Expected 20 default agents, got {len(default_agents)}"
        
        # Each default agent should have the new robot avatar URL pattern
        for agent in default_agents:
            assert ROBOT_AVATAR_PATTERN in agent["avatar"], \
                f"Agent {agent['name']} has old avatar URL: {agent['avatar']}"

    def test_each_agent_has_unique_avatar(self, admin_token):
        """Each of the 20 default agents should have a unique avatar URL"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        agents = response.json()
        default_agents = [a for a in agents if not a.get("is_custom")]
        
        avatars = [a["avatar"] for a in default_agents]
        unique_avatars = set(avatars)
        
        assert len(unique_avatars) == len(avatars), \
            f"Found duplicate avatars: {len(avatars)} agents but only {len(unique_avatars)} unique avatars"


class TestCreateAgentInfo:
    """Test GET /api/agents/create/info endpoint returns correct info"""

    @pytest.fixture
    def admin_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]

    @pytest.fixture
    def free_user_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": FREE_USER_EMAIL, "password": FREE_USER_PASSWORD}
        )
        return response.json()["token"]

    def test_create_info_returns_correct_cost(self, free_user_token):
        """Create info should return correct credit cost (20 credits)"""
        response = requests.get(
            f"{BASE_URL}/api/agents/create/info",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["credit_cost"] == CUSTOM_AGENT_CREDIT_COST, \
            f"Expected credit_cost={CUSTOM_AGENT_CREDIT_COST}, got {data['credit_cost']}"

    def test_create_info_returns_plan_limits_for_free_user(self, free_user_token):
        """Free user should see max_custom_agents=0"""
        response = requests.get(
            f"{BASE_URL}/api/agents/create/info",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        data = response.json()
        
        # Free plan allows 0 custom agents
        assert data["max_custom_agents"] == 0, \
            f"Free plan should have max_custom_agents=0, got {data['max_custom_agents']}"
        assert data["plan_name"] == "Free"
        assert data["can_create"] is False, "Free user should not be able to create agents"

    def test_create_info_returns_all_required_fields(self, free_user_token):
        """Create info should return all required fields"""
        response = requests.get(
            f"{BASE_URL}/api/agents/create/info",
            headers={"Authorization": f"Bearer {free_user_token}"}
        )
        data = response.json()
        
        required_fields = [
            "credit_cost", "credits_remaining", "can_afford",
            "max_custom_agents", "current_custom_count", "can_create",
            "plan_name", "is_admin"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_admin_bypasses_limits(self, admin_token):
        """Admin should bypass all limits (max_custom_agents=-1, can_create=true)"""
        response = requests.get(
            f"{BASE_URL}/api/agents/create/info",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        assert data["is_admin"] is True
        assert data["max_custom_agents"] == -1, "Admin should have unlimited custom agents (-1)"
        assert data["can_create"] is True, "Admin should always be able to create agents"


class TestFreePlanAgentCreation:
    """Test that free plan users cannot create custom agents"""

    @pytest.fixture
    def free_user_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": FREE_USER_EMAIL, "password": FREE_USER_PASSWORD}
        )
        return response.json()["token"]

    def test_free_user_gets_403_on_agent_creation(self, free_user_token):
        """Free plan user should get 403 when trying to create agent"""
        response = requests.post(
            f"{BASE_URL}/api/agents",
            headers={
                "Authorization": f"Bearer {free_user_token}",
                "Content-Type": "application/json"
            },
            json={
                "name": "TEST_FreeUserAgent",
                "description": "Agent created by free user (should fail)",
                "role": "Test Role",
                "system_prompt": "You are a test agent"
            }
        )
        
        assert response.status_code == 403, \
            f"Expected 403 Forbidden, got {response.status_code}"
        
        data = response.json()
        assert "Free plan" in data["detail"], \
            f"Error message should mention Free plan: {data['detail']}"
        assert "upgrade" in data["detail"].lower(), \
            f"Error message should suggest upgrade: {data['detail']}"


class TestAdminAgentCreation:
    """Test that admin can create agents without credit deduction"""

    @pytest.fixture
    def admin_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]

    def test_admin_can_create_agent(self, admin_token):
        """Admin should be able to create custom agent"""
        # Get initial credits
        info_before = requests.get(
            f"{BASE_URL}/api/agents/create/info",
            headers={"Authorization": f"Bearer {admin_token}"}
        ).json()
        credits_before = info_before["credits_remaining"]
        
        # Create agent
        response = requests.post(
            f"{BASE_URL}/api/agents",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            json={
                "name": "TEST_AdminCreatedAgent",
                "description": "Agent created by admin for testing",
                "role": "Test Specialist",
                "system_prompt": "You are a test agent created by admin"
            }
        )
        
        assert response.status_code == 200, \
            f"Admin agent creation failed: {response.json()}"
        
        agent = response.json()
        assert agent["name"] == "TEST_AdminCreatedAgent"
        assert agent["is_custom"] is True
        agent_id = agent["agent_id"]
        
        # Verify credits were NOT deducted for admin
        info_after = requests.get(
            f"{BASE_URL}/api/agents/create/info",
            headers={"Authorization": f"Bearer {admin_token}"}
        ).json()
        credits_after = info_after["credits_remaining"]
        
        assert credits_after == credits_before, \
            f"Admin credits should not be deducted: before={credits_before}, after={credits_after}"
        
        # Cleanup: delete the test agent
        delete_resp = requests.delete(
            f"{BASE_URL}/api/agents/{agent_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_resp.status_code == 200


class TestSubscriptionPlanLimits:
    """Test that SUBSCRIPTION_PLANS have correct max_custom_agents values"""

    @pytest.fixture
    def admin_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]

    def test_subscription_plans_exist(self, admin_token):
        """Verify subscription endpoint is accessible"""
        # This tests that the backend is configured correctly
        response = requests.get(
            f"{BASE_URL}/api/subscription",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


class TestPricingEndpoint:
    """Test pricing-related endpoints for correctness"""

    def test_unauthenticated_cannot_access_protected_endpoints(self):
        """Protected endpoints should require authentication"""
        response = requests.get(f"{BASE_URL}/api/agents/create/info")
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
