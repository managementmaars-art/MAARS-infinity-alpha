"""
Test User Agent Customization (Per-User Overrides) + Admin Brain Editor + Branding Tab
Iteration 34

Tests:
- GET /api/agents/{agent_id}/my-settings - User's override settings
- PUT /api/agents/{agent_id}/my-settings - Save user's override (temperature, max_tokens, personality_tone, custom_instructions)
- DELETE /api/agents/{agent_id}/my-settings - Reset to defaults
- PUT /api/admin/agents/{agent_id}/brain - Admin brain editor
- PUT /api/admin/agents/{agent_id}/settings - Admin agent toggle
- GET /api/branding/public - Public branding (no auth)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestAuthSetup:
    """Authentication setup - run first"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        assert res.status_code == 200, f"Admin login failed: {res.text}"
        data = res.json()
        assert "token" in data, "No token in response"
        return data["token"]
    
    def test_admin_login(self, admin_token):
        """Verify admin can login"""
        assert admin_token is not None
        assert len(admin_token) > 10
        print(f"Admin login successful, token length: {len(admin_token)}")


@pytest.fixture(scope="module")
def admin_session():
    """Admin authenticated session for all tests"""
    session = requests.Session()
    res = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
    })
    if res.status_code == 200:
        token = res.json().get("token")
        session.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        return session
    pytest.skip("Admin login failed")


@pytest.fixture(scope="module")
def test_agent_id(admin_session):
    """Get a test agent ID (first non-commander agent)"""
    res = admin_session.get(f"{BASE_URL}/api/agents")
    if res.status_code == 200:
        agents = res.json()
        for agent in agents:
            if not agent.get("is_commander") and agent.get("agent_id", "").startswith("agent_"):
                return agent["agent_id"]
    # Fallback to a known agent
    return "agent_graphics"


