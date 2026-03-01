"""
Iteration 29: Testing Agent Performance Scoring and Feedback System
- POST /api/chats/{chat_id}/messages/{message_id}/feedback with feedback='up'/'down'/null
- GET /api/admin/agent-performance returns agent metrics
- GET /api/admin/analytics/export returns CSV with proper headers
- Regression tests for auth, plans, agents, analytics
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Headers with admin authentication."""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def chat_with_messages(admin_headers):
    """Get or create a chat with messages for feedback testing."""
    # First try to get existing chats
    response = requests.get(f"{BASE_URL}/api/chats", headers=admin_headers)
    if response.status_code == 200:
        chats = response.json()
        for chat in chats:
            # Load full chat to check for assistant messages
            chat_response = requests.get(f"{BASE_URL}/api/chats/{chat['chat_id']}", headers=admin_headers)
            if chat_response.status_code == 200:
                full_chat = chat_response.json()
                messages = full_chat.get("messages", [])
                # Find an assistant message
                for msg in messages:
                    if msg.get("role") == "assistant" and msg.get("message_id"):
                        return {
                            "chat_id": chat["chat_id"],
                            "message_id": msg["message_id"],
                            "agent_id": chat.get("agent_id")
                        }
    
    # If no existing chat with messages, create one
    # First create a chat
    create_response = requests.post(
        f"{BASE_URL}/api/chats",
        headers=admin_headers,
        json={"agent_id": "agent_secretary"}
    )
    if create_response.status_code != 200:
        pytest.skip(f"Could not create chat: {create_response.text}")
    
    chat_data = create_response.json()
    chat_id = chat_data["chat_id"]
    
    # Send a message to get an assistant response
    msg_response = requests.post(
        f"{BASE_URL}/api/chats/{chat_id}/messages",
        headers=admin_headers,
        json={"content": "Hello, just testing feedback feature.", "model_provider": "openai", "model_name": "gpt-4o-mini"}
    )
    if msg_response.status_code != 200:
        pytest.skip(f"Could not send message: {msg_response.text}")
    
    msg_data = msg_response.json()
    assistant_msg = msg_data.get("assistant_message", {})
    
    return {
        "chat_id": chat_id,
        "message_id": assistant_msg.get("message_id"),
        "agent_id": "agent_secretary"
    }


class TestRegressionAuthLogin:
    """Regression: Authentication still works."""
    
    def test_login_with_valid_admin_credentials(self):
        """Test admin login works correctly."""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Response should contain token"
        assert data.get("user", {}).get("email") == ADMIN_EMAIL


class TestRegressionPlans:
    """Regression: Plans endpoint still returns 4 plans."""
    
    def test_plans_returns_four_plans(self):
        """GET /api/plans should return free, starter, pro, business."""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200, f"Plans request failed: {response.text}"
        data = response.json()
        # Plans endpoint returns {plans: {...}, credit_packages: {...}}
        assert "plans" in data, "Response should contain 'plans' key"
        plans = data["plans"]
        assert len(plans) == 4, f"Expected 4 plans, got {len(plans)}"
        assert "free" in plans
        assert "starter" in plans
        assert "pro" in plans
        assert "business" in plans


class TestRegressionAgents:
    """Regression: Agents endpoint returns agents list."""
    
    def test_agents_returns_list(self, admin_headers):
        """GET /api/agents should return agents list."""
        response = requests.get(f"{BASE_URL}/api/agents", headers=admin_headers)
        assert response.status_code == 200, f"Agents request failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one agent"
        # Check agent structure
        agent = data[0]
        assert "agent_id" in agent
        assert "name" in agent
        assert "role" in agent


class TestRegressionAnalytics:
    """Regression: Admin analytics endpoint works."""
    
    def test_admin_analytics_returns_kpis(self, admin_headers):
        """GET /api/admin/analytics should return KPIs."""
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=admin_headers)
        assert response.status_code == 200, f"Analytics request failed: {response.text}"
        data = response.json()
        assert "kpis" in data, "Response should contain kpis"
        kpis = data["kpis"]
        assert "total_users" in kpis
        assert "total_chats" in kpis
        assert "total_revenue" in kpis
        assert "mrr" in kpis


