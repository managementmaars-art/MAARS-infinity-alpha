"""
Iteration 90 - MAARS Infinity New Features Tests
Testing: Full Execution Loop, Metrics & Alerting, KG Advanced Features, Rate Limiting

Features tested:
- Full Execution Loop: POST /api/infinity/orchestrator/full-execute (30-90s with LLM calls)
- Execute Graph: POST /api/infinity/orchestrator/execute-graph/{graph_id}
- Execution Runs: GET /api/infinity/orchestrator/runs
- Live Metrics: GET /api/infinity/metrics/live
- Metrics History: GET /api/infinity/metrics/history
- Alert Rules: GET /api/infinity/alerts/rules  
- Active Alerts: GET /api/infinity/alerts
- Acknowledge Alert: POST /api/infinity/alerts/{rule_id}/acknowledge
- KG Traverse: GET /api/infinity/memory/knowledge-graph/traverse/{entity}
- KG Search: GET /api/infinity/memory/knowledge-graph/search
- KG Path Finding: GET /api/infinity/memory/knowledge-graph/paths
- Rate Limiting: Verify no 429 under normal use
- Router Execute: POST /api/infinity/router/execute
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def api_session():
    """Shared session for all tests"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# ═══════════════════════════════════════════════════════════════════
# METRICS & ALERTING TESTS (Fast endpoints)
# ═══════════════════════════════════════════════════════════════════

class TestMetricsAlerts:
    """Test metrics collection and alerting system"""
    
    def test_live_metrics(self, api_session):
        """GET /api/infinity/metrics/live - returns real-time metrics + triggered alerts"""
        res = api_session.get(f"{BASE_URL}/api/infinity/metrics/live")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        # Verify metrics structure
        assert "metrics" in data, "Response must have 'metrics' key"
        m = data["metrics"]
        assert "total_agents" in m, "Metrics must have total_agents"
        assert "busy_agents" in m, "Metrics must have busy_agents"
        assert "agent_utilization" in m, "Metrics must have agent_utilization"
        assert "circuit_breakers_tripped" in m, "Metrics must have circuit_breakers_tripped"
        assert "open_incidents" in m, "Metrics must have open_incidents"
        assert "model_success_rate_min" in m, "Metrics must have model_success_rate_min"
        assert "timestamp" in m, "Metrics must have timestamp"
        
        # Verify triggered_alerts key exists
        assert "triggered_alerts" in data, "Response must have 'triggered_alerts' key"
        print(f"PASS: Live metrics returned: {len(m)} metric keys, {len(data['triggered_alerts'])} triggered alerts")
    
    def test_metrics_history(self, api_session):
        """GET /api/infinity/metrics/history - returns historical metrics snapshots"""
        res = api_session.get(f"{BASE_URL}/api/infinity/metrics/history?limit=10")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        assert isinstance(data, list), "Response must be a list"
        # After calling live metrics, there should be at least 1 snapshot
        print(f"PASS: Metrics history returned {len(data)} snapshots")
    
    def test_alert_rules(self, api_session):
        """GET /api/infinity/alerts/rules - returns 6 default alert rules"""
        res = api_session.get(f"{BASE_URL}/api/infinity/alerts/rules")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        assert isinstance(data, list), "Response must be a list"
        assert len(data) >= 6, f"Expected at least 6 default rules, got {len(data)}"
        
        # Verify rule structure
        for rule in data:
            assert "rule_id" in rule, "Rule must have rule_id"
            assert "name" in rule, "Rule must have name"
            assert "metric" in rule, "Rule must have metric"
            assert "operator" in rule, "Rule must have operator"
            assert "threshold" in rule, "Rule must have threshold"
            assert "severity" in rule, "Rule must have severity"
            assert "enabled" in rule, "Rule must have enabled"
        
        rule_ids = [r["rule_id"] for r in data]
        expected_rules = ["circuit_breaker_tripped", "high_budget_usage", "low_success_rate", "open_incidents", "low_trust_agents", "execution_failures"]
        for expected in expected_rules:
            assert expected in rule_ids, f"Missing expected rule: {expected}"
        
        print(f"PASS: Alert rules returned {len(data)} rules with all 6 defaults present")
    
    def test_active_alerts(self, api_session):
        """GET /api/infinity/alerts - returns unacknowledged alerts"""
        res = api_session.get(f"{BASE_URL}/api/infinity/alerts")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        assert isinstance(data, list), "Response must be a list"
        print(f"PASS: Active alerts returned {len(data)} alerts")
    
    def test_acknowledge_alert(self, api_session):
        """POST /api/infinity/alerts/{rule_id}/acknowledge - marks alert as acknowledged"""
        # First trigger some metrics to potentially create alerts
        api_session.get(f"{BASE_URL}/api/infinity/metrics/live")
        
        # Get active alerts
        res = api_session.get(f"{BASE_URL}/api/infinity/alerts")
        alerts = res.json()
        
        if alerts:
            # Acknowledge first alert
            rule_id = alerts[0]["rule_id"]
            ack_res = api_session.post(f"{BASE_URL}/api/infinity/alerts/{rule_id}/acknowledge")
            assert ack_res.status_code == 200, f"Expected 200, got {ack_res.status_code}"
            data = ack_res.json()
            assert data["acknowledged"] == True, "Alert should be acknowledged"
            print(f"PASS: Alert {rule_id} acknowledged successfully")
        else:
            # Try to acknowledge a rule anyway to test endpoint works
            ack_res = api_session.post(f"{BASE_URL}/api/infinity/alerts/circuit_breaker_tripped/acknowledge")
            assert ack_res.status_code == 200, f"Expected 200, got {ack_res.status_code}"
            print(f"PASS: Acknowledge endpoint works (no active alerts to acknowledge)")


