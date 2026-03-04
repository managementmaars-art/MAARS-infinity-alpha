"""
Iteration 58: Voice Transcription and Admin Code Explorer API Tests
Tests for:
- GET /api/admin/code/tree - Full codebase file tree (admin only)
- GET /api/admin/code/file?path=... - File content with line numbers (admin only)
- GET /api/admin/code/search?q=... - File name search (admin only)
- POST /api/voice/transcribe - Voice transcription endpoint (auth required)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"


class TestAuthentication:
    """Get auth tokens for testing"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin user token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        token = data.get("token") or data.get("access_token")
        assert token, "No token in admin login response"
        return token
    
    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Get admin auth headers"""
        return {"Authorization": f"Bearer {admin_token}"}


class TestCodeTreeEndpoint(TestAuthentication):
    """Tests for GET /api/admin/code/tree"""
    
    def test_code_tree_requires_auth(self):
        """Code tree should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/code/tree")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_code_tree_success(self, admin_headers):
        """Admin can get code tree"""
        response = requests.get(f"{BASE_URL}/api/admin/code/tree", headers=admin_headers)
        assert response.status_code == 200, f"Code tree failed: {response.text}"
        
        data = response.json()
        assert "tree" in data, "Response should have 'tree' key"
        assert isinstance(data["tree"], list), "Tree should be a list"
        assert len(data["tree"]) > 0, "Tree should not be empty"
    
    def test_code_tree_structure(self, admin_headers):
        """Verify code tree has expected structure"""
        response = requests.get(f"{BASE_URL}/api/admin/code/tree", headers=admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        tree = data["tree"]
        
        # Check for expected directories (backend, frontend/src)
        dir_names = [node["name"] for node in tree if node["type"] == "directory"]
        assert "backend" in dir_names or any("backend" in d for d in dir_names), "Should have backend directory"
        
        # Check directory structure
        for node in tree:
            if node["type"] == "directory":
                assert "name" in node
                assert "path" in node
                assert "children" in node
                assert "count" in node
            elif node["type"] == "file":
                assert "name" in node
                assert "path" in node
                assert "size" in node
                assert "language" in node


class TestCodeFileEndpoint(TestAuthentication):
    """Tests for GET /api/admin/code/file"""
    
    def test_code_file_requires_auth(self):
        """Code file should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/code/file?path=backend/server.py")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_code_file_success(self, admin_headers):
        """Admin can get file content"""
        response = requests.get(
            f"{BASE_URL}/api/admin/code/file?path=backend/server.py",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Code file failed: {response.text}"
        
        data = response.json()
        assert "content" in data, "Response should have 'content' key"
        assert "path" in data
        assert "name" in data
        assert "language" in data
        assert "size" in data
        assert "lines" in data
        
        # Verify it's actually server.py content
        assert "FastAPI" in data["content"] or "fastapi" in data["content"].lower()
        assert data["language"] == "python"
        assert data["name"] == "server.py"
    
    def test_code_file_frontend_file(self, admin_headers):
        """Can read frontend files"""
        response = requests.get(
            f"{BASE_URL}/api/admin/code/file?path=frontend/src/App.js",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Frontend file failed: {response.text}"
        
        data = response.json()
        assert "React" in data["content"] or "react" in data["content"].lower()
        assert data["language"] == "javascript"
    
    def test_code_file_not_found(self, admin_headers):
        """Should return 404 for non-existent file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/code/file?path=nonexistent/file.py",
            headers=admin_headers
        )
        assert response.status_code in [403, 404], f"Expected 403/404 for non-existent file, got {response.status_code}"
    
    def test_code_file_path_traversal_blocked(self, admin_headers):
        """Path traversal should be blocked"""
        response = requests.get(
            f"{BASE_URL}/api/admin/code/file?path=../../../etc/passwd",
            headers=admin_headers
        )
        assert response.status_code == 400, f"Path traversal should return 400, got {response.status_code}"
    
    def test_code_file_outside_allowed_dirs(self, admin_headers):
        """Files outside allowed directories should be denied"""
        response = requests.get(
            f"{BASE_URL}/api/admin/code/file?path=secret/config.txt",
            headers=admin_headers
        )
        # Should be 403 (forbidden) or 404 (not found)
        assert response.status_code in [403, 404]


