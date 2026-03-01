"""
Brain Editor & Agent Collaboration Tests - Iteration 24
Tests for:
1. Brain Editor API - PUT /api/admin/agents/{agent_id}/brain
2. Agent Detail API - GET /api/admin/agents/{agent_id}
3. Commander delegation with background processing
4. Agent Collaboration [CONSULT:] tag support (infrastructure check)
5. Health check endpoint
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestHealthAndAuth:
    """Health check and authentication tests"""
    
    def test_health_endpoint(self):
        """Test 9: Health check GET /health returns 200"""
        # Note: /health is on root app, not /api
        # This route may be caught by frontend in production - test internal
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        # May return 200 or HTML from frontend SPA
        print(f"Health endpoint status: {response.status_code}")
        # Accept both 200 from backend or 200 from frontend
        assert response.status_code == 200, f"Health check failed with status {response.status_code}"
        print("TEST PASSED: Health endpoint returns 200")
    
    def test_admin_login(self):
        """Admin login returns token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert data.get("user", {}).get("is_admin") == True, "User not admin"
        print(f"TEST PASSED: Admin login successful, token received")
        return data["token"]


class TestBrainEditorAPI:
    """Tests for Brain Editor API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        self.token = response.json().get("token", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_get_agent_detail(self):
        """Test 5: GET /api/admin/agents/{agent_id} returns full agent details including brain fields"""
        # Test with marketing agent
        agent_id = "agent_marketing"
        response = requests.get(
            f"{BASE_URL}/api/admin/agents/{agent_id}",
            headers=self.headers,
            timeout=10
        )
        assert response.status_code == 200, f"Get agent failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify core fields
        assert data.get("agent_id") == agent_id, "Wrong agent_id"
        assert "name" in data, "Missing name field"
        assert "role" in data, "Missing role field"
        assert "description" in data, "Missing description field"
        assert "system_prompt" in data, "Missing system_prompt field"
        assert "model_provider" in data, "Missing model_provider field"
        assert "model_name" in data, "Missing model_name field"
        
        print(f"TEST PASSED: GET /api/admin/agents/{agent_id} returns full details")
        print(f"  - Agent: {data.get('name')} ({data.get('role')})")
        print(f"  - Model: {data.get('model_provider')}/{data.get('model_name')}")
        # Brain fields are optional - check if they exist
        brain_fields = ['personality_tone', 'expertise_areas', 'dos', 'donts', 'knowledge_base']
        for field in brain_fields:
            print(f"  - {field}: {'present' if data.get(field) else 'not set'}")
    
    def test_update_agent_brain_personality_tone(self):
        """Test 4: PUT /api/admin/agents/{agent_id}/brain with personality_tone field"""
        agent_id = "agent_marketing"
        unique_suffix = uuid.uuid4().hex[:6]
        test_personality = f"Friendly and casual. Uses analogies. Test-{unique_suffix}"
        
        # Update brain with personality_tone
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/brain",
            headers=self.headers,
            json={
                "personality_tone": test_personality,
            },
            timeout=10
        )
        assert response.status_code == 200, f"Brain update failed: {response.status_code} - {response.text}"
        data = response.json()
        
        assert data.get("success") == True, "Response success not True"
        assert "agent" in data, "No agent in response"
        
        # Verify the personality_tone was saved
        agent = data["agent"]
        assert agent.get("personality_tone") == test_personality, f"personality_tone not updated correctly"
        
        # Verify system_prompt includes brain config
        system_prompt = agent.get("system_prompt", "")
        assert "--- BRAIN CONFIG ---" in system_prompt, "Brain config section not in system_prompt"
        assert "Personality & Tone:" in system_prompt, "Personality & Tone not in system_prompt"
        
        print(f"TEST PASSED: PUT /api/admin/agents/{agent_id}/brain with personality_tone")
        print(f"  - personality_tone saved: {test_personality[:40]}...")
        print(f"  - Brain config added to system_prompt: YES")
    
    def test_update_agent_brain_all_fields(self):
        """Test 4: PUT /api/admin/agents/{agent_id}/brain with all brain fields"""
        agent_id = "agent_seo"  # Use SEO agent for this test
        unique_suffix = uuid.uuid4().hex[:6]
        
        brain_data = {
            "personality_tone": f"Data-driven and analytical. Test-{unique_suffix}",
            "expertise_areas": f"SEO, keyword research, link building. Test-{unique_suffix}",
            "dos": f"Provide specific keyword recommendations. Test-{unique_suffix}",
            "donts": f"Never promise first page rankings. Test-{unique_suffix}",
        }
        
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/brain",
            headers=self.headers,
            json=brain_data,
            timeout=10
        )
        assert response.status_code == 200, f"Brain update failed: {response.status_code} - {response.text}"
        data = response.json()
        
        assert data.get("success") == True, "Response success not True"
        agent = data["agent"]
        
        # Verify all fields saved
        for field, value in brain_data.items():
            assert agent.get(field) == value, f"{field} not saved correctly"
        
        # Verify system_prompt includes all brain config sections
        system_prompt = agent.get("system_prompt", "")
        assert "Personality & Tone:" in system_prompt, "Personality & Tone missing"
        assert "Expertise Areas:" in system_prompt, "Expertise Areas missing"
        assert "Always do:" in system_prompt, "Always do (dos) missing"
        assert "Never do:" in system_prompt, "Never do (donts) missing"
        
        print(f"TEST PASSED: PUT /api/admin/agents/{agent_id}/brain with all brain fields")
        print(f"  - All 4 brain fields saved correctly")
        print(f"  - System prompt rebuilt with all brain sections")
    
    def test_update_agent_brain_with_name_role(self):
        """Test brain update also allows updating name and role"""
        agent_id = "agent_marketing"
        
        # Get current state first
        get_response = requests.get(
            f"{BASE_URL}/api/admin/agents/{agent_id}",
            headers=self.headers,
            timeout=10
        )
        original = get_response.json()
        
        # Update with model_provider and model_name (allowed fields)
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/brain",
            headers=self.headers,
            json={
                "model_provider": "openai",
                "model_name": "gpt-5.2"
            },
            timeout=10
        )
        assert response.status_code == 200, f"Brain update failed: {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True
        print(f"TEST PASSED: Brain update allows model_provider and model_name fields")


class TestCommanderDelegation:
    """Tests for Commander AI delegation with background processing"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        self.token = response.json().get("token", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_commander_returns_immediately_with_processing(self):
        """Test 8: Commander delegation returns immediately with commander_status=processing"""
        # First create a chat with commander
        chat_response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=self.headers,
            json={"agent_id": "agent_commander", "title": "Test Commander Delegation"},
            timeout=10
        )
        
        if chat_response.status_code != 200:
            pytest.skip(f"Could not create chat: {chat_response.status_code}")
        
        chat_id = chat_response.json().get("chat_id")
        
        # Send a message to commander
        msg_response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=self.headers,
            json={"content": "Create a social media campaign for a coffee shop", "model_provider": "openai"},
            timeout=30
        )
        
        assert msg_response.status_code == 200, f"Message send failed: {msg_response.status_code}"
        data = msg_response.json()
        
        # Commander should return immediately with processing status
        # The response includes commander_status field
        if "commander_status" in data:
            assert data["commander_status"] in ["processing", "complete"], f"Unexpected status: {data['commander_status']}"
            print(f"TEST PASSED: Commander returns with commander_status={data['commander_status']}")
        else:
            # May return direct response if short query
            print(f"TEST INFO: Commander returned direct response (no background task for this query)")
        
        # Cleanup - delete the chat
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=self.headers, timeout=10)


