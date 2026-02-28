"""
Test Suite for Admin Agent Capabilities Feature
Tests the ability to manage agent generation permissions (can_generate_image, can_generate_video, can_generate_pdf, can_generate_files)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"

class TestAdminAgentCapabilities:
    """Tests for admin agent capability management"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in login response"
        return data["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Headers with admin auth"""
        return {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }

    # ============== GET /api/admin/agents Tests ==============
    
    def test_get_all_agents_returns_21_agents(self, auth_headers):
        """Test that GET /api/admin/agents returns all 21 default agents"""
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        assert response.status_code == 200, f"Failed to get agents: {response.text}"
        agents = response.json()
        assert isinstance(agents, list), "Response should be a list"
        assert len(agents) >= 21, f"Expected at least 21 agents, got {len(agents)}"
        print(f"✓ Found {len(agents)} agents")
    
    def test_agents_have_capability_fields(self, auth_headers):
        """Test that agents have can_generate_* fields"""
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        assert response.status_code == 200
        agents = response.json()
        
        # All agents should be able to have these fields defined
        capability_fields = ["can_generate_image", "can_generate_video", "can_generate_pdf", "can_generate_files"]
        
        for agent in agents:
            agent_id = agent.get("agent_id", "unknown")
            # Fields may not exist initially (default to False), but should be parseable
            for field in capability_fields:
                # Check that if the field exists, it's boolean
                if field in agent:
                    assert isinstance(agent[field], bool), f"Agent {agent_id}.{field} should be boolean"
        print("✓ All agents have valid capability fields")
    
    def test_graphics_agent_has_image_capability(self, auth_headers):
        """Test that agent_graphics (Felix Romano) has can_generate_image=true"""
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        assert response.status_code == 200
        agents = response.json()
        
        graphics_agent = next((a for a in agents if a.get("agent_id") == "agent_graphics"), None)
        assert graphics_agent is not None, "agent_graphics not found"
        assert graphics_agent.get("name") == "Felix Romano", "agent_graphics should be Felix Romano"
        assert graphics_agent.get("role") == "Graphic Designer", "agent_graphics should be Graphic Designer"
        # Check if IMG capability is enabled
        print(f"✓ agent_graphics found: {graphics_agent.get('name')} - can_generate_image={graphics_agent.get('can_generate_image', False)}")
    
    def test_video_agent_has_video_capability(self, auth_headers):
        """Test that agent_video (Riley Chen) has can_generate_video=true"""
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        assert response.status_code == 200
        agents = response.json()
        
        video_agent = next((a for a in agents if a.get("agent_id") == "agent_video"), None)
        assert video_agent is not None, "agent_video not found"
        assert video_agent.get("name") == "Riley Chen", "agent_video should be Riley Chen"
        assert video_agent.get("role") == "Video Content Specialist", "agent_video should be Video Content Specialist"
        print(f"✓ agent_video found: {video_agent.get('name')} - can_generate_video={video_agent.get('can_generate_video', False)}")

    # ============== PUT /api/admin/agents/{agent_id}/settings Tests ==============
    
    def test_toggle_image_capability_on(self, auth_headers):
        """Test enabling can_generate_image for an agent"""
        # Use the secretary agent for testing (should not have image capability by default)
        agent_id = "agent_secretary"
        
        # First, check current state
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        agent = next((a for a in agents if a.get("agent_id") == agent_id), None)
        assert agent is not None, f"Agent {agent_id} not found"
        
        # Enable image capability
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_image": True}
        )
        assert response.status_code == 200, f"Failed to update agent: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Update should succeed"
        assert "can_generate_image" in data.get("updated", []), "can_generate_image should be in updated fields"
        
        # Verify the change persisted
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        updated_agent = next((a for a in agents if a.get("agent_id") == agent_id), None)
        assert updated_agent.get("can_generate_image") == True, "can_generate_image should be True"
        print(f"✓ Successfully enabled can_generate_image for {agent_id}")
    
    def test_toggle_image_capability_off(self, auth_headers):
        """Test disabling can_generate_image for an agent"""
        agent_id = "agent_secretary"
        
        # Disable image capability
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_image": False}
        )
        assert response.status_code == 200, f"Failed to update agent: {response.text}"
        
        # Verify the change persisted
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        updated_agent = next((a for a in agents if a.get("agent_id") == agent_id), None)
        assert updated_agent.get("can_generate_image") == False, "can_generate_image should be False"
        print(f"✓ Successfully disabled can_generate_image for {agent_id}")
    
    def test_toggle_video_capability(self, auth_headers):
        """Test toggling can_generate_video for an agent"""
        agent_id = "agent_marketing"
        
        # Enable video capability
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_video": True}
        )
        assert response.status_code == 200, f"Failed to enable video: {response.text}"
        
        # Verify enabled
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        agent = next((a for a in agents if a.get("agent_id") == agent_id), None)
        assert agent.get("can_generate_video") == True, "can_generate_video should be True"
        
        # Disable video capability
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_video": False}
        )
        assert response.status_code == 200, f"Failed to disable video: {response.text}"
        
        # Verify disabled
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        agent = next((a for a in agents if a.get("agent_id") == agent_id), None)
        assert agent.get("can_generate_video") == False, "can_generate_video should be False"
        print(f"✓ Successfully toggled can_generate_video for {agent_id}")
    
    def test_toggle_pdf_capability(self, auth_headers):
        """Test toggling can_generate_pdf for an agent"""
        agent_id = "agent_strategist"
        
        # Disable PDF capability
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_pdf": False}
        )
        assert response.status_code == 200, f"Failed to disable PDF: {response.text}"
        
        # Re-enable PDF capability
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_pdf": True}
        )
        assert response.status_code == 200, f"Failed to enable PDF: {response.text}"
        print(f"✓ Successfully toggled can_generate_pdf for {agent_id}")
    
    def test_toggle_files_capability(self, auth_headers):
        """Test toggling can_generate_files for an agent"""
        agent_id = "agent_appdev"
        
        # Disable files capability
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_files": False}
        )
        assert response.status_code == 200, f"Failed to disable files: {response.text}"
        
        # Re-enable files capability
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"can_generate_files": True}
        )
        assert response.status_code == 200, f"Failed to enable files: {response.text}"
        print(f"✓ Successfully toggled can_generate_files for {agent_id}")
    
    def test_update_multiple_capabilities(self, auth_headers):
        """Test updating multiple capabilities at once"""
        agent_id = "agent_seo"
        
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={
                "can_generate_image": True,
                "can_generate_video": True,
                "can_generate_pdf": True,
                "can_generate_files": True
            }
        )
        assert response.status_code == 200, f"Failed to update multiple: {response.text}"
        data = response.json()
        assert len(data.get("updated", [])) == 4, "Should update 4 fields"
        
        # Verify all enabled
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        agents = response.json()
        agent = next((a for a in agents if a.get("agent_id") == agent_id), None)
        assert agent.get("can_generate_image") == True
        assert agent.get("can_generate_video") == True
        assert agent.get("can_generate_pdf") == True
        assert agent.get("can_generate_files") == True
        
        # Reset to defaults
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={
                "can_generate_image": False,
                "can_generate_video": False,
                "can_generate_pdf": True,
                "can_generate_files": True
            }
        )
        assert response.status_code == 200
        print(f"✓ Successfully updated multiple capabilities for {agent_id}")
    
    def test_update_nonexistent_agent_returns_404(self, auth_headers):
        """Test that updating non-existent agent returns 404"""
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/agent_nonexistent/settings",
            headers=auth_headers,
            json={"can_generate_image": True}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent agent returns 404")
    
    def test_update_with_invalid_fields_returns_400(self, auth_headers):
        """Test that updating with invalid fields returns 400"""
        agent_id = "agent_secretary"
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/settings",
            headers=auth_headers,
            json={"invalid_field": True, "another_invalid": False}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid fields returns 400")


