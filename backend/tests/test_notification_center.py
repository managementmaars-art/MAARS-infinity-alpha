"""
Test Notification Center Feature (Iteration 32)
Features tested:
- GET /api/notifications - Get notifications and unread count
- POST /api/notifications/{id}/read - Mark single notification as read
- POST /api/notifications/read-all - Mark all notifications as read
- DELETE /api/notifications/clear - Clear read notifications
- New user registration creates welcome notification
- Notification endpoints require authentication
- Regression tests for insights and agents endpoints
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"
TEST_USER_EMAIL = "notify_test@test.com"
TEST_USER_PASSWORD = "Test1234!"


class TestNotificationAuth:
    """Test that notification endpoints require authentication"""

    def test_get_notifications_requires_auth(self):
        """GET /api/notifications should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASSED: GET /api/notifications requires authentication")

    def test_mark_read_requires_auth(self):
        """POST /api/notifications/{id}/read should return 401 without token"""
        response = requests.post(f"{BASE_URL}/api/notifications/test_id/read")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: POST /api/notifications/{id}/read requires authentication")

    def test_mark_all_read_requires_auth(self):
        """POST /api/notifications/read-all should return 401 without token"""
        response = requests.post(f"{BASE_URL}/api/notifications/read-all")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: POST /api/notifications/read-all requires authentication")

    def test_clear_notifications_requires_auth(self):
        """DELETE /api/notifications/clear should return 401 without token"""
        response = requests.delete(f"{BASE_URL}/api/notifications/clear")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: DELETE /api/notifications/clear requires authentication")


