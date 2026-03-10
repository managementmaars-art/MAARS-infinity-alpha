"""
Test suite for MAARS Global Corporation Admin Panel endpoints.
Tests admin authentication, admin-only access, platform stats, user management,
agent management, and transaction visibility.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-coordination.preview.emergentagent.com')

# Admin credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"

# Regular user credentials
REGULAR_EMAIL = "admin@test.com"
REGULAR_PASSWORD = "Admin1234!"


class TestAdminAuthentication:
    """Test admin login and is_admin flag in responses"""

    def test_admin_login_returns_is_admin_true(self):
        """Admin user login should return is_admin=true"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify token returned
        assert "token" in data
        assert len(data["token"]) > 0
        
        # Verify is_admin=true
        assert "user" in data
        assert data["user"]["is_admin"] is True
        assert data["user"]["email"] == ADMIN_EMAIL

    def test_regular_user_login_returns_is_admin_false(self):
        """Regular user login should return is_admin=false"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": REGULAR_EMAIL, "password": REGULAR_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify is_admin=false
        assert "user" in data
        assert data["user"]["is_admin"] is False

    def test_auth_me_returns_is_admin_for_admin_user(self):
        """GET /api/auth/me should return is_admin=true for admin user"""
        # Login to get token
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = login_resp.json()["token"]
        
        # Call /auth/me
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_admin"] is True
        assert data["email"] == ADMIN_EMAIL

    def test_auth_me_returns_is_admin_false_for_regular_user(self):
        """GET /api/auth/me should return is_admin=false for regular user"""
        # Login to get token
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": REGULAR_EMAIL, "password": REGULAR_PASSWORD}
        )
        token = login_resp.json()["token"]
        
        # Call /auth/me
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_admin"] is False


class TestAdminEndpointAccess:
    """Test that admin endpoints return 403 for non-admin users"""

    @pytest.fixture
    def admin_token(self):
        """Get admin user token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]

    @pytest.fixture
    def regular_token(self):
        """Get regular user token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": REGULAR_EMAIL, "password": REGULAR_PASSWORD}
        )
        return response.json()["token"]

    def test_admin_stats_returns_403_for_non_admin(self, regular_token):
        """/api/admin/stats should return 403 for non-admin users"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {regular_token}"}
        )
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_admin_users_returns_403_for_non_admin(self, regular_token):
        """/api/admin/users should return 403 for non-admin users"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {regular_token}"}
        )
        assert response.status_code == 403

    def test_admin_agents_returns_403_for_non_admin(self, regular_token):
        """/api/admin/agents should return 403 for non-admin users"""
        response = requests.get(
            f"{BASE_URL}/api/admin/agents",
            headers={"Authorization": f"Bearer {regular_token}"}
        )
        assert response.status_code == 403

    def test_admin_transactions_returns_403_for_non_admin(self, regular_token):
        """/api/admin/transactions should return 403 for non-admin users"""
        response = requests.get(
            f"{BASE_URL}/api/admin/transactions",
            headers={"Authorization": f"Bearer {regular_token}"}
        )
        assert response.status_code == 403

    def test_admin_stats_returns_401_without_auth(self):
        """/api/admin/stats should return 401 without authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 401


class TestAdminStats:
    """Test /api/admin/stats endpoint returns correct platform statistics"""

    @pytest.fixture
    def admin_token(self):
        """Get admin user token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]

    def test_admin_stats_returns_all_fields(self, admin_token):
        """Admin stats should return all required platform statistics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected fields exist
        assert "total_users" in data
        assert "total_chats" in data
        assert "total_messages" in data
        assert "total_revenue" in data
        assert "total_agents" in data
        assert "custom_agents" in data
        assert "active_subscriptions" in data
        assert "plan_distribution" in data
        assert "total_transactions" in data
        assert "total_credits_used" in data
        assert "total_credits_remaining" in data
        
        # Verify data types
        assert isinstance(data["total_users"], int)
        assert isinstance(data["total_agents"], int)
        assert isinstance(data["total_revenue"], (int, float))
        assert data["total_agents"] >= 20  # Should have at least 20 default agents


class TestAdminUsers:
    """Test /api/admin/users endpoint returns all users"""

    @pytest.fixture
    def admin_token(self):
        """Get admin user token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]

    def test_admin_users_returns_all_users(self, admin_token):
        """Admin users endpoint should return list of all users with subscription info"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1  # At least admin user exists
        
        # Check each user has required fields
        for user in data:
            assert "user_id" in user
            assert "email" in user
            assert "name" in user
            assert "subscription" in user
            assert "is_admin" in user

    def test_admin_user_has_is_admin_true(self, admin_token):
        """Admin user should be marked with is_admin=true in users list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        admin_users = [u for u in data if u["email"] == ADMIN_EMAIL]
        assert len(admin_users) == 1
        assert admin_users[0]["is_admin"] is True


class TestAdminAgents:
    """Test /api/admin/agents CRUD operations"""

    @pytest.fixture
    def admin_token(self):
        """Get admin user token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]

    def test_admin_agents_returns_all_agents(self, admin_token):
        """Admin agents endpoint should return all 20+ agents"""
        response = requests.get(
            f"{BASE_URL}/api/admin/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 20  # At least 20 default agents
        
        # Check agent structure
        for agent in data:
            assert "agent_id" in agent
            assert "name" in agent
            assert "role" in agent
            assert "model_provider" in agent

    def test_admin_create_and_delete_agent(self, admin_token):
        """Admin should be able to create and delete agents"""
        # Create agent
        create_response = requests.post(
            f"{BASE_URL}/api/admin/agents",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            json={
                "name": "TEST_AdminCreatedAgent",
                "description": "Test agent created by admin during testing",
                "role": "Test Specialist",
                "system_prompt": "You are a test agent for automated testing.",
                "capabilities": ["Testing", "Automation"]
            }
        )
        assert create_response.status_code == 200
        created_agent = create_response.json()
        
        assert created_agent["name"] == "TEST_AdminCreatedAgent"
        assert created_agent["role"] == "Test Specialist"
        assert created_agent["is_custom"] is False  # Admin created agents are NOT custom
        assert created_agent["creator_id"] is None  # No creator_id for admin agents
        
        agent_id = created_agent["agent_id"]
        
        # Delete agent
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/agents/{agent_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Agent deleted"
        
        # Verify agent is deleted
        agents_response = requests.get(
            f"{BASE_URL}/api/admin/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        agents = agents_response.json()
        agent_ids = [a["agent_id"] for a in agents]
        assert agent_id not in agent_ids


class TestAdminTransactions:
    """Test /api/admin/transactions endpoint"""

    @pytest.fixture
    def admin_token(self):
        """Get admin user token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]

    def test_admin_transactions_returns_list(self, admin_token):
        """Admin transactions endpoint should return list (may be empty)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/transactions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Transactions may be empty, which is valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
