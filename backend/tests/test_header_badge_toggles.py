"""
Test Iteration 35: Header Badge Toggles (IMG, PDF, FILES)
Tests the fixed header badge toggles in admin Agents tab.
Previously the badges were display-only, now they're clickable buttons.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminHeaderBadgeToggles:
    """Test header badge toggle endpoints for IMG, PDF, FILES generation permissions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin and get token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "MaarsAdmin2024!"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        # Get an agent to test with
        agents_resp = requests.get(f"{BASE_URL}/api/admin/agents", headers=self.headers)
        assert agents_resp.status_code == 200, f"Failed to get agents: {agents_resp.text}"
        agents = agents_resp.json()
        assert len(agents) > 0, "No agents available for testing"
        self.test_agent = agents[0]
        self.agent_id = self.test_agent.get("agent_id")
    
    def test_toggle_can_generate_image(self):
        """Test toggling can_generate_image permission via settings endpoint"""
        # Get current state
        current_value = self.test_agent.get("can_generate_image", False)
        
        # Toggle to opposite
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_image": not current_value}
        )
        assert resp.status_code == 200, f"Toggle can_generate_image failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert data.get("success") == True
        assert "can_generate_image" in data.get("updated", [])
        
        # Verify change persisted by fetching agent again
        agents_resp = requests.get(f"{BASE_URL}/api/admin/agents", headers=self.headers)
        updated_agent = next((a for a in agents_resp.json() if a.get("agent_id") == self.agent_id), None)
        assert updated_agent is not None, "Agent not found after update"
        assert updated_agent.get("can_generate_image") == (not current_value), f"Value not toggled: expected {not current_value}, got {updated_agent.get('can_generate_image')}"
        
        # Toggle back to original
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_image": current_value}
        )
        assert resp.status_code == 200
    
    def test_toggle_can_generate_pdf(self):
        """Test toggling can_generate_pdf permission via settings endpoint"""
        current_value = self.test_agent.get("can_generate_pdf", False)
        
        # Toggle to opposite
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_pdf": not current_value}
        )
        assert resp.status_code == 200, f"Toggle can_generate_pdf failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert data.get("success") == True
        assert "can_generate_pdf" in data.get("updated", [])
        
        # Verify change persisted
        agents_resp = requests.get(f"{BASE_URL}/api/admin/agents", headers=self.headers)
        updated_agent = next((a for a in agents_resp.json() if a.get("agent_id") == self.agent_id), None)
        assert updated_agent.get("can_generate_pdf") == (not current_value)
        
        # Toggle back
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_pdf": current_value}
        )
        assert resp.status_code == 200
    
    def test_toggle_can_generate_files(self):
        """Test toggling can_generate_files permission via settings endpoint"""
        current_value = self.test_agent.get("can_generate_files", False)
        
        # Toggle to opposite
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_files": not current_value}
        )
        assert resp.status_code == 200, f"Toggle can_generate_files failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert data.get("success") == True
        assert "can_generate_files" in data.get("updated", [])
        
        # Verify change persisted
        agents_resp = requests.get(f"{BASE_URL}/api/admin/agents", headers=self.headers)
        updated_agent = next((a for a in agents_resp.json() if a.get("agent_id") == self.agent_id), None)
        assert updated_agent.get("can_generate_files") == (not current_value)
        
        # Toggle back
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_files": current_value}
        )
        assert resp.status_code == 200
    
    def test_toggle_is_active(self):
        """Test toggling is_active status (eye icon toggle)"""
        current_value = self.test_agent.get("is_active", True)
        
        # Toggle to opposite
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"is_active": not current_value}
        )
        assert resp.status_code == 200, f"Toggle is_active failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert data.get("success") == True
        assert "is_active" in data.get("updated", [])
        
        # Toggle back
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"is_active": current_value}
        )
        assert resp.status_code == 200
    
    def test_multiple_capability_toggle_in_single_request(self):
        """Test toggling multiple capabilities in a single request"""
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={
                "can_generate_image": True,
                "can_generate_pdf": True,
                "can_generate_files": True
            }
        )
        assert resp.status_code == 200, f"Multiple toggle failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert data.get("success") == True
        updated_fields = data.get("updated", [])
        assert "can_generate_image" in updated_fields
        assert "can_generate_pdf" in updated_fields
        assert "can_generate_files" in updated_fields
    
    def test_invalid_field_rejected(self):
        """Test that invalid fields are not saved"""
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"invalid_field": "test"}
        )
        # Should return 400 because no valid fields
        assert resp.status_code == 400
    
    def test_nonexistent_agent_returns_404(self):
        """Test that toggling for nonexistent agent returns 404"""
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/nonexistent-agent-12345/settings",
            headers=self.headers,
            json={"can_generate_image": True}
        )
        assert resp.status_code == 404


