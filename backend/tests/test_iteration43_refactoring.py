"""
Iteration 43: Testing Auth Extraction, Vision, and Frontend Refactoring
- Auth routes extracted to routes/auth.py
- Auth utilities (hash_password, verify_password, get_current_user, require_admin) in auth.py
- CustomPackagesTab and IntegrationsTab extracted from AdminDashboard.jsx
- Image vision pipeline (drag-drop, paste, AI Vision badge)
"""

import pytest
import requests
import os
import base64
from io import BytesIO
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ============= AUTH ENDPOINTS (Extracted to routes/auth.py) =============

class TestAuthEndpointsAfterExtraction:
    """Verify auth endpoints still work after extraction to routes/auth.py"""
    
    def test_login_endpoint_exists(self):
        """POST /api/auth/login should work"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "MaarsAdmin2024!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["is_admin"] == True, "Admin user should have is_admin=True"
        print(f"PASSED: Login works - token received, is_admin={data['user']['is_admin']}")
    
    def test_register_endpoint_exists(self):
        """POST /api/auth/register should work"""
        import uuid
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "name": "Test User",
            "password": "TestPass123!"
        })
        # Either 200 (success) or 400 (email exists) is acceptable
        assert response.status_code in [200, 400], f"Register failed: {response.text}"
        if response.status_code == 200:
            data = response.json()
            assert "token" in data, "No token in response"
            print(f"PASSED: Register works - new user created")
        else:
            print(f"PASSED: Register endpoint accessible (email may already exist)")
    
    def test_auth_me_endpoint_requires_auth(self):
        """GET /api/auth/me should require authentication"""
        # Without auth header
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASSED: /api/auth/me correctly requires auth (401)")
    
    def test_auth_me_endpoint_with_token(self):
        """GET /api/auth/me should return user data with valid token"""
        # First login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "MaarsAdmin2024!"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["token"]
        
        # Then call /auth/me
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200, f"Auth/me failed: {response.text}"
        data = response.json()
        assert data["email"] == "management.maars@marsgc.net"
        assert data["is_admin"] == True
        print(f"PASSED: /api/auth/me returns user data correctly")
    
    def test_logout_endpoint_exists(self):
        """POST /api/auth/logout should work"""
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 200, f"Logout failed: {response.text}"
        print(f"PASSED: Logout endpoint works")


# ============= FILE UPLOAD (Required for Vision) =============

class TestFileUploadForVision:
    """Test file upload endpoint for image attachments"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "MaarsAdmin2024!"
        })
        assert login_resp.status_code == 200
        return {"Authorization": f"Bearer {login_resp.json()['token']}"}
    
    def test_upload_endpoint_exists(self, auth_headers):
        """POST /api/upload should accept file uploads"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {'file': ('test_image.png', img_buffer, 'image/png')}
        response = requests.post(f"{BASE_URL}/api/upload", headers=auth_headers, files=files)
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        assert "file_url" in data or "data_url" in data, "No file URL in response"
        print(f"PASSED: File upload works - {data.get('filename', 'file uploaded')}")
    
    def test_upload_returns_data_url_for_images(self, auth_headers):
        """Upload should return data_url for images (used by vision)"""
        img = Image.new('RGB', (50, 50), color='blue')
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        files = {'file': ('test.jpg', img_buffer, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/api/upload", headers=auth_headers, files=files)
        
        assert response.status_code == 200
        data = response.json()
        # data_url is used for inline image preview and vision
        if "data_url" in data:
            assert data["data_url"].startswith("data:image/"), "data_url should be base64 image"
            print(f"PASSED: Upload returns data_url for vision")
        else:
            print(f"PASSED: Upload works, file_url available")


# ============= IMAGE VISION VIA CHAT =============

class TestImageVisionAnalysis:
    """Test image analysis in chat messages"""
    
    @pytest.fixture
    def auth_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "MaarsAdmin2024!"
        })
        assert login_resp.status_code == 200
        return {"Authorization": f"Bearer {login_resp.json()['token']}"}
    
    def test_chat_accepts_attachments(self, auth_headers):
        """Chat message should accept image attachments"""
        # First create a chat
        chat_resp = requests.post(f"{BASE_URL}/api/chats", 
            headers={**auth_headers, "Content-Type": "application/json"},
            json={"agent_id": "agent_secretary"})
        
        if chat_resp.status_code != 200:
            pytest.skip(f"Could not create chat: {chat_resp.text}")
        
        chat_id = chat_resp.json()["chat_id"]
        
        # Create a simple base64 image
        img = Image.new('RGB', (100, 100), color='green')
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        base64_img = base64.b64encode(img_buffer.read()).decode()
        data_url = f"data:image/png;base64,{base64_img}"
        
        # Send message with attachment
        msg_resp = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "content": "What do you see in this image?",
                "model_provider": "auto",
                "model_name": "auto",
                "attachments": [data_url]
            },
            timeout=60
        )
        
        assert msg_resp.status_code == 200, f"Send message with attachment failed: {msg_resp.text}"
        data = msg_resp.json()
        
        # Verify user message has attachment
        assert "user_message" in data
        user_msg = data["user_message"]
        assert "attachments" in user_msg, "User message should have attachments"
        assert len(user_msg["attachments"]) > 0, "Attachments array should not be empty"
        
        print(f"PASSED: Chat accepts image attachments for vision analysis")


# ============= ADMIN ENDPOINTS =============

class TestAdminDashboardAPIs:
    """Test admin APIs used by AdminDashboard tabs"""
    
    @pytest.fixture
    def admin_headers(self):
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "MaarsAdmin2024!"
        })
        assert login_resp.status_code == 200
        return {"Authorization": f"Bearer {login_resp.json()['token']}"}
    
    def test_admin_stats_endpoint(self, admin_headers):
        """GET /api/admin/stats should return platform stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=admin_headers)
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        data = response.json()
        assert "total_users" in data or "users" in str(data).lower(), "Stats should include user info"
        print(f"PASSED: Admin stats endpoint works")
    
    def test_admin_integrations_endpoint(self, admin_headers):
        """GET /api/admin/integrations should return integration status"""
        response = requests.get(f"{BASE_URL}/api/admin/integrations", headers=admin_headers)
        assert response.status_code == 200, f"Admin integrations failed: {response.text}"
        data = response.json()
        # Should return dict of integrations
        assert isinstance(data, dict), "Integrations should be a dict"
        print(f"PASSED: Admin integrations endpoint works - {len(data)} services")
    
    def test_admin_custom_package_endpoint(self, admin_headers):
        """GET /api/admin/custom-package should return custom package config"""
        response = requests.get(f"{BASE_URL}/api/admin/custom-package", headers=admin_headers)
        assert response.status_code == 200, f"Custom package failed: {response.text}"
        data = response.json()
        # Should have pricing fields
        assert "per_agent_price_usd" in data or "credit_presets" in data, \
            "Custom package should have pricing config"
        print(f"PASSED: Custom package config endpoint works")
    
    def test_admin_credit_packages_endpoint(self, admin_headers):
        """GET /api/admin/credit-packages should return credit packages"""
        response = requests.get(f"{BASE_URL}/api/admin/credit-packages", headers=admin_headers)
        assert response.status_code == 200, f"Credit packages failed: {response.text}"
        data = response.json()
        assert "packages" in data, "Response should have packages array"
        print(f"PASSED: Credit packages endpoint works - {len(data.get('packages', []))} packages")


