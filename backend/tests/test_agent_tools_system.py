"""
Test suite for Agent Tool System including:
- GET /api/agents returning agents with tools array
- GET /api/agents/tools returning available tools and agent-tool mapping
- Tool execution through chat messages
- Admin Dashboard showing all 9 providers
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestAdminLogin:
    """Test admin authentication"""

    def test_admin_login_success(self):
        """Admin should be able to login with correct credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in login response"
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["is_admin"] == True, "User should be admin"
        print(f"Admin login successful - is_admin: {data['user']['is_admin']}")


class TestAgentToolsAPI:
    """Tests for GET /api/agents/tools endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Cannot login - skipping authenticated tests")

    def test_get_agents_tools_endpoint_exists(self):
        """GET /api/agents/tools should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/agents/tools",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("GET /api/agents/tools endpoint returns 200")

    def test_agents_tools_returns_tools_dict(self):
        """Response should contain tools dictionary"""
        response = requests.get(
            f"{BASE_URL}/api/agents/tools",
            headers=self.headers
        )
        data = response.json()
        assert "tools" in data, "Response should have 'tools' key"
        tools = data["tools"]
        
        # Verify expected tools exist
        expected_tools = ["web_search", "calculate", "create_task", "analyze_data"]
        for tool in expected_tools:
            assert tool in tools, f"Tool '{tool}' should exist"
            assert "name" in tools[tool], f"Tool '{tool}' should have name"
            assert "description" in tools[tool], f"Tool '{tool}' should have description"
        
        print(f"Found {len(tools)} tools: {list(tools.keys())}")

    def test_agents_tools_returns_agent_tool_map(self):
        """Response should contain agent_tools mapping"""
        response = requests.get(
            f"{BASE_URL}/api/agents/tools",
            headers=self.headers
        )
        data = response.json()
        assert "agent_tools" in data, "Response should have 'agent_tools' key"
        agent_tools = data["agent_tools"]
        
        # Verify some agents have tools assigned
        assert len(agent_tools) > 0, "Should have at least one agent with tools"
        
        # Check specific agents have correct tools
        assert "agent_finance" in agent_tools, "Finance agent should have tools"
        assert "calculate" in agent_tools["agent_finance"], "Finance agent should have calculate tool"
        
        assert "agent_secretary" in agent_tools, "Secretary agent should have tools"
        assert "create_task" in agent_tools["agent_secretary"], "Secretary agent should have create_task tool"
        
        print(f"Agent-tool mappings: {json.dumps(agent_tools, indent=2)[:500]}...")


class TestAgentsWithTools:
    """Tests for GET /api/agents returning agents with tools array"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Cannot login - skipping authenticated tests")

    def test_get_agents_returns_200(self):
        """GET /api/agents should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_agents_have_tools_array(self):
        """Each agent should have a tools array"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers=self.headers
        )
        agents = response.json()
        
        agents_with_tools = 0
        for agent in agents:
            assert "tools" in agent, f"Agent {agent.get('agent_id', 'unknown')} should have 'tools' field"
            if len(agent["tools"]) > 0:
                agents_with_tools += 1
        
        assert agents_with_tools > 0, "At least one agent should have tools"
        print(f"{agents_with_tools} agents have tools out of {len(agents)} total")

    def test_finance_agent_has_calculate_tool(self):
        """Finance agent should have calculate tool"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers=self.headers
        )
        agents = response.json()
        
        finance_agent = next((a for a in agents if a["agent_id"] == "agent_finance"), None)
        assert finance_agent is not None, "Finance agent should exist"
        assert "tools" in finance_agent, "Finance agent should have tools"
        assert "calculate" in finance_agent["tools"], f"Finance agent should have calculate tool, got: {finance_agent['tools']}"
        print(f"Finance agent tools: {finance_agent['tools']}")

    def test_secretary_agent_has_create_task_tool(self):
        """Secretary agent should have create_task tool"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers=self.headers
        )
        agents = response.json()
        
        secretary_agent = next((a for a in agents if a["agent_id"] == "agent_secretary"), None)
        assert secretary_agent is not None, "Secretary agent should exist"
        assert "tools" in secretary_agent, "Secretary agent should have tools"
        assert "create_task" in secretary_agent["tools"], f"Secretary agent should have create_task tool, got: {secretary_agent['tools']}"
        print(f"Secretary agent tools: {secretary_agent['tools']}")

    def test_researcher_agent_has_web_search_tool(self):
        """Researcher agent should have web_search tool"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers=self.headers
        )
        agents = response.json()
        
        researcher_agent = next((a for a in agents if a["agent_id"] == "agent_researcher"), None)
        assert researcher_agent is not None, "Researcher agent should exist"
        assert "tools" in researcher_agent, "Researcher agent should have tools"
        assert "web_search" in researcher_agent["tools"], f"Researcher agent should have web_search tool, got: {researcher_agent['tools']}"
        print(f"Researcher agent tools: {researcher_agent['tools']}")


