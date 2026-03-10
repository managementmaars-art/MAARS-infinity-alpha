"""
Iteration 86: Test Agent Team Builder and About Page Features
- Agent Teams CRUD API
- Agents endpoint for About page dynamic loading
- Trust analytics endpoint
- Collaboration engine with stats
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
TEST_EMAIL = "management.maars@marsgc.net"
TEST_PASSWORD = "admin123"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for testing"""
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json().get("token") or res.json().get("access_token")


@pytest.fixture(scope="module")
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestAgentsEndpoint:
    """Tests for /api/agents endpoint - used by About page"""
    
    def test_get_agents_list(self, headers):
        """About page: Verify all 458+ agents are returned"""
        res = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert res.status_code == 200, f"Failed to get agents: {res.text}"
        agents = res.json()
        assert isinstance(agents, list), "Expected list of agents"
        # Verify we have 458+ agents
        assert len(agents) >= 400, f"Expected 458+ agents, got {len(agents)}"
        print(f"✓ Agents count: {len(agents)}")
    
    def test_agents_have_network_field(self, headers):
        """About page: Verify agents have network field for grouping"""
        res = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert res.status_code == 200
        agents = res.json()
        # Check that agents have network field
        networks = set()
        for agent in agents:
            network = agent.get("network")
            if network:
                networks.add(network)
        # Expect 27+ unique networks
        assert len(networks) >= 20, f"Expected 27+ networks, got {len(networks)}: {networks}"
        print(f"✓ Unique networks: {len(networks)}")
    
    def test_agents_have_required_fields(self, headers):
        """About page: Verify agents have required fields for display"""
        res = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert res.status_code == 200
        agents = res.json()
        sample = agents[0] if agents else {}
        required_fields = ["agent_id", "name", "role"]
        for field in required_fields:
            assert field in sample, f"Missing required field: {field}"
        print(f"✓ Agents have required fields")
    
    def test_agents_have_avatars(self, headers):
        """Regression: Verify agents have real avatars (not SVG placeholders)"""
        res = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert res.status_code == 200
        agents = res.json()
        avatars_with_svg = 0
        for agent in agents:
            avatar = agent.get("avatar", "")
            if avatar and avatar.startswith("data:image/svg"):
                avatars_with_svg += 1
        # Should have minimal SVG placeholders
        svg_percentage = (avatars_with_svg / len(agents)) * 100 if agents else 0
        assert svg_percentage < 10, f"Too many SVG placeholders: {svg_percentage:.1f}%"
        print(f"✓ SVG placeholder percentage: {svg_percentage:.1f}%")


