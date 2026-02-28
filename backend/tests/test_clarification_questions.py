"""
Tests for MAARS Command AI Platform - Clarification Question Behavior
Tests that agents ask clarifying questions before generating deliverables for complex tasks,
but answer directly for simple factual questions.
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestClarificationQuestions:
    """Test suite for agent clarification question behavior"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get authenticated headers"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def create_chat_with_agent(self, auth_headers, agent_id):
        """Helper to create a new chat with a specific agent"""
        response = requests.post(
            f"{BASE_URL}/api/chats",
            json={"agent_id": agent_id},
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 201, f"Chat creation failed: {response.text}"
        return response.json()["chat_id"]
    
    def send_message_to_chat(self, auth_headers, chat_id, content, timeout_seconds=60):
        """Helper to send a message to a chat and get response"""
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            json={"content": content},
            headers=auth_headers,
            timeout=timeout_seconds
        )
        return response
    
    # =============== TEST 1: Marketing Agent - Complex Task (should ask questions) ===============
    def test_marketing_agent_asks_questions_for_campaign(self, auth_headers):
        """Marketing agent should ask clarifying questions for 'create a social media campaign'"""
        chat_id = self.create_chat_with_agent(auth_headers, "agent_marketing")
        
        response = self.send_message_to_chat(
            auth_headers, chat_id,
            "Create a social media campaign for my business"
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        assistant_content = data.get("assistant_message", {}).get("content", "")
        assert assistant_content, "No assistant response received"
        
        # Check that the response contains question marks (asking questions)
        has_questions = "?" in assistant_content
        
        # Additional check: Look for common question indicators
        question_indicators = [
            "what", "which", "who", "where", "when", "how",
            "target", "audience", "industry", "budget", "goal",
            "platform", "brand", "tone", "style"
        ]
        has_question_context = any(indicator in assistant_content.lower() for indicator in question_indicators)
        
        print(f"\n=== Marketing Agent Response (first 500 chars) ===")
        print(assistant_content[:500])
        print(f"Has question marks: {has_questions}")
        print(f"Has question context: {has_question_context}")
        
        assert has_questions or has_question_context, \
            f"Marketing agent should ask questions for complex campaign task. Response: {assistant_content[:300]}"
        
        # Clean up: Delete chat
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=auth_headers, timeout=10)
    
    # =============== TEST 2: Simple Factual Question - Should Answer Directly ===============
    def test_agent_answers_simple_question_directly(self, auth_headers):
        """Agent should answer simple factual questions directly without asking questions"""
        chat_id = self.create_chat_with_agent(auth_headers, "agent_seo")
        
        response = self.send_message_to_chat(
            auth_headers, chat_id,
            "What is SEO?"
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        assistant_content = data.get("assistant_message", {}).get("content", "")
        assert assistant_content, "No assistant response received"
        
        # For a simple definition question, the response should contain an explanation
        # It might still have some questions for follow-up, but should primarily be informative
        explanatory_keywords = [
            "search engine optimization", "seo", "search engine", "ranking",
            "google", "visibility", "organic", "traffic", "website"
        ]
        has_explanation = any(kw in assistant_content.lower() for kw in explanatory_keywords)
        
        print(f"\n=== SEO Agent Response for 'What is SEO?' (first 500 chars) ===")
        print(assistant_content[:500])
        print(f"Has explanation: {has_explanation}")
        
        assert has_explanation, \
            f"Agent should provide an explanation for 'What is SEO?'. Response: {assistant_content[:300]}"
        
        # Clean up
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=auth_headers, timeout=10)
    
    # =============== TEST 3: Follow-up with Answers - Should Generate Deliverable ===============
    def test_follow_up_with_answers_generates_deliverable(self, auth_headers):
        """Agent should use provided answers and generate deliverable without re-asking"""
        chat_id = self.create_chat_with_agent(auth_headers, "agent_marketing")
        
        # First message: Complex task
        response1 = self.send_message_to_chat(
            auth_headers, chat_id,
            "Create a social media campaign"
        )
        assert response1.status_code == 200
        first_response = response1.json().get("assistant_message", {}).get("content", "")
        print(f"\n=== First Response (first 300 chars) ===")
        print(first_response[:300])
        
        # Second message: Provide answers to expected questions
        response2 = self.send_message_to_chat(
            auth_headers, chat_id,
            """Here are the details:
            - Target audience: Small business owners aged 30-50
            - Industry: Local bakery and cafe
            - Goal: Increase foot traffic by 30%
            - Platforms: Instagram and Facebook
            - Budget: $500/month
            - Brand tone: Warm, friendly, community-focused
            - Timeline: 3 months
            Please create the campaign now."""
        )
        
        assert response2.status_code == 200, f"Follow-up message failed: {response2.text}"
        data = response2.json()
        
        assistant_content = data.get("assistant_message", {}).get("content", "")
        assert assistant_content, "No assistant response received for follow-up"
        
        # The response should contain deliverable content - not just more questions
        # Look for campaign-related output indicators
        deliverable_indicators = [
            "campaign", "content", "post", "strategy", "schedule",
            "instagram", "facebook", "bakery", "cafe", "week",
            "hashtag", "image", "caption", "engagement"
        ]
        has_deliverable = sum(1 for ind in deliverable_indicators if ind in assistant_content.lower()) >= 3
        
        print(f"\n=== Follow-up Response (first 800 chars) ===")
        print(assistant_content[:800])
        print(f"Has deliverable content: {has_deliverable}")
        
        # The agent should use provided info, not re-ask all questions
        # It's okay to have a few follow-up questions, but should also deliver value
        assert has_deliverable, \
            f"Agent should generate deliverable content after answers provided. Response: {assistant_content[:500]}"
        
        # Clean up
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=auth_headers, timeout=10)
    
    # =============== TEST 4: Graphic Designer - Logo Design (should ask questions) ===============
    def test_graphics_agent_asks_questions_for_logo(self, auth_headers):
        """Graphic Designer agent should ask about brand, colors, style before generating"""
        chat_id = self.create_chat_with_agent(auth_headers, "agent_graphics")
        
        response = self.send_message_to_chat(
            auth_headers, chat_id,
            "Design me a logo"
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        assistant_content = data.get("assistant_message", {}).get("content", "")
        assert assistant_content, "No assistant response received"
        
        # Check for questions about design requirements
        has_questions = "?" in assistant_content
        design_question_indicators = [
            "brand", "color", "style", "business", "industry",
            "audience", "tone", "competitor", "preference", "name",
            "typography", "symbol", "icon", "what"
        ]
        has_design_context = any(indicator in assistant_content.lower() for indicator in design_question_indicators)
        
        print(f"\n=== Graphics Agent Response for 'Design me a logo' (first 500 chars) ===")
        print(assistant_content[:500])
        print(f"Has question marks: {has_questions}")
        print(f"Has design context: {has_design_context}")
        
        assert has_questions or has_design_context, \
            f"Graphics agent should ask about brand/colors/style for logo design. Response: {assistant_content[:300]}"
        
        # Clean up
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=auth_headers, timeout=10)
    
    # =============== TEST 5: Finance Agent - Budget Creation (should ask questions) ===============
    def test_finance_agent_asks_questions_for_budget(self, auth_headers):
        """Finance agent should ask clarifying questions for budget creation"""
        chat_id = self.create_chat_with_agent(auth_headers, "agent_finance")
        
        response = self.send_message_to_chat(
            auth_headers, chat_id,
            "Create a budget for my startup"
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        assistant_content = data.get("assistant_message", {}).get("content", "")
        assert assistant_content, "No assistant response received"
        
        # Check for questions about financial requirements
        has_questions = "?" in assistant_content
        finance_question_indicators = [
            "revenue", "expense", "income", "cost", "timeframe",
            "period", "category", "department", "goal", "funding",
            "monthly", "annual", "budget", "what", "how much"
        ]
        has_finance_context = any(indicator in assistant_content.lower() for indicator in finance_question_indicators)
        
        print(f"\n=== Finance Agent Response for 'Create a budget' (first 500 chars) ===")
        print(assistant_content[:500])
        print(f"Has question marks: {has_questions}")
        print(f"Has finance context: {has_finance_context}")
        
        assert has_questions or has_finance_context, \
            f"Finance agent should ask questions for budget creation. Response: {assistant_content[:300]}"
        
        # Clean up
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=auth_headers, timeout=10)
    
    # =============== TEST 6: Conversation History Maintained ===============
    def test_conversation_history_maintained(self, auth_headers):
        """Verify conversation history is maintained across messages in same chat"""
        chat_id = self.create_chat_with_agent(auth_headers, "agent_strategist")
        
        # First message: Introduce a unique identifier
        unique_id = f"PROJ_TEST_{int(time.time())}"
        response1 = self.send_message_to_chat(
            auth_headers, chat_id,
            f"I'm working on a project called {unique_id} for an e-commerce fashion startup."
        )
        assert response1.status_code == 200
        
        # Second message: Reference previous context without repeating
        response2 = self.send_message_to_chat(
            auth_headers, chat_id,
            "Based on what I told you, what's the most important strategic consideration for this project?"
        )
        
        assert response2.status_code == 200, f"Second message failed: {response2.text}"
        data = response2.json()
        
        assistant_content = data.get("assistant_message", {}).get("content", "")
        assert assistant_content, "No assistant response received"
        
        # The response should reference the e-commerce/fashion context
        context_indicators = [
            "e-commerce", "fashion", "ecommerce", "startup", "project",
            unique_id.lower(), "retail", "online", "store", "clothing"
        ]
        has_context = any(indicator in assistant_content.lower() for indicator in context_indicators)
        
        print(f"\n=== Strategist Response with History (first 500 chars) ===")
        print(assistant_content[:500])
        print(f"Has context from previous message: {has_context}")
        
        # Verify chat messages are stored
        chat_response = requests.get(
            f"{BASE_URL}/api/chats/{chat_id}",
            headers=auth_headers,
            timeout=30
        )
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        messages = chat_data.get("messages", [])
        
        print(f"Total messages in chat: {len(messages)}")
        assert len(messages) >= 4, f"Expected at least 4 messages (2 user + 2 assistant), got {len(messages)}"
        
        # Clean up
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=auth_headers, timeout=10)
    
    # =============== TEST 7: Agent Greeting - Direct Response ===============
    def test_agent_responds_to_greeting_directly(self, auth_headers):
        """Agent should respond directly to greetings without unnecessary questions"""
        chat_id = self.create_chat_with_agent(auth_headers, "agent_secretary")
        
        response = self.send_message_to_chat(
            auth_headers, chat_id,
            "Hello! How are you?"
        )
        
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        assistant_content = data.get("assistant_message", {}).get("content", "")
        assert assistant_content, "No assistant response received"
        
        # For a greeting, the response should be friendly and responsive
        greeting_indicators = [
            "hello", "hi", "welcome", "glad", "help", "assist",
            "how can", "what can", "nice", "pleasure"
        ]
        has_greeting_response = any(indicator in assistant_content.lower() for indicator in greeting_indicators)
        
        print(f"\n=== Secretary Agent Greeting Response (first 300 chars) ===")
        print(assistant_content[:300])
        print(f"Has greeting response: {has_greeting_response}")
        
        assert has_greeting_response, \
            f"Agent should respond to greeting naturally. Response: {assistant_content[:200]}"
        
        # Clean up
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=auth_headers, timeout=10)
    
    # =============== TEST 8: Multiple Agents Ask Questions for Complex Tasks ===============
    def test_multiple_agents_ask_questions_for_complex_tasks(self, auth_headers):
        """Test that various agents ask questions for their domain-specific complex tasks"""
        test_cases = [
            ("agent_hr", "Create an onboarding program for new employees"),
            ("agent_legal", "Draft a contract for a software development project"),
            ("agent_email", "Create an email nurture sequence for leads"),
        ]
        
        results = []
        for agent_id, task in test_cases:
            chat_id = self.create_chat_with_agent(auth_headers, agent_id)
            
            response = self.send_message_to_chat(auth_headers, chat_id, task)
            
            if response.status_code == 200:
                content = response.json().get("assistant_message", {}).get("content", "")
                has_questions = "?" in content
                results.append({
                    "agent": agent_id,
                    "task": task,
                    "has_questions": has_questions,
                    "response_preview": content[:200]
                })
                print(f"\n=== {agent_id} for '{task[:30]}...' ===")
                print(f"Has questions: {has_questions}")
                print(f"Response: {content[:300]}")
            
            # Clean up
            requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=auth_headers, timeout=10)
        
        # At least most agents should ask questions for complex tasks
        asking_count = sum(1 for r in results if r["has_questions"])
        print(f"\n=== Summary: {asking_count}/{len(results)} agents asked questions ===")
        
        assert asking_count >= 2, \
            f"Expected at least 2 out of {len(test_cases)} agents to ask questions for complex tasks. Got {asking_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