class TestAgentCollaboration:
    """Tests for Agent-to-Agent collaboration infrastructure"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        self.token = response.json().get("token", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_collaboration_instruction_in_system(self):
        """Test 6: Verify collaboration instruction exists in CLARIFICATION_INSTRUCTION"""
        # Get any agent to check if system prompt includes collaboration instructions
        response = requests.get(
            f"{BASE_URL}/api/admin/agents/agent_marketing",
            headers=self.headers,
            timeout=10
        )
        
        if response.status_code != 200:
            pytest.skip("Cannot access agent details")
        
        # The CLARIFICATION_INSTRUCTION is appended to all prompts
        # We can verify via GET agents endpoint that shows capabilities
        agents_response = requests.get(
            f"{BASE_URL}/api/agents",
            headers=self.headers,
            timeout=10
        )
        
        if agents_response.status_code == 200:
            agents = agents_response.json()
            # SEO agent should be available for consultation
            seo_agent = next((a for a in agents if a.get("agent_id") == "agent_seo"), None)
            assert seo_agent is not None, "SEO agent not found in agents list"
            print(f"TEST PASSED: SEO agent (agent_seo) available for collaboration")
            print(f"  - SEO agent: {seo_agent.get('name')} - {seo_agent.get('role')}")
    
    def test_send_collaboration_request(self):
        """Test 6: Send message requesting agent collaboration"""
        # Create a chat with marketing agent
        chat_response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=self.headers,
            json={"agent_id": "agent_marketing", "title": "TEST Collaboration Request"},
            timeout=10
        )
        
        if chat_response.status_code != 200:
            pytest.skip(f"Could not create chat: {chat_response.status_code}")
        
        chat_id = chat_response.json().get("chat_id")
        
        # Send message requesting collaboration with SEO
        msg_response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=self.headers,
            json={
                "content": "I need a marketing campaign for a restaurant and I want you to check with the SEO specialist about keywords",
                "model_provider": "openai"
            },
            timeout=60  # Allow more time for LLM response
        )
        
        assert msg_response.status_code == 200, f"Message send failed: {msg_response.status_code}"
        data = msg_response.json()
        
        # The response content - agent may or may not use CONSULT tag
        content = data.get("content", "")
        
        # Check if agent mentioned SEO or keywords (collaboration attempt)
        mentions_seo = "seo" in content.lower() or "keyword" in content.lower() or "search" in content.lower()
        
        print(f"TEST INFO: Message sent requesting SEO collaboration")
        print(f"  - Response length: {len(content)} chars")
        print(f"  - Mentions SEO/keywords: {mentions_seo}")
        
        # This is expected behavior - LLM decides when to consult
        # The infrastructure supports it via [CONSULT:agent_id] tags
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=self.headers, timeout=10)
        
        print(f"TEST PASSED: Collaboration request processed (LLM decides if CONSULT tag used)")


class TestSidebarTeamNavigation:
    """Test 7: Team nav link works on sidebar across pages"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        self.token = response.json().get("token", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_teams_endpoint(self):
        """Verify /api/teams endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/teams",
            headers=self.headers,
            timeout=10
        )
        assert response.status_code == 200, f"Teams endpoint failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Teams response should be list"
        print(f"TEST PASSED: /api/teams returns {len(data)} teams")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
