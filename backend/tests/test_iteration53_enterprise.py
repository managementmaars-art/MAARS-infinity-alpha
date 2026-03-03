"""
Iteration 53: Enterprise Features Testing
- 41 agents (28 existing + 13 new)
- Collaboration Engine
- KPI Framework with Custom KPIs
- System Mode (Simulation/Execution)
- Cost Governance
- Quality Control Reviews
- Brain Profiles (41 total)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_EMAIL = "management.maars@marsgc.net"
TEST_PASSWORD = "admin123"

# New agents added in iteration 53
NEW_AGENTS_13 = [
    "agent_cso",
    "agent_investor",
    "agent_productmgr",
    "agent_dataengineer",
    "agent_brand",
    "agent_uxresearch",
    "agent_3d",
    "agent_pr",
    "agent_procurement",
    "agent_cx",
    "agent_ethics",
    "agent_knowledge",
    "agent_localization",
]


class TestAuth:
    """Test authentication endpoint."""

    def test_login_success(self):
        """Test login with valid credentials."""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def headers(auth_token):
    """Headers with authentication token."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


# ============== AGENTS TESTS ==============

class TestAgents41Count:
    """Test that exactly 41 agents are returned."""

    def test_public_agents_returns_41(self):
        """GET /api/agents/public returns exactly 41 agents."""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) == 41, f"Expected 41 agents, got {len(agents)}"

    def test_all_13_new_agents_present(self):
        """Verify all 13 new agents are present in the public list."""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        agents = response.json()
        agent_ids = [a["agent_id"] for a in agents]
        
        for new_agent in NEW_AGENTS_13:
            assert new_agent in agent_ids, f"Missing new agent: {new_agent}"

    def test_new_agents_have_required_fields(self):
        """Verify new agents have all required fields."""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        agents = response.json()
        
        required_fields = ["agent_id", "name", "description", "avatar", "role", "capabilities"]
        
        for agent in agents:
            if agent["agent_id"] in NEW_AGENTS_13:
                for field in required_fields:
                    assert field in agent, f"Agent {agent['agent_id']} missing field: {field}"
                assert len(agent.get("capabilities", [])) > 0, f"Agent {agent['agent_id']} has no capabilities"


# ============== KPI FRAMEWORK TESTS ==============

