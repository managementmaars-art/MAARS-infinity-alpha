"""
Iteration 47: Test enhancement features - Chat Search, Message Pin/Export, Enhanced Analytics, Admin Audit Log
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
assert BASE_URL, "REACT_APP_BACKEND_URL must be set"

ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"
TEST_USER_EMAIL = "test@test.com"
TEST_USER_PASSWORD = "test123"


class TestHealthAndBasicEndpoints:
    """Basic endpoint tests"""

    def test_health_check(self):
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"
        print("PASS: Health check - status: ok")

    def test_public_agents(self):
        resp = requests.get(f"{BASE_URL}/api/agents/public")
        assert resp.status_code == 200
        agents = resp.json()
        assert len(agents) > 0
        print(f"PASS: Public agents - {len(agents)} agents returned")


class TestAuthentication:
    """Authentication tests"""

    def test_admin_login(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Admin login failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert "token" in data
        assert data.get("user", {}).get("is_admin") == True
        print("PASS: Admin login successful with is_admin=True")
        return data["token"]

    def test_user_login(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        # User may or may not exist
        if resp.status_code == 200:
            print("PASS: Test user login successful")
            return resp.json()["token"]
        else:
            print(f"INFO: Test user not found, will use admin for testing")
            return None


class TestChatSearchEndpoint:
    """Test /api/chats/search endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        # Login as admin
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        self.token = resp.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_chat_search_endpoint_exists(self):
        """Test that chat search endpoint returns valid response"""
        resp = requests.get(f"{BASE_URL}/api/chats/search?q=test", headers=self.headers)
        assert resp.status_code == 200, f"Chat search failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert "results" in data
        assert "total_matches" in data
        assert "query" in data
        print(f"PASS: Chat search endpoint works - {data.get('total_matches', 0)} matches for 'test'")

    def test_chat_search_requires_min_query(self):
        """Test that search requires at least 2 characters"""
        resp = requests.get(f"{BASE_URL}/api/chats/search?q=a", headers=self.headers)
        assert resp.status_code == 400
        print("PASS: Chat search correctly rejects query < 2 chars")


