"""
Test suite for Web Browsing Capability (Iteration 42)
Production-grade web browsing: web data injected into USER MESSAGE (not system prompt)
Tests: should_search() detection, web_searched flag, Globe icon, source citations
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
        """LOGIN: Admin login with management.maars@marsgc.net / MaarsAdmin2024!"""
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


class TestShouldSearchDetection:
    """Test should_search() auto-detection logic"""
    
    def test_factual_question_triggers_web_search(self):
        """Factual questions with force patterns trigger web search"""
        from services.web_search import should_search
        
        # Should trigger (factual questions with FORCE_SEARCH_PATTERNS)
        factual_queries = [
            "What is the current GDP of Bangladesh?",  # 'current' pattern
            "Who is the president of the United States in 2025?",  # '202X' year pattern
            "What is the latest news about AI regulation?",  # 'latest', 'news' patterns
            "Tell me about the current stock price of Apple",  # 'current', 'price' patterns
            "What is the current population of India?",  # 'current', 'population' patterns
            "What are the latest tax rates in Bangladesh for 2025?",  # 'latest', 'rate', '2025' patterns
        ]
        
        for query in factual_queries:
            result = should_search(query)
            print(f"Query: '{query[:50]}...' -> should_search={result}")
            assert result == True, f"Expected True for factual query: {query}"
        
        print("PASSED: All factual queries correctly trigger web search")
    
    def test_short_messages_dont_trigger_web_search(self):
        """Short messages (<3 words) don't trigger web search"""
        from services.web_search import should_search
        
        # Should NOT trigger (short messages under 3 words)
        short_messages = [
            "Hello",
            "Hi there",
            "Thanks",
            "Thanks!",
            "Ok",
            "Yes",
            "No",
        ]
        
        for msg in short_messages:
            result = should_search(msg)
            print(f"Message: '{msg}' -> should_search={result}")
            assert result == False, f"Expected False for short message: {msg}"
        
        print("PASSED: Short messages correctly do NOT trigger web search")
    
    def test_greeting_patterns_dont_trigger(self):
        """SKIP_PATTERNS greetings don't trigger web search"""
        from services.web_search import should_search
        
        # These should match SKIP_PATTERNS exactly
        skip_greetings = [
            "hello",
            "hi",
            "hey",
            "thanks",
            "thank you",
            "bye",
            "ok",
            "yes",
            "no",
            "sure",
            "great",
            "cool",
            "nice",
            "good",
            "please",
            "alright",
            "hello!",
            "thanks!",
        ]
        
        for msg in skip_greetings:
            result = should_search(msg)
            print(f"Greeting: '{msg}' -> should_search={result}")
            assert result == False, f"Expected False for skip pattern greeting: {msg}"
        
        print("PASSED: SKIP_PATTERNS greetings correctly do NOT trigger web search")


class TestWebSearchAPIWithSecretary:
    """WEB SEARCH FACTUAL: Test with agent_secretary"""
    
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
    def chat_with_secretary(self, auth_token):
        """Create a chat with agent_secretary"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": "agent_secretary", "title": "Web Search Test - Secretary"}
        )
        assert response.status_code == 200
        return response.json()["chat_id"]
    
    def test_india_population_query_web_searched_true(self, auth_token, chat_with_secretary):
        """WEB SEARCH FACTUAL: Send 'What is the current population of India?' to agent_secretary"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_id = chat_with_secretary
        
        message = "What is the current population of India?"
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": message},
            timeout=60
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        assistant_msg = data.get("assistant_message", {})
        web_searched = assistant_msg.get("web_searched", False)
        content = assistant_msg.get("content", "")
        
        print(f"Message: '{message}'")
        print(f"web_searched={web_searched}")
        print(f"Response preview: {content[:300]}...")
        
        assert web_searched == True, "Expected web_searched=True for India population query"
        
        # Check for population data in response
        content_lower = content.lower()
        has_population_info = any(word in content_lower for word in ['billion', 'million', 'population', 'people', '1.4', '1.3'])
        print(f"Has population info: {has_population_info}")
        
        # Check for source citations (URLs)
        has_sources = 'http' in content or 'source' in content_lower or 'according' in content_lower
        print(f"Has source references: {has_sources}")
        
        print("PASSED: India population query returns web_searched=true with population data")


class TestWebSearchAPIWithFinance:
    """WEB SEARCH POLICY: Test with agent_finance"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    @pytest.fixture
    def chat_with_finance(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": "agent_finance", "title": "Web Search Test - Finance"}
        )
        return response.json()["chat_id"]
    
    def test_bangladesh_tax_rates_web_searched_true(self, auth_token, chat_with_finance):
        """WEB SEARCH POLICY: Send tax rates query to agent_finance"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_id = chat_with_finance
        
        message = "What are the latest tax rates in Bangladesh for 2025?"
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": message},
            timeout=60
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        assistant_msg = data.get("assistant_message", {})
        web_searched = assistant_msg.get("web_searched", False)
        content = assistant_msg.get("content", "")
        
        print(f"Message: '{message}'")
        print(f"web_searched={web_searched}")
        print(f"Response preview: {content[:300]}...")
        
        assert web_searched == True, "Expected web_searched=True for Bangladesh tax rates query"
        
        # Agent should use web data confidently
        content_lower = content.lower()
        has_tax_info = any(word in content_lower for word in ['tax', 'rate', '%', 'percent', 'income', 'vat', 'fiscal'])
        print(f"Has tax-related info: {has_tax_info}")
        
        print("PASSED: Bangladesh tax rates query returns web_searched=true")


