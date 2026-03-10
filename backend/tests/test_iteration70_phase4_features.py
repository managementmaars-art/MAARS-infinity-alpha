"""
Iteration 70 - Phase 4 P0 Features Testing
Tests for:
1. Enterprise RBAC (roles, permissions, user assignments)
2. Circuit Breakers (8 breakers, configure, reset)
3. Cost Governance (overview, by-model, by-agent, budget)
4. Workflow Builder (CRUD operations)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
TEST_EMAIL = "management.maars@marsgc.net"
TEST_PASSWORD = "Admin123!"


class TestAuth:
    """Authentication for all tests"""
    token = None
    
    @classmethod
    def get_token(cls):
        if cls.token:
            return cls.token
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            cls.token = response.json().get("token")
        return cls.token


@pytest.fixture(scope="session")
def auth_token():
    """Get authentication token"""
    token = TestAuth.get_token()
    if not token:
        pytest.skip("Authentication failed - skipping tests")
    return token


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


# ==================== RBAC Tests ====================

class TestRBAC:
    """Test Enterprise RBAC with permissions management"""
    
    def test_rbac_config_returns_4_roles(self, auth_headers):
        """GET /api/kernel/rbac/config returns 4 roles with permissions"""
        response = requests.get(f"{BASE_URL}/api/kernel/rbac/config", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "roles" in data, "Response should have 'roles' key"
        roles = data["roles"]
        
        # Verify 4 roles exist
        expected_roles = ["admin", "manager", "analyst", "viewer"]
        for role in expected_roles:
            assert role in roles, f"Role '{role}' should exist"
        
        # Verify admin has all permissions
        admin = roles["admin"]
        assert admin["permissions"] == ["*"], "Admin should have wildcard permissions"
        assert admin["label"] == "Administrator"
        
        # Verify manager has specific permissions
        manager = roles["manager"]
        assert len(manager["permissions"]) > 5, "Manager should have multiple permissions"
        
        # Verify analyst has read permissions
        analyst = roles["analyst"]
        assert "agents:read" in analyst["permissions"]
        assert "agents:chat" in analyst["permissions"]
        
        # Verify viewer is read-only
        viewer = roles["viewer"]
        assert "agents:read" in viewer["permissions"]
        assert "agents:write" not in viewer["permissions"]
        
        # Verify resources and actions
        assert "resources" in data
        assert "actions" in data
        assert len(data["resources"]) >= 8
        assert "read" in data["actions"]
        assert "write" in data["actions"]
        
        print(f"✓ RBAC config: {len(roles)} roles, {len(data['resources'])} resources")
    
    def test_rbac_users_returns_user_list(self, auth_headers):
        """GET /api/kernel/rbac/users returns user list with roles"""
        response = requests.get(f"{BASE_URL}/api/kernel/rbac/users", headers=auth_headers)
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list), "Should return a list of users"
        
        if len(users) > 0:
            user = users[0]
            assert "user_id" in user
            assert "email" in user
            assert "role" in user
            print(f"✓ RBAC users: {len(users)} users found")
        else:
            print("✓ RBAC users: No users found (empty list)")
    
    def test_rbac_update_user_role(self, auth_headers):
        """PUT /api/kernel/rbac/users/{user_id}/role updates user role"""
        # First get user list
        response = requests.get(f"{BASE_URL}/api/kernel/rbac/users", headers=auth_headers)
        users = response.json()
        
        if len(users) == 0:
            pytest.skip("No users to update")
        
        user = users[0]
        user_id = user["user_id"]
        original_role = user.get("role", "viewer")
        
        # Update to a different role
        new_role = "analyst" if original_role != "analyst" else "manager"
        response = requests.put(
            f"{BASE_URL}/api/kernel/rbac/users/{user_id}/role",
            headers=auth_headers,
            json={"role": new_role}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["user_id"] == user_id
        assert data["role"] == new_role
        
        # Restore original role
        requests.put(
            f"{BASE_URL}/api/kernel/rbac/users/{user_id}/role",
            headers=auth_headers,
            json={"role": original_role}
        )
        
        print(f"✓ RBAC role update: {user_id} changed to {new_role}, restored to {original_role}")
    
    def test_rbac_invalid_role_rejected(self, auth_headers):
        """PUT /api/kernel/rbac/users/{user_id}/role rejects invalid roles"""
        response = requests.get(f"{BASE_URL}/api/kernel/rbac/users", headers=auth_headers)
        users = response.json()
        
        if len(users) == 0:
            pytest.skip("No users available")
        
        user_id = users[0]["user_id"]
        response = requests.put(
            f"{BASE_URL}/api/kernel/rbac/users/{user_id}/role",
            headers=auth_headers,
            json={"role": "invalid_role_xyz"}
        )
        assert response.status_code == 400, f"Should reject invalid role, got {response.status_code}"
        print("✓ RBAC invalid role rejected correctly")


# ==================== Circuit Breakers Tests ====================

class TestCircuitBreakers:
    """Test Circuit Breaker configuration UI"""
    
    def test_circuit_breakers_returns_8_breakers(self, auth_headers):
        """GET /api/kernel/circuit-breakers/full returns 8 circuit breakers"""
        response = requests.get(f"{BASE_URL}/api/kernel/circuit-breakers/full", headers=auth_headers)
        assert response.status_code == 200
        
        breakers = response.json()
        assert isinstance(breakers, list)
        assert len(breakers) == 8, f"Expected 8 circuit breakers, got {len(breakers)}"
        
        # Verify expected breakers exist
        breaker_ids = [b["breaker_id"] for b in breakers]
        expected = ["llm_gateway", "tool_execution", "memory_store", "web_search", 
                    "email_service", "calendar_service", "stripe_payments", "file_processing"]
        
        for exp_id in expected:
            assert exp_id in breaker_ids, f"Breaker '{exp_id}' should exist"
        
        # Verify breaker structure
        for breaker in breakers:
            assert "breaker_id" in breaker
            assert "name" in breaker
            assert "state" in breaker
            assert breaker["state"] in ["closed", "open", "half-open"]
            assert "failure_threshold" in breaker
            assert "reset_timeout_s" in breaker
            assert "failures" in breaker
            assert "description" in breaker
        
        print(f"✓ Circuit breakers: {len(breakers)} breakers found")
        for b in breakers:
            print(f"  - {b['name']}: {b['state']}, threshold={b['failure_threshold']}")
    
    def test_circuit_breaker_update_config(self, auth_headers):
        """PUT /api/kernel/circuit-breakers/{id} updates breaker config"""
        breaker_id = "tool_execution"
        
        # Get current config
        response = requests.get(f"{BASE_URL}/api/kernel/circuit-breakers/full", headers=auth_headers)
        breakers = response.json()
        original = next((b for b in breakers if b["breaker_id"] == breaker_id), None)
        assert original, f"Breaker {breaker_id} not found"
        
        original_threshold = original["failure_threshold"]
        
        # Update config
        new_threshold = original_threshold + 1
        response = requests.put(
            f"{BASE_URL}/api/kernel/circuit-breakers/{breaker_id}",
            headers=auth_headers,
            json={"failure_threshold": new_threshold, "reset_timeout_s": 45}
        )
        assert response.status_code == 200
        
        updated = response.json()
        assert updated["failure_threshold"] == new_threshold
        assert updated["reset_timeout_s"] == 45
        
        # Restore original
        requests.put(
            f"{BASE_URL}/api/kernel/circuit-breakers/{breaker_id}",
            headers=auth_headers,
            json={"failure_threshold": original_threshold, "reset_timeout_s": original.get("reset_timeout_s", 30)}
        )
        
        print(f"✓ Circuit breaker update: {breaker_id} threshold changed to {new_threshold}")
    
    def test_circuit_breaker_reset(self, auth_headers):
        """POST /api/kernel/circuit-breakers/{id}/reset resets breaker state"""
        breaker_id = "web_search"
        
        response = requests.post(
            f"{BASE_URL}/api/kernel/circuit-breakers/{breaker_id}/reset",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["state"] == "closed"
        assert data["failures"] == 0
        
        print(f"✓ Circuit breaker reset: {breaker_id} reset to closed state")
    
    def test_circuit_breaker_not_found(self, auth_headers):
        """PUT/POST returns 404 for non-existent breaker"""
        response = requests.put(
            f"{BASE_URL}/api/kernel/circuit-breakers/nonexistent_breaker",
            headers=auth_headers,
            json={"failure_threshold": 5}
        )
        assert response.status_code == 404
        
        response = requests.post(
            f"{BASE_URL}/api/kernel/circuit-breakers/nonexistent_breaker/reset",
            headers=auth_headers
        )
        assert response.status_code == 404
        
        print("✓ Circuit breaker 404 handling works correctly")


# ==================== Cost Governance Tests ====================

class TestCostGovernance:
    """Test Cost Governance dashboard with budget controls"""
    
    def test_cost_overview(self, auth_headers):
        """GET /api/kernel/cost/overview returns cost aggregation"""
        response = requests.get(f"{BASE_URL}/api/kernel/cost/overview", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_cost" in data
        assert "total_executions" in data
        assert "avg_cost" in data
        assert "max_cost" in data
        
        assert isinstance(data["total_cost"], (int, float))
        assert isinstance(data["total_executions"], int)
        
        print(f"✓ Cost overview: total=${data['total_cost']:.4f}, executions={data['total_executions']}")
    
    def test_cost_by_model(self, auth_headers):
        """GET /api/kernel/cost/by-model returns cost breakdown by model"""
        response = requests.get(f"{BASE_URL}/api/kernel/cost/by-model", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            model = data[0]
            assert "model" in model
            assert "total_cost" in model
            assert "count" in model
            print(f"✓ Cost by model: {len(data)} models, top={data[0]['model']}")
        else:
            print("✓ Cost by model: Empty (no execution data yet)")
    
    def test_cost_by_agent(self, auth_headers):
        """GET /api/kernel/cost/by-agent returns cost breakdown by agent"""
        response = requests.get(f"{BASE_URL}/api/kernel/cost/by-agent", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            agent = data[0]
            assert "agent_id" in agent
            assert "total_cost" in agent
            assert "count" in agent
            print(f"✓ Cost by agent: {len(data)} agents")
        else:
            print("✓ Cost by agent: Empty (no execution data yet)")
    
    def test_cost_budget_get(self, auth_headers):
        """GET /api/kernel/cost/budget returns budget configuration"""
        response = requests.get(f"{BASE_URL}/api/kernel/cost/budget", headers=auth_headers)
        assert response.status_code == 200
        
        budget = response.json()
        assert "monthly_limit" in budget
        assert "daily_limit" in budget
        assert "alert_threshold" in budget
        assert "auto_pause" in budget
        
        assert isinstance(budget["monthly_limit"], (int, float))
        assert isinstance(budget["daily_limit"], (int, float))
        assert 0 <= budget["alert_threshold"] <= 1
        
        print(f"✓ Cost budget: monthly=${budget['monthly_limit']}, daily=${budget['daily_limit']}, alert={budget['alert_threshold']*100}%")
    
    def test_cost_budget_update(self, auth_headers):
        """PUT /api/kernel/cost/budget updates budget limits"""
        # Get current
        response = requests.get(f"{BASE_URL}/api/kernel/cost/budget", headers=auth_headers)
        original = response.json()
        
        # Update
        new_limits = {
            "monthly_limit": 200.0,
            "daily_limit": 20.0,
            "alert_threshold": 0.75,
            "auto_pause": True
        }
        response = requests.put(
            f"{BASE_URL}/api/kernel/cost/budget",
            headers=auth_headers,
            json=new_limits
        )
        assert response.status_code == 200
        
        updated = response.json()
        assert updated["monthly_limit"] == 200.0
        assert updated["daily_limit"] == 20.0
        assert updated["alert_threshold"] == 0.75
        assert updated["auto_pause"] == True
        
        # Restore
        requests.put(
            f"{BASE_URL}/api/kernel/cost/budget",
            headers=auth_headers,
            json={
                "monthly_limit": original.get("monthly_limit", 100.0),
                "daily_limit": original.get("daily_limit", 10.0),
                "alert_threshold": original.get("alert_threshold", 0.8),
                "auto_pause": original.get("auto_pause", False)
            }
        )
        
        print(f"✓ Cost budget update: limits changed and restored")


# ==================== Workflow Builder Tests ====================

class TestWorkflowBuilder:
    """Test Visual Workflow Builder with drag-and-drop agent orchestration"""
    
    workflow_id = None  # Store created workflow for cleanup
    
    def test_workflow_create(self, auth_headers):
        """POST /api/kernel/workflows creates a new workflow"""
        payload = {
            "name": "TEST_Workflow_Iteration70",
            "description": "Test workflow for Phase 4 testing",
            "nodes": [
                {"id": "node_1", "agent_id": "research-agent", "name": "Research Agent", "x": 100, "y": 100},
                {"id": "node_2", "agent_id": "analysis-agent", "name": "Analysis Agent", "x": 300, "y": 100}
            ],
            "edges": [
                {"id": "edge_1", "source": "node_1", "target": "node_2"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/kernel/workflows",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        
        workflow = response.json()
        assert "workflow_id" in workflow
        assert workflow["name"] == "TEST_Workflow_Iteration70"
        assert len(workflow["nodes"]) == 2
        assert len(workflow["edges"]) == 1
        assert workflow["status"] == "draft"
        
        TestWorkflowBuilder.workflow_id = workflow["workflow_id"]
        
        print(f"✓ Workflow created: {workflow['workflow_id']}")
    
    def test_workflow_list(self, auth_headers):
        """GET /api/kernel/workflows returns user workflows"""
        response = requests.get(f"{BASE_URL}/api/kernel/workflows", headers=auth_headers)
        assert response.status_code == 200
        
        workflows = response.json()
        assert isinstance(workflows, list)
        
        # Find our test workflow
        test_wf = next((w for w in workflows if w.get("name") == "TEST_Workflow_Iteration70"), None)
        if TestWorkflowBuilder.workflow_id:
            assert test_wf is not None, "Created workflow should be in list"
        
        print(f"✓ Workflow list: {len(workflows)} workflows")
    
    def test_workflow_update(self, auth_headers):
        """PUT /api/kernel/workflows/{id} updates workflow nodes/edges"""
        if not TestWorkflowBuilder.workflow_id:
            pytest.skip("No workflow created to update")
        
        workflow_id = TestWorkflowBuilder.workflow_id
        
        # Add a node
        update_payload = {
            "name": "TEST_Workflow_Updated",
            "nodes": [
                {"id": "node_1", "agent_id": "research-agent", "name": "Research Agent", "x": 100, "y": 100},
                {"id": "node_2", "agent_id": "analysis-agent", "name": "Analysis Agent", "x": 300, "y": 100},
                {"id": "node_3", "agent_id": "report-agent", "name": "Report Agent", "x": 500, "y": 100}
            ],
            "edges": [
                {"id": "edge_1", "source": "node_1", "target": "node_2"},
                {"id": "edge_2", "source": "node_2", "target": "node_3"}
            ]
        }
        
        response = requests.put(
            f"{BASE_URL}/api/kernel/workflows/{workflow_id}",
            headers=auth_headers,
            json=update_payload
        )
        assert response.status_code == 200
        
        updated = response.json()
        assert updated["name"] == "TEST_Workflow_Updated"
        assert len(updated["nodes"]) == 3
        assert len(updated["edges"]) == 2
        
        print(f"✓ Workflow updated: {len(updated['nodes'])} nodes, {len(updated['edges'])} edges")
    
    def test_workflow_get_single(self, auth_headers):
        """GET /api/kernel/workflows/{id} returns single workflow"""
        if not TestWorkflowBuilder.workflow_id:
            pytest.skip("No workflow created")
        
        workflow_id = TestWorkflowBuilder.workflow_id
        response = requests.get(
            f"{BASE_URL}/api/kernel/workflows/{workflow_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        workflow = response.json()
        assert workflow["workflow_id"] == workflow_id
        
        print(f"✓ Workflow get: {workflow['name']}")
    
    def test_workflow_delete(self, auth_headers):
        """DELETE /api/kernel/workflows/{id} deletes workflow"""
        if not TestWorkflowBuilder.workflow_id:
            pytest.skip("No workflow created to delete")
        
        workflow_id = TestWorkflowBuilder.workflow_id
        response = requests.delete(
            f"{BASE_URL}/api/kernel/workflows/{workflow_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify deletion
        response = requests.get(
            f"{BASE_URL}/api/kernel/workflows/{workflow_id}",
            headers=auth_headers
        )
        assert response.status_code == 404 or response.json() is None
        
        TestWorkflowBuilder.workflow_id = None
        print(f"✓ Workflow deleted: {workflow_id}")
    
    def test_workflow_not_found(self, auth_headers):
        """GET/PUT/DELETE returns 404 for non-existent workflow"""
        fake_id = "wf_nonexistent12345"
        
        response = requests.get(
            f"{BASE_URL}/api/kernel/workflows/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == 404
        
        response = requests.put(
            f"{BASE_URL}/api/kernel/workflows/{fake_id}",
            headers=auth_headers,
            json={"name": "Test"}
        )
        assert response.status_code == 404
        
        print("✓ Workflow 404 handling works correctly")


# ==================== Auth Required Tests ====================

class TestAuthRequired:
    """Verify all endpoints require authentication"""
    
    def test_rbac_requires_auth(self):
        """RBAC endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/kernel/rbac/config")
        assert response.status_code == 401 or response.status_code == 403
        
        response = requests.get(f"{BASE_URL}/api/kernel/rbac/users")
        assert response.status_code == 401 or response.status_code == 403
        
        print("✓ RBAC endpoints require auth")
    
    def test_circuit_breakers_requires_auth(self):
        """Circuit breaker endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/kernel/circuit-breakers/full")
        assert response.status_code == 401 or response.status_code == 403
        
        print("✓ Circuit breaker endpoints require auth")
    
    def test_cost_requires_auth(self):
        """Cost governance endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/kernel/cost/overview")
        assert response.status_code == 401 or response.status_code == 403
        
        response = requests.get(f"{BASE_URL}/api/kernel/cost/budget")
        assert response.status_code == 401 or response.status_code == 403
        
        print("✓ Cost governance endpoints require auth")
    
    def test_workflows_requires_auth(self):
        """Workflow endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/kernel/workflows")
        assert response.status_code == 401 or response.status_code == 403
        
        print("✓ Workflow endpoints require auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