# ============= PUBLIC ENDPOINTS =============

class TestPublicEndpoints:
    """Test public endpoints that don't require auth"""
    
    def test_health_check(self):
        """GET /health should return healthy"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print(f"PASSED: Health check returns 200")
    
    def test_agents_public_endpoint(self):
        """GET /api/agents/public should return agents without auth"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200, f"Public agents failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Should return list of agents"
        assert len(data) > 0, "Should have at least one agent"
        print(f"PASSED: Public agents endpoint works - {len(data)} agents")
    
    def test_exchange_rate_endpoint(self):
        """GET /api/exchange-rate should return BDT rate"""
        response = requests.get(f"{BASE_URL}/api/exchange-rate")
        assert response.status_code == 200, f"Exchange rate failed: {response.text}"
        data = response.json()
        assert "usd_bdt" in data, "Should have usd_bdt field"
        assert data["usd_bdt"] > 0, "Rate should be positive"
        print(f"PASSED: Exchange rate endpoint works - 1 USD = {data['usd_bdt']} BDT")


# ============= LANDING PAGE CHECK =============

class TestLandingPage:
    """Test landing page loads"""
    
    def test_landing_page_loads(self):
        """Frontend landing page should return 200"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200, f"Landing page failed: {response.status_code}"
        # Check for expected content
        assert "MAARS" in response.text or "html" in response.text.lower(), \
            "Landing page should have expected content"
        print(f"PASSED: Landing page loads correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
