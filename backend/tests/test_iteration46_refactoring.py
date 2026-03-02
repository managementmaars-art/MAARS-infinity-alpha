"""
Iteration 46: Backend Refactoring Regression Tests
Tests all routes after backend server.py split from 6039 to ~90 lines.
Routes now in /app/backend/routes/ directory.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsGlobal2024!"
TEST_USER_EMAIL = "test@test.com"
TEST_USER_PASSWORD = "test123"


class TestHealthAndPublicEndpoints:
    """Test health and public endpoints (no auth required)"""

    def test_health_check(self):
        """Health endpoint should return OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data["status"] == "ok"
        assert "MAARS" in data.get("service", "")
        print("✓ Health check passed")

    def test_public_agents(self):
        """Public agents endpoint returns list of agents"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200, f"Public agents failed: {response.text}"
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) > 0, "No public agents returned"
        # Verify Commander is first
        commander = next((a for a in agents if a.get("agent_id") == "agent_commander"), None)
        assert commander is not None, "Commander agent not found in public agents"
        print(f"✓ Public agents returned {len(agents)} agents")

    def test_plans_endpoint(self):
        """Plans endpoint returns subscription plans"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200, f"Plans endpoint failed: {response.text}"
        data = response.json()
        assert "plans" in data
        plans = data["plans"]
        assert "free" in plans
        assert "starter" in plans
        assert "pro" in plans
        assert "business" in plans
        print("✓ Plans endpoint returned all plans")

    def test_exchange_rate(self):
        """Exchange rate endpoint returns USD/BDT rate"""
        response = requests.get(f"{BASE_URL}/api/exchange-rate")
        assert response.status_code == 200, f"Exchange rate failed: {response.text}"
        data = response.json()
        assert "usd_bdt" in data
        assert data["usd_bdt"] > 0, "Invalid exchange rate"
        print(f"✓ Exchange rate: {data['usd_bdt']} BDT per USD")


class TestAuthRoutes:
    """Test authentication routes"""

    def test_register_existing_user(self):
        """Registration with existing email should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": ADMIN_EMAIL,
            "name": "Test",
            "password": "testpass123"
        })
        # Should fail since admin email exists
        assert response.status_code == 400, "Should reject duplicate email"
        print("✓ Duplicate registration rejected correctly")

    def test_login_admin(self):
        """Admin login should succeed"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["is_admin"] == True
        print("✓ Admin login successful")

    def test_login_invalid_credentials(self):
        """Invalid credentials should return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, "Should reject invalid credentials"
        print("✓ Invalid credentials rejected correctly")

    def test_auth_me_without_token(self):
        """Auth me endpoint without token should fail"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code in [401, 403], "Should require authentication"
        print("✓ Auth me requires token")


@pytest.fixture(scope="class")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.text}")
    return response.json()["token"]


class TestAuthenticatedEndpoints:
    """Test endpoints requiring authentication"""

    def test_auth_me(self, admin_token):
        """Auth me should return user info"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        assert data["is_admin"] == True
        print("✓ Auth me returned correct user info")

    def test_get_chats(self, admin_token):
        """Get chats should return user's chats"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/chats", headers=headers)
        assert response.status_code == 200, f"Get chats failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get chats returned {len(data)} chats")

    def test_get_tasks(self, admin_token):
        """Get tasks should return user's tasks"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
        assert response.status_code == 200, f"Get tasks failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get tasks returned {len(data)} tasks")

    def test_get_notifications(self, admin_token):
        """Get notifications should return user's notifications"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200, f"Get notifications failed: {response.text}"
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        print(f"✓ Get notifications returned {len(data['notifications'])} notifications")

    def test_get_subscription(self, admin_token):
        """Get subscription should return user's subscription"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/subscription", headers=headers)
        assert response.status_code == 200, f"Get subscription failed: {response.text}"
        data = response.json()
        assert "plan_id" in data
        assert "credits" in data
        print(f"✓ Get subscription: plan={data['plan_id']}, credits={data['credits']}")

    def test_get_agents(self, admin_token):
        """Get agents should return all agents for user"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert response.status_code == 200, f"Get agents failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"✓ Get agents returned {len(data)} agents")

    def test_get_products(self, admin_token):
        """Get products should return user's product catalog"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/products", headers=headers)
        assert response.status_code == 200, f"Get products failed: {response.text}"
        data = response.json()
        assert "products" in data
        print(f"✓ Get products returned {len(data['products'])} products")

    def test_get_teams(self, admin_token):
        """Get teams should return user's teams"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/teams", headers=headers)
        assert response.status_code == 200, f"Get teams failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get teams returned {len(data)} teams")