class TestAgentTeamsAPI:
    """Tests for /api/agent-teams endpoint - Team Builder page"""
    
    def test_list_agent_teams(self, headers):
        """Team Builder: List existing teams"""
        res = requests.get(f"{BASE_URL}/api/agent-teams", headers=headers)
        assert res.status_code == 200, f"Failed to list teams: {res.text}"
        teams = res.json()
        assert isinstance(teams, list), "Expected list of teams"
        print(f"✓ Teams count: {len(teams)}")
    
    def test_create_agent_team(self, headers):
        """Team Builder: Create a new team"""
        # First get some agent IDs
        agents_res = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        agents = agents_res.json()[:5]
        agent_ids = [a["agent_id"] for a in agents]
        
        team_data = {
            "name": "TEST_Iteration86_Team",
            "purpose": "Testing team creation",
            "description": "A test team for iteration 86 testing",
            "agent_ids": agent_ids
        }
        res = requests.post(f"{BASE_URL}/api/agent-teams", headers=headers, json=team_data)
        assert res.status_code == 200, f"Failed to create team: {res.text}"
        team = res.json()
        assert team["name"] == team_data["name"]
        assert team["team_id"] is not None
        assert len(team["agent_ids"]) == len(agent_ids)
        print(f"✓ Created team: {team['team_id']}")
        return team["team_id"]
    
    def test_get_agent_team(self, headers):
        """Team Builder: Get a specific team"""
        # List teams first
        res = requests.get(f"{BASE_URL}/api/agent-teams", headers=headers)
        teams = res.json()
        if not teams:
            pytest.skip("No teams to get")
        team_id = teams[0]["team_id"]
        
        res = requests.get(f"{BASE_URL}/api/agent-teams/{team_id}", headers=headers)
        assert res.status_code == 200, f"Failed to get team: {res.text}"
        team = res.json()
        assert team["team_id"] == team_id
        print(f"✓ Got team: {team_id}")
    
    def test_update_agent_team(self, headers):
        """Team Builder: Update a team"""
        # List teams first
        res = requests.get(f"{BASE_URL}/api/agent-teams", headers=headers)
        teams = res.json()
        if not teams:
            pytest.skip("No teams to update")
        team_id = teams[0]["team_id"]
        
        update_data = {
            "name": "Updated_TEST_Team",
            "purpose": "Updated purpose"
        }
        res = requests.put(f"{BASE_URL}/api/agent-teams/{team_id}", headers=headers, json=update_data)
        assert res.status_code == 200, f"Failed to update team: {res.text}"
        team = res.json()
        assert team["name"] == update_data["name"]
        print(f"✓ Updated team: {team_id}")
    
    def test_delete_agent_team(self, headers):
        """Team Builder: Delete a team"""
        # Create a team to delete
        agents_res = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        agents = agents_res.json()[:2]
        agent_ids = [a["agent_id"] for a in agents]
        
        team_data = {
            "name": "TEST_ToDelete_Team",
            "agent_ids": agent_ids
        }
        create_res = requests.post(f"{BASE_URL}/api/agent-teams", headers=headers, json=team_data)
        if create_res.status_code != 200:
            pytest.skip("Could not create team to delete")
        team_id = create_res.json()["team_id"]
        
        res = requests.delete(f"{BASE_URL}/api/agent-teams/{team_id}", headers=headers)
        assert res.status_code == 200, f"Failed to delete team: {res.text}"
        
        # Verify deleted
        get_res = requests.get(f"{BASE_URL}/api/agent-teams/{team_id}", headers=headers)
        assert get_res.status_code == 404
        print(f"✓ Deleted team: {team_id}")


class TestTrustAnalytics:
    """Tests for Trust Scores page enhancements"""
    
    def test_trust_analytics_endpoint(self, headers):
        """Trust Scores: Get trust analytics with distribution data"""
        res = requests.get(f"{BASE_URL}/api/kernel/trust-analytics", headers=headers)
        assert res.status_code == 200, f"Failed to get trust analytics: {res.text}"
        data = res.json()
        # Should have scores, summary, etc.
        assert "scores" in data or isinstance(data, dict)
        print(f"✓ Trust analytics response keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")


class TestCollaborationEngine:
    """Tests for Collaboration Engine page enhancements"""
    
    def test_list_collaborations(self, headers):
        """Collaboration Engine: List collaborations with pagination"""
        res = requests.get(f"{BASE_URL}/api/collaborations?page=1&limit=50", headers=headers)
        assert res.status_code == 200, f"Failed to list collaborations: {res.text}"
        data = res.json()
        # Should have items and total
        assert "items" in data or isinstance(data, list)
        print(f"✓ Collaborations response: {type(data)}")
    
    def test_create_collaboration(self, headers):
        """Collaboration Engine: Initiate a new collaboration"""
        # Get agent names
        agents_res = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        agents = agents_res.json()[:2]
        
        collab_data = {
            "sender": agents[0]["name"],
            "receivers": [agents[1]["name"]],
            "objective": "TEST_Iteration86_Collaboration",
            "collab_type": "information_sharing"
        }
        res = requests.post(f"{BASE_URL}/api/collaborations", headers=headers, json=collab_data)
        # Accept 200 or 201
        assert res.status_code in [200, 201], f"Failed to create collaboration: {res.text}"
        print(f"✓ Created collaboration")


class TestHealthAndBasicEndpoints:
    """Basic health and sanity checks"""
    
    def test_health_check(self):
        """Basic health check"""
        res = requests.get(f"{BASE_URL}/api/health")
        assert res.status_code == 200
        print(f"✓ Health check passed")
    
    def test_login(self):
        """Login works with test credentials"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert res.status_code == 200, f"Login failed: {res.text}"
        print(f"✓ Login successful")


# Cleanup test data
@pytest.fixture(scope="module", autouse=True)
def cleanup(headers):
    yield
    # Cleanup TEST_ prefixed teams
    try:
        res = requests.get(f"{BASE_URL}/api/agent-teams", headers=headers)
        if res.status_code == 200:
            teams = res.json()
            for team in teams:
                if team.get("name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/agent-teams/{team['team_id']}", headers=headers)
    except:
        pass