class TestUserAgentCustomization:
    """User Agent Customization Endpoints (Per-User Overrides)"""
    
    def test_get_my_settings_no_override(self, admin_session, test_agent_id):
        """GET /api/agents/{id}/my-settings returns has_override: false when no override exists"""
        # First delete any existing override
        admin_session.delete(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings")
        
        res = admin_session.get(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings")
        assert res.status_code == 200, f"Failed to get my-settings: {res.text}"
        
        data = res.json()
        assert "agent_id" in data, "Missing agent_id in response"
        assert data["agent_id"] == test_agent_id
        assert data.get("has_override") == False, f"Expected has_override=false, got: {data}"
        print(f"GET my-settings (no override): {data}")
    
    def test_put_my_settings_temperature_and_max_tokens(self, admin_session, test_agent_id):
        """PUT /api/agents/{id}/my-settings saves temperature and max_tokens with validation"""
        payload = {
            "temperature": 1.5,
            "max_tokens": 8192
        }
        res = admin_session.put(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings", json=payload)
        assert res.status_code == 200, f"Failed to save settings: {res.text}"
        
        data = res.json()
        assert data.get("has_override") == True, "Expected has_override=true"
        assert data.get("temperature") == 1.5, f"Temperature not saved: {data}"
        assert data.get("max_tokens") == 8192, f"Max tokens not saved: {data}"
        print(f"PUT my-settings (temperature/max_tokens): {data}")
    
    def test_put_my_settings_personality_and_instructions(self, admin_session, test_agent_id):
        """PUT /api/agents/{id}/my-settings saves personality_tone and custom_instructions"""
        payload = {
            "personality_tone": "Be more casual and use humor",
            "custom_instructions": "Always respond in bullet points. Keep responses brief."
        }
        res = admin_session.put(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings", json=payload)
        assert res.status_code == 200, f"Failed to save settings: {res.text}"
        
        data = res.json()
        assert data.get("has_override") == True
        assert data.get("personality_tone") == payload["personality_tone"]
        assert data.get("custom_instructions") == payload["custom_instructions"]
        print(f"PUT my-settings (personality/instructions): personality_tone={data.get('personality_tone')[:30]}...")
    
    def test_put_my_settings_temperature_validation_min(self, admin_session, test_agent_id):
        """PUT /api/agents/{id}/my-settings validates temperature minimum (0)"""
        payload = {"temperature": -5.0}  # Should be clamped to 0
        res = admin_session.put(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings", json=payload)
        assert res.status_code == 200
        
        data = res.json()
        assert data.get("temperature") == 0.0, f"Temperature should be clamped to 0, got: {data.get('temperature')}"
        print(f"Temperature validation (min): {data.get('temperature')}")
    
    def test_put_my_settings_temperature_validation_max(self, admin_session, test_agent_id):
        """PUT /api/agents/{id}/my-settings validates temperature maximum (2)"""
        payload = {"temperature": 10.0}  # Should be clamped to 2
        res = admin_session.put(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings", json=payload)
        assert res.status_code == 200
        
        data = res.json()
        assert data.get("temperature") == 2.0, f"Temperature should be clamped to 2, got: {data.get('temperature')}"
        print(f"Temperature validation (max): {data.get('temperature')}")
    
    def test_put_my_settings_max_tokens_validation(self, admin_session, test_agent_id):
        """PUT /api/agents/{id}/my-settings validates max_tokens (256-16384)"""
        # Test min
        res = admin_session.put(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings", json={"max_tokens": 100})
        assert res.status_code == 200
        data = res.json()
        assert data.get("max_tokens") == 256, f"Max tokens should be clamped to 256, got: {data.get('max_tokens')}"
        
        # Test max
        res = admin_session.put(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings", json={"max_tokens": 50000})
        assert res.status_code == 200
        data = res.json()
        assert data.get("max_tokens") == 16384, f"Max tokens should be clamped to 16384, got: {data.get('max_tokens')}"
        print(f"Max tokens validation: min=256, max=16384")
    
    def test_get_my_settings_with_override(self, admin_session, test_agent_id):
        """GET /api/agents/{id}/my-settings returns saved override"""
        # First save some settings
        payload = {
            "temperature": 0.9,
            "max_tokens": 4096,
            "personality_tone": "Test personality",
            "custom_instructions": "Test instructions"
        }
        admin_session.put(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings", json=payload)
        
        # Now GET
        res = admin_session.get(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings")
        assert res.status_code == 200
        
        data = res.json()
        assert data.get("has_override") == True
        assert data.get("temperature") == 0.9
        assert data.get("max_tokens") == 4096
        assert data.get("personality_tone") == "Test personality"
        assert data.get("custom_instructions") == "Test instructions"
        print(f"GET my-settings (with override): has_override={data.get('has_override')}")
    
    def test_delete_my_settings(self, admin_session, test_agent_id):
        """DELETE /api/agents/{id}/my-settings resets to defaults"""
        res = admin_session.delete(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings")
        assert res.status_code == 200, f"Failed to delete settings: {res.text}"
        
        data = res.json()
        assert data.get("success") == True
        assert data.get("agent_id") == test_agent_id
        print(f"DELETE my-settings: {data}")
        
        # Verify it's reset
        res = admin_session.get(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings")
        data = res.json()
        assert data.get("has_override") == False, "Override should be cleared after delete"
    
    def test_put_my_settings_empty_payload_error(self, admin_session, test_agent_id):
        """PUT /api/agents/{id}/my-settings with no valid fields returns 400"""
        res = admin_session.put(f"{BASE_URL}/api/agents/{test_agent_id}/my-settings", json={"invalid_field": "value"})
        assert res.status_code == 400, f"Expected 400 for invalid payload, got: {res.status_code}"
        print("Empty/invalid payload returns 400: PASSED")


class TestAdminBrainEditor:
    """Admin Brain Editor Endpoints"""
    
    def test_admin_get_agent_detail(self, admin_session, test_agent_id):
        """GET /api/admin/agents/{id} returns full agent details"""
        res = admin_session.get(f"{BASE_URL}/api/admin/agents/{test_agent_id}")
        assert res.status_code == 200, f"Failed to get agent detail: {res.text}"
        
        data = res.json()
        assert data.get("agent_id") == test_agent_id
        assert "name" in data
        assert "role" in data
        print(f"GET admin agent detail: {data.get('name')} - {data.get('role')}")
    
    def test_admin_update_brain_name_and_role(self, admin_session, test_agent_id):
        """PUT /api/admin/agents/{id}/brain saves name and role"""
        # Get original values first
        original = admin_session.get(f"{BASE_URL}/api/admin/agents/{test_agent_id}").json()
        
        # Update
        payload = {
            "name": f"TEST_{original.get('name', 'Agent')}",
            "role": f"TEST_{original.get('role', 'Specialist')}"
        }
        res = admin_session.put(f"{BASE_URL}/api/admin/agents/{test_agent_id}/brain", json=payload)
        assert res.status_code == 200, f"Failed to update brain: {res.text}"
        
        data = res.json()
        assert data.get("success") == True
        assert data["agent"]["name"] == payload["name"]
        assert data["agent"]["role"] == payload["role"]
        print(f"PUT admin brain (name/role): {data['agent']['name']} - {data['agent']['role']}")
        
        # Restore original
        admin_session.put(f"{BASE_URL}/api/admin/agents/{test_agent_id}/brain", json={
            "name": original.get("name"),
            "role": original.get("role")
        })
    
    def test_admin_update_brain_personality_tone(self, admin_session, test_agent_id):
        """PUT /api/admin/agents/{id}/brain saves personality_tone and rebuilds system prompt"""
        payload = {
            "personality_tone": "Professional yet friendly, uses clear and concise language"
        }
        res = admin_session.put(f"{BASE_URL}/api/admin/agents/{test_agent_id}/brain", json=payload)
        assert res.status_code == 200, f"Failed to update brain: {res.text}"
        
        data = res.json()
        assert data.get("success") == True
        # Check that personality_tone was saved
        agent = data.get("agent", {})
        assert agent.get("personality_tone") == payload["personality_tone"] or "BRAIN CONFIG" in agent.get("system_prompt", "")
        print(f"PUT admin brain (personality_tone): Updated and saved")
    
    def test_admin_update_brain_model_settings(self, admin_session, test_agent_id):
        """PUT /api/admin/agents/{id}/brain saves model_provider, temperature, max_tokens"""
        original = admin_session.get(f"{BASE_URL}/api/admin/agents/{test_agent_id}").json()
        
        payload = {
            "model_provider": "openai",
            "temperature": 0.8,
            "max_tokens": 2048
        }
        res = admin_session.put(f"{BASE_URL}/api/admin/agents/{test_agent_id}/brain", json=payload)
        assert res.status_code == 200, f"Failed to update brain: {res.text}"
        
        data = res.json()
        assert data.get("success") == True
        agent = data.get("agent", {})
        assert agent.get("model_provider") == "openai"
        assert agent.get("temperature") == 0.8
        assert agent.get("max_tokens") == 2048
        print(f"PUT admin brain (model settings): provider={agent.get('model_provider')}, temp={agent.get('temperature')}, max_tokens={agent.get('max_tokens')}")
        
        # Restore
        admin_session.put(f"{BASE_URL}/api/admin/agents/{test_agent_id}/brain", json={
            "model_provider": original.get("model_provider"),
            "temperature": original.get("temperature"),
            "max_tokens": original.get("max_tokens")
        })


class TestAdminAgentToggle:
    """Admin Agent Settings Toggle"""
    
    def test_admin_update_agent_settings_toggle(self, admin_session, test_agent_id):
        """PUT /api/admin/agents/{id}/settings toggles is_active and capability flags"""
        original = admin_session.get(f"{BASE_URL}/api/admin/agents/{test_agent_id}").json()
        
        # Toggle can_generate_image
        original_can_generate = original.get("can_generate_image", False)
        payload = {
            "can_generate_image": not original_can_generate
        }
        res = admin_session.put(f"{BASE_URL}/api/admin/agents/{test_agent_id}/settings", json=payload)
        assert res.status_code == 200, f"Failed to update settings: {res.text}"
        
        data = res.json()
        assert data.get("success") == True
        assert "can_generate_image" in data.get("updated", [])
        print(f"PUT admin settings (toggle): can_generate_image toggled")
        
        # Restore
        admin_session.put(f"{BASE_URL}/api/admin/agents/{test_agent_id}/settings", json={
            "can_generate_image": original_can_generate
        })
    
    def test_admin_update_agent_is_active(self, admin_session, test_agent_id):
        """PUT /api/admin/agents/{id}/settings toggles is_active"""
        payload = {"is_active": True}
        res = admin_session.put(f"{BASE_URL}/api/admin/agents/{test_agent_id}/settings", json=payload)
        assert res.status_code == 200
        
        data = res.json()
        assert data.get("success") == True
        print(f"PUT admin settings (is_active): {data}")


class TestPublicBranding:
    """Public Branding Endpoint (No Auth Required)"""
    
    def test_public_branding_no_auth_required(self):
        """GET /api/branding/public returns 200 without authentication"""
        res = requests.get(f"{BASE_URL}/api/branding/public")
        assert res.status_code == 200, f"Public branding failed: {res.text}"
        print(f"GET /api/branding/public: 200 OK (no auth)")
    
    def test_public_branding_has_required_fields(self):
        """GET /api/branding/public returns required branding fields"""
        res = requests.get(f"{BASE_URL}/api/branding/public")
        assert res.status_code == 200
        
        data = res.json()
        required_fields = ["platform_name", "primary_color", "accent_color"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        print(f"Public branding fields: platform_name={data.get('platform_name')}, colors={data.get('primary_color')}/{data.get('accent_color')}")


class TestRegressionBasic:
    """Basic Regression Tests"""
    
    def test_health_endpoint(self):
        """Health endpoint returns 200"""
        res = requests.get(f"{BASE_URL}/health")
        assert res.status_code == 200
        print("Health check: OK")
    
    def test_agents_list(self, admin_session):
        """GET /api/agents returns agents list"""
        res = admin_session.get(f"{BASE_URL}/api/agents")
        assert res.status_code == 200
        agents = res.json()
        assert len(agents) > 0, "No agents returned"
        print(f"Agents list: {len(agents)} agents")
    
    def test_auth_me(self, admin_session):
        """GET /api/auth/me returns current user"""
        res = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert res.status_code == 200
        data = res.json()
        assert data.get("email") == ADMIN_EMAIL
        assert data.get("is_admin") == True
        print(f"Auth me: {data.get('email')} (is_admin={data.get('is_admin')})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