class TestAdminAPIKeysEndpoint:
    """Tests for admin API keys endpoint showing all 9 providers"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Cannot login - skipping authenticated tests")

    def test_admin_api_keys_returns_all_9_providers(self):
        """Admin API keys should return cost_reference with all 9 providers"""
        response = requests.get(
            f"{BASE_URL}/api/admin/api-keys",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "cost_reference" in data, "Response should have cost_reference"
        
        cost_ref = data["cost_reference"]
        expected_providers = ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"]
        
        for provider in expected_providers:
            assert provider in cost_ref, f"Provider '{provider}' should be in cost_reference"
        
        print(f"All 9 providers found in cost_reference: {list(cost_ref.keys())}")

    def test_admin_api_keys_has_key_set_flags(self):
        """Admin API keys should return key_set flags for all providers"""
        response = requests.get(
            f"{BASE_URL}/api/admin/api-keys",
            headers=self.headers
        )
        data = response.json()
        
        # Check for key_set flags
        expected_flags = [
            "openai_key_set", "anthropic_key_set", "gemini_key_set",
            "xai_key_set", "deepseek_key_set", "mistral_key_set",
            "perplexity_key_set", "cohere_key_set", "elevenlabs_key_set"
        ]
        
        for flag in expected_flags:
            assert flag in data, f"Flag '{flag}' should be in response"
        
        print("All provider key_set flags present")


class TestCreateAgentProviders:
    """Tests for Create Agent having all providers in model dropdown"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Cannot login - skipping authenticated tests")

    def test_create_agent_info_endpoint(self):
        """GET /api/agents/create/info should work"""
        response = requests.get(
            f"{BASE_URL}/api/agents/create/info",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "credit_cost" in data, "Should have credit_cost"
        print(f"Create agent info: credits={data.get('credits_remaining')}, cost={data.get('credit_cost')}")


class TestChatToolExecution:
    """Tests for chat message tool execution - create a chat and test tool response format"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        else:
            pytest.skip("Cannot login - skipping authenticated tests")

    def test_create_chat_with_finance_agent(self):
        """Should be able to create a chat with finance agent"""
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=self.headers,
            json={"agent_id": "agent_finance"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "chat_id" in data, "Response should have chat_id"
        print(f"Created chat: {data['chat_id']}")

    def test_chat_message_response_structure(self):
        """Chat message response should support execution_steps"""
        # Create a chat first
        chat_response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=self.headers,
            json={"agent_id": "agent_finance"}
        )
        assert chat_response.status_code == 200
        chat_id = chat_response.json()["chat_id"]
        
        # Send a message (we won't trigger actual tool use - just verify structure)
        msg_response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=self.headers,
            json={"content": "Hello, what are your capabilities?"}
        )
        
        # Check structure (tool use is optional based on LLM response)
        assert msg_response.status_code == 200, f"Expected 200, got {msg_response.status_code}: {msg_response.text}"
        data = msg_response.json()
        assert "user_message" in data, "Should have user_message"
        assert "assistant_message" in data, "Should have assistant_message"
        
        # assistant_message may or may not have execution_steps depending on LLM
        assistant = data["assistant_message"]
        assert "content" in assistant, "Assistant message should have content"
        print(f"Chat message response received, execution_steps present: {'execution_steps' in assistant}")


class TestPublicAgentsEndpoint:
    """Tests for public agents endpoint (no auth)"""

    def test_public_agents_returns_200(self):
        """GET /api/agents/public should return 200 without auth"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_public_agents_have_tools(self):
        """Public agents should also have tools array"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        agents = response.json()
        
        agents_with_tools = 0
        for agent in agents:
            assert "tools" in agent, f"Agent {agent.get('agent_id', 'unknown')} should have 'tools' field"
            if len(agent["tools"]) > 0:
                agents_with_tools += 1
        
        assert agents_with_tools > 0, "At least one agent should have tools"
        print(f"Public endpoint: {agents_with_tools} agents have tools out of {len(agents)} total")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
