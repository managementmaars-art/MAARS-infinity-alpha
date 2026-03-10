"""
Iteration 68: Chat Agent Selector Tests
Tests for enhanced chat agent selector with network-grouped browsing and search.
Phase 2 features: Agent search, Browse Networks, Chat with Agent button on AgentNetworks
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Authentication tests"""
    
    def test_login_admin(self):
        """Test admin login returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 0


class TestAgentsAPI:
    """Tests for /api/agents endpoint - returns all 458 agents"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        return response.json().get("token")
    
    def test_get_agents_returns_458_agents(self, auth_token):
        """GET /api/agents should return 458 agents (41 original + 417 infinity)"""
        response = requests.get(f"{BASE_URL}/api/agents", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) == 458
    
    def test_agents_include_original_with_avatars(self, auth_token):
        """Original agents should have avatar URLs"""
        response = requests.get(f"{BASE_URL}/api/agents", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        agents = response.json()
        original_agents = [a for a in agents if not a.get('is_infinity')]
        
        assert len(original_agents) == 41
        # At least some original agents should have avatars
        agents_with_avatars = [a for a in original_agents if a.get('avatar')]
        assert len(agents_with_avatars) > 30  # Most original agents should have avatars
    
    def test_agents_include_infinity_without_avatars(self, auth_token):
        """Infinity agents should have empty avatar strings"""
        response = requests.get(f"{BASE_URL}/api/agents", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        agents = response.json()
        infinity_agents = [a for a in agents if a.get('is_infinity')]
        
        assert len(infinity_agents) == 417
        # Infinity agents should have empty avatars
        for agent in infinity_agents[:10]:  # Check first 10
            assert agent.get('avatar') == '' or agent.get('avatar') is None
            assert 'network' in agent
    
    def test_agent_structure_has_required_fields(self, auth_token):
        """All agents should have required fields"""
        response = requests.get(f"{BASE_URL}/api/agents", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        agents = response.json()
        
        required_fields = ['agent_id', 'name', 'role']
        for agent in agents[:20]:  # Check first 20
            for field in required_fields:
                assert field in agent, f"Missing field {field} in agent {agent.get('agent_id')}"


class TestNetworksAPI:
    """Tests for /api/kernel/networks endpoint - returns 27 networks"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        return response.json().get("token")
    
    def test_get_networks_returns_27_networks(self, auth_token):
        """GET /api/kernel/networks should return 27 networks"""
        response = requests.get(f"{BASE_URL}/api/kernel/networks", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        networks = response.json()
        assert isinstance(networks, list)
        assert len(networks) == 27
    
    def test_network_structure_has_required_fields(self, auth_token):
        """Networks should have required fields"""
        response = requests.get(f"{BASE_URL}/api/kernel/networks", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        networks = response.json()
        
        required_fields = ['key', 'code', 'name', 'purpose', 'agent_count']
        for network in networks[:5]:
            for field in required_fields:
                assert field in network, f"Missing field {field} in network {network.get('key')}"
    
    def test_networks_have_positive_agent_counts(self, auth_token):
        """All networks should have at least 1 agent"""
        response = requests.get(f"{BASE_URL}/api/kernel/networks", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        networks = response.json()
        
        for network in networks:
            assert network.get('agent_count', 0) > 0, f"Network {network.get('key')} has no agents"
    
    def test_total_agents_across_networks_is_417(self, auth_token):
        """Total agents across all networks should be 417 infinity agents"""
        response = requests.get(f"{BASE_URL}/api/kernel/networks", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        networks = response.json()
        
        total_agents = sum(n.get('agent_count', 0) for n in networks)
        assert total_agents == 417


class TestNetworkAgentsAPI:
    """Tests for /api/kernel/networks/{network_key}/agents endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        return response.json().get("token")
    
    def test_get_engineering_network_agents(self, auth_token):
        """GET /api/kernel/networks/engineering/agents should return agents"""
        response = requests.get(f"{BASE_URL}/api/kernel/networks/engineering/agents", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert 'agents' in data
        assert len(data['agents']) > 0
    
    def test_get_core_platform_network_agents(self, auth_token):
        """GET /api/kernel/networks/core_platform/agents should return agents"""
        response = requests.get(f"{BASE_URL}/api/kernel/networks/core_platform/agents", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert 'agents' in data
        assert len(data['agents']) > 0
    
    def test_invalid_network_returns_404(self, auth_token):
        """GET /api/kernel/networks/invalid_network/agents should return 404"""
        response = requests.get(f"{BASE_URL}/api/kernel/networks/invalid_network_xyz/agents", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 404


class TestAuthenticationRequired:
    """Tests that endpoints require authentication"""
    
    def test_agents_requires_auth(self):
        """GET /api/agents should return 401/403 without auth"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code in [401, 403]
    
    def test_networks_requires_auth(self):
        """GET /api/kernel/networks should return 401/403 without auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/networks")
        assert response.status_code in [401, 403]