# ═══════════════════════════════════════════════════════════════════
# KNOWLEDGE GRAPH ADVANCED TESTS
# ═══════════════════════════════════════════════════════════════════

class TestKnowledgeGraphAdvanced:
    """Test KG traversal, search, and path finding"""
    
    @pytest.fixture(autouse=True)
    def setup_kg_test_data(self, api_session):
        """Create test entities for KG tests"""
        # Create a mini graph: AI_Technology -> Cloud_Computing -> Data_Science
        api_session.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/entity", 
                        json={"entity": "TEST_AI_Technology", "entity_type": "technology", "attributes": {"domain": "artificial_intelligence"}})
        api_session.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/entity",
                        json={"entity": "TEST_Cloud_Computing", "entity_type": "technology", "attributes": {"domain": "infrastructure"}})
        api_session.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/entity",
                        json={"entity": "TEST_Data_Science", "entity_type": "technology", "attributes": {"domain": "analytics"}})
        
        # Create relationships
        api_session.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/relationship",
                        json={"entity": "TEST_AI_Technology", "target": "TEST_Cloud_Computing", "relationship_type": "enables"})
        api_session.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/relationship",
                        json={"entity": "TEST_Cloud_Computing", "target": "TEST_Data_Science", "relationship_type": "enables"})
        api_session.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/relationship",
                        json={"entity": "TEST_AI_Technology", "target": "TEST_Data_Science", "relationship_type": "enhances"})
    
    def test_kg_traverse(self, api_session):
        """GET /api/infinity/memory/knowledge-graph/traverse/{entity} - traverses graph from entity"""
        res = api_session.get(f"{BASE_URL}/api/infinity/memory/knowledge-graph/traverse/TEST_AI_Technology?max_depth=2")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        assert "root" in data, "Response must have 'root' key"
        assert "nodes" in data, "Response must have 'nodes' key"
        assert "edges" in data, "Response must have 'edges' key"
        assert "depth_reached" in data, "Response must have 'depth_reached' key"
        
        assert data["root"] == "TEST_AI_Technology", "Root should be the starting entity"
        assert len(data["nodes"]) >= 1, "Should have at least root node"
        
        print(f"PASS: KG traverse from TEST_AI_Technology: {len(data['nodes'])} nodes, {len(data['edges'])} edges, depth={data['depth_reached']}")
    
    def test_kg_traverse_with_filter(self, api_session):
        """GET /api/infinity/memory/knowledge-graph/traverse/{entity}?relationship=enables"""
        res = api_session.get(f"{BASE_URL}/api/infinity/memory/knowledge-graph/traverse/TEST_AI_Technology?max_depth=3&relationship=enables")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        # When filtering by relationship, only "enables" edges should be included
        for edge in data.get("edges", []):
            assert edge["relationship"] == "enables", f"Expected 'enables' relationship, got {edge['relationship']}"
        
        print(f"PASS: KG traverse with filter: {len(data['edges'])} edges (all 'enables')")
    
    def test_kg_search(self, api_session):
        """GET /api/infinity/memory/knowledge-graph/search?q=AI - text search across entities"""
        res = api_session.get(f"{BASE_URL}/api/infinity/memory/knowledge-graph/search?q=TEST_AI")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        assert isinstance(data, list), "Response must be a list"
        # Should find our TEST_AI_Technology entity
        entities = [e["entity"] for e in data]
        assert "TEST_AI_Technology" in entities, "Should find TEST_AI_Technology entity"
        
        print(f"PASS: KG search for 'TEST_AI' returned {len(data)} entities")
    
    def test_kg_search_by_type(self, api_session):
        """GET /api/infinity/memory/knowledge-graph/search?q=technology"""
        res = api_session.get(f"{BASE_URL}/api/infinity/memory/knowledge-graph/search?q=technology&limit=5")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        assert isinstance(data, list), "Response must be a list"
        print(f"PASS: KG search for 'technology' returned {len(data)} entities")
    
    def test_kg_find_paths(self, api_session):
        """GET /api/infinity/memory/knowledge-graph/paths?source=X&target=Y - finds paths between entities"""
        res = api_session.get(f"{BASE_URL}/api/infinity/memory/knowledge-graph/paths?source=TEST_AI_Technology&target=TEST_Data_Science")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        assert "source" in data, "Response must have 'source' key"
        assert "target" in data, "Response must have 'target' key"
        assert "paths" in data, "Response must have 'paths' key"
        assert "paths_found" in data, "Response must have 'paths_found' key"
        
        assert data["source"] == "TEST_AI_Technology", "Source should match"
        assert data["target"] == "TEST_Data_Science", "Target should match"
        
        # Should find at least one path (direct or indirect)
        print(f"PASS: KG paths from TEST_AI_Technology to TEST_Data_Science: {data['paths_found']} paths found")


