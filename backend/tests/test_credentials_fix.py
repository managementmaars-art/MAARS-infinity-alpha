"""
Test suite for MAARS Command Admin API functionality
Tests the fix: credentials:'include' removal from frontend fetch calls

This test verifies that admin APIs work correctly with JWT auth headers only
(no cookie-based credentials needed).

Bug Fixed: User reported 'Failed to save' and 'Failed to update' errors when
toggling generation permissions and saving brain in the admin Agents tab.
Root cause: credentials:'include' in fetch calls caused CORS issues.
Fix: Removed credentials:'include' from ALL frontend fetch calls since JWT auth
via Authorization header doesn't need cookies.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


@pytest.fixture(scope="module")
def auth_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    pytest.skip(f"Authentication failed: {response.status_code}")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with JWT auth token - NO COOKIES needed"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestAdminLogin:
    """Test admin authentication"""
    
    def test_admin_login_success(self):
        """Admin can login with correct credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 0
        print(f"✅ Admin login successful, token received")


class TestAgentsTab:
    """Test Agents tab functionality - main bug area"""
    
    def test_fetch_agents_list(self, auth_headers):
        """GET /admin/agents returns list of agents"""
        response = requests.get(
            f"{BASE_URL}/api/admin/agents",
            headers=auth_headers
        )
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) == 21, f"Expected 21 agents, got {len(agents)}"
        print(f"✅ Found {len(agents)} agents")
    
    def test_toggle_image_generation(self, auth_headers):
        """PUT /admin/agents/{id}/settings - toggle can_generate_image"""
        # First get an agent
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        agent_id = agents[0]["agent_id"]
        current_state = agents[0].get("can_generate_image", False)
        
        # Toggle the setting
        toggle_response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_image": not current_state}
        )
        assert toggle_response.status_code == 200
        print(f"✅ Image generation toggle: {current_state} -> {not current_state}")
        
        # Toggle back to original
        requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_image": current_state}
        )
    
    def test_toggle_pdf_generation(self, auth_headers):
        """PUT /admin/agents/{id}/settings - toggle can_generate_pdf"""
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        agent_id = agents[0]["agent_id"]
        current_state = agents[0].get("can_generate_pdf", False)
        
        toggle_response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_pdf": not current_state}
        )
        assert toggle_response.status_code == 200
        print(f"✅ PDF generation toggle: {current_state} -> {not current_state}")
        
        # Toggle back
        requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_pdf": current_state}
        )
    
    def test_toggle_files_generation(self, auth_headers):
        """PUT /admin/agents/{id}/settings - toggle can_generate_files"""
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        agent_id = agents[0]["agent_id"]
        current_state = agents[0].get("can_generate_files", False)
        
        toggle_response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_files": not current_state}
        )
        assert toggle_response.status_code == 200
        print(f"✅ Files generation toggle: {current_state} -> {not current_state}")
        
        # Toggle back
        requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_files": current_state}
        )
    
    def test_toggle_active_status(self, auth_headers):
        """PUT /admin/agents/{id}/settings - toggle is_active (eye icon)"""
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        agent_id = agents[0]["agent_id"]
        current_state = agents[0].get("is_active", True)
        
        toggle_response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"is_active": not current_state}
        )
        assert toggle_response.status_code == 200
        print(f"✅ Active status toggle: {current_state} -> {not current_state}")
        
        # Toggle back
        requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"is_active": current_state}
        )


class TestBrainEditor:
    """Test Brain Editor save functionality - part of the bug"""
    
    def test_brain_editor_save(self, auth_headers):
        """PUT /admin/agents/{id}/brain - save brain settings"""
        # Get first agent
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        agent = agents[0]
        agent_id = agent["agent_id"]
        
        # Save brain with current values (no actual change)
        brain_data = {
            "name": agent.get("name", ""),
            "role": agent.get("role", ""),
            "description": agent.get("description", ""),
            "model_provider": agent.get("model_provider", "openai"),
            "model_name": agent.get("model_name", "gpt-5.2"),
            "temperature": agent.get("temperature", 0.7),
            "max_tokens": agent.get("max_tokens", 4096)
        }
        
        save_response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/brain",
            headers=auth_headers,
            json=brain_data
        )
        assert save_response.status_code == 200
        data = save_response.json()
        assert "agent" in data
        print(f"✅ Brain editor save successful for {agent.get('name')}")


class TestAdminTabs:
    """Test all admin dashboard tabs load correctly"""
    
    def test_overview_stats(self, auth_headers):
        """GET /admin/stats - Overview tab data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        print(f"✅ Overview stats: {data.get('total_users')} users")
    
    def test_analytics_data(self, auth_headers):
        """GET /admin/analytics - Analytics tab data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        print(f"✅ Analytics loaded: {data['kpis'].get('total_users')} total users")
    
    def test_api_keys_config(self, auth_headers):
        """GET /admin/api-keys - API Keys & Integrations"""
        response = requests.get(
            f"{BASE_URL}/api/admin/api-keys",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "active_provider" in data
        print(f"✅ API Keys config loaded: provider={data.get('active_provider')}")
    
    def test_save_api_keys(self, auth_headers):
        """PUT /admin/api-keys - Save API keys config"""
        response = requests.put(
            f"{BASE_URL}/api/admin/api-keys",
            headers=auth_headers,
            json={"active_provider": "emergent"}
        )
        assert response.status_code == 200
        print("✅ API keys save successful")
    
    def test_pricing_config(self, auth_headers):
        """GET /admin/pricing - Pricing tab data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/pricing",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        print("✅ Pricing config loaded")
    
    def test_pricing_save(self, auth_headers):
        """PUT /admin/pricing - Save/Publish pricing changes"""
        # Get current pricing
        get_response = requests.get(
            f"{BASE_URL}/api/admin/pricing",
            headers=auth_headers
        )
        current = get_response.json()
        
        # Save with current values (acts as publish)
        response = requests.put(
            f"{BASE_URL}/api/admin/pricing",
            headers=auth_headers,
            json=current
        )
        assert response.status_code == 200
        print("✅ Pricing save/publish successful")
    
    def test_branding_config(self, auth_headers):
        """GET /admin/branding - Branding tab data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/branding",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Branding config loaded: {data.get('platform_name', 'N/A')}")
    
    def test_branding_save(self, auth_headers):
        """POST /admin/branding - Save branding"""
        # Get current config
        get_response = requests.get(
            f"{BASE_URL}/api/admin/branding",
            headers=auth_headers
        )
        current = get_response.json()
        
        # Save with same values
        save_data = {
            "platform_name": current.get("platform_name", "MAARS Command"),
            "tagline": current.get("tagline", ""),
            "primary_color": current.get("primary_color", "#ef4444"),
            "accent_color": current.get("accent_color", "#f97316")
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/branding",
            headers=auth_headers,
            json=save_data
        )
        assert response.status_code == 200
        print("✅ Branding save successful")
    
    def test_smtp_config(self, auth_headers):
        """GET /admin/smtp-config - SMTP tab data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/smtp-config",
            headers=auth_headers
        )
        assert response.status_code == 200
        print("✅ SMTP config loaded")


class TestUsersList:
    """Test Users tab functionality"""
    
    def test_fetch_users(self, auth_headers):
        """GET /admin/users - Fetch all users"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers=auth_headers
        )
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        print(f"✅ Found {len(users)} users")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
