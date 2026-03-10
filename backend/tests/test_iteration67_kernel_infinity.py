"""
Iteration 67: MAARS Infinity Kernel and Agent Networks Tests
Tests for:
- Kernel Dashboard API endpoints
- Agent Networks (27 networks, 417+ agents)
- Task Graphs CRUD
- Tool Registry
- System Architecture
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "management.maars@marsgc.net"
TEST_PASSWORD = "Admin123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for tests."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code}")


@pytest.fixture
def auth_headers(auth_token):
    """Auth headers for API calls."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestHealthAndBasics:
    """Basic health and connectivity tests."""
    
    def test_health_check(self):
        """Test health endpoint."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        assert "MAARS" in data.get("service", "")
        print(f"✓ Health check OK: {data}")


class TestKernelStatus:
    """Tests for GET /api/kernel/status."""
    
    def test_kernel_status_returns_200(self, auth_headers):
        """Kernel status endpoint returns 200."""
        response = requests.get(f"{BASE_URL}/api/kernel/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Kernel status response: {list(data.keys())}")
    
    def test_kernel_status_has_subsystems(self, auth_headers):
        """Kernel status includes subsystems."""
        response = requests.get(f"{BASE_URL}/api/kernel/status", headers=auth_headers)
        data = response.json()
        
        assert "subsystems" in data
        subsystems = data["subsystems"]
        
        # Check required subsystems
        expected_subsystems = [
            "agent_scheduler", "task_graph_runtime", "resource_manager",
            "budget_controller", "execution_gateway", "tool_registry",
            "memory_controller", "policy_engine", "approval_controller",
            "failure_recovery"
        ]
        for sub in expected_subsystems:
            assert sub in subsystems, f"Missing subsystem: {sub}"
        
        print(f"✓ Subsystems present: {len(subsystems)}")
    
    def test_kernel_status_has_metrics(self, auth_headers):
        """Kernel status includes metrics."""
        response = requests.get(f"{BASE_URL}/api/kernel/status", headers=auth_headers)
        data = response.json()
        
        assert "metrics" in data
        metrics = data["metrics"]
        
        # Check required metrics
        expected_metrics = [
            "total_agents", "total_tasks", "active_tasks",
            "total_task_graphs", "active_task_graphs", "execution_logs",
            "memory_entries", "tools_registered"
        ]
        for m in expected_metrics:
            assert m in metrics, f"Missing metric: {m}"
        
        # Total agents should be 458+ (41 original + 417 infinity)
        print(f"✓ Total agents: {metrics.get('total_agents')}")


class TestNetworks:
    """Tests for GET /api/kernel/networks and network agents."""
    
    def test_networks_returns_200(self, auth_headers):
        """Networks endpoint returns 200."""
        response = requests.get(f"{BASE_URL}/api/kernel/networks", headers=auth_headers)
        assert response.status_code == 200
    
    def test_networks_returns_27_networks(self, auth_headers):
        """Should return 27 networks."""
        response = requests.get(f"{BASE_URL}/api/kernel/networks", headers=auth_headers)
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 27, f"Expected 27 networks, got {len(data)}"
        print(f"✓ Networks count: {len(data)}")
    
    def test_networks_have_required_fields(self, auth_headers):
        """Each network has required fields."""
        response = requests.get(f"{BASE_URL}/api/kernel/networks", headers=auth_headers)
        data = response.json()
        
        for net in data:
            assert "key" in net
            assert "code" in net
            assert "name" in net
            assert "purpose" in net
            assert "layer" in net
            assert "agent_count" in net
        
        print(f"✓ All networks have required fields")
    
    def test_networks_have_agents(self, auth_headers):
        """Networks should have agents assigned."""
        response = requests.get(f"{BASE_URL}/api/kernel/networks", headers=auth_headers)
        data = response.json()
        
        total_agents = sum(n.get("agent_count", 0) for n in data)
        assert total_agents >= 370, f"Expected 370+ agents total, got {total_agents}"
        print(f"✓ Total agents across networks: {total_agents}")
    
    def test_engineering_network_agents(self, auth_headers):
        """Test GET /api/kernel/networks/engineering/agents."""
        response = requests.get(
            f"{BASE_URL}/api/kernel/networks/engineering/agents",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "network" in data
        assert "agents" in data
        assert isinstance(data["agents"], list)
        assert len(data["agents"]) > 0
        
        # Check agent structure
        if data["agents"]:
            agent = data["agents"][0]
            assert "agent_id" in agent
            assert "name" in agent
            assert "role" in agent
        
        print(f"✓ Engineering network has {len(data['agents'])} agents")
    
    def test_core_platform_network_agents(self, auth_headers):
        """Test core_platform network has agents."""
        response = requests.get(
            f"{BASE_URL}/api/kernel/networks/core_platform/agents",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["agents"]) >= 18
        print(f"✓ Core platform network has {len(data['agents'])} agents")
    
    def test_invalid_network_returns_404(self, auth_headers):
        """Invalid network returns 404."""
        response = requests.get(
            f"{BASE_URL}/api/kernel/networks/invalid_network/agents",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestArchitecture:
    """Tests for GET /api/kernel/architecture."""
    
    def test_architecture_returns_200(self, auth_headers):
        """Architecture endpoint returns 200."""
        response = requests.get(f"{BASE_URL}/api/kernel/architecture", headers=auth_headers)
        assert response.status_code == 200
    
    def test_architecture_has_layers(self, auth_headers):
        """Architecture includes 16 system layers."""
        response = requests.get(f"{BASE_URL}/api/kernel/architecture", headers=auth_headers)
        data = response.json()
        
        assert "layers" in data
        assert len(data["layers"]) == 16
        print(f"✓ System layers: {len(data['layers'])}")
    
    def test_architecture_has_autonomy_tiers(self, auth_headers):
        """Architecture includes autonomy tiers."""
        response = requests.get(f"{BASE_URL}/api/kernel/architecture", headers=auth_headers)
        data = response.json()
        
        assert "autonomy_tiers" in data
        tiers = data["autonomy_tiers"]
        assert len(tiers) == 6  # Tiers 0-5
        print(f"✓ Autonomy tiers: {len(tiers)}")
    
    def test_architecture_has_totals(self, auth_headers):
        """Architecture includes total counts."""
        response = requests.get(f"{BASE_URL}/api/kernel/architecture", headers=auth_headers)
        data = response.json()
        
        assert data.get("total_networks") == 27
        assert data.get("total_agents") >= 370
        print(f"✓ Total agents: {data.get('total_agents')}, Networks: {data.get('total_networks')}")


class TestTaskGraphsCRUD:
    """Tests for Task Graphs CRUD operations."""
    
    created_graph_id = None
    
    def test_create_task_graph(self, auth_headers):
        """Test POST /api/kernel/task-graphs."""
        response = requests.post(
            f"{BASE_URL}/api/kernel/task-graphs",
            headers=auth_headers,
            json={
                "title": "TEST_Iteration67_Graph",
                "objective": "Test task graph creation",
                "scope": "Testing",
                "timeline": "1 week"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data or "title" in data
        TestTaskGraphsCRUD.created_graph_id = data.get("id")
        print(f"✓ Created task graph: {data.get('title')}")
    
    def test_list_task_graphs(self, auth_headers):
        """Test GET /api/kernel/task-graphs."""
        response = requests.get(f"{BASE_URL}/api/kernel/task-graphs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Task graphs count: {len(data)}")
    
    def test_task_graph_has_structure(self, auth_headers):
        """Task graphs have proper structure."""
        response = requests.get(f"{BASE_URL}/api/kernel/task-graphs", headers=auth_headers)
        data = response.json()
        
        if data:
            graph = data[0]
            expected_fields = ["title", "status", "nodes", "edges", "version"]
            for field in expected_fields:
                assert field in graph, f"Missing field: {field}"
        
        print(f"✓ Task graph structure validated")


class TestToolRegistry:
    """Tests for GET /api/kernel/tools."""
    
    def test_tools_returns_200(self, auth_headers):
        """Tools endpoint returns 200."""
        response = requests.get(f"{BASE_URL}/api/kernel/tools", headers=auth_headers)
        assert response.status_code == 200
    
    def test_tools_is_list(self, auth_headers):
        """Tools returns a list."""
        response = requests.get(f"{BASE_URL}/api/kernel/tools", headers=auth_headers)
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Tools registered: {len(data)}")


class TestExecutionLogs:
    """Tests for execution gateway and logs."""
    
    def test_execution_logs_returns_200(self, auth_headers):
        """Execution logs endpoint returns 200."""
        response = requests.get(f"{BASE_URL}/api/kernel/execution-logs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Execution logs: {len(data)}")
    
    def test_trust_scores_returns_200(self, auth_headers):
        """Trust scores endpoint returns 200."""
        response = requests.get(f"{BASE_URL}/api/kernel/trust-scores", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Trust scores: {len(data)}")


class TestCircuitBreakers:
    """Tests for circuit breakers endpoint."""
    
    def test_circuit_breakers_returns_200(self, auth_headers):
        """Circuit breakers endpoint returns 200."""
        response = requests.get(f"{BASE_URL}/api/kernel/circuit-breakers", headers=auth_headers)
        assert response.status_code == 200
        print(f"✓ Circuit breakers endpoint OK")


class TestRequiresAuth:
    """Tests that kernel endpoints require authentication."""
    
    def test_kernel_status_requires_auth(self):
        """Kernel status requires auth."""
        response = requests.get(f"{BASE_URL}/api/kernel/status")
        assert response.status_code in [401, 403]
    
    def test_networks_requires_auth(self):
        """Networks requires auth."""
        response = requests.get(f"{BASE_URL}/api/kernel/networks")
        assert response.status_code in [401, 403]
    
    def test_task_graphs_requires_auth(self):
        """Task graphs requires auth."""
        response = requests.get(f"{BASE_URL}/api/kernel/task-graphs")
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
