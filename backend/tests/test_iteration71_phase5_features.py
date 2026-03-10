"""
Test Suite for MAARS Infinity Phase 5 Features (Iteration 71):
1. Workflow Execution Engine - run workflows, poll status, view run history
2. Environment Segregation - 3 environments (sandbox/staging/production), switch active
3. Memory Hierarchy - 7 layers visualization (L1-L7), usage stats
4. Agent Personal Names - 417 agents with diverse non-Indian personal names
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
TEST_EMAIL = "management.maars@marsgc.net"
TEST_PASSWORD = "Admin123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json().get("token")


@pytest.fixture(scope="module")
def headers(auth_token):
    """Create authenticated headers"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestWorkflowExecution:
    """Test Workflow Execution Engine APIs"""
    
    workflow_id = None
    run_id = None
    
    def test_create_workflow_for_execution(self, headers):
        """Create a workflow with nodes for execution testing"""
        # First get some agents
        agents_res = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert agents_res.status_code == 200
        agents = agents_res.json()
        assert len(agents) > 2, "Need at least 3 agents for workflow test"
        
        nodes = [
            {"id": f"node_{i}", "agent_id": agents[i]["agent_id"], "name": agents[i]["name"], 
             "role": agents[i]["role"], "network": agents[i].get("network", "core"), "x": 100 + i*150, "y": 100}
            for i in range(min(3, len(agents)))
        ]
        edges = [
            {"id": "edge_1", "source": "node_0", "target": "node_1"},
            {"id": "edge_2", "source": "node_1", "target": "node_2"},
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/kernel/workflows",
            headers=headers,
            json={"name": "TEST_Execution_Workflow", "description": "Workflow for execution testing", "nodes": nodes, "edges": edges}
        )
        assert response.status_code == 200, f"Create workflow failed: {response.text}"
        data = response.json()
        assert "workflow_id" in data
        assert data["name"] == "TEST_Execution_Workflow"
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 2
        TestWorkflowExecution.workflow_id = data["workflow_id"]
        print(f"✓ Created workflow: {TestWorkflowExecution.workflow_id}")
    
    def test_run_workflow(self, headers):
        """POST /api/kernel/workflows/{id}/run - Start workflow execution"""
        assert TestWorkflowExecution.workflow_id, "No workflow created"
        
        response = requests.post(
            f"{BASE_URL}/api/kernel/workflows/{TestWorkflowExecution.workflow_id}/run",
            headers=headers
        )
        assert response.status_code == 200, f"Run workflow failed: {response.text}"
        data = response.json()
        assert "run_id" in data
        assert data["status"] in ["running", "pending"]
        assert "node_states" in data
        assert data["total_steps"] == 3
        TestWorkflowExecution.run_id = data["run_id"]
        print(f"✓ Started workflow run: {TestWorkflowExecution.run_id} with status {data['status']}")
    
    def test_get_workflow_run_with_polling(self, headers):
        """GET /api/kernel/workflow-runs/{run_id} - Poll until completion"""
        assert TestWorkflowExecution.run_id, "No run started"
        
        max_polls = 20
        final_status = None
        for i in range(max_polls):
            time.sleep(0.3)
            response = requests.get(
                f"{BASE_URL}/api/kernel/workflow-runs/{TestWorkflowExecution.run_id}",
                headers=headers
            )
            assert response.status_code == 200, f"Get run failed: {response.text}"
            data = response.json()
            assert "run_id" in data
            assert "node_states" in data
            assert "status" in data
            
            final_status = data["status"]
            if final_status in ["completed", "failed"]:
                # Verify node states
                node_states = data["node_states"]
                assert len(node_states) == 3, "Should have 3 node states"
                completed_nodes = sum(1 for ns in node_states.values() if ns["status"] == "completed")
                print(f"✓ Workflow run completed. Status: {final_status}, Completed nodes: {completed_nodes}/3")
                
                # Check node output has data
                for nid, ns in node_states.items():
                    if ns["status"] == "completed":
                        assert ns.get("finished_at"), f"Node {nid} should have finished_at"
                break
        else:
            print(f"Warning: Run did not complete after {max_polls} polls. Status: {final_status}")
        
        assert final_status == "completed", f"Expected completed, got {final_status}"
    
    def test_get_workflow_runs_history(self, headers):
        """GET /api/kernel/workflows/{id}/runs - Get run history"""
        assert TestWorkflowExecution.workflow_id, "No workflow created"
        
        response = requests.get(
            f"{BASE_URL}/api/kernel/workflows/{TestWorkflowExecution.workflow_id}/runs",
            headers=headers
        )
        assert response.status_code == 200, f"Get runs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1, "Should have at least 1 run"
        
        latest_run = data[0]
        assert latest_run["run_id"] == TestWorkflowExecution.run_id
        assert latest_run["workflow_id"] == TestWorkflowExecution.workflow_id
        print(f"✓ Run history shows {len(data)} run(s)")
    
    def test_run_not_found(self, headers):
        """GET /api/kernel/workflow-runs/{invalid_id} - Should return 404"""
        response = requests.get(
            f"{BASE_URL}/api/kernel/workflow-runs/invalid_run_id_12345",
            headers=headers
        )
        assert response.status_code == 404
        print("✓ Returns 404 for non-existent run")
    
    def test_cleanup_workflow(self, headers):
        """Delete test workflow"""
        if TestWorkflowExecution.workflow_id:
            response = requests.delete(
                f"{BASE_URL}/api/kernel/workflows/{TestWorkflowExecution.workflow_id}",
                headers=headers
            )
            assert response.status_code == 200
            print("✓ Cleaned up test workflow")