class TestAdminEndpoints:
    """Test admin-only endpoints"""

    def test_admin_stats(self, admin_token):
        """Admin stats should return platform statistics"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        data = response.json()
        assert "total_users" in data
        assert "total_chats" in data
        assert "total_agents" in data
        print(f"✓ Admin stats: users={data['total_users']}, chats={data['total_chats']}, agents={data['total_agents']}")

    def test_admin_pricing(self, admin_token):
        """Admin pricing should return pricing configuration"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/pricing", headers=headers)
        assert response.status_code == 200, f"Admin pricing failed: {response.text}"
        data = response.json()
        assert "plans" in data or "config_type" in data
        print("✓ Admin pricing configuration returned")

    def test_admin_users(self, admin_token):
        """Admin users should return all users"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        assert response.status_code == 200, f"Admin users failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin users returned {len(data)} users")

    def test_admin_agents(self, admin_token):
        """Admin agents should return all agents including custom"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=headers)
        assert response.status_code == 200, f"Admin agents failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin agents returned {len(data)} agents")

    def test_admin_transactions(self, admin_token):
        """Admin transactions should return payment history"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/transactions", headers=headers)
        assert response.status_code == 200, f"Admin transactions failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin transactions returned {len(data)} transactions")

    def test_admin_integrations(self, admin_token):
        """Admin integrations should return integration configs"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/integrations", headers=headers)
        assert response.status_code == 200, f"Admin integrations failed: {response.text}"
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Admin integrations returned {len(data)} services")

    def test_admin_api_keys(self, admin_token):
        """Admin API keys should return key configuration"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        assert response.status_code == 200, f"Admin API keys failed: {response.text}"
        data = response.json()
        assert "active_provider" in data
        print(f"✓ Admin API keys: active_provider={data['active_provider']}")

    def test_admin_profit(self, admin_token):
        """Admin profit should return revenue analytics"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/profit", headers=headers)
        assert response.status_code == 200, f"Admin profit failed: {response.text}"
        data = response.json()
        assert "revenue" in data
        assert "net_profit" in data
        print(f"✓ Admin profit: revenue=${data['revenue']}, net_profit=${data['net_profit']}")

    def test_admin_analytics(self, admin_token):
        """Admin analytics should return dashboard data"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        assert response.status_code == 200, f"Admin analytics failed: {response.text}"
        data = response.json()
        assert "kpis" in data
        print(f"✓ Admin analytics: total_users={data['kpis'].get('total_users')}")

    def test_admin_products(self, admin_token):
        """Admin products should return all users' products"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/products", headers=headers)
        assert response.status_code == 200, f"Admin products failed: {response.text}"
        data = response.json()
        assert "products" in data
        print(f"✓ Admin products returned {len(data['products'])} products")


