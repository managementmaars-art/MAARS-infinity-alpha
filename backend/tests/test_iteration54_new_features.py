"""
Iteration 54: Testing MAARS Command P0/P1 Features
- Activity Monitor page & API (GET /api/activity/live)
- Vibe Coding page & API (POST/GET /api/vibe/projects)
- Reference Intelligence page & API (POST /api/reference/analyze, GET /api/reference/history)
- LLM Config API (GET/PUT /api/llm/config)
- Actions Integrations API (GET /api/actions/integrations)
- Google OAuth status (GET /api/oauth/gmail/status)
- Send email & create event actions (simulation mode)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication for API access"""
    
    def test_login_success(self):
        """Login with admin credentials to get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data or "user_id" in data, "No token or user_id in response"
        return data


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for all tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "management.maars@marsgc.net",
        "password": "admin123"
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    pytest.skip("Authentication failed")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


# ============== ACTIVITY MONITOR ==============
class TestActivityMonitor:
    """Test Activity Monitor API - GET /api/activity/live"""
    
    def test_get_activity_live_returns_required_fields(self, auth_headers):
        """GET /api/activity/live returns agent_activity, communication_flows, task_graph, recent_tool_calls"""
        response = requests.get(f"{BASE_URL}/api/activity/live", headers=auth_headers)
        assert response.status_code == 200, f"Activity live failed: {response.text}"
        data = response.json()
        
        # Check all required fields
        assert "agent_activity" in data, "Missing agent_activity"
        assert "communication_flows" in data, "Missing communication_flows"
        assert "task_graph" in data, "Missing task_graph"
        assert "recent_tool_calls" in data, "Missing recent_tool_calls"
        assert "timestamp" in data, "Missing timestamp"
    
    def test_activity_live_agent_activity_structure(self, auth_headers):
        """Agent activity should have agent, task_count, completed, latest fields"""
        response = requests.get(f"{BASE_URL}/api/activity/live", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        if data["agent_activity"]:
            agent = data["agent_activity"][0]
            assert "agent" in agent, "Missing agent field"
            assert "task_count" in agent, "Missing task_count"
            assert "completed" in agent, "Missing completed"
    
    def test_activity_live_has_active_projects(self, auth_headers):
        """Activity live may have active_projects field"""
        response = requests.get(f"{BASE_URL}/api/activity/live", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "active_projects" in data, "Missing active_projects"


# ============== VIBE CODING ==============
class TestVibeCoding:
    """Test Vibe Coding APIs - /api/vibe/projects"""
    
    def test_list_vibe_projects(self, auth_headers):
        """GET /api/vibe/projects returns list of projects"""
        response = requests.get(f"{BASE_URL}/api/vibe/projects", headers=auth_headers)
        assert response.status_code == 200, f"List vibe projects failed: {response.text}"
        data = response.json()
        assert "items" in data, "Missing items in response"
        assert isinstance(data["items"], list), "items should be a list"
    
    def test_create_vibe_project_requires_description(self, auth_headers):
        """POST /api/vibe/projects requires description"""
        response = requests.post(f"{BASE_URL}/api/vibe/projects", headers=auth_headers, json={})
        assert response.status_code == 400, "Should fail without description"
    
    def test_create_vibe_project_with_simple_description(self, auth_headers):
        """POST /api/vibe/projects creates a project with LLM-generated code"""
        # Use a simple description to avoid long LLM wait times
        response = requests.post(f"{BASE_URL}/api/vibe/projects", headers=auth_headers, json={
            "description": "TEST_Iteration54_Simple HTML page with hello world"
        }, timeout=60)  # Allow 60 seconds for LLM response
        
        assert response.status_code == 200, f"Create vibe project failed: {response.text}"
        data = response.json()
        
        assert "vibe_id" in data, "Missing vibe_id"
        assert "title" in data, "Missing title"
        assert "files" in data or "status" in data, "Missing files or status"
        
        return data.get("vibe_id")


# ============== REFERENCE INTELLIGENCE ==============
class TestReferenceIntelligence:
    """Test Reference Intelligence APIs - /api/reference/*"""
    
    def test_get_reference_history(self, auth_headers):
        """GET /api/reference/history returns analysis history"""
        response = requests.get(f"{BASE_URL}/api/reference/history", headers=auth_headers)
        assert response.status_code == 200, f"Reference history failed: {response.text}"
        data = response.json()
        assert "items" in data, "Missing items"
        assert isinstance(data["items"], list), "items should be a list"
    
    def test_analyze_text_reference(self, auth_headers):
        """POST /api/reference/analyze with type=text analyzes text"""
        response = requests.post(f"{BASE_URL}/api/reference/analyze", headers=auth_headers, json={
            "type": "text",
            "content": "TEST_Iteration54_Sample brand voice: We believe in excellence, innovation, and customer-first thinking. Our products are designed with simplicity in mind."
        }, timeout=60)  # Allow time for LLM
        
        assert response.status_code == 200, f"Text analysis failed: {response.text}"
        data = response.json()
        
        assert "ref_id" in data, "Missing ref_id"
        assert "type" in data, "Missing type"
        assert data["type"] == "text", "Type should be text"
        assert "analysis" in data, "Missing analysis"
    
    def test_analyze_reference_requires_content(self, auth_headers):
        """POST /api/reference/analyze fails without content"""
        response = requests.post(f"{BASE_URL}/api/reference/analyze", headers=auth_headers, json={
            "type": "text",
            "content": ""
        })
        assert response.status_code == 400, "Should fail without content"


# ============== LLM CONFIG ==============
class TestLLMConfig:
    """Test LLM Configuration APIs - /api/llm/config"""
    
    def test_get_llm_config(self, auth_headers):
        """GET /api/llm/config returns provider, model, and available_providers"""
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=auth_headers)
        assert response.status_code == 200, f"Get LLM config failed: {response.text}"
        data = response.json()
        
        assert "provider" in data, "Missing provider"
        assert "model" in data, "Missing model"
        assert "available_providers" in data, "Missing available_providers"
        
        # Check available providers structure
        assert isinstance(data["available_providers"], list), "available_providers should be list"
        if data["available_providers"]:
            provider = data["available_providers"][0]
            assert "id" in provider, "Provider missing id"
            assert "name" in provider, "Provider missing name"
            assert "models" in provider, "Provider missing models"
    
    def test_set_llm_config(self, auth_headers):
        """PUT /api/llm/config changes provider/model preference"""
        response = requests.put(f"{BASE_URL}/api/llm/config", headers=auth_headers, json={
            "provider": "openai",
            "model": "gpt-5.2"
        })
        assert response.status_code == 200, f"Set LLM config failed: {response.text}"
        data = response.json()
        
        assert data["provider"] == "openai", "Provider not updated"
        assert data["model"] == "gpt-5.2", "Model not updated"
    
    def test_llm_config_available_providers_include_all(self, auth_headers):
        """Available providers should include OpenAI, Anthropic, Gemini"""
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        provider_ids = [p["id"] for p in data["available_providers"]]
        assert "openai" in provider_ids, "OpenAI missing from providers"
        assert "anthropic" in provider_ids, "Anthropic missing from providers"
        assert "gemini" in provider_ids, "Gemini missing from providers"


# ============== ACTIONS INTEGRATIONS ==============
class TestActionsIntegrations:
    """Test Actions Integrations APIs - /api/actions/*"""
    
    def test_get_integrations_list(self, auth_headers):
        """GET /api/actions/integrations returns integrations and system mode"""
        response = requests.get(f"{BASE_URL}/api/actions/integrations", headers=auth_headers)
        assert response.status_code == 200, f"Get integrations failed: {response.text}"
        data = response.json()
        
        assert "integrations" in data, "Missing integrations"
        assert "system_mode" in data, "Missing system_mode"
        assert isinstance(data["integrations"], list), "integrations should be list"
        
        # Check Google integration structure
        if data["integrations"]:
            google = data["integrations"][0]
            assert "id" in google, "Integration missing id"
            assert "name" in google, "Integration missing name"
            assert "connected" in google, "Integration missing connected status"
            assert "actions" in google, "Integration missing actions"


# ============== GOOGLE OAUTH ==============
class TestGoogleOAuth:
    """Test Google OAuth APIs - /api/oauth/gmail/*"""
    
    def test_gmail_status(self, auth_headers):
        """GET /api/oauth/gmail/status returns connection status"""
        response = requests.get(f"{BASE_URL}/api/oauth/gmail/status", headers=auth_headers)
        assert response.status_code == 200, f"Gmail status failed: {response.text}"
        data = response.json()
        
        assert "connected" in data, "Missing connected status"
        assert "configured" in data, "Missing configured status"
        assert isinstance(data["connected"], bool), "connected should be bool"
        assert isinstance(data["configured"], bool), "configured should be bool"


# ============== SEND EMAIL / CREATE EVENT (SIMULATION) ==============
class TestActionsSimulation:
    """Test send-email and create-event actions in simulation mode"""
    
    def test_send_email_in_simulation_mode(self, auth_headers):
        """POST /api/actions/send-email returns simulated response in simulation mode"""
        # First ensure we're in simulation mode
        requests.put(f"{BASE_URL}/api/system/mode", headers=auth_headers, json={"mode": "simulation"})
        
        response = requests.post(f"{BASE_URL}/api/actions/send-email", headers=auth_headers, json={
            "to": "test@example.com",
            "subject": "TEST_Iteration54 Test Email",
            "body": "This is a test email"
        })
        assert response.status_code == 200, f"Send email failed: {response.text}"
        data = response.json()
        
        assert data.get("status") == "simulated", f"Expected simulated status, got: {data}"
        assert "message" in data, "Missing message"
    
    def test_create_event_in_simulation_mode(self, auth_headers):
        """POST /api/actions/create-event returns simulated response in simulation mode"""
        # Ensure simulation mode
        requests.put(f"{BASE_URL}/api/system/mode", headers=auth_headers, json={"mode": "simulation"})
        
        response = requests.post(f"{BASE_URL}/api/actions/create-event", headers=auth_headers, json={
            "summary": "TEST_Iteration54 Test Meeting",
            "start": "2026-01-20T10:00:00Z",
            "end": "2026-01-20T11:00:00Z"
        })
        assert response.status_code == 200, f"Create event failed: {response.text}"
        data = response.json()
        
        assert data.get("status") == "simulated", f"Expected simulated status, got: {data}"
        assert "message" in data, "Missing message"


# ============== NAVIGATION VERIFICATION (Additional) ==============
class TestNavigationRoutes:
    """Verify new page routes exist and load"""
    
    def test_activity_monitor_route(self, auth_headers):
        """Activity Monitor page should be accessible"""
        # The frontend route exists - we check that API works
        response = requests.get(f"{BASE_URL}/api/activity/live", headers=auth_headers)
        assert response.status_code == 200, "Activity Monitor API should be accessible"
    
    def test_vibe_coding_route(self, auth_headers):
        """Vibe Coding page API should be accessible"""
        response = requests.get(f"{BASE_URL}/api/vibe/projects", headers=auth_headers)
        assert response.status_code == 200, "Vibe Coding API should be accessible"
    
    def test_reference_intelligence_route(self, auth_headers):
        """Reference Intelligence page API should be accessible"""
        response = requests.get(f"{BASE_URL}/api/reference/history", headers=auth_headers)
        assert response.status_code == 200, "Reference Intelligence API should be accessible"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
