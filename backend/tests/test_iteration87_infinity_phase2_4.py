"""
MAARS Infinity Phase 2-4 Backend API Tests
Tests: Working Memory, Episodic Memory, Knowledge Graph, Intelligence Search (DuckDuckGo),
Intelligence Monitors, Citations, Tool Registry, System Status, Commander Orion, Venture Portfolio
"""

import pytest
import requests
import os
import time
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')
assert BASE_URL, "REACT_APP_BACKEND_URL environment variable must be set"
BASE_URL = BASE_URL.rstrip('/')


class TestSystemStatus:
    """Phase 1: System Status endpoint"""
    
    def test_system_status_returns_200(self):
        """GET /api/infinity/system/status should return 200"""
        response = requests.get(f"{BASE_URL}/api/infinity/system/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "status" in data
        assert data["status"] in ["operational", "degraded"]
        print(f"System Status: {data['status']}")
    
    def test_system_status_contains_metrics(self):
        """System status should contain core metrics"""
        response = requests.get(f"{BASE_URL}/api/infinity/system/status")
        data = response.json()
        assert "total_agents" in data
        assert "agent_networks" in data
        assert "active_workflows" in data
        assert "circuit_breakers_tripped" in data
        print(f"Agents: {data['total_agents']}, Networks: {data['agent_networks']}")


class TestWorkingMemory:
    """Phase 2: Working Memory CRUD APIs"""
    
    def test_store_working_memory(self):
        """POST /api/infinity/memory/working/store - Store working memory"""
        test_task_id = f"TEST_wm_{int(time.time())}"
        payload = {
            "task_id": test_task_id,
            "agent_id": "TEST_agent_1",
            "context": {"goal": "Test memory storage", "priority": "high"},
            "intermediate_results": [{"step": 1, "result": "initialized"}]
        }
        response = requests.post(f"{BASE_URL}/api/infinity/memory/working/store", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["task_id"] == test_task_id
        assert data["status"] == "stored"
        print(f"Working memory stored: {data}")
        return test_task_id
    
    def test_get_working_memory(self):
        """GET /api/infinity/memory/working/{task_id} - Retrieve working memory"""
        # First store some memory
        test_task_id = f"TEST_wm_get_{int(time.time())}"
        store_payload = {
            "task_id": test_task_id,
            "agent_id": "TEST_agent_get",
            "context": {"operation": "retrieval_test"},
        }
        requests.post(f"{BASE_URL}/api/infinity/memory/working/store", json=store_payload)
        
        # Now retrieve it
        response = requests.get(f"{BASE_URL}/api/infinity/memory/working/{test_task_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["task_id"] == test_task_id
        print(f"Retrieved working memory: {len(data)} entries")
    
    def test_append_result_to_working_memory(self):
        """POST /api/infinity/memory/working/append - Append result"""
        test_task_id = f"TEST_wm_append_{int(time.time())}"
        # First store
        requests.post(f"{BASE_URL}/api/infinity/memory/working/store", json={
            "task_id": test_task_id, "agent_id": "TEST_append_agent", "context": {"init": True}
        })
        
        # Append a result
        append_payload = {
            "task_id": test_task_id,
            "agent_id": "TEST_append_agent",
            "result": {"step": 2, "output": "test output", "metrics": {"accuracy": 0.95}}
        }
        response = requests.post(f"{BASE_URL}/api/infinity/memory/working/append", json=append_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["appended"] == True
        print(f"Appended result: {data}")
    
    def test_delete_working_memory(self):
        """DELETE /api/infinity/memory/working/{task_id} - Clear working memory"""
        test_task_id = f"TEST_wm_del_{int(time.time())}"
        # First store
        requests.post(f"{BASE_URL}/api/infinity/memory/working/store", json={
            "task_id": test_task_id, "agent_id": "TEST_del_agent", "context": {"to_delete": True}
        })
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/infinity/memory/working/{test_task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == test_task_id
        assert "cleared" in data
        print(f"Cleared working memory: {data}")


class TestEpisodicMemory:
    """Phase 2: Episodic Memory APIs"""
    
    def test_record_episode(self):
        """POST /api/infinity/memory/episodic/record - Record an episode"""
        payload = {
            "agent_id": f"TEST_ep_agent_{int(time.time())}",
            "event_type": "task_completion",
            "event_data": {"task": "unit_test", "duration_ms": 1500},
            "outcome": "success",
            "lessons_learned": "Unit tests are important for reliability"
        }
        response = requests.post(f"{BASE_URL}/api/infinity/memory/episodic/record", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == payload["agent_id"]
        assert data["event_type"] == "task_completion"
        assert "timestamp" in data
        print(f"Recorded episode: {data['event_type']}")
    
    def test_recall_episodes_by_agent(self):
        """GET /api/infinity/memory/episodic/{agent_id} - Recall episodes for agent"""
        agent_id = f"TEST_recall_{int(time.time())}"
        # Record an episode first
        requests.post(f"{BASE_URL}/api/infinity/memory/episodic/record", json={
            "agent_id": agent_id, "event_type": "test_event",
            "event_data": {"test": True}, "outcome": "pass"
        })
        
        # Recall
        response = requests.get(f"{BASE_URL}/api/infinity/memory/episodic/{agent_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"Recalled {len(data)} episodes for agent")
    
    def test_recall_collective_episodes(self):
        """GET /api/infinity/memory/episodic/collective/{event_type} - Collective recall"""
        event_type = "collective_test_event"
        # Record a couple episodes
        for i in range(2):
            requests.post(f"{BASE_URL}/api/infinity/memory/episodic/record", json={
                "agent_id": f"TEST_collective_{i}", "event_type": event_type,
                "event_data": {"index": i}, "outcome": "success"
            })
        
        # Collective recall
        response = requests.get(f"{BASE_URL}/api/infinity/memory/episodic/collective/{event_type}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Collective recall returned {len(data)} episodes")
    
    def test_get_lessons_learned(self):
        """GET /api/infinity/memory/lessons - Get lessons learned"""
        # Record episode with lesson
        requests.post(f"{BASE_URL}/api/infinity/memory/episodic/record", json={
            "agent_id": "TEST_lesson_agent", "event_type": "learning",
            "event_data": {"topic": "testing"}, "lessons_learned": "Always validate response structure"
        })
        
        response = requests.get(f"{BASE_URL}/api/infinity/memory/lessons")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Retrieved {len(data)} lessons")


class TestKnowledgeGraph:
    """Phase 2: Knowledge Graph APIs"""
    
    def test_add_entity(self):
        """POST /api/infinity/memory/knowledge-graph/entity - Add entity"""
        entity_name = f"TEST_entity_{int(time.time())}"
        payload = {
            "entity": entity_name,
            "entity_type": "test_concept",
            "attributes": {"importance": "high", "domain": "testing"},
            "source": "pytest"
        }
        response = requests.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/entity", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["entity"] == entity_name
        assert data["entity_type"] == "test_concept"
        print(f"Added entity: {data}")
        return entity_name
    
    def test_add_relationship(self):
        """POST /api/infinity/memory/knowledge-graph/relationship - Add relationship"""
        ts = int(time.time())
        entity1 = f"TEST_rel_e1_{ts}"
        entity2 = f"TEST_rel_e2_{ts}"
        
        # Add entities
        requests.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/entity", json={
            "entity": entity1, "entity_type": "concept"
        })
        requests.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/entity", json={
            "entity": entity2, "entity_type": "concept"
        })
        
        # Add relationship
        payload = {
            "entity": entity1,
            "target": entity2,
            "relationship_type": "relates_to",
            "weight": 0.85,
            "source": "pytest"
        }
        response = requests.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/relationship", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["entity"] == entity1
        assert data["target"] == entity2
        print(f"Added relationship: {data}")
    
    def test_get_entity(self):
        """GET /api/infinity/memory/knowledge-graph/entity/{entity} - Get entity"""
        entity_name = f"TEST_get_ent_{int(time.time())}"
        # Add entity
        requests.post(f"{BASE_URL}/api/infinity/memory/knowledge-graph/entity", json={
            "entity": entity_name, "entity_type": "retrieval_test",
            "attributes": {"test": True}
        })
        
        # Get entity
        response = requests.get(f"{BASE_URL}/api/infinity/memory/knowledge-graph/entity/{entity_name}")
        assert response.status_code == 200
        data = response.json()
        assert data["entity"] == entity_name
        assert data["entity_type"] == "retrieval_test"
        print(f"Retrieved entity: {entity_name}")
    
    def test_query_knowledge_graph(self):
        """GET /api/infinity/memory/knowledge-graph/query - Query graph"""
        response = requests.get(f"{BASE_URL}/api/infinity/memory/knowledge-graph/query")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Knowledge graph query returned {len(data)} entities")
    
    def test_get_graph_stats(self):
        """GET /api/infinity/memory/knowledge-graph/stats - Get stats"""
        response = requests.get(f"{BASE_URL}/api/infinity/memory/knowledge-graph/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_entities" in data
        assert "total_relationships" in data
        print(f"Graph stats: {data['total_entities']} entities, {data['total_relationships']} relationships")


class TestIntelligenceSearch:
    """Phase 2: Intelligence Search APIs (Real DuckDuckGo)"""
    
    def test_search_and_rank(self):
        """POST /api/infinity/intelligence/search - Real DuckDuckGo search"""
        payload = {
            "query": "artificial intelligence enterprise applications 2025",
            "freshness": "standard"
        }
        response = requests.post(f"{BASE_URL}/api/infinity/intelligence/search", json=payload, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert isinstance(data["results"], list)
        # Note: Real search might return 0 results if rate limited, but should still return valid structure
        print(f"Search returned {len(data['results'])} results, source: {data.get('source', 'unknown')}")
    
    def test_search_plan_query(self):
        """POST /api/infinity/intelligence/search/plan - Plan search queries"""
        # This endpoint takes goal as query parameter
        goal = "Research competitive landscape for enterprise AI platforms"
        response = requests.post(f"{BASE_URL}/api/infinity/intelligence/search/plan?goal={goal}")
        assert response.status_code == 200
        data = response.json()
        assert "goal" in data
        assert "queries" in data
        assert isinstance(data["queries"], list)
        assert len(data["queries"]) >= 1
        print(f"Planned {len(data['queries'])} queries for goal")
    
    def test_verify_sources(self):
        """POST /api/infinity/intelligence/verify-sources - Cross-verify claim"""
        payload = {
            "claim": "AI adoption is increasing in enterprise",
            "results": [
                {"title": "Enterprise AI Trends", "snippet": "AI adoption is increasing rapidly in enterprise environments", "url": "https://example.com/ai"},
                {"title": "Tech Report 2025", "snippet": "Enterprise AI spending has grown significantly", "url": "https://example.com/report"}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/infinity/intelligence/verify-sources", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "claim" in data
        assert "status" in data
        assert "confidence" in data
        assert data["status"] in ["verified", "likely", "conflicting", "unconfirmed"]
        print(f"Claim verification: {data['status']} (confidence: {data['confidence']})")


class TestIntelligenceMonitors:
    """Phase 2: Intelligence Monitors APIs"""
    
    def test_create_monitor(self):
        """POST /api/infinity/intelligence/monitors - Create monitor"""
        ts = int(time.time())
        payload = {
            "monitor_type": "news",
            "target": f"TEST_target_{ts}",
            "config": {"keywords": ["AI", "enterprise"], "frequency": "daily"}
        }
        response = requests.post(f"{BASE_URL}/api/infinity/intelligence/monitors", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["monitor_type"] == "news"
        assert data["status"] == "active"
        print(f"Created monitor: {data['monitor_type']} for {data['target']}")
    
    def test_get_monitors(self):
        """GET /api/infinity/intelligence/monitors - List monitors"""
        response = requests.get(f"{BASE_URL}/api/infinity/intelligence/monitors")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Retrieved {len(data)} monitors")
    
    def test_run_monitor(self):
        """POST /api/infinity/intelligence/monitors/run - Run monitor (real search)"""
        # Create a monitor first
        target = f"AI_enterprise_{int(time.time())}"
        requests.post(f"{BASE_URL}/api/infinity/intelligence/monitors", json={
            "monitor_type": "news", "target": target
        })
        
        # Run it (query params)
        response = requests.post(
            f"{BASE_URL}/api/infinity/intelligence/monitors/run?monitor_type=news&target={target}",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checked_at" in data
        print(f"Monitor run status: {data['status']}, results: {data.get('result_count', 0)}")
    
    def test_get_alerts(self):
        """GET /api/infinity/intelligence/alerts - Get alerts"""
        response = requests.get(f"{BASE_URL}/api/infinity/intelligence/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Retrieved {len(data)} alerts")


class TestCitations:
    """Phase 2: Citations APIs"""
    
    def test_create_citation(self):
        """POST /api/infinity/intelligence/citations - Create citation"""
        payload = {
            "claim": f"Test claim {int(time.time())}",
            "sources": [
                {"url": "https://example.com/source1", "title": "Source 1"},
                {"url": "https://example.com/source2", "title": "Source 2"}
            ],
            "confidence": 0.85,
            "verified": True
        }
        response = requests.post(f"{BASE_URL}/api/infinity/intelligence/citations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "claim" in data
        assert data["confidence"] == 0.85
        assert data["verified"] == True
        print(f"Created citation: confidence={data['confidence']}")
    
    def test_get_citations(self):
        """GET /api/infinity/intelligence/citations - Get citations"""
        response = requests.get(f"{BASE_URL}/api/infinity/intelligence/citations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Retrieved {len(data)} citations")


class TestToolRegistry:
    """Phase 2: Tool Registry APIs"""
    
    def test_register_tool(self):
        """POST /api/infinity/tools/register - Register tool"""
        ts = int(time.time())
        payload = {
            "tool_id": f"TEST_tool_{ts}",
            "name": "Test Tool",
            "description": "A test tool for pytest",
            "schema": {
                "type": "object",
                "required": ["input"],
                "properties": {"input": {"type": "string"}}
            },
            "permissions": ["read", "write"],
            "category": "testing"
        }
        response = requests.post(f"{BASE_URL}/api/infinity/tools/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["tool_id"] == payload["tool_id"]
        assert data["status"] == "active"
        print(f"Registered tool: {data['name']}")
        return payload["tool_id"]
    
    def test_get_tools(self):
        """GET /api/infinity/tools - List tools"""
        response = requests.get(f"{BASE_URL}/api/infinity/tools")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Retrieved {len(data)} tools")
    
    def test_record_tool_call(self):
        """POST /api/infinity/tools/record-call - Record tool call"""
        # Register a tool first
        tool_id = f"TEST_call_tool_{int(time.time())}"
        requests.post(f"{BASE_URL}/api/infinity/tools/register", json={
            "tool_id": tool_id, "name": "Call Test", "description": "Test",
            "schema": {"type": "object"}
        })
        
        # Record a call
        payload = {"tool_id": tool_id, "success": True, "latency_ms": 150}
        response = requests.post(f"{BASE_URL}/api/infinity/tools/record-call", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["recorded"] == True
        print(f"Recorded tool call for {tool_id}")
    
    def test_get_tool_health(self):
        """GET /api/infinity/tools/health - Get tool health metrics"""
        response = requests.get(f"{BASE_URL}/api/infinity/tools/health")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Retrieved health for {len(data)} tools")


class TestCommanderOrion:
    """Phase 3: Commander Orion Orchestration APIs"""
    
    def test_execute_goal_simulation(self):
        """POST /api/infinity/orchestrator/execute - Execute goal (simulation mode)"""
        payload = {
            "description": "Analyze market trends for enterprise software",
            "requester_id": "pytest",
            "environment": "simulation"
        }
        response = requests.post(f"{BASE_URL}/api/infinity/orchestrator/execute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "goal" in data
        assert "classification" in data
        assert "graph_id" in data
        assert "nodes" in data
        assert data["environment"] == "simulation"
        print(f"Executed goal: {data['nodes']} nodes, type={data['classification']['goal_type']}")
    
    def test_execute_goal_classification(self):
        """Commander should classify goals by type"""
        test_cases = [
            ("Research the competitive landscape", "research"),
            ("Build a microservices architecture", "engineering"),
            ("Run a brand campaign for our social media launch", "marketing"),
        ]
        for goal_desc, expected_type in test_cases:
            response = requests.post(f"{BASE_URL}/api/infinity/orchestrator/execute", json={
                "description": goal_desc, "environment": "simulation"
            })
            data = response.json()
            assert data["classification"]["goal_type"] == expected_type, f"Expected {expected_type} for '{goal_desc}'"
            print(f"Goal '{goal_desc[:30]}...' classified as {data['classification']['goal_type']}")
    
    def test_get_commander_log(self):
        """GET /api/infinity/orchestrator/log - Get commander log"""
        response = requests.get(f"{BASE_URL}/api/infinity/orchestrator/log?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Commander log: {len(data)} entries")


class TestVenturePortfolio:
    """Phase 4: Venture Portfolio APIs"""
    
    def test_create_venture(self):
        """POST /api/infinity/portfolio/ventures - Create venture"""
        ts = int(time.time())
        payload = {
            "name": f"TEST_Venture_{ts}",
            "description": "A test venture for pytest",
            "stage": "idea",
            "initial_investment": 10000
        }
        response = requests.post(f"{BASE_URL}/api/infinity/portfolio/ventures", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["stage"] == "idea"
        assert data["status"] == "active"
        print(f"Created venture: {data['name']}")
        return payload["name"]
    
    def test_get_ventures(self):
        """GET /api/infinity/portfolio/ventures - List ventures"""
        response = requests.get(f"{BASE_URL}/api/infinity/portfolio/ventures")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Retrieved {len(data)} ventures")
    
    def test_get_portfolio_summary(self):
        """GET /api/infinity/portfolio/summary - Portfolio summary"""
        response = requests.get(f"{BASE_URL}/api/infinity/portfolio/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_ventures" in data
        assert "total_revenue" in data
        assert "total_costs" in data
        print(f"Portfolio summary: {data['total_ventures']} ventures, ${data['total_revenue']} revenue")
    
    def test_update_venture_metrics(self):
        """POST /api/infinity/portfolio/ventures/metrics - Update metrics"""
        # Create a venture first
        venture_name = f"TEST_Metrics_{int(time.time())}"
        requests.post(f"{BASE_URL}/api/infinity/portfolio/ventures", json={
            "name": venture_name, "description": "Metrics test", "stage": "mvp"
        })
        
        # Update metrics
        payload = {
            "name": venture_name,
            "metrics": {
                "revenue": 50000,
                "costs": 30000,
                "cac": 100,
                "ltv": 500,
                "cash_on_hand": 100000
            }
        }
        response = requests.post(f"{BASE_URL}/api/infinity/portfolio/ventures/metrics", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == venture_name
        assert "opportunity_score" in data
        assert "next_action" in data
        print(f"Updated metrics: score={data['opportunity_score']}, action={data['next_action']}")
    
    def test_venture_stage_transition(self):
        """POST /api/infinity/portfolio/ventures/{name}/transition - Stage transition"""
        venture_name = f"TEST_Transition_{int(time.time())}"
        requests.post(f"{BASE_URL}/api/infinity/portfolio/ventures", json={
            "name": venture_name, "description": "Transition test", "stage": "idea"
        })
        
        # Transition to validation
        response = requests.post(f"{BASE_URL}/api/infinity/portfolio/ventures/{venture_name}/transition?stage=validation")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == venture_name
        assert data["stage"] == "validation"
        print(f"Transitioned {venture_name} to validation stage")


class TestRouterPerformance:
    """Additional Phase 2: Router Performance APIs"""
    
    def test_route_task(self):
        """POST /api/infinity/router/route - Route a task"""
        payload = {"task_description": "Analyze quarterly financial data"}
        response = requests.post(f"{BASE_URL}/api/infinity/router/route", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "classification" in data
        assert "selection" in data
        assert "provider" in data["selection"]
        assert "model" in data["selection"]
        print(f"Routed to {data['selection']['provider']}/{data['selection']['model']}")
    
    def test_get_router_performance(self):
        """GET /api/infinity/router/performance - Router performance stats"""
        response = requests.get(f"{BASE_URL}/api/infinity/router/performance")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Router performance: {len(data)} models tracked")


# Run cleanup test at the end
class TestCleanup:
    """Cleanup test data created during testing"""
    
    def test_cleanup_working_memory(self):
        """Clean up test working memory entries"""
        # This is handled by individual tests via unique task IDs
        print("Test data uses unique timestamps - no global cleanup needed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