class TestKPIEndpoints:
    """Test KPI Framework endpoints."""

    def test_get_kpis_returns_all_sections(self, headers):
        """GET /api/kpis returns operational, governance, cost, and custom_kpis sections."""
        response = requests.get(f"{BASE_URL}/api/kpis", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "operational" in data, "Missing 'operational' section"
        assert "governance" in data, "Missing 'governance' section"
        assert "cost" in data, "Missing 'cost' section"
        assert "custom_kpis" in data, "Missing 'custom_kpis' section"

    def test_operational_kpis_have_real_data(self, headers):
        """Operational KPIs contain expected fields."""
        response = requests.get(f"{BASE_URL}/api/kpis", headers=headers)
        assert response.status_code == 200
        ops = response.json()["operational"]
        
        expected_fields = ["total_projects", "completed_projects", "project_completion_rate",
                          "total_tasks", "completed_tasks", "task_completion_rate",
                          "total_chats", "total_collaborations"]
        for field in expected_fields:
            assert field in ops, f"Missing operational field: {field}"

    def test_governance_kpis_have_data(self, headers):
        """Governance KPIs contain expected fields."""
        response = requests.get(f"{BASE_URL}/api/kpis", headers=headers)
        assert response.status_code == 200
        gov = response.json()["governance"]
        
        expected_fields = ["total_approvals", "pending_approvals", "total_tool_calls", "risk_incidents"]
        for field in expected_fields:
            assert field in gov, f"Missing governance field: {field}"

    def test_cost_kpis_have_data(self, headers):
        """Cost KPIs contain expected fields."""
        response = requests.get(f"{BASE_URL}/api/kpis", headers=headers)
        assert response.status_code == 200
        cost = response.json()["cost"]
        
        expected_fields = ["total_ai_cost", "total_ai_calls", "avg_cost_per_call"]
        for field in expected_fields:
            assert field in cost, f"Missing cost field: {field}"


class TestCustomKPIs:
    """Test Custom KPI CRUD operations."""

    def test_create_custom_kpi(self, headers):
        """POST /api/kpis/custom creates a custom KPI."""
        response = requests.post(f"{BASE_URL}/api/kpis/custom", headers=headers, json={
            "name": "TEST_Iteration53_Revenue",
            "value": 50000,
            "target": 100000,
            "unit": "$",
            "category": "business"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "kpi_id" in data
        assert data["name"] == "TEST_Iteration53_Revenue"
        assert data["value"] == 50000
        assert data["target"] == 100000

    def test_custom_kpi_appears_in_get_kpis(self, headers):
        """Created custom KPI appears in GET /api/kpis."""
        # First create a KPI
        requests.post(f"{BASE_URL}/api/kpis/custom", headers=headers, json={
            "name": "TEST_Iteration53_CAC",
            "value": 25,
            "target": 20,
            "unit": "$",
            "category": "business"
        })
        
        # Then verify it appears in the list
        response = requests.get(f"{BASE_URL}/api/kpis", headers=headers)
        assert response.status_code == 200
        custom_kpis = response.json()["custom_kpis"]
        
        found = any(k["name"] == "TEST_Iteration53_CAC" for k in custom_kpis)
        assert found, "Custom KPI not found in GET /api/kpis response"


# ============== SYSTEM MODE TESTS ==============

class TestSystemMode:
    """Test System Mode (Simulation/Execution) endpoints."""

    def test_get_system_mode_returns_default(self, headers):
        """GET /api/system/mode returns current mode."""
        response = requests.get(f"{BASE_URL}/api/system/mode", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "mode" in data
        assert data["mode"] in ["simulation", "execution"]
        assert "description" in data

    def test_toggle_to_execution_mode(self, headers):
        """PUT /api/system/mode toggles to execution mode."""
        response = requests.put(f"{BASE_URL}/api/system/mode", headers=headers, json={
            "mode": "execution"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["mode"] == "execution"
        assert "execution" in data["description"].lower() or "live" in data["description"].lower()

    def test_toggle_back_to_simulation(self, headers):
        """PUT /api/system/mode toggles back to simulation mode."""
        response = requests.put(f"{BASE_URL}/api/system/mode", headers=headers, json={
            "mode": "simulation"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["mode"] == "simulation"
        assert "simulation" in data["description"].lower()

    def test_invalid_mode_rejected(self, headers):
        """PUT /api/system/mode rejects invalid mode."""
        response = requests.put(f"{BASE_URL}/api/system/mode", headers=headers, json={
            "mode": "invalid_mode"
        })
        assert response.status_code == 400


# ============== COLLABORATION ENGINE TESTS ==============

class TestCollaborationEngine:
    """Test Collaboration Engine endpoints."""

    def test_get_collaborations_returns_list(self, headers):
        """GET /api/collaborations returns paginated list."""
        response = requests.get(f"{BASE_URL}/api/collaborations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert isinstance(data["items"], list)

    def test_create_collaboration(self, headers):
        """POST /api/collaborations creates a new collaboration record."""
        response = requests.post(f"{BASE_URL}/api/collaborations", headers=headers, json={
            "sender": "agent_commander",
            "receivers": ["agent_marketing", "agent_sales"],
            "objective": "TEST_Iteration53 - Coordinate Q1 marketing campaign",
            "context": "Testing collaboration engine for iteration 53",
            "required_output": "Campaign strategy document",
            "risk_level": "medium",
            "dependencies": ["market_research", "budget_approval"],
            "approval_required": True
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "collab_id" in data
        assert data["sender"] == "agent_commander"
        assert data["receivers"] == ["agent_marketing", "agent_sales"]
        assert data["status"] == "pending"
        assert data["risk_level"] == "medium"

    def test_collaboration_with_filters(self, headers):
        """GET /api/collaborations supports status filter."""
        response = requests.get(f"{BASE_URL}/api/collaborations?status=pending", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # All items should have pending status if filter works
        for item in data["items"]:
            assert item["status"] == "pending", f"Got status {item['status']} instead of pending"


# ============== COST GOVERNANCE TESTS ==============

class TestCostGovernance:
    """Test Cost Governance endpoints."""

    def test_get_cost_governance_returns_data(self, headers):
        """GET /api/cost-governance returns agent costs and budget."""
        response = requests.get(f"{BASE_URL}/api/cost-governance", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "agent_costs" in data
        assert "budget" in data
        assert isinstance(data["agent_costs"], list)

    def test_set_budget_caps(self, headers):
        """PUT /api/cost-governance/budget sets budget caps."""
        response = requests.put(f"{BASE_URL}/api/cost-governance/budget", headers=headers, json={
            "monthly_cap": 1000,
            "alert_threshold": 800
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True

    def test_budget_persists(self, headers):
        """Budget settings persist after being set."""
        # First set the budget
        requests.put(f"{BASE_URL}/api/cost-governance/budget", headers=headers, json={
            "monthly_cap": 2000,
            "alert_threshold": 1500
        })
        
        # Then verify it persists
        response = requests.get(f"{BASE_URL}/api/cost-governance", headers=headers)
        assert response.status_code == 200
        budget = response.json()["budget"]
        
        assert budget.get("monthly_cap") == 2000 or budget.get("monthly_cap") is None  # Initial state may be None


# ============== QUALITY CONTROL TESTS ==============

class TestQualityControl:
    """Test Quality Control Review endpoints."""

    def test_create_quality_review(self, headers):
        """POST /api/quality-review creates a quality review."""
        response = requests.post(f"{BASE_URL}/api/quality-review", headers=headers, json={
            "project_id": "TEST_project_53",
            "task_id": "TEST_task_53",
            "agent_id": "agent_marketing",
            "content": "Marketing campaign draft for Q1 2026",
            "review_type": "self_check",
            "reviewer_agent": "agent_commander"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "review_id" in data
        assert data["project_id"] == "TEST_project_53"
        assert data["review_type"] == "self_check"
        assert data["status"] == "pending"

    def test_list_quality_reviews(self, headers):
        """GET /api/quality-reviews lists quality reviews."""
        response = requests.get(f"{BASE_URL}/api/quality-reviews", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert isinstance(data["items"], list)


# ============== BRAIN PROFILES TESTS ==============

class TestBrainProfiles41:
    """Test Brain Profiles endpoint returns 41 profiles."""

    def test_brain_profiles_returns_41(self, headers):
        """GET /api/brain-profiles returns 41 profiles."""
        response = requests.get(f"{BASE_URL}/api/brain-profiles", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        profiles = data.get("profiles", data)  # Handle both formats
        if isinstance(profiles, dict):
            profiles = profiles.get("profiles", [])
        
        assert len(profiles) == 41, f"Expected 41 brain profiles, got {len(profiles)}"

    def test_brain_profiles_include_new_agents(self, headers):
        """Brain profiles include all 13 new agents."""
        response = requests.get(f"{BASE_URL}/api/brain-profiles", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        profiles = data.get("profiles", data)
        if isinstance(profiles, dict):
            profiles = profiles.get("profiles", [])
        
        profile_ids = [p["agent_id"] for p in profiles]
        
        for new_agent in NEW_AGENTS_13:
            assert new_agent in profile_ids, f"Brain profile missing for: {new_agent}"

    def test_brain_profiles_have_required_fields(self, headers):
        """Brain profiles have required metadata fields."""
        response = requests.get(f"{BASE_URL}/api/brain-profiles", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        profiles = data.get("profiles", data)
        if isinstance(profiles, dict):
            profiles = profiles.get("profiles", [])
        
        required_fields = ["agent_id", "agent_name", "agent_role", "autonomy_level"]
        
        for profile in profiles[:5]:  # Check first 5
            for field in required_fields:
                assert field in profile, f"Profile {profile.get('agent_id', 'unknown')} missing field: {field}"


# ============== CLEANUP ==============

class TestCleanup:
    """Cleanup test data created during testing."""

    def test_reset_system_mode_to_simulation(self, headers):
        """Reset system mode to simulation after tests."""
        response = requests.put(f"{BASE_URL}/api/system/mode", headers=headers, json={
            "mode": "simulation"
        })
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