class TestChatAndMessageRoutes:
    """Test chat CRUD and messaging routes"""

    def test_create_chat(self, admin_token):
        """Should be able to create a new chat"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Get first agent
        agents_response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        agents = agents_response.json()
        agent_id = agents[0]["agent_id"] if agents else "agent_commander"

        response = requests.post(f"{BASE_URL}/api/chats", headers=headers, json={
            "agent_id": agent_id,
            "title": "TEST_Refactoring Test Chat"
        })
        assert response.status_code == 200, f"Create chat failed: {response.text}"
        data = response.json()
        assert "chat_id" in data
        assert data["agent_id"] == agent_id
        print(f"✓ Created chat: {data['chat_id']}")
        return data["chat_id"]

    def test_get_chat(self, admin_token):
        """Should be able to get a specific chat"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # First create a chat
        agents_response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        agents = agents_response.json()
        agent_id = agents[0]["agent_id"] if agents else "agent_commander"

        create_response = requests.post(f"{BASE_URL}/api/chats", headers=headers, json={
            "agent_id": agent_id,
            "title": "TEST_Get Chat Test"
        })
        chat_id = create_response.json()["chat_id"]

        # Now get it
        response = requests.get(f"{BASE_URL}/api/chats/{chat_id}", headers=headers)
        assert response.status_code == 200, f"Get chat failed: {response.text}"
        data = response.json()
        assert data["chat_id"] == chat_id
        print(f"✓ Got chat: {chat_id}")


class TestAgentTools:
    """Test agent tools endpoint"""

    def test_get_available_tools(self):
        """Should return available tools"""
        response = requests.get(f"{BASE_URL}/api/agents/tools")
        assert response.status_code == 200, f"Get tools failed: {response.text}"
        data = response.json()
        assert "tools" in data
        assert "agent_tools" in data
        # Verify product_scan tool exists
        assert "product_scan" in data["tools"], "product_scan tool missing"
        print(f"✓ Available tools: {list(data['tools'].keys())}")


class TestCustomPackageEndpoints:
    """Test custom package configuration"""

    def test_get_custom_package_config(self):
        """Should return custom package pricing config"""
        response = requests.get(f"{BASE_URL}/api/custom-package/config")
        assert response.status_code == 200, f"Custom package config failed: {response.text}"
        data = response.json()
        # Check for expected fields
        assert "per_agent_price_usd" in data or "credit_presets" in data
        print("✓ Custom package config returned")

    def test_admin_custom_package(self, admin_token):
        """Admin should be able to get custom package config"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/custom-package", headers=headers)
        assert response.status_code == 200, f"Admin custom package failed: {response.text}"
        print("✓ Admin custom package config returned")


class TestRouteModularity:
    """Verify all route modules are properly connected"""

    def test_auth_routes_connected(self):
        """Auth routes module should be connected"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@test.com",
            "password": "wrong"
        })
        # Should return 401, not 404
        assert response.status_code != 404, "Auth routes not connected"
        print("✓ Auth routes connected")

    def test_agents_routes_connected(self):
        """Agents routes module should be connected"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200, "Agents routes not connected"
        print("✓ Agents routes connected")

    def test_subscriptions_routes_connected(self):
        """Subscriptions routes module should be connected"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200, "Subscriptions routes not connected"
        print("✓ Subscriptions routes connected")

    def test_admin_routes_connected(self, admin_token):
        """Admin routes module should be connected"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200, "Admin routes not connected"
        print("✓ Admin routes connected")

    def test_chats_routes_connected(self, admin_token):
        """Chats routes module should be connected"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/chats", headers=headers)
        assert response.status_code == 200, "Chats routes not connected"
        print("✓ Chats routes connected")

    def test_tasks_routes_connected(self, admin_token):
        """Tasks routes module should be connected"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
        assert response.status_code == 200, "Tasks routes not connected"
        print("✓ Tasks routes connected")

    def test_teams_routes_connected(self, admin_token):
        """Teams routes module should be connected"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/teams", headers=headers)
        assert response.status_code == 200, "Teams routes not connected"
        print("✓ Teams routes connected")

    def test_notifications_routes_connected(self, admin_token):
        """Notifications routes module should be connected"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200, "Notifications routes not connected"
        print("✓ Notifications routes connected")

    def test_products_routes_connected(self, admin_token):
        """Products routes module should be connected"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/products", headers=headers)
        assert response.status_code == 200, "Products routes not connected"
        print("✓ Products routes connected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