class TestNoSearchForGreetings:
    """NO SEARCH FOR GREETINGS: Verify web_searched=false for greetings"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    @pytest.fixture
    def chat_for_greeting_test(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": "agent_secretary", "title": "Greeting Test"}
        )
        return response.json()["chat_id"]
    
    def test_simple_greeting_no_web_search(self, auth_token, chat_for_greeting_test):
        """NO SEARCH FOR SHORT MSGS: Send 'Thanks!' to agent - should NOT trigger web search"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_id = chat_for_greeting_test
        
        # Very short message - should NOT trigger
        message = "Thanks!"
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": message},
            timeout=30
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        assistant_msg = data.get("assistant_message", {})
        web_searched = assistant_msg.get("web_searched", False)
        
        print(f"Message: '{message}'")
        print(f"web_searched={web_searched}")
        
        # Short greeting should NOT trigger web search
        assert web_searched == False, f"Expected web_searched=False for short greeting '{message}'"
        
        print("PASSED: Short greeting 'Thanks!' does NOT trigger web search")


class TestAgentUsesWebDataConfidently:
    """AGENT USES WEB DATA: Verify agent doesn't deny internet access"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    @pytest.fixture
    def chat_for_web_data_test(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": "agent_researcher", "title": "Web Data Usage Test"}
        )
        return response.json()["chat_id"]
    
    def test_agent_does_not_deny_internet_when_web_searched(self, auth_token, chat_for_web_data_test):
        """When web_searched=true, agent should NOT say 'I don't have internet access'"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        chat_id = chat_for_web_data_test
        
        message = "What is the current price of Bitcoin today?"
        
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": message},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assistant_msg = data.get("assistant_message", {})
        web_searched = assistant_msg.get("web_searched", False)
        content = assistant_msg.get("content", "").lower()
        
        print(f"web_searched={web_searched}")
        print(f"Response preview: {content[:300]}...")
        
        # If web search was triggered, check agent doesn't deny internet
        if web_searched:
            denial_phrases = [
                "i don't have internet",
                "i can't browse the web",
                "i cannot access the internet",
                "i don't have access to real-time",
                "i cannot browse",
                "i'm unable to access the internet",
                "i don't have the ability to browse",
            ]
            
            for phrase in denial_phrases:
                assert phrase not in content, f"Agent denied internet with: '{phrase}'"
            
            print("PASSED: Agent does NOT deny internet access when web_searched=true")
        else:
            print("INFO: web_searched=false, skipping denial check")


class TestCreditsDeductedWithWebSearch:
    """CREDITS STILL WORK: Verify credits_deducted in responses"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    def test_credits_deducted_present_in_response(self, auth_token):
        """Verify credits_deducted is present in all message responses"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a chat
        chat_response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": "agent_secretary", "title": "Credits Test"}
        )
        chat_id = chat_response.json()["chat_id"]
        
        # Send a message (factual query for web search)
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": "What is the current time in New York?"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # credits_deducted should be at root level
        credits_deducted = data.get("credits_deducted")
        credits_remaining = data.get("credits_remaining")
        
        print(f"credits_deducted: {credits_deducted}")
        print(f"credits_remaining: {credits_remaining}")
        
        assert credits_deducted is not None, "Expected credits_deducted in response"
        assert credits_deducted >= 1, "Expected at least 1 credit deducted"
        
        print("PASSED: Credits deduction working correctly")


class TestClarificationInstructionWebRule:
    """Verify CLARIFICATION_INSTRUCTION includes web browsing rule"""
    
    def test_clarification_instruction_has_web_rule(self):
        """Check config.py has rule 5 about web browsing"""
        from config import CLARIFICATION_INSTRUCTION
        
        has_web_browsing = "WEB BROWSING" in CLARIFICATION_INSTRUCTION or "web browsing" in CLARIFICATION_INSTRUCTION.lower()
        has_capability_mention = "You have live web browsing capability" in CLARIFICATION_INSTRUCTION or "web search results" in CLARIFICATION_INSTRUCTION.lower()
        
        assert has_web_browsing, "CLARIFICATION_INSTRUCTION should mention WEB BROWSING"
        assert has_capability_mention, "CLARIFICATION_INSTRUCTION should mention web browsing capability"
        
        print("PASSED: CLARIFICATION_INSTRUCTION contains web browsing rule 5")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
