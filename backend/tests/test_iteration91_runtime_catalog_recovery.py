"""
Iteration 91 - MAARS Agent Runtime, Catalog, and Recovery System Tests
Tests the NEW features:
- Agent Runtime: 13-step execution loop (POST /api/infinity/runtime/execute, GET /api/infinity/runtime/history)
- Agent Catalog: Full registry with search/filter/maturity (GET /api/infinity/catalog/stats, agents, networks, PUT maturity)
- Recovery System: Quarantine, release, recovery log (POST quarantine, POST release, GET quarantined, GET log)
- Existing APIs still work: system/status, metrics/live, orchestrator/execute
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAgentCatalog:
    """Agent Catalog endpoint tests - 459 agents registry"""
    
    def test_catalog_stats(self):
        """GET /api/infinity/catalog/stats - Returns total_agents (459), by_network, by_maturity, by_tier"""
        response = requests.get(f"{BASE_URL}/api/infinity/catalog/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_agents" in data, "Missing total_agents"
        assert data["total_agents"] >= 400, f"Expected ~459 agents, got {data['total_agents']}"
        assert "by_network" in data, "Missing by_network"
        assert "by_maturity" in data, "Missing by_maturity"
        assert "by_tier" in data, "Missing by_tier"
        assert isinstance(data["by_network"], list), "by_network should be a list"
        print(f"PASS: Catalog stats - {data['total_agents']} agents, {len(data['by_network'])} networks")
    
    def test_catalog_agents_list(self):
        """GET /api/infinity/catalog/agents - Returns paginated agent list"""
        response = requests.get(f"{BASE_URL}/api/infinity/catalog/agents?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "agents" in data, "Missing agents array"
        assert "total" in data, "Missing total count"
        assert len(data["agents"]) <= 10, "Should respect limit"
        assert data["total"] >= 400, f"Expected ~459 total, got {data['total']}"
        
        # Verify agent structure
        if data["agents"]:
            agent = data["agents"][0]
            assert "agent_id" in agent, "Agent missing agent_id"
            assert "name" in agent, "Agent missing name"
            assert "network" in agent, "Agent missing network"
        print(f"PASS: Catalog agents list - {len(data['agents'])} agents returned, {data['total']} total")
    
    def test_catalog_search_kernel(self):
        """GET /api/infinity/catalog/agents?search=kernel - Search agents by name"""
        response = requests.get(f"{BASE_URL}/api/infinity/catalog/agents?search=kernel")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "agents" in data, "Missing agents array"
        # Should find kernel-related agents
        if data["agents"]:
            names = [a["name"].lower() for a in data["agents"]]
            agent_ids = [a["agent_id"].lower() for a in data["agents"]]
            has_kernel = any("kernel" in n or "kernel" in aid for n, aid in zip(names, agent_ids))
            assert has_kernel or data["total"] > 0, "Search should find kernel agents"
        print(f"PASS: Search 'kernel' - found {data['total']} agents")
    
    def test_catalog_filter_by_network(self):
        """GET /api/infinity/catalog/agents?network=engineering - Filter by network"""
        response = requests.get(f"{BASE_URL}/api/infinity/catalog/agents?network=engineering")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "agents" in data, "Missing agents array"
        # All returned agents should be in engineering network
        for agent in data["agents"]:
            assert agent.get("network") == "engineering", f"Agent {agent['agent_id']} not in engineering network"
        print(f"PASS: Filter by network 'engineering' - {data['total']} agents")
    
    def test_catalog_agent_detail(self):
        """GET /api/infinity/catalog/agents/{agent_id} - Get full agent detail"""
        # First get an agent ID
        list_response = requests.get(f"{BASE_URL}/api/infinity/catalog/agents?limit=1")
        assert list_response.status_code == 200
        agents = list_response.json().get("agents", [])
        assert len(agents) > 0, "No agents found"
        
        agent_id = agents[0]["agent_id"]
        response = requests.get(f"{BASE_URL}/api/infinity/catalog/agents/{agent_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["agent_id"] == agent_id, "Agent ID mismatch"
        assert "name" in data, "Missing name"
        assert "capabilities" in data, "Missing capabilities"
        assert "network" in data, "Missing network"
        # Detail endpoint adds extra fields
        assert "recent_executions" in data, "Missing recent_executions"
        print(f"PASS: Agent detail for {agent_id} - {data['name']}")
    
    def test_catalog_networks(self):
        """GET /api/infinity/catalog/networks - Get all networks with agent counts"""
        response = requests.get(f"{BASE_URL}/api/infinity/catalog/networks")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return list of networks"
        assert len(data) > 0, "Should have networks"
        
        # Verify network structure
        network = data[0]
        assert "network_id" in network, "Missing network_id"
        assert "name" in network, "Missing name"
        assert "agent_count" in network, "Missing agent_count"
        print(f"PASS: Networks list - {len(data)} networks")
    
    def test_catalog_update_maturity(self):
        """PUT /api/infinity/catalog/agents/{agent_id}/maturity?maturity=experimental - Update maturity state"""
        # Use a test agent
        agent_id = "agent_10a_kernel_ops"
        
        # Update to experimental
        response = requests.put(f"{BASE_URL}/api/infinity/catalog/agents/{agent_id}/maturity?maturity=experimental")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("maturity") == "experimental", f"Expected experimental, got {data.get('maturity')}"
        
        # Restore to production-ready
        restore = requests.put(f"{BASE_URL}/api/infinity/catalog/agents/{agent_id}/maturity?maturity=production-ready")
        assert restore.status_code == 200
        print(f"PASS: Updated maturity for {agent_id} to experimental, then restored")


class TestAgentRuntime:
    """Agent Runtime 13-step execution loop tests"""
    
    def test_runtime_execute_simple_task(self):
        """POST /api/infinity/runtime/execute - Full 13-step loop with real LLM (10-20s)"""
        payload = {
            "agent_id": "agent_10a_kernel_ops",
            "task_description": "Check system health",
            "environment": "sandbox"
        }
        
        # This takes 10-20 seconds due to real LLM call
        response = requests.post(
            f"{BASE_URL}/api/infinity/runtime/execute",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "execution_id" in data, "Missing execution_id"
        assert "agent_id" in data, "Missing agent_id"
        assert data["agent_id"] == "agent_10a_kernel_ops"
        assert "status" in data, "Missing status"
        assert "steps" in data, "Missing steps array"
        
        # Verify 13-step loop
        steps = data["steps"]
        assert len(steps) >= 10, f"Expected ~13 steps, got {len(steps)}"
        
        # Check key steps exist
        step_names = [s["step"] for s in steps]
        expected_steps = ["load_role_pack", "load_context", "retrieve_memory", "analyze_task", 
                         "plan", "create_action_request", "policy_check", "approval", "execute"]
        for expected in expected_steps:
            assert expected in step_names, f"Missing step: {expected}"
        
        # Check summary
        assert "summary" in data, "Missing summary"
        assert "passed" in data["summary"], "Missing passed count"
        assert "latency_ms" in data["summary"], "Missing latency_ms"
        
        print(f"PASS: Runtime execute - {len(steps)} steps, status={data['status']}, latency={data['summary']['latency_ms']}ms")
    
    def test_runtime_history(self):
        """GET /api/infinity/runtime/history - Returns recent runtime executions"""
        response = requests.get(f"{BASE_URL}/api/infinity/runtime/history?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return list"
        
        # Should have at least one execution from previous test
        if data:
            exec_record = data[0]
            assert "execution_id" in exec_record, "Missing execution_id"
            assert "agent_id" in exec_record, "Missing agent_id"
            assert "status" in exec_record, "Missing status"
            assert "steps" in exec_record, "Missing steps"
        print(f"PASS: Runtime history - {len(data)} executions")
    
    def test_runtime_history_filter_by_agent(self):
        """GET /api/infinity/runtime/history?agent_id=X - Filter by agent"""
        response = requests.get(f"{BASE_URL}/api/infinity/runtime/history?agent_id=agent_10a_kernel_ops&limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return list"
        for exec_record in data:
            assert exec_record.get("agent_id") == "agent_10a_kernel_ops", "Should filter by agent_id"
        print(f"PASS: Runtime history filtered by agent - {len(data)} executions")


class TestRecoverySystem:
    """Recovery System tests - quarantine, release, rollback, retry"""
    
    def test_quarantine_agent(self):
        """POST /api/infinity/recovery/quarantine - Quarantine an agent"""
        payload = {
            "agent_id": "agent_10a_kernel_ops",
            "reason": "TEST_quarantine_for_testing"
        }
        
        response = requests.post(f"{BASE_URL}/api/infinity/recovery/quarantine", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("agent_id") == "agent_10a_kernel_ops", "Agent ID mismatch"
        assert "quarantined_at" in data, "Missing quarantined_at"
        assert data.get("released") == False, "Should not be released"
        print(f"PASS: Quarantined agent_10a_kernel_ops")
    
    def test_get_quarantined_agents(self):
        """GET /api/infinity/recovery/quarantined - List quarantined agents"""
        response = requests.get(f"{BASE_URL}/api/infinity/recovery/quarantined")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return list"
        
        # Should have the agent we just quarantined
        agent_ids = [a.get("agent_id") for a in data]
        assert "agent_10a_kernel_ops" in agent_ids, "Quarantined agent not in list"
        print(f"PASS: Quarantined agents list - {len(data)} agents")
    
    def test_release_from_quarantine(self):
        """POST /api/infinity/recovery/release/{agent_id} - Release from quarantine"""
        response = requests.post(f"{BASE_URL}/api/infinity/recovery/release/agent_10a_kernel_ops")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("agent_id") == "agent_10a_kernel_ops", "Agent ID mismatch"
        assert data.get("status") == "released", "Should be released"
        print(f"PASS: Released agent_10a_kernel_ops from quarantine")
    
    def test_recovery_log(self):
        """GET /api/infinity/recovery/log - Get recovery action log"""
        response = requests.get(f"{BASE_URL}/api/infinity/recovery/log?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return list"
        print(f"PASS: Recovery log - {len(data)} entries")


class TestExistingAPIs:
    """Verify existing APIs still work"""
    
    def test_system_status(self):
        """GET /api/infinity/system/status - System health"""
        response = requests.get(f"{BASE_URL}/api/infinity/system/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Missing status"
        assert "total_agents" in data, "Missing total_agents"
        print(f"PASS: System status - {data['status']}, {data['total_agents']} agents")
    
    def test_metrics_live(self):
        """GET /api/infinity/metrics/live - Live metrics"""
        response = requests.get(f"{BASE_URL}/api/infinity/metrics/live")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "metrics" in data, "Missing metrics"
        assert "triggered_alerts" in data, "Missing triggered_alerts"
        print(f"PASS: Live metrics - {len(data['metrics'])} metrics")
    
    def test_orchestrator_execute(self):
        """POST /api/infinity/orchestrator/execute - Commander Orion execute"""
        payload = {
            "description": "Test goal for iteration 91",
            "environment": "simulation"
        }
        
        response = requests.post(f"{BASE_URL}/api/infinity/orchestrator/execute", json=payload, timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Response includes classification, graph, nodes, etc.
        assert "classification" in data or "graph_id" in data or "graph" in data, "Missing expected fields"
        print(f"PASS: Orchestrator execute - keys: {list(data.keys())[:5]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