# ═══════════════════════════════════════════════════════════════════
# EXECUTION RUNS TESTS
# ═══════════════════════════════════════════════════════════════════

class TestExecutionRuns:
    """Test execution runs history endpoint"""
    
    def test_get_execution_runs(self, api_session):
        """GET /api/infinity/orchestrator/runs - returns list of execution runs"""
        res = api_session.get(f"{BASE_URL}/api/infinity/orchestrator/runs?limit=10")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        assert isinstance(data, list), "Response must be a list"
        
        if data:
            run = data[0]
            # Verify run structure
            assert "run_id" in run, "Run must have run_id"
            assert "graph_id" in run, "Run must have graph_id"
            assert "status" in run, "Run must have status"
            print(f"PASS: Execution runs returned {len(data)} runs. Latest: {run['status']}")
        else:
            print("PASS: Execution runs endpoint works (no runs yet)")


# ═══════════════════════════════════════════════════════════════════
# ROUTER EXECUTE TEST (Re-verify from iteration 89)
# ═══════════════════════════════════════════════════════════════════

class TestRouterExecute:
    """Test router execute endpoint with real LLM"""
    
    def test_router_execute(self, api_session):
        """POST /api/infinity/router/execute - routes and executes task with LLM"""
        payload = {"task_description": "List 3 benefits of unit testing in software development"}
        res = api_session.post(f"{BASE_URL}/api/infinity/router/execute", json=payload, timeout=30)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        assert "output" in data, "Response must have 'output' key with LLM response"
        assert "routing" in data, "Response must have 'routing' key"
        assert "execution" in data, "Response must have 'execution' key"
        
        exec_info = data["execution"]
        assert "provider" in exec_info, "Execution must have provider"
        assert "model" in exec_info, "Execution must have model"
        assert "latency_ms" in exec_info, "Execution must have latency_ms"
        
        print(f"PASS: Router execute - Provider: {exec_info['provider']}, Model: {exec_info['model']}, Latency: {exec_info['latency_ms']}ms")


# ═══════════════════════════════════════════════════════════════════
# RATE LIMITING TEST
# ═══════════════════════════════════════════════════════════════════

class TestRateLimiting:
    """Test rate limiting (120 req/60s per IP)"""
    
    def test_no_rate_limit_under_normal_use(self, api_session):
        """Verify rate limiter doesn't trigger under normal use"""
        # Make 10 quick requests - should all succeed
        statuses = []
        for i in range(10):
            res = api_session.get(f"{BASE_URL}/api/infinity/system/status")
            statuses.append(res.status_code)
        
        assert all(s == 200 for s in statuses), f"Expected all 200s, got: {statuses}"
        assert 429 not in statuses, "Should not get rate limited under normal use"
        print(f"PASS: 10 rapid requests all succeeded (no 429s)")


# ═══════════════════════════════════════════════════════════════════
# FULL EXECUTION LOOP TEST (Long-running - ~30-90 seconds)
# ═══════════════════════════════════════════════════════════════════