class TestNotificationEndpoints:
    """Test notification CRUD operations with authenticated user"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for test user"""
        # Login with existing test user
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Could not login test user: {response.text}")
        self.token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        print(f"Logged in as {TEST_USER_EMAIL}")
    
    def test_get_notifications_returns_array_and_count(self):
        """GET /api/notifications should return notifications array and unread_count"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "notifications" in data, "Response should have 'notifications' key"
        assert "unread_count" in data, "Response should have 'unread_count' key"
        assert isinstance(data["notifications"], list), "notifications should be a list"
        assert isinstance(data["unread_count"], int), "unread_count should be an integer"
        print(f"PASSED: GET /api/notifications returns {len(data['notifications'])} notifications, {data['unread_count']} unread")
        return data
    
    def test_notification_structure(self):
        """Notifications should have correct schema"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        if data["notifications"]:
            notif = data["notifications"][0]
            expected_fields = ["notification_id", "user_id", "type", "title", "message", "read", "created_at"]
            for field in expected_fields:
                assert field in notif, f"Notification missing field: {field}"
            # link is optional
            assert notif["notification_id"].startswith("notif_"), f"notification_id should start with 'notif_'"
            assert isinstance(notif["read"], bool), "read should be boolean"
            print(f"PASSED: Notification has correct structure: {list(notif.keys())}")
        else:
            print("SKIPPED: No notifications to verify structure (test user may not have any)")
    
    def test_mark_notification_as_read(self):
        """POST /api/notifications/{id}/read should mark notification as read"""
        # First get notifications
        get_resp = requests.get(f"{BASE_URL}/api/notifications", headers=self.headers)
        assert get_resp.status_code == 200
        
        notifications = get_resp.json().get("notifications", [])
        unread = [n for n in notifications if not n.get("read")]
        
        if not unread:
            print("SKIPPED: No unread notifications to mark as read")
            return
        
        notif_id = unread[0]["notification_id"]
        
        # Mark as read
        response = requests.post(
            f"{BASE_URL}/api/notifications/{notif_id}/read",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        
        # Verify it's now read
        verify_resp = requests.get(f"{BASE_URL}/api/notifications", headers=self.headers)
        notifs = verify_resp.json().get("notifications", [])
        marked = next((n for n in notifs if n["notification_id"] == notif_id), None)
        
        if marked:
            assert marked["read"] == True, "Notification should be marked as read"
        
        print(f"PASSED: Notification {notif_id} marked as read")
    
    def test_mark_all_notifications_as_read(self):
        """POST /api/notifications/read-all should mark all as read"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/read-all",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        
        # Verify all are read
        verify_resp = requests.get(f"{BASE_URL}/api/notifications", headers=self.headers)
        verify_data = verify_resp.json()
        
        assert verify_data["unread_count"] == 0, f"unread_count should be 0 after read-all, got {verify_data['unread_count']}"
        print(f"PASSED: All notifications marked as read (unread_count=0)")
    
    def test_clear_read_notifications(self):
        """DELETE /api/notifications/clear should remove read notifications"""
        response = requests.delete(
            f"{BASE_URL}/api/notifications/clear",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        
        # Verify read notifications are cleared
        verify_resp = requests.get(f"{BASE_URL}/api/notifications", headers=self.headers)
        notifs = verify_resp.json().get("notifications", [])
        
        for notif in notifs:
            # If any remain, they should be unread
            if notif.get("read"):
                pytest.fail(f"Read notification {notif['notification_id']} should have been cleared")
        
        print(f"PASSED: Read notifications cleared, {len(notifs)} remaining (all unread or none)")


class TestWelcomeNotification:
    """Test that new user registration creates welcome notification"""
    
    def test_new_user_gets_welcome_notification(self):
        """Registering a new user should auto-create welcome notification"""
        # Generate unique email
        unique_suffix = uuid.uuid4().hex[:8]
        new_email = f"test_notif_{unique_suffix}@test.com"
        new_password = "Test1234!"
        new_name = f"Test User {unique_suffix}"
        
        # Register new user
        register_resp = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": new_email, "password": new_password, "name": new_name}
        )
        
        assert register_resp.status_code == 200, f"Registration failed: {register_resp.text}"
        token = register_resp.json().get("token")
        assert token, "Registration should return token"
        
        # Get notifications for new user
        headers = {"Authorization": f"Bearer {token}"}
        notif_resp = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        
        assert notif_resp.status_code == 200, f"Failed to get notifications: {notif_resp.text}"
        data = notif_resp.json()
        
        # Should have at least one notification (welcome)
        notifications = data.get("notifications", [])
        assert len(notifications) > 0, "New user should have at least 1 notification"
        
        # Find welcome notification
        welcome = next((n for n in notifications if n.get("type") == "welcome"), None)
        assert welcome is not None, f"Welcome notification not found. Types: {[n.get('type') for n in notifications]}"
        
        assert "Welcome" in welcome.get("title", ""), f"Welcome notification title wrong: {welcome.get('title')}"
        assert welcome.get("read") == False, "Welcome notification should be unread"
        
        # Verify unread count
        assert data.get("unread_count", 0) >= 1, "Should have at least 1 unread notification"
        
        print(f"PASSED: New user {new_email} got welcome notification: {welcome.get('title')}")


class TestRegressionEndpoints:
    """Regression tests for existing endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Could not login admin: {response.text}")
        self.token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_user_insights_endpoint_still_works(self):
        """GET /api/user/insights should still work (regression)"""
        response = requests.get(
            f"{BASE_URL}/api/user/insights",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "stats" in data, "Should have stats"
        assert "favorite_agents" in data, "Should have favorite_agents"
        assert "recommendations" in data, "Should have recommendations"
        assert "daily_activity" in data, "Should have daily_activity"
        
        print(f"PASSED: /api/user/insights still returns correct structure")
    
    def test_agents_endpoint_returns_21_agents(self):
        """GET /api/agents should return 21 agents (regression)"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        agents = response.json()
        assert isinstance(agents, list), "Should return list of agents"
        assert len(agents) == 21, f"Expected 21 agents, got {len(agents)}"
        
        # Check Commander is first
        assert agents[0].get("agent_id") == "agent_commander", "Commander should be first"
        
        print(f"PASSED: /api/agents returns {len(agents)} agents with Commander first")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
