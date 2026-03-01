"""
Test suite for Web Browsing Capability (Iteration 41)
Tests: Auto web search detection, web_searched flag in responses, Globe icon display
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestAdminLogin:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Login with admin credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["is_admin"] == True
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"PASSED: Admin login successful, is_admin={data['user']['is_admin']}")
        return data["token"]


class TestWebSearchDetection:
    """Test needs_web_search() auto-detection logic"""
    
    def test_factual_question_triggers_web_search(self):
        """Test that factual questions with keywords trigger web search detection"""
        from services.web_search import needs_web_search
        
        # Should trigger (factual questions with multiple patterns)
        factual_queries = [
            "What is the current GDP of Bangladesh?",
            "Who is the president of the United States in 2025?",
            "What is the latest news about AI regulation?",
            "Tell me about the current stock price of Apple",
            "What is the population of Bangladesh and its capital?",
        ]
        
        for query in factual_queries:
            result = needs_web_search(query)
            print(f"Query: '{query[:50]}...' -> needs_web_search={result}")
            assert result == True, f"Expected True for factual query: {query}"
        
        print("PASSED: All factual queries correctly trigger web search")
    
    def test_greetings_dont_trigger_web_search(self):
        """Test that simple greetings and short messages don't trigger web search"""
        from services.web_search import needs_web_search
        
        # Should NOT trigger (greetings, short messages)
        simple_messages = [
            "Hello",
            "Hi there",
            "Thanks",
            "Ok",
            "Yes",
            "How are you?",  # Under 4 words
        ]
        
        for msg in simple_messages:
            result = needs_web_search(msg)
            print(f"Message: '{msg}' -> needs_web_search={result}")
            assert result == False, f"Expected False for greeting/short message: {msg}"
        
        print("PASSED: Greetings correctly do NOT trigger web search")


class TestWebSearchAPI:
    """Test web search API integration"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["token"]
    
    @pytest.fixture
    def chat_with_agent(self, auth_token):
        """Create a chat with an agent for testing"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Use agent_secretary or agent_finance for testing
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": "agent_secretary", "title": "Web Search Test Chat"}
        )
        assert response.status_code == 200
        return response.json()["chat_id"]
    
    def test_factual_question_returns_web_searched_true(self, auth_token, chat_with_agent):
        """Send a factual question and verify web_searched=true in response"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_id = chat_with_agent
        
        # Send a factual question that should trigger web search
        message = "What is the current GDP of Bangladesh in 2025?"
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": message}
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        # Check assistant message has web_searched flag
        assistant_msg = data.get("assistant_message", {})
        web_searched = assistant_msg.get("web_searched", False)
        
        print(f"Message: '{message[:50]}...'")
        print(f"web_searched={web_searched}")
        print(f"Response preview: {assistant_msg.get('content', '')[:200]}...")
        
        assert web_searched == True, "Expected web_searched=True for factual question"
        assert "credits_deducted" in data or "credits_used" in data, "Expected credits deduction info"
        
        print("PASSED: Factual question returns web_searched=true")
    
    def test_greeting_returns_web_searched_false(self, auth_token, chat_with_agent):
        """Send a greeting and verify web_searched=false in response"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_id = chat_with_agent
        
        # Send a simple greeting (should NOT trigger web search)
        message = "Hello, how are you today?"
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": message}
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        assistant_msg = data.get("assistant_message", {})
        web_searched = assistant_msg.get("web_searched", False)
        
        print(f"Message: '{message}'")
        print(f"web_searched={web_searched}")
        
        # Greeting should NOT trigger web search
        assert web_searched == False, "Expected web_searched=False for greeting"
        
        print("PASSED: Greeting returns web_searched=false")


class TestAgentDoesNotDenyInternet:
    """Test that agent doesn't say 'I don't have internet access' when web results are injected"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    @pytest.fixture
    def chat_with_finance_agent(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": "agent_finance", "title": "Finance Agent Web Test"}
        )
        return response.json()["chat_id"]
    
    def test_agent_uses_web_data_not_denies_internet(self, auth_token, chat_with_finance_agent):
        """Agent should use web data and NOT say it lacks internet access"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_id = chat_with_finance_agent
        
        # Ask a question that requires current data
        message = "What is the current US Federal Reserve interest rate policy for 2025?"
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": message}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assistant_msg = data.get("assistant_message", {})
        content = assistant_msg.get("content", "").lower()
        
        # Check for denial phrases
        denial_phrases = [
            "i don't have internet",
            "i can't browse the web",
            "i cannot access the internet",
            "i don't have access to real-time",
            "i cannot browse",
            "i'm unable to access the internet",
        ]
        
        for phrase in denial_phrases:
            assert phrase not in content, f"Agent denied internet access with phrase: '{phrase}'"
        
        # If web search was triggered, agent should use the data
        if assistant_msg.get("web_searched"):
            print(f"Web search triggered, agent should be using injected data")
            # Check response has some substantive content (not just a denial)
            assert len(content) > 100, "Response too short - agent may not be using web data"
        
        print("PASSED: Agent does not deny internet access")


class TestCreditsStillWork:
    """Verify credit system still works with web search feature"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    def test_credits_deducted_in_response(self, auth_token):
        """Verify credits_deducted is present in responses"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a chat
        chat_response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": "agent_secretary", "title": "Credits Test"}
        )
        chat_id = chat_response.json()["chat_id"]
        
        # Send a message
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": "What tasks do I have today?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check credits info is present
        assistant_msg = data.get("assistant_message", {})
        credits_deducted = assistant_msg.get("credits_deducted")
        credits_used = data.get("credits_used")
        
        print(f"credits_deducted in message: {credits_deducted}")
        print(f"credits_used in response: {credits_used}")
        
        # At least one should be present
        assert credits_deducted is not None or credits_used is not None, "Expected credits info in response"
        
        print("PASSED: Credits deduction working with web search feature")


class TestClarificationInstructionUpdate:
    """Verify CLARIFICATION_INSTRUCTION includes web browsing rule"""
    
    def test_clarification_instruction_has_web_rule(self):
        """Check config.py has rule 5 about web browsing"""
        from config import CLARIFICATION_INSTRUCTION
        
        assert "WEB BROWSING" in CLARIFICATION_INSTRUCTION or "web browsing" in CLARIFICATION_INSTRUCTION.lower()
        assert "You have live web browsing capability" in CLARIFICATION_INSTRUCTION or "web search results" in CLARIFICATION_INSTRUCTION.lower()
        
        print("PASSED: CLARIFICATION_INSTRUCTION contains web browsing rule")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
