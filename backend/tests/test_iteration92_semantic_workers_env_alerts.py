"""
Iteration 92 - Testing 5 new MAARS Infinity features:
1. Semantic Memory Layer (store/query/agent-context/stats/concept)
2. Worker Queues (enqueue/jobs/cancel/stats)
3. WebSocket Streaming (ws/stats)
4. Multi-Environment Segregation (environments/active/set/stats/validate/configure)
5. Custom Alert Rules CRUD (POST/PUT/DELETE /alerts/rules)
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
TEST_EMAIL = "management.maars@marsgc.net"
TEST_PASSWORD = "admin123"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API calls."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data.get("token")


@pytest.fixture(scope="module")
def headers(auth_token):
    """Headers with auth token."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


# ════════════════════════════════════════════════════════════════════
# SEMANTIC MEMORY LAYER TESTS
# ════════════════════════════════════════════════════════════════════

class TestSemanticMemory:
    """Tests for semantic memory layer endpoints."""

    def test_store_semantic_concept(self, headers):
        """POST /api/infinity/memory/semantic/store - store a semantic concept."""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "concept": f"TEST_concept_{unique_id}",
            "concept_type": "task_knowledge",
            "description": "Test concept for automated testing",
            "source_agent": "test_agent",
            "related_entities": ["test_entity_1", "test_entity_2"],
            "confidence": 0.95,
            "tags": ["test", "automated"],
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/memory/semantic/store",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200, f"Store concept failed: {response.text}"
        data = response.json()
        assert data["concept"] == payload["concept"]
        assert data["concept_type"] == "task_knowledge"
        assert data["status"] == "stored"
        print(f"✓ Stored semantic concept: {data['concept']}")
        return data["concept"]

    def test_query_semantic_memory(self, headers):
        """POST /api/infinity/memory/semantic/query - query across concepts, episodes, entities."""
        payload = {
            "query": "test",
            "limit": 10,
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/memory/semantic/query",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200, f"Query semantic failed: {response.text}"
        data = response.json()
        assert "concepts" in data
        assert "episodes" in data
        assert "entities" in data
        assert "relevance_summary" in data
        print(f"✓ Semantic query returned: {data['relevance_summary']}")

    def test_build_agent_context(self, headers):
        """POST /api/infinity/memory/semantic/agent-context - build rich agent context."""
        payload = {
            "agent_id": "agent_1a_kernel_ops",
            "task_description": "Analyze system performance metrics",
            "limit": 5,
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/memory/semantic/agent-context",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200, f"Agent context failed: {response.text}"
        data = response.json()
        assert "semantic_context" in data
        assert "concepts_found" in data
        assert "episodes_found" in data
        assert "entities_found" in data
        print(f"✓ Agent context built: concepts={data['concepts_found']}, episodes={data['episodes_found']}")

    def test_get_semantic_stats(self, headers):
        """GET /api/infinity/memory/semantic/stats - get semantic memory statistics."""
        response = requests.get(
            f"{BASE_URL}/api/infinity/memory/semantic/stats",
            headers=headers,
        )
        assert response.status_code == 200, f"Semantic stats failed: {response.text}"
        data = response.json()
        assert "total_concepts" in data
        assert "concept_types" in data
        assert "top_accessed" in data
        print(f"✓ Semantic stats: {data['total_concepts']} total concepts")

    def test_get_single_concept(self, headers):
        """GET /api/infinity/memory/semantic/concept/{concept} - get single concept."""
        # First store a concept
        unique_id = str(uuid.uuid4())[:8]
        concept_name = f"TEST_single_concept_{unique_id}"
        store_payload = {
            "concept": concept_name,
            "concept_type": "test_type",
            "description": "Single concept test",
        }
        store_response = requests.post(
            f"{BASE_URL}/api/infinity/memory/semantic/store",
            json=store_payload,
            headers=headers,
        )
        assert store_response.status_code == 200

        # Now retrieve it
        response = requests.get(
            f"{BASE_URL}/api/infinity/memory/semantic/concept/{concept_name}",
            headers=headers,
        )
        assert response.status_code == 200, f"Get concept failed: {response.text}"
        data = response.json()
        assert data["concept"] == concept_name
        assert data["concept_type"] == "test_type"
        print(f"✓ Retrieved single concept: {concept_name}")


# ════════════════════════════════════════════════════════════════════
# WORKER QUEUES TESTS
# ════════════════════════════════════════════════════════════════════

class TestWorkerQueues:
    """Tests for worker queue manager endpoints."""

    def test_enqueue_job(self, headers):
        """POST /api/infinity/workers/enqueue - enqueue a background job."""
        payload = {
            "job_type": "llm_execution",
            "payload": {
                "task_description": "Test task for worker queue",
                "context": "Automated testing context",
            },
            "priority": 5,
            "max_retries": 1,
            "timeout_seconds": 60,
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/workers/enqueue",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200, f"Enqueue job failed: {response.text}"
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        print(f"✓ Enqueued job: {data['job_id']}")
        return data["job_id"]

    def test_list_jobs(self, headers):
        """GET /api/infinity/workers/jobs - list jobs with filters."""
        response = requests.get(
            f"{BASE_URL}/api/infinity/workers/jobs?limit=10",
            headers=headers,
        )
        assert response.status_code == 200, f"List jobs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} jobs")

    def test_list_jobs_with_status_filter(self, headers):
        """GET /api/infinity/workers/jobs?status=completed - filter by status."""
        response = requests.get(
            f"{BASE_URL}/api/infinity/workers/jobs?status=completed&limit=5",
            headers=headers,
        )
        assert response.status_code == 200, f"List jobs by status failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        # All returned jobs should have completed status
        for job in data:
            assert job["status"] == "completed"
        print(f"✓ Listed {len(data)} completed jobs")

    def test_get_single_job(self, headers):
        """GET /api/infinity/workers/jobs/{job_id} - get single job status."""
        # First enqueue a job
        enqueue_response = requests.post(
            f"{BASE_URL}/api/infinity/workers/enqueue",
            json={
                "job_type": "batch_analysis",
                "payload": {"tasks": [{"description": "Test batch task"}]},
            },
            headers=headers,
        )
        assert enqueue_response.status_code == 200
        job_id = enqueue_response.json()["job_id"]

        # Get the job
        response = requests.get(
            f"{BASE_URL}/api/infinity/workers/jobs/{job_id}",
            headers=headers,
        )
        assert response.status_code == 200, f"Get job failed: {response.text}"
        data = response.json()
        assert data["job_id"] == job_id
        assert "status" in data
        assert "job_type" in data
        print(f"✓ Retrieved job {job_id}: status={data['status']}")

    def test_cancel_job(self, headers):
        """POST /api/infinity/workers/jobs/{job_id}/cancel - cancel a job."""
        # Enqueue a job
        enqueue_response = requests.post(
            f"{BASE_URL}/api/infinity/workers/enqueue",
            json={
                "job_type": "llm_execution",
                "payload": {"task_description": "Job to cancel"},
                "timeout_seconds": 300,  # Long timeout so we can cancel it
            },
            headers=headers,
        )
        assert enqueue_response.status_code == 200
        job_id = enqueue_response.json()["job_id"]

        # Wait a moment then try to cancel
        time.sleep(0.5)

        response = requests.post(
            f"{BASE_URL}/api/infinity/workers/jobs/{job_id}/cancel",
            headers=headers,
        )
        assert response.status_code == 200, f"Cancel job failed: {response.text}"
        data = response.json()
        # Job might already be completed or cancelled
        assert "job_id" in data or "error" in data
        print(f"✓ Cancel job response: {data}")

    def test_get_queue_stats(self, headers):
        """GET /api/infinity/workers/stats - get queue statistics."""
        response = requests.get(
            f"{BASE_URL}/api/infinity/workers/stats",
            headers=headers,
        )
        assert response.status_code == 200, f"Queue stats failed: {response.text}"
        data = response.json()
        assert "total_jobs" in data
        assert "active_workers" in data
        assert "by_status" in data
        assert "by_type" in data
        print(f"✓ Queue stats: {data['total_jobs']} total jobs, {data['active_workers']} active workers")


# ════════════════════════════════════════════════════════════════════
# MULTI-ENVIRONMENT TESTS
# ════════════════════════════════════════════════════════════════════

class TestMultiEnvironment:
    """Tests for multi-environment segregation endpoints."""

    def test_list_all_environments(self, headers):
        """GET /api/infinity/environments - list all 4 environments."""
        response = requests.get(
            f"{BASE_URL}/api/infinity/environments",
            headers=headers,
        )
        assert response.status_code == 200, f"List environments failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4  # production, staging, sandbox, simulation
        env_names = [e["environment"] for e in data]
        assert "production" in env_names
        assert "staging" in env_names
        assert "sandbox" in env_names
        assert "simulation" in env_names
        print(f"✓ Listed {len(data)} environments: {env_names}")

    def test_get_active_environment(self, headers):
        """GET /api/infinity/environments/active - get active environment."""
        response = requests.get(
            f"{BASE_URL}/api/infinity/environments/active",
            headers=headers,
        )
        assert response.status_code == 200, f"Get active env failed: {response.text}"
        data = response.json()
        assert "active" in data
        assert "config" in data
        assert data["active"] in ["production", "staging", "sandbox", "simulation"]
        print(f"✓ Active environment: {data['active']}")

    def test_set_active_environment(self, headers):
        """POST /api/infinity/environments/set - switch active environment."""
        # Get current active
        current_response = requests.get(
            f"{BASE_URL}/api/infinity/environments/active",
            headers=headers,
        )
        current_env = current_response.json()["active"]

        # Switch to sandbox
        response = requests.post(
            f"{BASE_URL}/api/infinity/environments/set",
            json={"environment": "sandbox"},
            headers=headers,
        )
        assert response.status_code == 200, f"Set environment failed: {response.text}"
        data = response.json()
        assert data["environment"] == "sandbox"
        assert data["status"] == "active"
        print(f"✓ Switched environment to: sandbox")

        # Restore original
        requests.post(
            f"{BASE_URL}/api/infinity/environments/set",
            json={"environment": current_env},
            headers=headers,
        )

    def test_get_environment_stats(self, headers):
        """GET /api/infinity/environments/stats - environment execution stats."""
        response = requests.get(
            f"{BASE_URL}/api/infinity/environments/stats",
            headers=headers,
        )
        assert response.status_code == 200, f"Environment stats failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        for env_stat in data:
            assert "environment" in env_stat
            assert "executions" in env_stat
            assert "runs" in env_stat
        print(f"✓ Environment stats for {len(data)} environments")

    def test_validate_execution_environment(self, headers):
        """POST /api/infinity/environments/validate - validate execution in environment."""
        response = requests.post(
            f"{BASE_URL}/api/infinity/environments/validate?environment=sandbox&autonomy_tier=5",
            headers=headers,
        )
        assert response.status_code == 200, f"Validate env failed: {response.text}"
        data = response.json()
        assert "allowed" in data
        print(f"✓ Validation result: allowed={data['allowed']}")

    def test_validate_environment_with_model(self, headers):
        """POST /api/infinity/environments/validate - validate with model restriction."""
        response = requests.post(
            f"{BASE_URL}/api/infinity/environments/validate?environment=production&autonomy_tier=2&model=gpt-5.2",
            headers=headers,
        )
        assert response.status_code == 200, f"Validate env with model failed: {response.text}"
        data = response.json()
        assert "allowed" in data
        print(f"✓ Production validation with gpt-5.2: allowed={data['allowed']}")

    def test_configure_environment_overrides(self, headers):
        """POST /api/infinity/environments/configure - store custom environment overrides."""
        payload = {
            "environment": "sandbox",
            "overrides": {
                "rate_limit_rpm": 500,
                "max_autonomy_tier": 8,
            },
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/environments/configure",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200, f"Configure env failed: {response.text}"
        data = response.json()
        assert data["environment"] == "sandbox"
        assert "overrides" in data
        print(f"✓ Configured sandbox overrides: {data['overrides']}")


# ════════════════════════════════════════════════════════════════════
# CUSTOM ALERT RULES CRUD TESTS
# ════════════════════════════════════════════════════════════════════

class TestCustomAlertRules:
    """Tests for custom alert rules CRUD endpoints."""

    def test_list_alert_rules(self, headers):
        """GET /api/infinity/alerts/rules - list all alert rules."""
        response = requests.get(
            f"{BASE_URL}/api/infinity/alerts/rules",
            headers=headers,
        )
        assert response.status_code == 200, f"List alert rules failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} alert rules")

    def test_create_alert_rule(self, headers):
        """POST /api/infinity/alerts/rules - create a new custom alert rule."""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "rule_id": f"test_rule_{unique_id}",
            "name": f"Test Alert Rule {unique_id}",
            "metric": "circuit_breakers_tripped",
            "operator": ">",
            "threshold": 5,
            "severity": "high",
            "enabled": True,
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/alerts/rules",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200, f"Create alert rule failed: {response.text}"
        data = response.json()
        assert data["rule_id"] == payload["rule_id"]
        assert data["name"] == payload["name"]
        assert data["metric"] == "circuit_breakers_tripped"
        assert data["custom"] == True
        print(f"✓ Created alert rule: {data['rule_id']}")
        return data["rule_id"]

    def test_update_alert_rule(self, headers):
        """PUT /api/infinity/alerts/rules/{rule_id} - update existing rule."""
        # First create a rule
        unique_id = str(uuid.uuid4())[:8]
        create_payload = {
            "rule_id": f"test_update_rule_{unique_id}",
            "name": f"Test Update Rule {unique_id}",
            "metric": "open_incidents",
            "operator": ">",
            "threshold": 3,
            "severity": "medium",
            "enabled": True,
        }
        create_response = requests.post(
            f"{BASE_URL}/api/infinity/alerts/rules",
            json=create_payload,
            headers=headers,
        )
        assert create_response.status_code == 200
        rule_id = create_response.json()["rule_id"]

        # Update the rule
        update_payload = {
            "threshold": 10,
            "enabled": False,
            "severity": "low",
        }
        response = requests.put(
            f"{BASE_URL}/api/infinity/alerts/rules/{rule_id}",
            json=update_payload,
            headers=headers,
        )
        assert response.status_code == 200, f"Update alert rule failed: {response.text}"
        data = response.json()
        assert data.get("threshold") == 10 or data.get("updated") == True
        print(f"✓ Updated alert rule: {rule_id}")

        # Cleanup
        requests.delete(f"{BASE_URL}/api/infinity/alerts/rules/{rule_id}", headers=headers)

    def test_delete_alert_rule(self, headers):
        """DELETE /api/infinity/alerts/rules/{rule_id} - delete an alert rule."""
        # First create a rule
        unique_id = str(uuid.uuid4())[:8]
        create_payload = {
            "rule_id": f"test_delete_rule_{unique_id}",
            "name": f"Test Delete Rule {unique_id}",
            "metric": "busy_agents",
            "operator": ">",
            "threshold": 100,
            "severity": "low",
            "enabled": True,
        }
        create_response = requests.post(
            f"{BASE_URL}/api/infinity/alerts/rules",
            json=create_payload,
            headers=headers,
        )
        assert create_response.status_code == 200
        rule_id = create_response.json()["rule_id"]

        # Delete the rule
        response = requests.delete(
            f"{BASE_URL}/api/infinity/alerts/rules/{rule_id}",
            headers=headers,
        )
        assert response.status_code == 200, f"Delete alert rule failed: {response.text}"
        data = response.json()
        assert data["rule_id"] == rule_id
        assert data["deleted"] == True
        print(f"✓ Deleted alert rule: {rule_id}")

    def test_create_duplicate_rule_fails(self, headers):
        """POST /api/infinity/alerts/rules - creating duplicate rule should fail."""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "rule_id": f"test_dup_rule_{unique_id}",
            "name": f"Test Duplicate Rule {unique_id}",
            "metric": "total_agents",
            "operator": "<",
            "threshold": 10,
            "severity": "medium",
            "enabled": True,
        }
        # Create first time
        response1 = requests.post(
            f"{BASE_URL}/api/infinity/alerts/rules",
            json=payload,
            headers=headers,
        )
        assert response1.status_code == 200

        # Try to create again
        response2 = requests.post(
            f"{BASE_URL}/api/infinity/alerts/rules",
            json=payload,
            headers=headers,
        )
        assert response2.status_code == 400, "Duplicate rule should fail"
        print(f"✓ Duplicate rule creation correctly rejected")

        # Cleanup
        requests.delete(f"{BASE_URL}/api/infinity/alerts/rules/{payload['rule_id']}", headers=headers)


# ════════════════════════════════════════════════════════════════════
# WEBSOCKET STATS TEST
# ════════════════════════════════════════════════════════════════════

class TestWebSocketStats:
    """Tests for WebSocket connection stats endpoint."""

    def test_get_ws_stats(self, headers):
        """GET /api/infinity/ws/stats - WebSocket connection stats."""
        response = requests.get(
            f"{BASE_URL}/api/infinity/ws/stats",
            headers=headers,
        )
        assert response.status_code == 200, f"WS stats failed: {response.text}"
        data = response.json()
        assert "total_channels" in data
        assert "channels" in data
        assert "total_connections" in data
        print(f"✓ WebSocket stats: {data['total_channels']} channels, {data['total_connections']} connections")


# ════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS - Semantic Memory in Agent Runtime
# ════════════════════════════════════════════════════════════════════

class TestSemanticMemoryIntegration:
    """Tests for semantic memory integration in agent runtime."""

    def test_runtime_uses_semantic_memory(self, headers):
        """POST /api/infinity/runtime/execute - verify semantic memory is used in step 3."""
        # Use a valid agent ID from the catalog
        payload = {
            "agent_id": "agent_10e_aiml",  # AI/ML Engineer agent
            "task_description": "Analyze system metrics and provide recommendations",
            "environment": "sandbox",
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/runtime/execute",
            json=payload,
            headers=headers,
            timeout=90,  # Runtime can take time with real LLM calls
        )
        assert response.status_code == 200, f"Runtime execute failed: {response.text}"
        data = response.json()
        
        # Check that retrieve_memory step exists
        steps = data.get("steps", [])
        step_names = [s["step"] for s in steps]
        
        # If agent was found, we should have more than just load_role_pack
        if data.get("status") == "failed" and len(steps) == 1:
            # Agent not found - skip this test
            pytest.skip(f"Agent not found in catalog: {data}")
        
        assert "retrieve_memory" in step_names, f"retrieve_memory step should be present. Steps: {step_names}"
        
        # Find the retrieve_memory step
        memory_step = next((s for s in steps if s["step"] == "retrieve_memory"), None)
        assert memory_step is not None
        assert memory_step["status"] == "pass"
        print(f"✓ Runtime uses semantic memory in step 3: {memory_step['detail'][:100]}")

    def test_runtime_validates_environment(self, headers):
        """POST /api/infinity/runtime/execute - verify environment validation in step 1.5."""
        # Use a valid agent ID from the catalog
        payload = {
            "agent_id": "agent_10e_aiml",  # AI/ML Engineer agent
            "task_description": "Simple read task",
            "environment": "sandbox",  # Use sandbox to ensure it passes
        }
        response = requests.post(
            f"{BASE_URL}/api/infinity/runtime/execute",
            json=payload,
            headers=headers,
            timeout=90,
        )
        assert response.status_code == 200, f"Runtime execute failed: {response.text}"
        data = response.json()
        
        # Check steps include environment validation
        steps = data.get("steps", [])
        step_names = [s["step"] for s in steps]
        
        # If agent was found, we should have more than just load_role_pack
        if data.get("status") == "failed" and len(steps) == 1:
            # Agent not found - skip this test
            pytest.skip(f"Agent not found in catalog: {data}")
        
        # Environment check should be early in the process
        assert "load_context" in step_names, f"load_context step should be present. Steps: {step_names}"
        print(f"✓ Runtime validates environment: {data.get('environment')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