class TestCodeSearchEndpoint(TestAuthentication):
    """Tests for GET /api/admin/code/search"""
    
    def test_code_search_requires_auth(self):
        """Code search should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/code/search?q=test")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_code_search_success(self, admin_headers):
        """Admin can search files"""
        response = requests.get(
            f"{BASE_URL}/api/admin/code/search?q=server",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Code search failed: {response.text}"
        
        data = response.json()
        assert "results" in data, "Response should have 'results' key"
        assert isinstance(data["results"], list), "Results should be a list"
        
        # Should find server.py
        found_server = any("server" in r["name"].lower() for r in data["results"])
        assert found_server, "Should find server.py or similar"
    
    def test_code_search_voice_files(self, admin_headers):
        """Search should find voice-related files"""
        response = requests.get(
            f"{BASE_URL}/api/admin/code/search?q=voice",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should find voice.py
        found_voice = any("voice" in r["name"].lower() for r in data["results"])
        assert found_voice, "Should find voice.py"
    
    def test_code_search_result_structure(self, admin_headers):
        """Search results should have proper structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/code/search?q=app",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        if data["results"]:
            result = data["results"][0]
            assert "name" in result
            assert "path" in result
            assert "language" in result
            assert "size" in result
    
    def test_code_search_limit(self, admin_headers):
        """Search should be limited to prevent overload"""
        response = requests.get(
            f"{BASE_URL}/api/admin/code/search?q=.py",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should be limited to 50 results max
        assert len(data["results"]) <= 50


class TestVoiceTranscribeEndpoint(TestAuthentication):
    """Tests for POST /api/voice/transcribe"""
    
    def test_voice_transcribe_requires_auth(self):
        """Voice transcribe should require authentication"""
        response = requests.post(f"{BASE_URL}/api/voice/transcribe")
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"
    
    def test_voice_transcribe_no_file(self, admin_headers):
        """Should reject request without file"""
        response = requests.post(
            f"{BASE_URL}/api/voice/transcribe",
            headers=admin_headers
        )
        # 422 Unprocessable Entity expected for missing file
        assert response.status_code == 422, f"Expected 422 for missing file, got {response.status_code}"
    
    def test_voice_transcribe_empty_file(self, admin_headers):
        """Should reject empty file"""
        import io
        files = {"file": ("test.webm", io.BytesIO(b""), "audio/webm")}
        response = requests.post(
            f"{BASE_URL}/api/voice/transcribe",
            headers=admin_headers,
            files=files
        )
        # Empty file might be rejected with 400 or processed (depends on implementation)
        assert response.status_code in [400, 500], f"Expected 400/500 for empty file, got {response.status_code}"
    
    def test_voice_transcribe_with_small_audio(self, admin_headers):
        """Test with minimal audio data (will likely fail transcription but endpoint should respond)"""
        import io
        # Create a minimal audio-like bytes (not valid audio, just for endpoint testing)
        fake_audio = b"\x00" * 1000  # 1KB of zeros
        files = {"file": ("test.webm", io.BytesIO(fake_audio), "audio/webm")}
        response = requests.post(
            f"{BASE_URL}/api/voice/transcribe",
            headers=admin_headers,
            files=files
        )
        # Endpoint should accept the request but may fail on transcription
        # We're testing the endpoint exists and processes files
        assert response.status_code in [200, 400, 500], f"Endpoint should process file, got {response.status_code}"


class TestAdminOnlyAccess:
    """Test that admin endpoints require admin privileges"""
    
    @pytest.fixture(scope="class")
    def regular_user_token(self):
        """Create or get a non-admin user token"""
        # First try to register a new user
        test_email = f"test_nonadmin_{os.urandom(4).hex()}@test.com"
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        
        if register_response.status_code in [200, 201]:
            data = register_response.json()
            return data.get("token") or data.get("access_token")
        
        # If registration fails (user exists), try login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            return data.get("token") or data.get("access_token")
        
        # Skip test if we can't create a regular user
        pytest.skip("Could not create regular user for admin-only test")
    
    def test_code_tree_denied_for_non_admin(self, regular_user_token):
        """Non-admin users should be denied access to code tree"""
        if not regular_user_token:
            pytest.skip("No regular user token available")
        
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/code/tree", headers=headers)
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
    
    def test_code_file_denied_for_non_admin(self, regular_user_token):
        """Non-admin users should be denied access to code file"""
        if not regular_user_token:
            pytest.skip("No regular user token available")
        
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/code/file?path=backend/server.py",
            headers=headers
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
    
    def test_code_search_denied_for_non_admin(self, regular_user_token):
        """Non-admin users should be denied access to code search"""
        if not regular_user_token:
            pytest.skip("No regular user token available")
        
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/code/search?q=test",
            headers=headers
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"


class TestHealthAndRouterRegistration:
    """Verify routes are properly registered"""
    
    def test_health_endpoint(self):
        """Health endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
    
    def test_voice_router_registered(self):
        """Voice router should be registered (returns 401/422 not 404)"""
        response = requests.post(f"{BASE_URL}/api/voice/transcribe")
        # Should NOT be 404 - that would mean route isn't registered
        assert response.status_code != 404, "Voice endpoint should be registered"
    
    def test_admin_code_router_registered(self):
        """Admin code router should be registered (returns 401/403 not 404)"""
        response = requests.get(f"{BASE_URL}/api/admin/code/tree")
        # Should NOT be 404 - that would mean route isn't registered
        assert response.status_code != 404, "Admin code tree endpoint should be registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