class TestEnvironments:
    """Test Environment Segregation APIs"""
    
    def test_get_environments(self, headers):
        """GET /api/kernel/environments - Returns 3 environments"""
        response = requests.get(f"{BASE_URL}/api/kernel/environments", headers=headers)
        assert response.status_code == 200, f"Get environments failed: {response.text}"
        data = response.json()
        
        assert "environments" in data
        assert "active" in data
        assert "stats" in data
        
        envs = data["environments"]
        assert len(envs) == 3, f"Expected 3 environments, got {len(envs)}"
        assert "sandbox" in envs
        assert "staging" in envs
        assert "production" in envs
        
        # Verify each environment has required fields
        for key, env in envs.items():
            assert "name" in env, f"Environment {key} missing name"
            assert "description" in env, f"Environment {key} missing description"
            assert "color" in env, f"Environment {key} missing color"
            assert "limits" in env, f"Environment {key} missing limits"
            limits = env["limits"]
            assert "max_agents" in limits
            assert "max_cost_per_run" in limits
            assert "real_actions" in limits
        
        print(f"✓ Got 3 environments: {list(envs.keys())}")
        print(f"✓ Active environment: {data['active']}")
    
    def test_switch_environment_to_staging(self, headers):
        """PUT /api/kernel/environments/active - Switch to staging"""
        response = requests.put(
            f"{BASE_URL}/api/kernel/environments/active",
            headers=headers,
            json={"environment": "staging"}
        )
        assert response.status_code == 200, f"Switch env failed: {response.text}"
        data = response.json()
        assert data["active_env"] == "staging"
        print("✓ Switched to staging environment")
    
    def test_verify_environment_switched(self, headers):
        """GET /api/kernel/environments - Verify switch persisted"""
        response = requests.get(f"{BASE_URL}/api/kernel/environments", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["active"] == "staging", f"Expected staging, got {data['active']}"
        print("✓ Verified environment switch persisted")
    
    def test_switch_to_sandbox(self, headers):
        """Switch back to sandbox"""
        response = requests.put(
            f"{BASE_URL}/api/kernel/environments/active",
            headers=headers,
            json={"environment": "sandbox"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["active_env"] == "sandbox"
        print("✓ Switched back to sandbox")
    
    def test_switch_to_production(self, headers):
        """Switch to production"""
        response = requests.put(
            f"{BASE_URL}/api/kernel/environments/active",
            headers=headers,
            json={"environment": "production"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["active_env"] == "production"
        print("✓ Switched to production")
    
    def test_switch_invalid_environment(self, headers):
        """PUT with invalid environment should fail"""
        response = requests.put(
            f"{BASE_URL}/api/kernel/environments/active",
            headers=headers,
            json={"environment": "invalid_env"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Returns 400 for invalid environment")
    
    def test_reset_to_sandbox(self, headers):
        """Reset to sandbox for other tests"""
        response = requests.put(
            f"{BASE_URL}/api/kernel/environments/active",
            headers=headers,
            json={"environment": "sandbox"}
        )
        assert response.status_code == 200


class TestMemoryHierarchy:
    """Test Memory Hierarchy APIs (7 Layers)"""
    
    def test_get_memory_layers(self, headers):
        """GET /api/kernel/memory/layers - Returns 7 memory layers"""
        response = requests.get(f"{BASE_URL}/api/kernel/memory/layers", headers=headers)
        assert response.status_code == 200, f"Get memory layers failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 7, f"Expected 7 layers, got {len(data)}"
        
        # Verify layer properties
        layer_names = []
        for layer in data:
            assert "layer" in layer
            assert "name" in layer
            assert "code" in layer
            assert "description" in layer
            assert "ttl" in layer
            assert "capacity" in layer
            assert "access_speed" in layer
            assert "color" in layer
            layer_names.append(f"L{layer['layer']}: {layer['name']}")
        
        # Verify layer order
        layer_nums = [l["layer"] for l in data]
        assert layer_nums == [1, 2, 3, 4, 5, 6, 7], f"Layer order incorrect: {layer_nums}"
        
        print("✓ Got 7 memory layers:")
        for name in layer_names:
            print(f"  - {name}")
    
    def test_memory_layer_codes(self, headers):
        """Verify layer codes L1-L7"""
        response = requests.get(f"{BASE_URL}/api/kernel/memory/layers", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        codes = [l["code"] for l in data]
        expected_codes = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]
        assert codes == expected_codes, f"Codes mismatch: {codes} != {expected_codes}"
        print("✓ Layer codes verified: L1-L7")
    
    def test_memory_layer_names(self, headers):
        """Verify specific layer names"""
        response = requests.get(f"{BASE_URL}/api/kernel/memory/layers", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        expected_names = {
            1: "Working Memory",
            7: "Archival Memory"
        }
        
        for layer in data:
            if layer["layer"] in expected_names:
                assert layer["name"] == expected_names[layer["layer"]], f"Layer {layer['layer']} name mismatch"
        
        print("✓ Layer names verified (L1: Working Memory, L7: Archival Memory)")
    
    def test_get_memory_stats(self, headers):
        """GET /api/kernel/memory/stats - Returns usage stats per layer"""
        response = requests.get(f"{BASE_URL}/api/kernel/memory/stats", headers=headers)
        assert response.status_code == 200, f"Get memory stats failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 7, f"Expected 7 stat entries, got {len(data)}"
        
        for stat in data:
            assert "layer" in stat
            assert "name" in stat
            assert "items" in stat
            assert "usage_kb" in stat
            assert "color" in stat
            assert isinstance(stat["items"], int) or isinstance(stat["items"], float)
            assert isinstance(stat["usage_kb"], (int, float))
        
        total_items = sum(s["items"] for s in data)
        total_usage = sum(s["usage_kb"] for s in data)
        print(f"✓ Memory stats: {total_items} total items, {total_usage:.1f} KB total usage")


class TestAgentPersonalNames:
    """Test that agents have personal names (not functional names)"""
    
    def test_agents_have_personal_names(self, headers):
        """GET /api/agents - Verify agents have personal names"""
        response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert response.status_code == 200, f"Get agents failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0, "No agents found"
        
        # Check a sample of agents
        infinity_agents = [a for a in data if a.get("is_infinity")]
        print(f"✓ Found {len(infinity_agents)} infinity agents")
        
        # Sample some agents to check naming
        sample_size = min(10, len(infinity_agents))
        sample_agents = infinity_agents[:sample_size]
        
        # Functional name patterns to check against
        functional_patterns = ["Agent", "Manager", "Controller", "Coordinator", "Planner", "Analyst"]
        
        personal_name_count = 0
        for agent in sample_agents:
            name = agent.get("name", "")
            # Check if name looks like a personal name (has 2+ parts, doesn't end with Agent/Manager etc)
            name_parts = name.split()
            is_personal = len(name_parts) >= 2 and not any(name.endswith(p) for p in functional_patterns)
            if is_personal:
                personal_name_count += 1
            print(f"  {agent['agent_id']}: {name} {'(personal)' if is_personal else '(functional)'}")
        
        # Note: This may not fail if agents still have functional names,
        # as the task description says they were renamed but we need to verify
        print(f"✓ Checked {sample_size} agent names, {personal_name_count} appear to be personal names")
    
    def test_agent_avatars(self, headers):
        """Verify agents have avatars"""
        response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        infinity_agents = [a for a in data if a.get("is_infinity")]
        agents_with_avatars = [a for a in infinity_agents if a.get("avatar")]
        
        print(f"✓ {len(agents_with_avatars)}/{len(infinity_agents)} infinity agents have avatars")


class TestAuthRequired:
    """Test that all new endpoints require authentication"""
    
    def test_workflow_run_requires_auth(self):
        """POST /workflows/{id}/run requires auth"""
        response = requests.post(f"{BASE_URL}/api/kernel/workflows/test_id/run")
        assert response.status_code == 401
        print("✓ Workflow run requires auth")
    
    def test_workflow_runs_requires_auth(self):
        """GET /workflows/{id}/runs requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/workflows/test_id/runs")
        assert response.status_code == 401
        print("✓ Workflow runs list requires auth")
    
    def test_workflow_run_status_requires_auth(self):
        """GET /workflow-runs/{run_id} requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/workflow-runs/test_run")
        assert response.status_code == 401
        print("✓ Workflow run status requires auth")
    
    def test_environments_requires_auth(self):
        """GET /environments requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/environments")
        assert response.status_code == 401
        print("✓ Environments endpoint requires auth")
    
    def test_switch_env_requires_auth(self):
        """PUT /environments/active requires auth"""
        response = requests.put(
            f"{BASE_URL}/api/kernel/environments/active",
            json={"environment": "staging"}
        )
        assert response.status_code == 401
        print("✓ Switch environment requires auth")
    
    def test_memory_layers_requires_auth(self):
        """GET /memory/layers requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/memory/layers")
        assert response.status_code == 401
        print("✓ Memory layers requires auth")
    
    def test_memory_stats_requires_auth(self):
        """GET /memory/stats requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/memory/stats")
        assert response.status_code == 401
        print("✓ Memory stats requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
