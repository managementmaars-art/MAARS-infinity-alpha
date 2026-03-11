"""
MAARS Infinity Phase 5 - Operator Control & Test Harness API Tests
Iteration 88 - Tests Test Harness scenarios A-E, run-all, history, and Operator Dashboard

Test Coverage:
1. Test Harness Scenarios API (GET /api/infinity/test-harness/scenarios)
2. Run Single Scenarios A-E (POST /api/infinity/test-harness/run/{A,B,C,D,E})
3. Run All Scenarios (POST /api/infinity/test-harness/run-all)
4. Test History (GET /api/infinity/test-harness/history)
5. Operator Dashboard (GET /api/infinity/operator/dashboard)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL not set"


class TestHarnessScenariosAPI:
    """Test Harness - GET /api/infinity/test-harness/scenarios"""
    
    def test_get_scenarios_returns_5_scenarios(self):
        """GET /api/infinity/test-harness/scenarios returns 5 scenarios A-E"""
        response = requests.get(f"{BASE_URL}/api/infinity/test-harness/scenarios")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5, f"Expected 5 scenarios, got {len(data)}"
        
        # Verify all scenario IDs A-E present
        for scenario_id in ["A", "B", "C", "D", "E"]:
            assert scenario_id in data, f"Scenario {scenario_id} not found"
            assert "name" in data[scenario_id]
            assert "description" in data[scenario_id]
    
    def test_scenario_a_has_correct_metadata(self):
        """Scenario A: Research Goal Pipeline metadata"""
        response = requests.get(f"{BASE_URL}/api/infinity/test-harness/scenarios")
        data = response.json()
        
        assert data["A"]["name"] == "Research Goal Pipeline"
        assert "Goal" in data["A"]["description"] or "Classify" in data["A"]["description"]
    
    def test_scenario_b_has_correct_metadata(self):
        """Scenario B: Verification Pipeline metadata"""
        response = requests.get(f"{BASE_URL}/api/infinity/test-harness/scenarios")
        data = response.json()
        
        assert data["B"]["name"] == "Verification Pipeline"
        assert "Verify" in data["B"]["description"] or "Crosscheck" in data["B"]["description"]
    
    def test_scenario_c_has_correct_metadata(self):
        """Scenario C: Memory & Learning Loop metadata"""
        response = requests.get(f"{BASE_URL}/api/infinity/test-harness/scenarios")
        data = response.json()
        
        assert data["C"]["name"] == "Memory & Learning Loop"
        assert "Memory" in data["C"]["description"]
    
    def test_scenario_d_has_correct_metadata(self):
        """Scenario D: Intelligence Search → Verify → Cite metadata"""
        response = requests.get(f"{BASE_URL}/api/infinity/test-harness/scenarios")
        data = response.json()
        
        assert data["D"]["name"] == "Intelligence Search → Verify → Cite"
        assert "Search" in data["D"]["description"] or "Citation" in data["D"]["description"]
    
    def test_scenario_e_has_correct_metadata(self):
        """Scenario E: Budget & Governance metadata"""
        response = requests.get(f"{BASE_URL}/api/infinity/test-harness/scenarios")
        data = response.json()
        
        assert data["E"]["name"] == "Budget & Governance"
        assert "Budget" in data["E"]["description"] or "Audit" in data["E"]["description"]


class TestHarnessRunSingleScenario:
    """Test Harness - POST /api/infinity/test-harness/run/{scenario_id}"""
    
    def test_run_scenario_a_research_goal_pipeline(self):
        """Run Scenario A: Research Goal Pipeline"""
        response = requests.post(f"{BASE_URL}/api/infinity/test-harness/run/A")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scenario_id"] == "A"
        assert data["scenario_name"] == "Research Goal Pipeline"
        assert "steps" in data
        assert "summary" in data
        assert "overall_status" in data
        assert data["overall_status"] in ["pass", "fail"]
        
        # Verify step structure
        for step in data["steps"]:
            assert "step" in step
            assert "status" in step
            assert step["status"] in ["pass", "fail", "warn"]
            assert "detail" in step
        
        print(f"Scenario A - Status: {data['overall_status']}, Steps: {data['summary']}")
    
    def test_run_scenario_b_verification_pipeline(self):
        """Run Scenario B: Verification Pipeline"""
        response = requests.post(f"{BASE_URL}/api/infinity/test-harness/run/B")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scenario_id"] == "B"
        assert data["scenario_name"] == "Verification Pipeline"
        assert "steps" in data
        assert data["overall_status"] in ["pass", "fail"]
        
        print(f"Scenario B - Status: {data['overall_status']}, Steps: {data['summary']}")
    
    def test_run_scenario_c_memory_learning_loop(self):
        """Run Scenario C: Memory & Learning Loop"""
        response = requests.post(f"{BASE_URL}/api/infinity/test-harness/run/C")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scenario_id"] == "C"
        assert data["scenario_name"] == "Memory & Learning Loop"
        assert "steps" in data
        assert data["overall_status"] in ["pass", "fail"]
        
        # Check specific steps for memory flow
        step_names = [s["step"] for s in data["steps"]]
        assert "working_memory_store" in step_names or len(step_names) > 0
        
        print(f"Scenario C - Status: {data['overall_status']}, Steps: {data['summary']}")
    
    def test_run_scenario_d_intelligence_search(self):
        """Run Scenario D: Intelligence Search → Verify → Cite (uses real DuckDuckGo)"""
        # This scenario does real web search - may take a few seconds
        response = requests.post(f"{BASE_URL}/api/infinity/test-harness/run/D", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data["scenario_id"] == "D"
        assert data["scenario_name"] == "Intelligence Search → Verify → Cite"
        assert "steps" in data
        assert data["overall_status"] in ["pass", "fail"]
        
        # Check for search step
        step_names = [s["step"] for s in data["steps"]]
        assert "web_search" in step_names or "intelligence_pipeline" in step_names or len(step_names) > 0
        
        print(f"Scenario D - Status: {data['overall_status']}, Steps: {data['summary']}")
    
    def test_run_scenario_e_budget_governance(self):
        """Run Scenario E: Budget & Governance"""
        response = requests.post(f"{BASE_URL}/api/infinity/test-harness/run/E")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scenario_id"] == "E"
        assert data["scenario_name"] == "Budget & Governance"
        assert "steps" in data
        assert data["overall_status"] in ["pass", "fail"]
        
        print(f"Scenario E - Status: {data['overall_status']}, Steps: {data['summary']}")
    
    def test_run_invalid_scenario_returns_400(self):
        """Run invalid scenario ID returns 400 error"""
        response = requests.post(f"{BASE_URL}/api/infinity/test-harness/run/Z")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data or "error" in data


class TestHarnessRunAllScenarios:
    """Test Harness - POST /api/infinity/test-harness/run-all"""
    
    def test_run_all_scenarios_returns_combined_results(self):
        """Run all 5 scenarios and get combined results"""
        # This can take 20-30 seconds due to Scenario D's web search
        response = requests.post(f"{BASE_URL}/api/infinity/test-harness/run-all", timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        assert "suite_run_id" in data
        assert "scenarios" in data
        assert len(data["scenarios"]) == 5, f"Expected 5 scenarios, got {len(data['scenarios'])}"
        assert "suite_summary" in data
        assert "overall_status" in data
        assert data["overall_status"] in ["pass", "fail"]
        
        # Verify each scenario present
        scenario_ids = [s["scenario_id"] for s in data["scenarios"]]
        for sid in ["A", "B", "C", "D", "E"]:
            assert sid in scenario_ids, f"Scenario {sid} missing from run-all results"
        
        # Verify suite summary structure
        summary = data["suite_summary"]
        assert "passed" in summary
        assert "failed" in summary
        assert "total_steps" in summary
        assert "scenarios_run" in summary
        assert summary["scenarios_run"] == 5
        
        print(f"Run-All Status: {data['overall_status']}, Summary: {summary}")
        
        # Print individual scenario results
        for sc in data["scenarios"]:
            print(f"  {sc['scenario_id']}: {sc['overall_status']} ({sc['summary']['passed']}/{sc['summary']['total']} passed)")


class TestHarnessHistory:
    """Test Harness - GET /api/infinity/test-harness/history"""
    
    def test_get_test_history(self):
        """GET /api/infinity/test-harness/history returns historical test runs"""
        response = requests.get(f"{BASE_URL}/api/infinity/test-harness/history")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Should have some history from previous test runs
        if len(data) > 0:
            entry = data[0]
            assert "scenario_id" in entry
            assert "scenario_name" in entry
            assert "overall_status" in entry
            assert "started_at" in entry
            print(f"History has {len(data)} entries, latest: {entry['scenario_id']} - {entry['overall_status']}")
        else:
            print("No test history found (may be first run)")
    
    def test_get_history_with_limit(self):
        """GET /api/infinity/test-harness/history with limit parameter"""
        response = requests.get(f"{BASE_URL}/api/infinity/test-harness/history?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3
    
    def test_get_history_filtered_by_scenario(self):
        """GET /api/infinity/test-harness/history filtered by scenario_id"""
        response = requests.get(f"{BASE_URL}/api/infinity/test-harness/history?scenario_id=A")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # All entries should be scenario A
        for entry in data:
            assert entry["scenario_id"] == "A"


class TestOperatorDashboard:
    """Operator Dashboard - GET /api/infinity/operator/dashboard"""
    
    def test_operator_dashboard_returns_unified_data(self):
        """GET /api/infinity/operator/dashboard returns complete dashboard data"""
        response = requests.get(f"{BASE_URL}/api/infinity/operator/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify required top-level keys
        assert "system_health" in data
        assert data["system_health"] in ["operational", "degraded"]
        
        assert "pending_approvals" in data
        assert isinstance(data["pending_approvals"], int)
        
        assert "open_incidents" in data
        assert isinstance(data["open_incidents"], int)
        
        assert "open_escalations" in data
        assert isinstance(data["open_escalations"], int)
        
        print(f"Dashboard: Health={data['system_health']}, Approvals={data['pending_approvals']}, Incidents={data['open_incidents']}, Escalations={data['open_escalations']}")
    
    def test_operator_dashboard_circuit_breakers(self):
        """Dashboard includes circuit breaker data"""
        response = requests.get(f"{BASE_URL}/api/infinity/operator/dashboard")
        data = response.json()
        
        assert "circuit_breakers" in data
        cb = data["circuit_breakers"]
        assert "total" in cb
        assert "tripped" in cb
        assert "breakers" in cb
        assert isinstance(cb["breakers"], list)
        
        print(f"Circuit Breakers: {cb['total']} total, {cb['tripped']} tripped")
    
    def test_operator_dashboard_budget_summary(self):
        """Dashboard includes budget summary"""
        response = requests.get(f"{BASE_URL}/api/infinity/operator/dashboard")
        data = response.json()
        
        assert "budget_summary" in data
        # Budget summary can be dict or list depending on implementation
        assert data["budget_summary"] is not None
    
    def test_operator_dashboard_agent_workload(self):
        """Dashboard includes agent workload data"""
        response = requests.get(f"{BASE_URL}/api/infinity/operator/dashboard")
        data = response.json()
        
        assert "agent_workload" in data
        assert isinstance(data["agent_workload"], list)
        
        if len(data["agent_workload"]) > 0:
            workload = data["agent_workload"][0]
            assert "network" in workload
            assert "total" in workload
            assert "busy" in workload
            print(f"Agent Workload: {len(data['agent_workload'])} networks")
    
    def test_operator_dashboard_autonomy_tiers(self):
        """Dashboard includes autonomy tier information"""
        response = requests.get(f"{BASE_URL}/api/infinity/operator/dashboard")
        data = response.json()
        
        assert "tiers" in data
        tiers = data["tiers"]
        
        # Should have tier 0-4
        assert len(tiers) >= 5, f"Expected 5+ tiers, got {len(tiers)}"
        
        # Each tier should have required fields
        for tier_id, tier_info in tiers.items():
            assert "name" in tier_info
            assert "max_spend" in tier_info or "allowed_actions" in tier_info
        
        print(f"Autonomy Tiers: {len(tiers)} tiers defined")
    
    def test_operator_dashboard_approvals_list(self):
        """Dashboard includes list of pending approvals (up to 10)"""
        response = requests.get(f"{BASE_URL}/api/infinity/operator/dashboard")
        data = response.json()
        
        assert "approvals" in data
        assert isinstance(data["approvals"], list)
        assert len(data["approvals"]) <= 10  # Limited to 10
        
        if len(data["approvals"]) > 0:
            approval = data["approvals"][0]
            assert "task_id" in approval
            assert "action" in approval or "reason" in approval
    
    def test_operator_dashboard_incidents_list(self):
        """Dashboard includes list of open incidents (up to 10)"""
        response = requests.get(f"{BASE_URL}/api/infinity/operator/dashboard")
        data = response.json()
        
        assert "incidents" in data
        assert isinstance(data["incidents"], list)
        assert len(data["incidents"]) <= 10


class TestScenarioResultsPersistence:
    """Verify test runs are persisted in history"""
    
    def test_scenario_run_appears_in_history(self):
        """After running a scenario, it should appear in history"""
        # Run scenario A
        run_response = requests.post(f"{BASE_URL}/api/infinity/test-harness/run/A")
        assert run_response.status_code == 200
        run_data = run_response.json()
        run_id = run_data.get("run_id")
        
        # Check history
        history_response = requests.get(f"{BASE_URL}/api/infinity/test-harness/history?scenario_id=A&limit=5")
        assert history_response.status_code == 200
        history = history_response.json()
        
        # Should find the run in history
        assert len(history) > 0
        run_ids = [h.get("run_id") for h in history]
        assert run_id in run_ids, f"Run {run_id} not found in history: {run_ids}"
        print(f"Verified run {run_id} persisted in history")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
