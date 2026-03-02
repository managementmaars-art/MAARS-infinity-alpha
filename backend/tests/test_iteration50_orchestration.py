"""
Test Iteration 50: Autonomous Orchestration Engine and Executive Command Dashboard

Tests:
- Projects CRUD with goal scoring, strategic planning, milestones, tasks
- Execution modes (draft/approval/autonomous)
- Autonomy slider settings
- Project execution endpoint
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"
TEST_EMAIL = "test@test.com"
TEST_PASSWORD = "test123"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def test_user_token(api_client):
    """Get test user token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json().get("token")


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json().get("token")


class TestHealthCheck:
    """Basic health check"""

    def test_health_endpoint(self, api_client):
        """Test health endpoint is accessible"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "MAARS Command"


class TestProjectsList:
    """Test GET /api/projects endpoint"""

    def test_projects_list_requires_auth(self, api_client):
        """Projects list requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 401

    def test_projects_list_returns_array(self, api_client, test_user_token):
        """Projects list returns {projects: [...]}"""
        response = api_client.get(
            f"{BASE_URL}/api/projects",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)

    def test_projects_list_filter_by_status(self, api_client, test_user_token):
        """Projects can be filtered by status query param"""
        response = api_client.get(
            f"{BASE_URL}/api/projects?status=planning",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        # All returned projects should have status=planning
        for p in data["projects"]:
            assert p.get("status") == "planning"


class TestProjectsActiveSummary:
    """Test GET /api/projects/active-summary endpoint"""

    def test_active_summary_requires_auth(self, api_client):
        """Active summary requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/projects/active-summary")
        assert response.status_code == 401

    def test_active_summary_returns_counts(self, api_client, test_user_token):
        """Active summary returns projects array and counts"""
        response = api_client.get(
            f"{BASE_URL}/api/projects/active-summary",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields exist
        assert "projects" in data
        assert "active_count" in data
        assert "completed_count" in data
        assert "total_count" in data
        assert "agents_working" in data
        
        # Validate types
        assert isinstance(data["projects"], list)
        assert isinstance(data["active_count"], int)
        assert isinstance(data["completed_count"], int)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["agents_working"], int)


class TestProjectDetail:
    """Test GET /api/projects/{project_id} endpoint"""

    def test_project_detail_requires_auth(self, api_client):
        """Project detail requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/projects/proj_2814634f13c4")
        assert response.status_code == 401

    def test_project_detail_returns_full_data(self, api_client, test_user_token):
        """Project detail returns full project with tasks_detail"""
        response = api_client.get(
            f"{BASE_URL}/api/projects/proj_2814634f13c4",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check core fields
        assert "project_id" in data
        assert data["project_id"] == "proj_2814634f13c4"
        assert "goal" in data
        assert "title" in data
        assert "status" in data
        assert "execution_mode" in data
        assert "priority" in data
        
        # Check scores
        assert "scores" in data
        scores = data["scores"]
        assert "clarity" in scores
        assert "complexity" in scores
        assert "confidence" in scores
        assert "risk_level" in scores
        assert "estimated_agents" in scores
        assert "estimated_hours" in scores
        
        # Check milestones
        assert "milestones" in data
        assert isinstance(data["milestones"], list)
        if data["milestones"]:
            ms = data["milestones"][0]
            assert "milestone_id" in ms
            assert "title" in ms
            assert "task_ids" in ms
        
        # Check tasks_detail (enriched task data)
        assert "tasks_detail" in data
        assert isinstance(data["tasks_detail"], list)

    def test_project_detail_404_for_invalid_id(self, api_client, test_user_token):
        """Project detail returns 404 for invalid project_id"""
        response = api_client.get(
            f"{BASE_URL}/api/projects/nonexistent_project_id",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 404


class TestProjectUpdate:
    """Test PATCH /api/projects/{project_id} endpoint"""

    def test_project_update_requires_auth(self, api_client):
        """Project update requires authentication"""
        response = api_client.patch(
            f"{BASE_URL}/api/projects/proj_2814634f13c4",
            json={"priority": "low"}
        )
        assert response.status_code == 401

    def test_project_update_changes_fields(self, api_client, test_user_token):
        """Project update modifies fields and returns success"""
        # Update to medium
        response = api_client.patch(
            f"{BASE_URL}/api/projects/proj_2814634f13c4",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={"priority": "medium"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        # Verify change
        verify = api_client.get(
            f"{BASE_URL}/api/projects/proj_2814634f13c4",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert verify.json()["priority"] == "medium"
        
        # Reset to high
        api_client.patch(
            f"{BASE_URL}/api/projects/proj_2814634f13c4",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={"priority": "high"}
        )

    def test_project_update_404_for_invalid_id(self, api_client, test_user_token):
        """Project update returns 404 for invalid project_id"""
        response = api_client.patch(
            f"{BASE_URL}/api/projects/nonexistent_id",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={"priority": "low"}
        )
        assert response.status_code == 404


class TestProjectExecute:
    """Test POST /api/projects/{project_id}/execute endpoint"""

    def test_project_execute_requires_auth(self, api_client):
        """Project execute requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/projects/proj_2814634f13c4/execute")
        assert response.status_code == 401

    def test_project_execute_rejects_completed_projects(self, api_client, test_user_token):
        """Project execute returns 400 for completed projects"""
        # First check if project is completed
        check = api_client.get(
            f"{BASE_URL}/api/projects/proj_2814634f13c4",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        status = check.json().get("status", "")
        
        response = api_client.post(
            f"{BASE_URL}/api/projects/proj_2814634f13c4/execute",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        # If project is completed/completed_with_issues, expect 400
        if status in ("completed", "completed_with_issues"):
            assert response.status_code == 400
            assert "completed" in response.json().get("detail", "").lower()
        else:
            # Otherwise it should start execution
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") == True

    def test_project_execute_404_for_invalid_id(self, api_client, test_user_token):
        """Project execute returns 404 for invalid project_id"""
        response = api_client.post(
            f"{BASE_URL}/api/projects/nonexistent_id/execute",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 404


class TestAutonomySettings:
    """Test /api/user/autonomy endpoints"""

    def test_get_autonomy_requires_auth(self, api_client):
        """Get autonomy requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/user/autonomy")
        assert response.status_code == 401

    def test_get_autonomy_returns_level(self, api_client, test_user_token):
        """Get autonomy returns {autonomy_level: string}"""
        response = api_client.get(
            f"{BASE_URL}/api/user/autonomy",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "autonomy_level" in data
        assert data["autonomy_level"] in ("manual", "approval", "autonomous")

    def test_put_autonomy_requires_auth(self, api_client):
        """Set autonomy requires authentication"""
        response = api_client.put(
            f"{BASE_URL}/api/user/autonomy",
            json={"autonomy_level": "manual"}
        )
        assert response.status_code == 401

    def test_put_autonomy_changes_level(self, api_client, test_user_token):
        """Set autonomy updates user's autonomy_level"""
        # Set to manual
        response = api_client.put(
            f"{BASE_URL}/api/user/autonomy",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={"autonomy_level": "manual"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("autonomy_level") == "manual"
        
        # Verify change
        verify = api_client.get(
            f"{BASE_URL}/api/user/autonomy",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert verify.json()["autonomy_level"] == "manual"
        
        # Set to autonomous
        response2 = api_client.put(
            f"{BASE_URL}/api/user/autonomy",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={"autonomy_level": "autonomous"}
        )
        assert response2.status_code == 200
        assert response2.json()["autonomy_level"] == "autonomous"
        
        # Reset to approval
        api_client.put(
            f"{BASE_URL}/api/user/autonomy",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={"autonomy_level": "approval"}
        )

    def test_put_autonomy_rejects_invalid_level(self, api_client, test_user_token):
        """Set autonomy rejects invalid levels"""
        response = api_client.put(
            f"{BASE_URL}/api/user/autonomy",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={"autonomy_level": "invalid_level"}
        )
        assert response.status_code == 400


class TestProjectCreate:
    """Test POST /api/projects endpoint (creates project with LLM calls)
    
    NOTE: Project creation takes 15-20 seconds due to LLM calls for goal scoring
    and strategic planning. Use shorter goals for faster tests.
    """

    def test_project_create_requires_auth(self, api_client):
        """Project create requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/projects",
            json={"goal": "Test goal", "execution_mode": "draft", "priority": "high"}
        )
        assert response.status_code == 401

    def test_project_create_short_goal_draft_mode(self, api_client, test_user_token):
        """Create a project with draft mode - full end-to-end test
        
        This test takes ~15-20 seconds due to LLM processing.
        """
        goal = "Write a blog post"  # Short goal for faster LLM processing
        
        response = api_client.post(
            f"{BASE_URL}/api/projects",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "goal": goal,
                "execution_mode": "draft",
                "priority": "high"
            },
            timeout=60  # Extended timeout for LLM calls
        )
        
        assert response.status_code == 200, f"Create failed: {response.text}"
        data = response.json()
        
        # Validate project structure
        assert "project_id" in data
        assert data["project_id"].startswith("proj_")
        assert "goal" in data
        assert data["goal"] == goal
        assert "title" in data
        assert "status" in data
        assert data["status"] == "planning"  # draft mode starts in planning
        assert "execution_mode" in data
        assert data["execution_mode"] == "draft"
        
        # Validate scores from LLM goal scoring
        assert "scores" in data
        scores = data["scores"]
        assert "clarity" in scores
        assert "complexity" in scores
        assert "confidence" in scores
        assert isinstance(scores["clarity"], int)
        
        # Validate strategic plan from LLM
        assert "milestones" in data
        assert isinstance(data["milestones"], list)
        assert len(data["milestones"]) > 0  # Should have at least 1 milestone
        
        # Validate task_ids created
        assert "task_ids" in data
        assert isinstance(data["task_ids"], list)
        assert len(data["task_ids"]) > 0
        
        # Store project_id for cleanup
        project_id = data["project_id"]
        
        # Clean up: delete the test project
        cleanup = api_client.delete(
            f"{BASE_URL}/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert cleanup.status_code == 200


class TestProjectDelete:
    """Test DELETE /api/projects/{project_id} endpoint"""

    def test_project_delete_requires_auth(self, api_client):
        """Project delete requires authentication"""
        response = api_client.delete(f"{BASE_URL}/api/projects/some_project_id")
        assert response.status_code == 401

    def test_project_delete_404_for_invalid_id(self, api_client, test_user_token):
        """Project delete returns 404 for invalid project_id"""
        response = api_client.delete(
            f"{BASE_URL}/api/projects/nonexistent_id_12345",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 404


class TestExistingProjectData:
    """Validate existing test project data structure (proj_2814634f13c4)"""

    def test_existing_project_has_valid_structure(self, api_client, test_user_token):
        """Existing project has all required fields from orchestration engine"""
        response = api_client.get(
            f"{BASE_URL}/api/projects/proj_2814634f13c4",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Core fields
        assert data["project_id"] == "proj_2814634f13c4"
        assert "Millennial Fitness App" in data["title"]
        assert data["execution_mode"] == "draft"
        # Status can be planning, active, executing, completed, completed_with_issues
        assert data["status"] in ("planning", "active", "executing", "completed", "completed_with_issues", "error")
        
        # Scores
        scores = data["scores"]
        assert scores["clarity"] >= 1 and scores["clarity"] <= 10
        assert scores["complexity"] >= 1 and scores["complexity"] <= 10
        assert scores["confidence"] >= 1 and scores["confidence"] <= 10
        assert scores["risk_level"] in ("low", "medium", "high")
        
        # Strategic content
        assert "execution_strategy" in data
        assert "success_criteria" in data
        assert isinstance(data["success_criteria"], list)
        
        # Milestones
        assert len(data["milestones"]) >= 2
        for ms in data["milestones"]:
            assert "milestone_id" in ms
            assert "title" in ms
            assert "phase" in ms
            assert "status" in ms
            assert "task_ids" in ms
        
        # Tasks detail
        assert len(data["tasks_detail"]) >= 1
        task = data["tasks_detail"][0]
        assert "task_id" in task
        assert "title" in task
        assert "description" in task
        assert "status" in task
        assert "agent_name" in task
        assert "project_id" in task
        assert task["project_id"] == "proj_2814634f13c4"
