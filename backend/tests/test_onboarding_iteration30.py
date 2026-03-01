"""
Iteration 30: Onboarding Flow Tests
Tests user onboarding flow - new user registration, onboarding_completed field, and /auth/onboarding-complete endpoint
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"

# Generate unique test user for this run
TEST_USER_PREFIX = f"testuser_onboard_{uuid.uuid4().hex[:8]}"
TEST_USER_EMAIL = f"{TEST_USER_PREFIX}@test.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Onboarding Test User"


class TestAdminLogin:
    """Regression: Admin can login"""
    
    def test_admin_login_success(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token returned"
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"✓ Admin login successful")


class TestOnboardingEndpoints:
    """Tests for onboarding-related API endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["token"]
    
    def test_admin_me_returns_onboarding_completed(self, admin_token):
        """Admin user (who completed onboarding) should have onboarding_completed=true"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"GET /auth/me failed: {response.text}"
        data = response.json()
        
        # Verify onboarding_completed field exists
        assert "onboarding_completed" in data, "onboarding_completed field missing from /auth/me response"
        # Admin should have completed onboarding (from previous iterations)
        assert data["onboarding_completed"] == True, f"Admin should have onboarding_completed=true, got: {data['onboarding_completed']}"
        print(f"✓ Admin /auth/me returns onboarding_completed=true")
    
    def test_admin_me_response_structure(self, admin_token):
        """Verify /auth/me returns all expected fields"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["user_id", "email", "name", "is_admin", "created_at", "onboarding_completed"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"✓ /auth/me returns all required fields: {required_fields}")


class TestNewUserOnboarding:
    """Tests for new user registration and onboarding flow"""
    
    @pytest.fixture(scope="class")
    def new_user_token(self):
        """Register a new test user and return their token"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token returned from registration"
        print(f"✓ New test user registered: {TEST_USER_EMAIL}")
        return data["token"]
    
    def test_new_user_onboarding_completed_is_false(self, new_user_token):
        """New users should have onboarding_completed=false by default"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {new_user_token}"}
        )
        assert response.status_code == 200, f"GET /auth/me failed: {response.text}"
        data = response.json()
        
        assert "onboarding_completed" in data, "onboarding_completed field missing"
        assert data["onboarding_completed"] == False, f"New user should have onboarding_completed=false, got: {data['onboarding_completed']}"
        print(f"✓ New user has onboarding_completed=false")
    
    def test_complete_onboarding_endpoint(self, new_user_token):
        """POST /auth/onboarding-complete should mark onboarding as done"""
        response = requests.post(
            f"{BASE_URL}/api/auth/onboarding-complete",
            headers={"Authorization": f"Bearer {new_user_token}"}
        )
        assert response.status_code == 200, f"POST /auth/onboarding-complete failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=true, got: {data}"
        print(f"✓ POST /auth/onboarding-complete returned success=true")
    
    def test_onboarding_completed_persists(self, new_user_token):
        """After calling onboarding-complete, /auth/me should return onboarding_completed=true"""
        # First ensure onboarding-complete was called (idempotent, safe to call again)
        requests.post(
            f"{BASE_URL}/api/auth/onboarding-complete",
            headers={"Authorization": f"Bearer {new_user_token}"}
        )
        
        # Now verify the change persisted
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {new_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["onboarding_completed"] == True, f"After completion, onboarding_completed should be true, got: {data['onboarding_completed']}"
        print(f"✓ onboarding_completed=true persisted after calling /auth/onboarding-complete")


class TestRegressionEndpoints:
    """Regression tests for existing functionality"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_agents_endpoint_returns_list(self, admin_token):
        """GET /api/agents should return agent list"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"GET /agents failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of agents"
        assert len(data) > 0, "Expected at least one agent"
        print(f"✓ GET /agents returns {len(data)} agents")
    
    def test_admin_analytics_endpoint(self, admin_token):
        """GET /api/admin/analytics should return analytics data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"GET /admin/analytics failed: {response.text}"
        data = response.json()
        
        # Verify KPI fields exist
        expected_kpis = ["total_users", "total_chats", "total_revenue", "mrr"]
        for kpi in expected_kpis:
            assert kpi in data, f"Missing KPI: {kpi}"
        
        print(f"✓ GET /admin/analytics returns KPIs: {expected_kpis}")
    
    def test_agents_public_endpoint(self):
        """GET /api/agents/public should return public agents without auth"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200, f"GET /agents/public failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of agents"
        assert len(data) > 0, "Expected at least one public agent"
        print(f"✓ GET /agents/public returns {len(data)} agents (no auth required)")


class TestFeedbackRegression:
    """Regression: Feedback buttons should still work"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_agent_performance_endpoint(self, admin_token):
        """GET /api/admin/agent-performance should return agent performance data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/agent-performance",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"GET /admin/agent-performance failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of agent performance data"
        
        if len(data) > 0:
            # Verify expected fields
            agent = data[0]
            expected_fields = ["agent_id", "name", "total_messages", "thumbs_up", "thumbs_down"]
            for field in expected_fields:
                assert field in agent, f"Missing field: {field}"
        
        print(f"✓ GET /admin/agent-performance returns {len(data)} agents with performance metrics")


# Cleanup fixture to delete test user after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_user():
    """Cleanup: delete test user after all tests complete"""
    yield
    # Note: In production, you'd delete the test user here
    # For now, test users are left in DB (prefixed with testuser_onboard_)
    print(f"Note: Test user {TEST_USER_EMAIL} created during tests")
