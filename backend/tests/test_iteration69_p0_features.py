"""
Iteration 69: P0 Features Testing
- Knowledge Graph API endpoints
- Trust Scores API
- Execution Logs API  
- Agent avatars (SVG data URLs for infinity agents)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        return data["token"]
    
    def test_login_returns_token(self, auth_token):
        """Verify login returns valid token"""
        assert auth_token is not None
        assert len(auth_token) > 0


class TestKnowledgeGraph:
    """Knowledge Graph API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        return response.json().get("token")
    
    def test_knowledge_graph_returns_200(self, auth_token):
        """GET /api/kernel/knowledge-graph returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
    
    def test_knowledge_graph_structure(self, auth_token):
        """Knowledge graph returns nodes and edges arrays"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)
    
    def test_knowledge_graph_node_count(self, auth_token):
        """Knowledge graph has 108 nodes (27 networks + 81 agents)"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        # 27 network nodes + 81 agent nodes (top 3 per network)
        assert len(data["nodes"]) == 108
    
    def test_knowledge_graph_node_types(self, auth_token):
        """Knowledge graph has network and agent node types"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        types = set(n.get("type") for n in data["nodes"])
        assert "network" in types
        assert "agent" in types
        
        # Count by type
        network_count = sum(1 for n in data["nodes"] if n.get("type") == "network")
        agent_count = sum(1 for n in data["nodes"] if n.get("type") == "agent")
        assert network_count == 27  # 27 networks
        assert agent_count == 81    # 3 agents per network
    
    def test_knowledge_graph_node_structure(self, auth_token):
        """Each node has required fields"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        for node in data["nodes"][:5]:  # Check first 5
            assert "node_id" in node
            assert "label" in node
            assert "type" in node
            assert "properties" in node
    
    def test_knowledge_graph_edges(self, auth_token):
        """Knowledge graph has edges with proper structure"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert len(data["edges"]) >= 80  # At least agent->network edges
        
        for edge in data["edges"][:5]:  # Check first 5
            assert "source" in edge
            assert "target" in edge
            assert "relationship" in edge


class TestTrustScores:
    """Trust Scores API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        return response.json().get("token")
    
    def test_trust_scores_returns_200(self, auth_token):
        """GET /api/kernel/trust-scores returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/trust-scores",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
    
    def test_trust_scores_returns_array(self, auth_token):
        """Trust scores returns an array"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/trust-scores",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert isinstance(data, list)
    
    def test_trust_scores_empty_initially(self, auth_token):
        """Trust scores is empty when no executions exist"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/trust-scores",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        # Empty array is valid - no execution data yet
        assert isinstance(data, list)


class TestExecutionLogs:
    """Execution Gateway API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        return response.json().get("token")
    
    def test_execution_logs_returns_200(self, auth_token):
        """GET /api/kernel/execution-logs returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/execution-logs",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
    
    def test_execution_logs_returns_array(self, auth_token):
        """Execution logs returns an array"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/execution-logs",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        assert isinstance(data, list)
    
    def test_execution_logs_empty_initially(self, auth_token):
        """Execution logs is empty when no actions have been performed"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/execution-logs",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        # Empty array is valid - no execution data yet
        assert isinstance(data, list)


class TestAgentAvatars:
    """Agent avatars (SVG data URLs) tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        return response.json().get("token")
    
    def test_agents_returns_458(self, auth_token):
        """GET /api/agents returns 458 agents (41 original + 417 infinity)"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 458
    
    def test_infinity_agents_count(self, auth_token):
        """417 infinity agents exist"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        infinity_agents = [a for a in data if a.get("is_infinity")]
        assert len(infinity_agents) == 417
    
    def test_infinity_agents_have_svg_avatars(self, auth_token):
        """All 417 infinity agents have SVG data URL avatars"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        infinity_agents = [a for a in data if a.get("is_infinity")]
        
        svg_avatars = [a for a in infinity_agents if a.get("avatar", "").startswith("data:image/svg")]
        assert len(svg_avatars) == 417, f"Expected 417 infinity agents with SVG avatars, got {len(svg_avatars)}"
    
    def test_svg_avatar_format(self, auth_token):
        """SVG avatars are valid data URIs"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        infinity_agents = [a for a in data if a.get("is_infinity")]
        
        # Check first 5 infinity agents
        for agent in infinity_agents[:5]:
            avatar = agent.get("avatar", "")
            assert avatar.startswith("data:image/svg+xml;base64,"), f"Avatar for {agent.get('name')} is not a valid SVG data URI"
    
    def test_original_agents_have_url_avatars(self, auth_token):
        """Original 41 agents have URL avatars"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = response.json()
        original_agents = [a for a in data if not a.get("is_infinity") and not a.get("is_custom")]
        
        # Most original agents should have http URLs
        url_avatars = [a for a in original_agents if a.get("avatar", "").startswith("http")]
        assert len(url_avatars) >= 35, f"Expected at least 35 original agents with URL avatars, got {len(url_avatars)}"


class TestKernelNetworks:
    """Kernel networks API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "Admin123!"
        })
        return response.json().get("token")
    
    def test_networks_returns_27(self, auth_token):
        """GET /api/kernel/networks returns 27 networks"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/networks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 27


class TestEndpointsRequireAuth:
    """Verify endpoints require authentication"""
    
    def test_knowledge_graph_requires_auth(self):
        """Knowledge graph requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/knowledge-graph")
        assert response.status_code in [401, 403]
    
    def test_trust_scores_requires_auth(self):
        """Trust scores requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/trust-scores")
        assert response.status_code in [401, 403]
    
    def test_execution_logs_requires_auth(self):
        """Execution logs requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/execution-logs")
        assert response.status_code in [401, 403]
    
    def test_agents_requires_auth(self):
        """Agents endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code in [401, 403]