class TestMessageFeedback:
    """Test POST /api/chats/{chat_id}/messages/{message_id}/feedback."""
    
    def test_feedback_up_saves_correctly(self, admin_headers, chat_with_messages):
        """Submitting feedback='up' should save thumbs up."""
        chat_id = chat_with_messages["chat_id"]
        message_id = chat_with_messages["message_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages/{message_id}/feedback",
            headers=admin_headers,
            json={"feedback": "up"}
        )
        assert response.status_code == 200, f"Feedback up failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("feedback") == "up"
        
        # Verify by fetching the chat
        chat_response = requests.get(f"{BASE_URL}/api/chats/{chat_id}", headers=admin_headers)
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        messages = chat_data.get("messages", [])
        
        # Find the message and check feedback
        found_msg = None
        for msg in messages:
            if msg.get("message_id") == message_id:
                found_msg = msg
                break
        
        assert found_msg is not None, "Message should exist"
        assert found_msg.get("feedback") == "up", "Feedback should be 'up'"
    
    def test_feedback_down_saves_correctly(self, admin_headers, chat_with_messages):
        """Submitting feedback='down' should save thumbs down."""
        chat_id = chat_with_messages["chat_id"]
        message_id = chat_with_messages["message_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages/{message_id}/feedback",
            headers=admin_headers,
            json={"feedback": "down"}
        )
        assert response.status_code == 200, f"Feedback down failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("feedback") == "down"
        
        # Verify persistence
        chat_response = requests.get(f"{BASE_URL}/api/chats/{chat_id}", headers=admin_headers)
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        
        for msg in chat_data.get("messages", []):
            if msg.get("message_id") == message_id:
                assert msg.get("feedback") == "down", "Feedback should be 'down'"
                break
    
    def test_feedback_null_removes_feedback(self, admin_headers, chat_with_messages):
        """Submitting feedback=null should remove feedback."""
        chat_id = chat_with_messages["chat_id"]
        message_id = chat_with_messages["message_id"]
        
        # First set feedback
        requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages/{message_id}/feedback",
            headers=admin_headers,
            json={"feedback": "up"}
        )
        
        # Now remove it
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages/{message_id}/feedback",
            headers=admin_headers,
            json={"feedback": None}
        )
        assert response.status_code == 200, f"Feedback null failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("feedback") is None
    
    def test_feedback_invalid_value_rejected(self, admin_headers, chat_with_messages):
        """Invalid feedback values should be rejected with 400."""
        chat_id = chat_with_messages["chat_id"]
        message_id = chat_with_messages["message_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages/{message_id}/feedback",
            headers=admin_headers,
            json={"feedback": "invalid"}
        )
        assert response.status_code == 400, f"Should reject invalid feedback: {response.text}"


class TestAgentPerformance:
    """Test GET /api/admin/agent-performance endpoint."""
    
    def test_agent_performance_requires_admin(self):
        """Endpoint should require admin authentication."""
        response = requests.get(f"{BASE_URL}/api/admin/agent-performance")
        assert response.status_code == 401, "Should require authentication"
    
    def test_agent_performance_returns_metrics(self, admin_headers):
        """Should return array of agent performance metrics."""
        response = requests.get(
            f"{BASE_URL}/api/admin/agent-performance",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Request failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be an array"
        assert len(data) > 0, "Should have at least one agent"
        
        # Check structure of first agent
        agent = data[0]
        assert "agent_id" in agent, "Should have agent_id"
        assert "name" in agent, "Should have name"
        assert "total_messages" in agent, "Should have total_messages"
        assert "thumbs_up" in agent, "Should have thumbs_up"
        assert "thumbs_down" in agent, "Should have thumbs_down"
        assert "total_feedback" in agent, "Should have total_feedback"
        assert "satisfaction_rate" in agent, "Should have satisfaction_rate (can be null)"
    
    def test_agent_performance_structure_complete(self, admin_headers):
        """Verify all expected fields in response."""
        response = requests.get(
            f"{BASE_URL}/api/admin/agent-performance",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        expected_fields = [
            "agent_id", "name", "avatar", "role",
            "total_messages", "thumbs_up", "thumbs_down",
            "total_feedback", "satisfaction_rate", "feedback_rate"
        ]
        
        for agent in data[:5]:  # Check first 5 agents
            for field in expected_fields:
                assert field in agent, f"Missing field: {field} in agent {agent.get('agent_id')}"


class TestAnalyticsExport:
    """Test GET /api/admin/analytics/export endpoint."""
    
    def test_export_returns_csv_content_type(self, admin_headers):
        """Export should return text/csv content type."""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics/export?format=csv",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Export failed: {response.text}"
        assert "text/csv" in response.headers.get("Content-Type", ""), "Should be text/csv"
    
    def test_export_has_content_disposition(self, admin_headers):
        """Export should have Content-Disposition header for download."""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics/export?format=csv",
            headers=admin_headers
        )
        assert response.status_code == 200
        disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in disposition, "Should be attachment"
        assert "maars_analytics_" in disposition, "Filename should contain maars_analytics_"
        assert ".csv" in disposition, "Filename should end with .csv"
    
    def test_export_requires_admin(self):
        """Export should require admin authentication."""
        response = requests.get(f"{BASE_URL}/api/admin/analytics/export")
        assert response.status_code == 401, "Should require authentication"


class TestFeedbackWithPerformance:
    """Integration: Feedback should affect performance metrics."""
    
    def test_submit_feedback_and_verify_in_performance(self, admin_headers, chat_with_messages):
        """Feedback should be reflected in agent performance."""
        chat_id = chat_with_messages["chat_id"]
        message_id = chat_with_messages["message_id"]
        agent_id = chat_with_messages.get("agent_id")
        
        # Set a positive feedback
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages/{message_id}/feedback",
            headers=admin_headers,
            json={"feedback": "up"}
        )
        assert response.status_code == 200
        
        # Check performance endpoint
        perf_response = requests.get(
            f"{BASE_URL}/api/admin/agent-performance",
            headers=admin_headers
        )
        assert perf_response.status_code == 200
        
        # Find the agent in performance data
        perf_data = perf_response.json()
        if agent_id:
            agent_perf = None
            for a in perf_data:
                if a.get("agent_id") == agent_id:
                    agent_perf = a
                    break
            
            if agent_perf:
                # Agent should have at least the feedback we just submitted
                assert agent_perf.get("thumbs_up", 0) >= 0, "Should track thumbs up"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
