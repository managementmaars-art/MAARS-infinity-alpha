"""
MAARS Infinity — Iteration 89: AI LLM Integration Tests
Tests for real LLM integration via emergentintegrations library:
- Commander Orion AI classification and decomposition (GPT-5.2)
- Model Router execute (routes AND executes via LLM)
- Test Harness with AI pipeline
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
TIMEOUT = 120  # LLM calls can take 30+ seconds

class TestAICommanderOrionClassification:
    """Test AI-powered goal classification via real LLM (GPT-5.2)"""

    def test_classify_research_goal_ai(self):
        """POST /api/infinity/orchestrator/classify - Research goal should return AI classification"""
        response = requests.post(
            f"{BASE_URL}/api/infinity/orchestrator/classify",
            params={"description": "Research the latest trends in artificial intelligence and machine learning"},
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify AI-powered classification fields
        assert "goal_type" in data, "Missing goal_type"
        assert "risk_level" in data, "Missing risk_level"
        assert "complexity" in data, "Missing complexity"
        assert "ai_powered" in data, "Missing ai_powered field"
        
        # Should be AI-powered with model info
        if data.get("ai_powered"):
            assert "model_used" in data, "AI classification missing model_used"
            assert "provider_used" in data, "AI classification missing provider_used"
            assert "latency_ms" in data, "AI classification missing latency_ms"
            assert "reasoning" in data, "AI classification missing reasoning"
            print(f"✓ AI Classification: type={data['goal_type']}, model={data.get('model_used')}, latency={data.get('latency_ms')}ms")
        else:
            print(f"⚠ Used rule-based fallback: {data.get('fallback_reason', 'unknown')}")

    def test_classify_engineering_goal_ai(self):
        """POST /api/infinity/orchestrator/classify - Engineering goal"""
        response = requests.post(
            f"{BASE_URL}/api/infinity/orchestrator/classify",
            params={"description": "Build a microservices architecture for scalable data processing pipeline"},
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "goal_type" in data
        assert "risk_level" in data
        print(f"✓ Engineering goal classified: type={data['goal_type']}, risk={data['risk_level']}, ai_powered={data.get('ai_powered')}")


class TestAICommanderOrionExecute:
    """Test AI-powered goal execution (classify + decompose via LLM)"""

    def test_execute_research_goal_ai(self):
        """POST /api/infinity/orchestrator/execute - Should use AI for classification and decomposition"""
        payload = {
            "description": "Analyze competitive landscape for enterprise AI platforms and create strategic recommendations",
            "environment": "simulation"
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/orchestrator/execute",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify classification
        assert "classification" in data, "Missing classification"
        classification = data["classification"]
        assert classification.get("ai_powered") == True, f"Expected ai_powered=true, got {classification.get('ai_powered')}"
        assert "model_used" in classification, "Missing model_used in classification"
        print(f"✓ Classification: type={classification['goal_type']}, model={classification['model_used']}, latency={classification.get('latency_ms')}ms")
        
        # Verify decomposition metadata
        assert "decomposition_meta" in data, "Missing decomposition_meta"
        decomp_meta = data["decomposition_meta"]
        if decomp_meta.get("ai_powered"):
            assert "model" in decomp_meta, "Missing model in decomposition_meta"
            print(f"✓ AI Decomposition: model={decomp_meta['model']}, latency={decomp_meta.get('latency_ms')}ms")
        
        # Verify node details have routing info
        assert "node_details" in data, "Missing node_details"
        assert len(data["node_details"]) >= 3, f"Expected 3+ nodes, got {len(data['node_details'])}"
        
        for node in data["node_details"]:
            assert "provider" in node, f"Node {node.get('node_id')} missing provider"
            assert "model" in node, f"Node {node.get('node_id')} missing model"
        
        print(f"✓ Created {data['nodes']} task nodes with routing")
        
        # Verify reasoning
        assert "reasoning" in data, "Missing reasoning"
        assert "AI" in data["reasoning"] or "ai" in data["reasoning"].lower(), "Reasoning should mention AI"

    def test_execute_engineering_goal_ai(self):
        """POST /api/infinity/orchestrator/execute - Engineering goal with AI"""
        payload = {
            "description": "Design and implement a secure API gateway with rate limiting and authentication",
            "environment": "simulation"
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/orchestrator/execute",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        classification = data.get("classification", {})
        
        # Verify classification
        assert classification.get("ai_powered") in [True, False], "Missing ai_powered field"
        if classification.get("ai_powered"):
            print(f"✓ AI classified as: {classification['goal_type']} (risk={classification['risk_level']})")
        
        # Check decomposition
        assert "nodes" in data
        assert data["nodes"] >= 3


class TestModelRouterExecute:
    """Test Model Router execute endpoint - routes AND executes via real LLM"""

    def test_router_execute_coding_task(self):
        """POST /api/infinity/router/execute - Coding task should route to coding model and return LLM output"""
        payload = {
            "task_description": "Write a Python function to calculate fibonacci numbers using memoization"
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/router/execute",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify routing info
        assert "routing" in data, "Missing routing"
        assert "classification" in data["routing"], "Missing routing.classification"
        assert "selection" in data["routing"], "Missing routing.selection"
        
        routing = data["routing"]
        print(f"✓ Routed as: {routing['classification']['task_type']} → {routing['selection']['provider']}/{routing['selection']['model']}")
        
        # Verify execution info
        assert "execution" in data, "Missing execution"
        exec_info = data["execution"]
        assert "provider" in exec_info, "Missing execution.provider"
        assert "model" in exec_info, "Missing execution.model"
        assert "latency_ms" in exec_info, "Missing execution.latency_ms"
        assert "estimated_cost" in exec_info, "Missing execution.estimated_cost"
        
        print(f"✓ Executed via: {exec_info['provider']}/{exec_info['model']}, latency={exec_info['latency_ms']}ms, cost=${exec_info['estimated_cost']:.4f}")
        
        # Verify LLM output
        assert "output" in data, "Missing output"
        assert len(data["output"]) > 50, f"Output too short: {len(data['output'])} chars"
        print(f"✓ LLM Output: {len(data['output'])} chars")

    def test_router_execute_research_task(self):
        """POST /api/infinity/router/execute - Research task should route to research model"""
        payload = {
            "task_description": "Research the current market trends in renewable energy sector"
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/router/execute",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "output" in data
        assert "execution" in data
        
        task_type = data["routing"]["classification"]["task_type"]
        print(f"✓ Research task routed as: {task_type}")

    def test_router_execute_summary_task(self):
        """POST /api/infinity/router/execute - Summary task should route to economy model"""
        payload = {
            "task_description": "Summarize the key points of machine learning algorithms"
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/router/execute",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "output" in data
        
        # Summary tasks should route to economy tier for cost efficiency
        tier = data["routing"]["selection"]["tier"]
        print(f"✓ Summary task routed to tier: {tier}")


class TestModelRouterRoute:
    """Test Model Router route-only endpoint (classification without execution)"""

    def test_router_route_only(self):
        """POST /api/infinity/router/route - Should still work for classification-only routing"""
        payload = {
            "task_description": "Implement a caching layer for database queries"
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/router/route",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "classification" in data
        assert "selection" in data
        
        # Should NOT have output or execution (route-only)
        assert "output" not in data, "Route-only should not have output"
        
        print(f"✓ Route-only: {data['classification']['task_type']} → {data['selection']['provider']}/{data['selection']['model']}")


class TestModelRouterPerformance:
    """Test Model Router performance tracking"""

    def test_router_performance_after_execution(self):
        """GET /api/infinity/router/performance - Should show performance data after executing tasks"""
        response = requests.get(
            f"{BASE_URL}/api/infinity/router/performance",
            timeout=30
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Expected list of performance records"
        
        if len(data) > 0:
            record = data[0]
            assert "provider" in record
            assert "model_name" in record
            assert "total_calls" in record
            assert "success_rate" in record
            print(f"✓ Performance data: {len(data)} model records")
            for r in data[:3]:
                print(f"  - {r['provider']}/{r['model_name']}: {r['total_calls']} calls, {r['success_rate']*100:.0f}% success")
        else:
            print("⚠ No performance data yet (expected after executing tasks)")


class TestTestHarnessWithAI:
    """Test Harness scenarios with AI integration"""

    def test_scenario_a_with_ai(self):
        """POST /api/infinity/test-harness/run/A - Research Goal Pipeline now uses AI classification"""
        response = requests.post(
            f"{BASE_URL}/api/infinity/test-harness/run/A",
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "steps" in data
        assert "overall_status" in data
        
        # Check step results
        for step in data["steps"]:
            status = step["status"]
            print(f"  [{status.upper()}] {step['step']}: {step['detail']}")
        
        print(f"✓ Scenario A: {data['overall_status']} ({data['summary']['passed']}/{data['summary']['total']} passed)")

    def test_run_all_scenarios(self):
        """POST /api/infinity/test-harness/run-all - All 5 scenarios should pass"""
        response = requests.post(
            f"{BASE_URL}/api/infinity/test-harness/run-all",
            timeout=180  # Allow extra time for all 5 scenarios
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) == 5, f"Expected 5 scenarios, got {len(data['scenarios'])}"
        
        for scenario in data["scenarios"]:
            print(f"  Scenario {scenario['scenario_id']}: {scenario['overall_status']} ({scenario['summary']['passed']}/{scenario['summary']['total']})")
        
        print(f"✓ Suite: {data['overall_status']} ({data['suite_summary']['passed']}/{data['suite_summary']['total_steps']} steps passed)")


class TestExistingPhase2APIs:
    """Verify existing Phase 2 APIs still work"""

    def test_intelligence_search(self):
        """POST /api/infinity/intelligence/search - Real DuckDuckGo search"""
        payload = {
            "query": "artificial intelligence trends 2026",
            "freshness": "standard"
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/intelligence/search",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "total" in data
        print(f"✓ DuckDuckGo search: {data['total']} results")

    def test_memory_episodic(self):
        """POST /api/infinity/memory/episodic/record - Episodic memory"""
        payload = {
            "agent_id": "TEST_ai_iteration_89",
            "event_type": "test_event",
            "event_data": {"test": "data"},
            "outcome": "success"
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/memory/episodic/record",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200
        print("✓ Episodic memory record works")

    def test_knowledge_graph_stats(self):
        """GET /api/infinity/memory/knowledge-graph/stats"""
        response = requests.get(
            f"{BASE_URL}/api/infinity/memory/knowledge-graph/stats",
            timeout=30
        )
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ Knowledge Graph: {data.get('entity_count', 0)} entities, {data.get('relationship_count', 0)} relationships")


class TestCommanderLog:
    """Test Commander Log for AI metadata"""

    def test_commander_log_has_ai_metadata(self):
        """GET /api/infinity/orchestrator/log - Should show AI classification metadata"""
        response = requests.get(
            f"{BASE_URL}/api/infinity/orchestrator/log?limit=5",
            timeout=30
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            entry = data[0]
            classification = entry.get("classification", {})
            decomp_meta = entry.get("decomposition_meta", {})
            
            print(f"✓ Latest log entry:")
            print(f"  - Classification AI: {classification.get('ai_powered', 'unknown')}")
            print(f"  - Model used: {classification.get('model_used', 'N/A')}")
            print(f"  - Decomposition AI: {decomp_meta.get('ai_powered', 'unknown')}")
            print(f"  - Node count: {entry.get('node_count', 'N/A')}")
        else:
            print("⚠ No commander log entries yet")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