class TestChatExportEndpoint:
    """Test /api/chats/{chat_id}/export endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        self.token = resp.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_get_chats_and_export(self):
        """Test chat export functionality"""
        # Get user's chats
        resp = requests.get(f"{BASE_URL}/api/chats", headers=self.headers)
        assert resp.status_code == 200
        chats = resp.json()
        
        if len(chats) == 0:
            print("INFO: No chats found, skipping export test")
            pytest.skip("No chats available for export test")
        
        chat_id = chats[0]["chat_id"]
        
        # Test export endpoint
        resp = requests.get(f"{BASE_URL}/api/chats/{chat_id}/export", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data
        assert "title" in data
        assert "message_count" in data
        print(f"PASS: Chat export works - exported chat with {data.get('message_count', 0)} messages")


class TestMessagePinEndpoint:
    """Test /api/chats/{chat_id}/messages/{msg_id}/pin endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        self.token = resp.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_pin_message_toggle(self):
        """Test message pin/unpin functionality"""
        # Get user's chats
        resp = requests.get(f"{BASE_URL}/api/chats", headers=self.headers)
        assert resp.status_code == 200
        chats = resp.json()
        
        # Find a chat with messages
        chat_with_messages = None
        msg_id = None
        for chat in chats:
            if chat.get("messages") and len(chat.get("messages", [])) > 0:
                for msg in chat["messages"]:
                    if msg.get("role") == "assistant" and msg.get("message_id"):
                        chat_with_messages = chat
                        msg_id = msg["message_id"]
                        break
                if msg_id:
                    break
        
        if not msg_id:
            print("INFO: No assistant messages found to pin")
            pytest.skip("No assistant messages available for pin test")
        
        chat_id = chat_with_messages["chat_id"]
        
        # Test pin toggle
        resp = requests.post(f"{BASE_URL}/api/chats/{chat_id}/messages/{msg_id}/pin", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data
        assert "pinned" in data
        assert data["success"] == True
        print(f"PASS: Message pin toggle works - pinned: {data['pinned']}")
    
    def test_get_pinned_messages(self):
        """Test fetching pinned messages"""
        resp = requests.get(f"{BASE_URL}/api/chats", headers=self.headers)
        assert resp.status_code == 200
        chats = resp.json()
        
        if len(chats) == 0:
            pytest.skip("No chats available")
        
        chat_id = chats[0]["chat_id"]
        resp = requests.get(f"{BASE_URL}/api/chats/{chat_id}/pinned", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"PASS: Get pinned messages works - {len(data)} pinned messages")


class TestAdminAuditLogEndpoint:
    """Test /api/admin/audit-log endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        self.token = resp.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_audit_log_endpoint(self):
        """Test audit log retrieval"""
        resp = requests.get(f"{BASE_URL}/api/admin/audit-log", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"PASS: Audit log endpoint works - {len(data)} entries")
        
        # Check structure if entries exist
        if len(data) > 0:
            entry = data[0]
            # Audit log entries should have these fields
            print(f"  - Sample entry: action={entry.get('action')}, admin={entry.get('admin_email')}")


class TestEnhancedAnalyticsEndpoints:
    """Test enhanced analytics endpoints - retention, projections, credit-burn"""

    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        self.token = resp.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_retention_analytics(self):
        """Test /api/admin/analytics/retention endpoint"""
        resp = requests.get(f"{BASE_URL}/api/admin/analytics/retention", headers=self.headers)
        assert resp.status_code == 200, f"Retention failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"PASS: Retention analytics - {len(data)} weekly cohorts returned")
        
        if len(data) > 0:
            cohort = data[0]
            assert "week" in cohort or "week_start" in cohort
            assert "signed_up" in cohort
            print(f"  - Sample cohort: {cohort.get('week', cohort.get('week_start'))}, signed_up={cohort.get('signed_up')}")

    def test_projections_analytics(self):
        """Test /api/admin/analytics/projections endpoint"""
        resp = requests.get(f"{BASE_URL}/api/admin/analytics/projections", headers=self.headers)
        assert resp.status_code == 200, f"Projections failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        assert "current" in data
        assert "projections" in data
        
        current = data["current"]
        assert "mrr" in current
        assert "revenue_30d" in current
        assert "profit_margin" in current
        
        print(f"PASS: Revenue projections - MRR=${current.get('mrr')}, 30d Rev=${current.get('revenue_30d')}")
        print(f"  - {len(data['projections'])} month projections returned")

    def test_credit_burn_analytics(self):
        """Test /api/admin/analytics/credit-burn endpoint"""
        resp = requests.get(f"{BASE_URL}/api/admin/analytics/credit-burn", headers=self.headers)
        assert resp.status_code == 200, f"Credit burn failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        # Should have by_model, by_agent, daily_burn
        assert "by_model" in data or "daily_burn" in data
        print(f"PASS: Credit burn analytics returned")
        
        if "by_model" in data and len(data["by_model"]) > 0:
            print(f"  - {len(data['by_model'])} models tracked")
        if "by_agent" in data and len(data["by_agent"]) > 0:
            print(f"  - {len(data['by_agent'])} agents tracked")
        if "daily_burn" in data:
            print(f"  - {len(data.get('daily_burn', []))} days of burn data")


class TestMainAnalyticsEndpoint:
    """Test main analytics dashboard endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        self.token = resp.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_analytics_dashboard(self):
        """Test /api/admin/analytics endpoint"""
        resp = requests.get(f"{BASE_URL}/api/admin/analytics", headers=self.headers)
        assert resp.status_code == 200, f"Analytics failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        assert "kpis" in data
        assert "daily_signups" in data
        assert "daily_messages" in data
        
        kpis = data["kpis"]
        print(f"PASS: Analytics dashboard - Users={kpis.get('total_users')}, Chats={kpis.get('total_chats')}")


class TestActivityFeedEndpoint:
    """Test activity feed endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        self.token = resp.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_activity_feed(self):
        """Test /api/admin/activity-feed endpoint"""
        resp = requests.get(f"{BASE_URL}/api/admin/activity-feed?limit=20", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"PASS: Activity feed - {len(data)} events returned")


class TestAgentPerformanceEndpoint:
    """Test agent performance endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        self.token = resp.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_agent_performance(self):
        """Test /api/admin/agent-performance endpoint"""
        resp = requests.get(f"{BASE_URL}/api/admin/agent-performance", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"PASS: Agent performance - {len(data)} agents with performance data")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
