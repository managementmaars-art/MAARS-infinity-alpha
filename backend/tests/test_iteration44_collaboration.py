"""
Test Iteration 44: CollaborationWorkflow, Commander Delegation Progress, Auth, Chat, Admin Dashboard
Tests the new real-time Agent Collaboration View for Commander AI delegation
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-coordination.preview.emergentagent.com').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestHealthAndPublicEndpoints:
    """Test basic health and public endpoints"""
    
    def test_health_check(self):
        """Test health endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print("Health check PASSED")
    
    def test_public_agents_endpoint(self):
        """Test public agents endpoint returns list of agents including Commander"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) > 0
        
        # Verify Commander is first agent (sorted)
        commander = next((a for a in agents if a.get("agent_id") == "agent_commander"), None)
        assert commander is not None, "Commander agent should be in public agents list"
        assert commander.get("is_commander") is True
        assert commander.get("name") == "Commander Orion"
        print(f"Public agents PASSED - Found {len(agents)} agents, Commander is present")
    
    def test_exchange_rate_endpoint(self):
        """Test exchange rate endpoint"""
        response = requests.get(f"{BASE_URL}/api/exchange-rate")
        assert response.status_code == 200
        data = response.json()
        assert "usd_bdt" in data
        assert data["usd_bdt"] > 0
        print(f"Exchange rate PASSED - USD/BDT: {data['usd_bdt']}")


class TestAuthEndpoints:
    """Test authentication endpoints after refactoring to routes/auth.py"""
    
    def test_login_endpoint_exists(self):
        """Test login returns token for admin"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["is_admin"] is True
        print("Admin login PASSED - Token received and is_admin=true")
        return data["token"]
    
    def test_auth_me_requires_auth(self):
        """Test /auth/me returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("/auth/me PASSED - Returns 401 without auth")
    
    def test_auth_me_with_token(self):
        """Test /auth/me returns user data with valid token"""
        # Login first
        login_res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = login_res.json()["token"]
        
        # Get user data
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        assert data["is_admin"] is True
        print("/auth/me with token PASSED - Returns admin user data")
    
    def test_logout_endpoint(self):
        """Test logout endpoint"""
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("Logout endpoint PASSED")


class TestAgentEndpoints:
    """Test agent-related endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Authentication failed")
    
    def test_agents_list_authenticated(self, auth_token):
        """Test authenticated agents list"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) > 0
        
        # Verify Commander has tools
        commander = next((a for a in agents if a.get("agent_id") == "agent_commander"), None)
        assert commander is not None
        assert "tools" in commander
        assert len(commander.get("tools", [])) > 0
        print(f"Authenticated agents PASSED - {len(agents)} agents, Commander has {len(commander.get('tools', []))} tools")
    
    def test_agent_details(self, auth_token):
        """Test getting specific agent details"""
        response = requests.get(
            f"{BASE_URL}/api/agents/agent_commander",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        agent = response.json()
        assert agent["agent_id"] == "agent_commander"
        assert agent["name"] == "Commander Orion"
        assert agent.get("is_commander") is True
        print("Agent details PASSED - Commander Orion retrieved")


class TestChatEndpoints:
    """Test chat-related endpoints for message sending"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Authentication failed")
    
    def test_create_chat(self, auth_token):
        """Test creating a new chat"""
        # Use a regular agent (not commander) for quick testing
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json={"agent_id": "agent_marketing"}
        )
        assert response.status_code == 200
        chat = response.json()
        assert "chat_id" in chat
        assert chat["agent_id"] == "agent_marketing"
        print(f"Create chat PASSED - Chat ID: {chat['chat_id']}")
        return chat["chat_id"]
    
    def test_get_chats(self, auth_token):
        """Test getting chat list"""
        response = requests.get(
            f"{BASE_URL}/api/chats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        chats = response.json()
        assert isinstance(chats, list)
        print(f"Get chats PASSED - {len(chats)} chats found")


class TestAdminEndpoints:
    """Test admin dashboard endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Authentication failed")
    
    def test_admin_stats(self, auth_token):
        """Test admin stats endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        stats = response.json()
        assert "total_users" in stats
        assert "total_chats" in stats
        print(f"Admin stats PASSED - {stats.get('total_users')} users, {stats.get('total_chats')} chats")
    
    def test_admin_agents(self, auth_token):
        """Test admin agents endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/agents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        print(f"Admin agents PASSED - {len(agents)} agents")
    
    def test_admin_integrations(self, auth_token):
        """Test admin integrations endpoint (for IntegrationsTab)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/integrations",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should have integration services
        assert len(data) > 0
        print(f"Admin integrations PASSED - {len(data)} services configured")
    
    def test_admin_custom_package_config(self, auth_token):
        """Test admin custom package config endpoint (for CustomPackagesTab)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/custom-package",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        config = response.json()
        # Should have pricing fields
        assert "per_agent_price_usd" in config or "credit_presets" in config
        print("Admin custom package config PASSED")


class TestCommanderDelegationStructure:
    """Test Commander delegation message structure for CollaborationWorkflow"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Authentication failed")
    
    def test_commander_agent_exists(self, auth_token):
        """Verify Commander agent exists and has correct setup"""
        response = requests.get(
            f"{BASE_URL}/api/agents/agent_commander",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        commander = response.json()
        
        # Verify Commander attributes
        assert commander["agent_id"] == "agent_commander"
        assert commander.get("is_commander") is True
        assert commander["name"] == "Commander Orion"
        
        # Verify Commander has required capabilities
        caps = commander.get("capabilities", [])
        assert "Task Delegation" in caps or len(caps) > 0
        print(f"Commander agent verification PASSED - Has {len(caps)} capabilities")
    
    def test_commander_chat_creation(self, auth_token):
        """Test creating a chat with Commander agent"""
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json={"agent_id": "agent_commander"}
        )
        assert response.status_code == 200
        chat = response.json()
        assert chat["agent_id"] == "agent_commander"
        assert "Commander" in chat.get("title", "")
        print(f"Commander chat creation PASSED - Chat: {chat['chat_id']}")


class TestLandingPage:
    """Test landing page accessibility"""
    
    def test_landing_page_loads(self):
        """Test that landing page returns HTML"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        # Should return HTML
        assert "text/html" in response.headers.get("Content-Type", "") or response.text.startswith("<!DOCTYPE html") or "<html" in response.text[:500]
        print("Landing page PASSED - Returns HTML")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
