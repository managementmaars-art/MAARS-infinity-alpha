"""
Iteration 48: Testing New P0/P1 Features
- GET /api/admin/integration-status - Tool status dashboard
- GET /api/teams/{team_id}/stats - Team statistics 
- GET /api/teams/{team_id}/activity - Team activity feed
- Google Suite delegate_email field in INTEGRATION_SERVICES
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://multi-agent-ai-16.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"
TEST_USER_EMAIL = "test@test.com"
TEST_USER_PASSWORD = "test123"
TEST_TEAM_ID = "team_72034d0a7167"


class TestHealthCheck:
    """Basic health check to ensure backend is running"""
    
    def test_health_endpoint(self):
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200, f"Health check failed: {resp.text}"
        data = resp.json()
        assert data.get("status") == "ok"
        print("PASSED: Health check - status: ok")


class TestAdminIntegrationStatus:
    """Test GET /api/admin/integration-status endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        token = resp.json().get("token")
        assert token, "No token returned"
        return token
    
    def test_integration_status_requires_auth(self):
        """Endpoint should require admin authentication"""
        resp = requests.get(f"{BASE_URL}/api/admin/integration-status")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        print("PASSED: integration-status requires auth")
    
    def test_integration_status_returns_tools(self, admin_token):
        """Should return list of tools with status"""
        resp = requests.get(
            f"{BASE_URL}/api/admin/integration-status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200, f"Failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        # Check structure
        assert "tools" in data, "Response missing 'tools' field"
        assert "active_count" in data, "Response missing 'active_count' field"
        assert "total_count" in data, "Response missing 'total_count' field"
        
        # Check tools array
        tools = data["tools"]
        assert isinstance(tools, list), "tools should be a list"
        assert len(tools) > 0, "tools list should not be empty"
        
        # Each tool should have required fields
        for tool in tools:
            assert "tool_name" in tool, f"Tool missing 'tool_name': {tool}"
            assert "display_name" in tool, f"Tool missing 'display_name': {tool}"
            assert "status" in tool, f"Tool missing 'status': {tool}"
            assert tool["status"] in ["active", "inactive"], f"Invalid status: {tool['status']}"
            assert "reason" in tool, f"Tool missing 'reason': {tool}"
        
        # Core tools (no integration required) should be active
        core_tools = ["web_search", "calculate", "create_task", "analyze_data", "query_tasks", "update_task"]
        active_tools = [t["tool_name"] for t in tools if t["status"] == "active"]
        for core_tool in core_tools:
            assert core_tool in active_tools, f"Core tool {core_tool} should be active"
        
        print(f"PASSED: integration-status returns {len(tools)} tools, {data['active_count']} active")
    
    def test_google_calendar_and_gmail_tools_exist(self, admin_token):
        """Google Calendar and Gmail tools should be in the list"""
        resp = requests.get(
            f"{BASE_URL}/api/admin/integration-status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        tools = resp.json()["tools"]
        tool_names = [t["tool_name"] for t in tools]
        
        assert "google_calendar" in tool_names, "google_calendar tool not found"
        assert "send_gmail" in tool_names, "send_gmail tool not found"
        
        # These should require google_suite
        for tool in tools:
            if tool["tool_name"] in ["google_calendar", "send_gmail"]:
                assert tool.get("requires_service") == "google_suite", f"{tool['tool_name']} should require google_suite"
        
        print("PASSED: google_calendar and send_gmail tools exist and require google_suite")


class TestTeamStats:
    """Test GET /api/teams/{team_id}/stats endpoint"""
    
    @pytest.fixture
    def user_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD
        })
        assert resp.status_code == 200, f"User login failed: {resp.text}"
        return resp.json().get("token")
    
    def test_team_stats_requires_auth(self):
        """Endpoint should require authentication"""
        resp = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/stats")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        print("PASSED: team stats requires auth")
    
    def test_team_stats_returns_expected_fields(self, user_token):
        """Should return member_count, total_chats, shared_chats, members array"""
        resp = requests.get(
            f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/stats",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert resp.status_code == 200, f"Failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        # Check required fields
        assert "team_id" in data, "Missing team_id"
        assert "member_count" in data, "Missing member_count"
        assert "total_chats" in data, "Missing total_chats"
        assert "shared_chats" in data, "Missing shared_chats"
        assert "members" in data, "Missing members array"
        
        # Validate types
        assert isinstance(data["member_count"], int), "member_count should be int"
        assert isinstance(data["total_chats"], int), "total_chats should be int"
        assert isinstance(data["shared_chats"], int), "shared_chats should be int"
        assert isinstance(data["members"], list), "members should be a list"
        
        # Each member should have required fields
        for member in data["members"]:
            assert "user_id" in member
            assert "name" in member
            assert "email" in member
            assert "role" in member
            assert "chats" in member
        
        print(f"PASSED: team stats - {data['member_count']} members, {data['total_chats']} total chats, {data['shared_chats']} shared")
    
    def test_team_stats_404_for_invalid_team(self, user_token):
        """Should return 404 for non-existent team"""
        resp = requests.get(
            f"{BASE_URL}/api/teams/invalid_team_id/stats",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print("PASSED: team stats returns 404 for invalid team")


class TestTeamActivity:
    """Test GET /api/teams/{team_id}/activity endpoint"""
    
    @pytest.fixture
    def user_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD
        })
        assert resp.status_code == 200
        return resp.json().get("token")
    
    def test_team_activity_requires_auth(self):
        """Endpoint should require authentication"""
        resp = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/activity")
        assert resp.status_code == 401
        print("PASSED: team activity requires auth")
    
    def test_team_activity_returns_array(self, user_token):
        """Should return activity array"""
        resp = requests.get(
            f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/activity",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert resp.status_code == 200, f"Failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        # Should return a list
        assert isinstance(data, list), "Activity should be a list"
        
        # If there's activity, check structure
        for item in data:
            assert "type" in item, "Activity item missing 'type'"
            assert "user_name" in item, "Activity item missing 'user_name'"
            assert "title" in item, "Activity item missing 'title'"
            assert "timestamp" in item, "Activity item missing 'timestamp'"
        
        print(f"PASSED: team activity returns array with {len(data)} items")
    
    def test_team_activity_with_limit(self, user_token):
        """Should respect limit parameter"""
        resp = requests.get(
            f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/activity?limit=5",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) <= 5, f"Expected max 5 items, got {len(data)}"
        print("PASSED: team activity respects limit parameter")
    
    def test_team_activity_404_for_invalid_team(self, user_token):
        """Should return 404 for non-existent team"""
        resp = requests.get(
            f"{BASE_URL}/api/teams/invalid_team_id/activity",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert resp.status_code == 404
        print("PASSED: team activity returns 404 for invalid team")


class TestAdminIntegrationsGoogleSuite:
    """Test that Google Suite config includes delegate_email field"""
    
    @pytest.fixture
    def admin_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        return resp.json().get("token")
    
    def test_integrations_includes_google_suite(self, admin_token):
        """GET /api/admin/integrations should include google_suite with delegate_email"""
        resp = requests.get(
            f"{BASE_URL}/api/admin/integrations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Check google_suite exists
        assert "google_suite" in data, "google_suite not in integrations"
        gs = data["google_suite"]
        
        # Check key_fields includes delegate_email
        assert "key_fields" in gs, "google_suite missing key_fields"
        key_fields = gs["key_fields"]
        assert "service_account_json" in key_fields, "google_suite missing service_account_json field"
        assert "delegate_email" in key_fields, "google_suite missing delegate_email field"
        
        print(f"PASSED: google_suite has key_fields: {key_fields}")


class TestAdminLogin:
    """Test admin login and basic access"""
    
    def test_admin_login(self):
        """Admin can login successfully"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        data = resp.json()
        assert "token" in data
        assert data.get("user", {}).get("is_admin") == True, "User should be admin"
        print("PASSED: Admin login successful, is_admin=True")
    
    def test_user_login(self):
        """Regular user can login"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD
        })
        assert resp.status_code == 200, f"User login failed: {resp.text}"
        print("PASSED: Regular user login successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
