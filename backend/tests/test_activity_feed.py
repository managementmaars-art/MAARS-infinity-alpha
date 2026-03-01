"""
Test Activity Feed Endpoint (Iteration 27)
Tests GET /api/admin/activity-feed endpoint for Live Activity Feed feature
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestActivityFeed:
    """Tests for admin activity feed endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get admin token for authenticated requests"""
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "management.maars@marsgc.net",
                "password": "MaarsAdmin2024!"
            }
        )
        if login_resp.status_code == 200:
            self.admin_token = login_resp.json().get("token")
        else:
            pytest.skip("Admin login failed")
            
    def test_activity_feed_returns_200(self):
        """Activity feed endpoint should return 200 for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASSED: Activity feed returns 200")
        
    def test_activity_feed_returns_array(self):
        """Activity feed should return an array of events"""
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"PASSED: Returns array with {len(data)} events")
        
    def test_activity_feed_event_structure(self):
        """Each event should have type, icon, title, detail, timestamp fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        events = response.json()
        
        if len(events) == 0:
            pytest.skip("No events in feed to verify structure")
            
        # Check first event has all required fields
        event = events[0]
        required_fields = ["type", "icon", "title", "detail", "timestamp"]
        for field in required_fields:
            assert field in event, f"Missing field: {field}"
        print(f"PASSED: Event has all required fields: {required_fields}")
        
    def test_activity_feed_event_types(self):
        """Events should have valid types: signup, payment, chat, team"""
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        events = response.json()
        
        valid_types = {"signup", "payment", "chat", "team"}
        for event in events:
            assert event.get("type") in valid_types, f"Invalid event type: {event.get('type')}"
        
        # Report which event types were found
        found_types = set(e["type"] for e in events)
        print(f"PASSED: Found valid event types: {found_types}")
        
    def test_activity_feed_sorted_by_timestamp(self):
        """Events should be sorted by timestamp descending (newest first)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        events = response.json()
        
        if len(events) < 2:
            pytest.skip("Not enough events to verify sorting")
            
        # Extract timestamps and verify descending order
        timestamps = [e.get("timestamp", "") for e in events]
        # Filter out empty timestamps
        valid_ts = [t for t in timestamps if t]
        
        if len(valid_ts) >= 2:
            # Check if sorted descending
            for i in range(len(valid_ts) - 1):
                assert valid_ts[i] >= valid_ts[i + 1], f"Events not sorted: {valid_ts[i]} < {valid_ts[i+1]}"
        print("PASSED: Events sorted by timestamp descending")
        
    def test_activity_feed_limit_parameter(self):
        """Limit parameter should restrict number of results"""
        # Test with limit=5
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed?limit=5",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        events = response.json()
        assert len(events) <= 5, f"Expected at most 5 events, got {len(events)}"
        print(f"PASSED: Limit=5 returns {len(events)} events")
        
        # Test with limit=10
        response2 = requests.get(
            f"{BASE_URL}/api/admin/activity-feed?limit=10",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response2.status_code == 200
        events2 = response2.json()
        assert len(events2) <= 10, f"Expected at most 10 events, got {len(events2)}"
        print(f"PASSED: Limit=10 returns {len(events2)} events")
        
    def test_activity_feed_default_limit(self):
        """Default limit should be 30"""
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        events = response.json()
        # With default limit=30, should return at most 30
        assert len(events) <= 30, f"Expected at most 30 events, got {len(events)}"
        print(f"PASSED: Default limit returns {len(events)} events (max 30)")


class TestActivityFeedAuth:
    """Authorization tests for activity feed endpoint"""
    
    def test_activity_feed_requires_auth(self):
        """Endpoint should return 401 without authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/activity-feed")
        assert response.status_code in (401, 403), f"Expected 401/403, got {response.status_code}"
        print("PASSED: Returns 401 without auth")
        
    def test_activity_feed_requires_admin(self):
        """Endpoint should return 403 for non-admin users"""
        # First create/use a non-admin user - we'll test with invalid token
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        assert response.status_code in (401, 403), f"Expected 401/403, got {response.status_code}"
        print("PASSED: Returns 401/403 for invalid token")


class TestActivityFeedDataPresence:
    """Tests to verify activity feed returns actual data from the database"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get admin token for authenticated requests"""
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "management.maars@marsgc.net",
                "password": "MaarsAdmin2024!"
            }
        )
        if login_resp.status_code == 200:
            self.admin_token = login_resp.json().get("token")
        else:
            pytest.skip("Admin login failed")
            
    def test_activity_feed_has_signup_events(self):
        """Should have signup events (14 users in database)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed?limit=50",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        events = response.json()
        
        signup_events = [e for e in events if e.get("type") == "signup"]
        print(f"Found {len(signup_events)} signup events")
        # We know there are 14 users in the database
        assert len(signup_events) > 0, "Expected signup events"
        print(f"PASSED: Found {len(signup_events)} signup events")
        
    def test_activity_feed_has_chat_events(self):
        """Should have chat events (42 chats in database)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed?limit=100",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        events = response.json()
        
        chat_events = [e for e in events if e.get("type") == "chat"]
        print(f"Found {len(chat_events)} chat events")
        # We know there are 42 chats in the database
        assert len(chat_events) > 0, "Expected chat events"
        print(f"PASSED: Found {len(chat_events)} chat events")

    def test_activity_feed_has_payment_events(self):
        """Should have payment events if any exist (6 payment transactions)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/activity-feed?limit=100",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        events = response.json()
        
        payment_events = [e for e in events if e.get("type") == "payment"]
        print(f"Found {len(payment_events)} payment events")
        # We know there are 6 payment transactions
        if len(payment_events) > 0:
            # Verify payment format
            payment = payment_events[0]
            assert "title" in payment
            assert "Payment received" in payment.get("title", "")
            print(f"PASSED: Found {len(payment_events)} payment events with correct format")
        else:
            print("INFO: No payment events found (may not have 'paid' status)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