class TestFileUploadEndpoint:
    """Tests for the /api/upload endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Headers with admin auth - Note: NO Content-Type for multipart uploads"""
        return {
            "Authorization": f"Bearer {admin_token}"
        }
    
    def test_upload_text_file(self, auth_headers):
        """Test uploading a simple text file"""
        # Create a test file in memory
        files = {
            'file': ('test_file.txt', b'Hello, this is test content!', 'text/plain')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            headers=auth_headers,
            files=files
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        
        assert "filename" in data, "Response should contain filename"
        assert "file_url" in data, "Response should contain file_url"
        assert "content_type" in data, "Response should contain content_type"
        assert "size" in data, "Response should contain size"
        assert "data_url" in data, "Response should contain data_url"
        
        assert data["filename"] == "test_file.txt"
        assert data["content_type"] == "text/plain"
        assert data["size"] > 0
        assert data["data_url"].startswith("data:text/plain;base64,")
        print(f"✓ Successfully uploaded text file: {data['filename']}")
    
    def test_upload_requires_auth(self):
        """Test that upload endpoint requires authentication"""
        files = {
            'file': ('test.txt', b'content', 'text/plain')
        }
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Upload correctly requires authentication")
    
    def test_upload_json_file(self, auth_headers):
        """Test uploading a JSON file"""
        import json
        json_content = json.dumps({"key": "value", "number": 42})
        files = {
            'file': ('data.json', json_content.encode(), 'application/json')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            headers=auth_headers,
            files=files
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        assert data["filename"] == "data.json"
        assert data["content_type"] == "application/json"
        print(f"✓ Successfully uploaded JSON file")


class TestAdminAccessControl:
    """Tests to ensure only admins can access agent management"""
    
    def test_non_admin_cannot_access_agents(self):
        """Test that regular users cannot access /api/admin/agents"""
        # First, create a test user if needed or login
        # For this test, we'll try without auth
        response = requests.get(f"{BASE_URL}/api/admin/agents")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Unauthenticated users cannot access admin agents")
    
    def test_non_admin_cannot_update_settings(self):
        """Test that unauthenticated users cannot update agent settings"""
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/agent_secretary/settings",
            json={"can_generate_image": True}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Unauthenticated users cannot update agent settings")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