class TestAdminBrainEditorSave:
    """Test brain editor save functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin and get token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "MaarsAdmin2024!"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        # Get an agent to test with
        agents_resp = requests.get(f"{BASE_URL}/api/admin/agents", headers=self.headers)
        assert agents_resp.status_code == 200
        agents = agents_resp.json()
        self.test_agent = agents[0]
        self.agent_id = self.test_agent.get("agent_id")
        self.original_name = self.test_agent.get("name")
    
    def test_brain_editor_save_name(self):
        """Test saving agent name through brain editor"""
        new_name = "TEST_Agent_Name_12345"
        
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/brain",
            headers=self.headers,
            json={"name": new_name}
        )
        assert resp.status_code == 200, f"Brain save failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert data.get("agent", {}).get("name") == new_name
        
        # Restore original name
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/brain",
            headers=self.headers,
            json={"name": self.original_name}
        )
        assert resp.status_code == 200
    
    def test_brain_editor_save_multiple_fields(self):
        """Test saving multiple brain editor fields"""
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/brain",
            headers=self.headers,
            json={
                "role": "Test Role Updated",
                "description": "Test Description Updated",
                "personality_tone": "Professional but friendly",
                "temperature": 0.8,
                "max_tokens": 2048
            }
        )
        assert resp.status_code == 200, f"Brain save failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        agent = data.get("agent", {})
        assert agent.get("role") == "Test Role Updated"
        assert agent.get("description") == "Test Description Updated"
        assert agent.get("temperature") == 0.8
        assert agent.get("max_tokens") == 2048
        
        # Restore original values
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/brain",
            headers=self.headers,
            json={
                "role": self.test_agent.get("role"),
                "description": self.test_agent.get("description", ""),
                "temperature": self.test_agent.get("temperature", 0.7),
                "max_tokens": self.test_agent.get("max_tokens", 4096)
            }
        )
        assert resp.status_code == 200
    
    def test_brain_editor_invalid_field_rejected(self):
        """Test that invalid fields return 400"""
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/brain",
            headers=self.headers,
            json={"invalid_field_xyz": "test"}
        )
        assert resp.status_code == 400


class TestGenerationPermissionsInExpandedRow:
    """Test the GENERATION PERMISSIONS toggles in expanded agent row"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get test agent"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "MaarsAdmin2024!"
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        agents_resp = requests.get(f"{BASE_URL}/api/admin/agents", headers=self.headers)
        agents = agents_resp.json()
        # Use second agent to avoid conflicts with first test class
        self.test_agent = agents[1] if len(agents) > 1 else agents[0]
        self.agent_id = self.test_agent.get("agent_id")
    
    def test_toggle_images_in_expanded_row(self):
        """Test Images toggle in GENERATION PERMISSIONS section"""
        current = self.test_agent.get("can_generate_image", False)
        
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_image": not current}
        )
        assert resp.status_code == 200
        
        # Restore
        requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_image": current}
        )
    
    def test_toggle_videos_in_expanded_row(self):
        """Test Videos toggle (can_generate_video) in GENERATION PERMISSIONS section"""
        current = self.test_agent.get("can_generate_video", False)
        
        resp = requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_video": not current}
        )
        assert resp.status_code == 200
        
        # Restore
        requests.put(
            f"{BASE_URL}/api/admin/agents/{self.agent_id}/settings",
            headers=self.headers,
            json={"can_generate_video": current}
        )