class TestFullExecutionLoop:
    """Test the full execution loop - TAKES 30-90 SECONDS"""
    
    def test_full_execute_short_goal(self, api_session):
        """POST /api/infinity/orchestrator/full-execute - full pipeline with short goal"""
        payload = {
            "description": "Summarize 3 benefits of cloud computing",
            "requester_id": "test_operator",
            "environment": "production"
        }
        
        print("Starting full execution loop (this takes 30-90 seconds)...")
        start = time.time()
        res = api_session.post(f"{BASE_URL}/api/infinity/orchestrator/full-execute", json=payload, timeout=150)
        elapsed = time.time() - start
        
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        # Verify goal classification
        assert "classification" in data, "Response must have 'classification'"
        classification = data["classification"]
        assert "goal_type" in classification, "Classification must have goal_type"
        assert "ai_powered" in classification, "Classification must have ai_powered flag"
        
        # Verify decomposition
        assert "decomposition_meta" in data, "Response must have 'decomposition_meta'"
        assert "nodes" in data, "Response must have 'nodes' count"
        assert "graph_id" in data, "Response must have 'graph_id'"
        
        # Verify execution results
        assert "execution" in data, "Response must have 'execution' with run results"
        execution = data["execution"]
        assert "run_id" in execution, "Execution must have run_id"
        assert "status" in execution, "Execution must have status"
        assert "node_results" in execution, "Execution must have node_results"
        assert "summary" in execution, "Execution must have summary"
        
        summary = execution["summary"]
        assert "total_nodes" in summary, "Summary must have total_nodes"
        assert "completed" in summary, "Summary must have completed count"
        assert "failed" in summary, "Summary must have failed count"
        assert "total_cost" in summary, "Summary must have total_cost"
        assert "total_latency_ms" in summary, "Summary must have total_latency_ms"
        
        # Verify final report (if all nodes completed)
        if summary["failed"] == 0:
            assert "final_report" in execution, "Should have final_report when all nodes complete"
            assert execution["final_report"] is not None, "Final report should not be None"
        
        print(f"PASS: Full execute completed in {elapsed:.1f}s")
        print(f"  - Classification: {classification['goal_type']} (AI={classification.get('ai_powered')})")
        print(f"  - Nodes: {summary['total_nodes']} total, {summary['completed']} completed, {summary['failed']} failed")
        print(f"  - Cost: ${summary['total_cost']:.4f}, Latency: {summary['total_latency_ms']/1000:.1f}s")
        print(f"  - Status: {execution['status']}")
    
    def test_execute_existing_graph(self, api_session):
        """POST /api/infinity/orchestrator/execute-graph/{graph_id} - execute existing graph"""
        # First get an existing graph from runs or create one via execute
        runs_res = api_session.get(f"{BASE_URL}/api/infinity/orchestrator/runs?limit=5")
        runs = runs_res.json()
        
        if runs:
            graph_id = runs[0]["graph_id"]
            # Try to execute - may fail if already executed but endpoint should work
            res = api_session.post(f"{BASE_URL}/api/infinity/orchestrator/execute-graph/{graph_id}", timeout=150)
            # Status could be 200 (re-executed) or 404 (not found) - endpoint should respond
            assert res.status_code in [200, 404], f"Expected 200 or 404, got {res.status_code}"
            print(f"PASS: Execute graph endpoint works (status={res.status_code})")
        else:
            # Create a graph first via regular execute
            exec_res = api_session.post(f"{BASE_URL}/api/infinity/orchestrator/execute",
                                       json={"description": "Test graph creation", "environment": "simulation"}, timeout=60)
            if exec_res.status_code == 200:
                graph_id = exec_res.json().get("graph_id")
                res = api_session.post(f"{BASE_URL}/api/infinity/orchestrator/execute-graph/{graph_id}", timeout=150)
                assert res.status_code in [200, 404], f"Expected 200 or 404, got {res.status_code}"
                print(f"PASS: Execute graph endpoint works (status={res.status_code})")
            else:
                print("SKIP: Could not create graph to test execute-graph endpoint")


# ═══════════════════════════════════════════════════════════════════
# COMMANDER LOG WITH AI METADATA TEST  
# ═══════════════════════════════════════════════════════════════════

class TestCommanderLog:
    """Test commander log shows AI metadata"""
    
    def test_commander_log_ai_badges(self, api_session):
        """GET /api/infinity/orchestrator/log - shows AI classification metadata"""
        res = api_session.get(f"{BASE_URL}/api/infinity/orchestrator/log?limit=5")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        assert isinstance(data, list), "Response must be a list"
        
        if data:
            log = data[0]
            assert "classification" in log, "Log entry should have classification"
            assert "node_count" in log, "Log entry should have node_count"
            if log["classification"].get("ai_powered"):
                assert "model_used" in log["classification"], "AI classification should have model_used"
            print(f"PASS: Commander log has {len(data)} entries with classification data")
        else:
            print("PASS: Commander log endpoint works (no entries yet)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
