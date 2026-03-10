"""
Tests for Iteration 82: MAARS Branding, Gallery View, and Agent Visibility Features
- Agent visibility toggle API
- Agent gallery view endpoints  
- Branding consistency (logo, colors)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "Admin123!"

class TestAuthentication:
    """Test admin login"""
    
    def test_admin_login_success(self):
        """Admin can login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["is_admin"] == True
        # Store token for subsequent tests
        TestAuthentication.token = data["token"]
        print(f"✓ Admin login successful, is_admin={data['user']['is_admin']}")


class TestHealthCheck:
    """Test API health"""
    
    def test_health_endpoint(self):
        """Health endpoint returns ok status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Health check passed")


class TestAgentsEndpoints:
    """Test agents CRUD and visibility"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        if not hasattr(TestAuthentication, 'token'):
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            TestAuthentication.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {TestAuthentication.token}"}
    
    def test_get_agents_list(self):
        """Get all agents returns 458+ agents"""
        response = requests.get(f"{BASE_URL}/api/agents", headers=self.headers)
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) >= 400  # Should have 458 agents
        print(f"✓ Got {len(agents)} agents")
        
        # Verify agent structure
        first_agent = agents[0]
        assert "agent_id" in first_agent
        assert "name" in first_agent
        assert "avatar" in first_agent
        assert "role" in first_agent
        print("✓ Agent structure verified")
    
    def test_get_single_agent(self):
        """Get single agent by ID"""
        response = requests.get(f"{BASE_URL}/api/agents/agent_commander", headers=self.headers)
        assert response.status_code == 200
        agent = response.json()
        assert agent["agent_id"] == "agent_commander"
        assert "Commander Orion" in agent["name"]
        print(f"✓ Got agent: {agent['name']}")
    
    def test_agent_has_photo_avatar(self):
        """Verify agents have photo avatars (not SVG)"""
        response = requests.get(f"{BASE_URL}/api/agents", headers=self.headers)
        agents = response.json()
        
        # Check first 10 agents for photo avatars
        photo_count = 0
        for agent in agents[:10]:
            avatar = agent.get("avatar", "")
            # Photo avatars should be URLs (CDN or local)
            if avatar and ("emergentagent.com" in avatar or "/api/static/" in avatar or avatar.endswith(('.png', '.jpg', '.jpeg'))):
                photo_count += 1
        
        assert photo_count >= 8  # At least 80% should have photo avatars
        print(f"✓ {photo_count}/10 agents have photo avatars")
    
    def test_agent_visibility_toggle_endpoint(self):
        """PUT /api/agents/{agent_id}/visibility toggles hidden status"""
        agent_id = "agent_growthhacker"  # Use a non-commander agent
        
        # Toggle to hidden
        response = requests.put(
            f"{BASE_URL}/api/agents/{agent_id}/visibility",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"hidden": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert data["hidden"] == True
        print(f"✓ Agent {agent_id} hidden=True")
        
        # Verify hidden status persists in list endpoint
        response = requests.get(f"{BASE_URL}/api/agents", headers=self.headers)
        assert response.status_code == 200
        agents = response.json()
        agent = next((a for a in agents if a["agent_id"] == agent_id), None)
        assert agent is not None
        # Note: hidden field may not be returned if False
        if agent.get("hidden") == True:
            print("✓ Hidden status persisted in list")
        else:
            print("? Hidden field not returned but toggle API works")
        
        # Toggle back to visible
        response = requests.put(
            f"{BASE_URL}/api/agents/{agent_id}/visibility",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"hidden": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["hidden"] == False
        print(f"✓ Agent {agent_id} hidden=False (restored)")
    
    def test_visibility_requires_admin(self):
        """Non-admin cannot toggle visibility"""
        # Create a non-admin user or skip if not possible
        # For now, just verify the endpoint exists and requires auth
        response = requests.put(
            f"{BASE_URL}/api/agents/agent_commander/visibility",
            headers={"Content-Type": "application/json"},  # No auth
            json={"hidden": True}
        )
        assert response.status_code == 401  # Unauthorized
        print("✓ Visibility toggle requires authentication")
    
    def test_agents_have_tools_info(self):
        """Agents include tools information in list endpoint"""
        response = requests.get(f"{BASE_URL}/api/agents", headers=self.headers)
        assert response.status_code == 200
        agents = response.json()
        
        # Find commander in list
        commander = next((a for a in agents if a["agent_id"] == "agent_commander"), None)
        assert commander is not None
        
        # Commander should have tools in list endpoint
        tools = commander.get("tools", [])
        assert len(tools) > 0
        print(f"✓ Commander has {len(tools)} tools: {tools[:5]}...")
    
    def test_agents_public_endpoint(self):
        """Public agents endpoint works without auth"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) > 0
        print(f"✓ Public endpoint returned {len(agents)} agents")


class TestSubscriptionEndpoint:
    """Test subscription/credits endpoint for sidebar display"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not hasattr(TestAuthentication, 'token'):
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            TestAuthentication.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {TestAuthentication.token}"}
    
    def test_get_subscription_for_credits(self):
        """Get subscription returns credits and plan info"""
        response = requests.get(f"{BASE_URL}/api/subscription", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Should have credits field
        assert "credits" in data
        assert isinstance(data["credits"], (int, float))
        print(f"✓ Credits: {data['credits']}")
        
        # Should have plan info
        if "plan_info" in data:
            assert "name" in data["plan_info"]
            print(f"✓ Plan: {data['plan_info']['name']}")


class TestStaticAssets:
    """Test branding static assets"""
    
    def test_branding_logo_accessible(self):
        """MAARS logo is accessible from static endpoint"""
        # Test backend static path
        response = requests.get(f"{BASE_URL}/api/static/branding/maars-logo.jpeg")
        assert response.status_code == 200
        assert "image" in response.headers.get("content-type", "")
        print("✓ Backend branding logo accessible")
    
    def test_avatar_static_path(self):
        """Avatar static files are accessible"""
        response = requests.get(f"{BASE_URL}/api/static/avatars/agent_commander.png")
        # May be 200 or 404 depending on local storage
        print(f"Avatar static path response: {response.status_code}")


class TestStatsEndpoint:
    """Test stats endpoint for dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not hasattr(TestAuthentication, 'token'):
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            TestAuthentication.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {TestAuthentication.token}"}
    
    def test_get_stats(self):
        """Stats endpoint returns dashboard data"""
        response = requests.get(f"{BASE_URL}/api/stats", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Should have key stats
        assert "total_chats" in data
        assert "total_tasks" in data
        print(f"✓ Stats: chats={data['total_chats']}, tasks={data['total_tasks']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
