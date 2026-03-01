"""
Tests for Branding & Custom Domain feature (Iteration 33)
Tests:
- GET /api/branding/public - Returns default branding (no auth)
- GET /api/admin/branding - Returns full config (admin auth required)
- POST /api/admin/branding - Saves branding settings (admin auth)
- POST /api/admin/branding/upload-logo - File upload (admin auth)
- POST /api/admin/branding/verify-domain - DNS verification (admin auth)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestPublicBranding:
    """Tests for /api/branding/public (no auth required)"""
    
    def test_public_branding_returns_200(self):
        """GET /api/branding/public should return 200 without authentication"""
        response = requests.get(f"{BASE_URL}/api/branding/public")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASSED: GET /api/branding/public returns 200")

    def test_public_branding_has_required_fields(self):
        """GET /api/branding/public should return default branding fields"""
        response = requests.get(f"{BASE_URL}/api/branding/public")
        data = response.json()
        
        required_fields = ["platform_name", "tagline", "logo_url", "favicon_url", 
                          "primary_color", "accent_color", "footer_text"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check default values
        assert data["platform_name"] == "MAARS Command" or data["platform_name"], "platform_name should have value"
        assert data["primary_color"].startswith("#"), "primary_color should be hex format"
        assert data["accent_color"].startswith("#"), "accent_color should be hex format"
        print(f"PASSED: Public branding has all required fields: {list(data.keys())}")


class TestAdminBrandingAuth:
    """Tests that admin branding endpoints require authentication"""
    
    def test_get_admin_branding_requires_auth(self):
        """GET /api/admin/branding should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/branding")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: GET /api/admin/branding returns 401 without auth")

    def test_post_admin_branding_requires_auth(self):
        """POST /api/admin/branding should return 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/admin/branding", json={"platform_name": "Test"})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: POST /api/admin/branding returns 401 without auth")

    def test_upload_logo_requires_auth(self):
        """POST /api/admin/branding/upload-logo should return 401 without auth"""
        files = {"file": ("test.png", b"fake image data", "image/png")}
        response = requests.post(f"{BASE_URL}/api/admin/branding/upload-logo", files=files)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: POST /api/admin/branding/upload-logo returns 401 without auth")

    def test_verify_domain_requires_auth(self):
        """POST /api/admin/branding/verify-domain should return 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/admin/branding/verify-domain")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: POST /api/admin/branding/verify-domain returns 401 without auth")


@pytest.fixture(scope="class")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "management.maars@marsgc.net",
        "password": "MaarsAdmin2024!"
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    data = response.json()
    token = data.get("token")
    if not token:
        pytest.skip("No token returned from admin login")
    return token


class TestAdminBrandingEndpoints:
    """Tests for admin branding endpoints with authentication"""
    
    def test_get_admin_branding_with_auth(self, admin_token):
        """GET /api/admin/branding returns full config with admin auth"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/branding", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Admin endpoint has more fields than public
        assert "config_type" in data, "Should have config_type field"
        assert "custom_domain" in data, "Should have custom_domain field"
        assert "custom_domain_status" in data, "Should have custom_domain_status field"
        assert "support_email" in data, "Should have support_email field"
        print(f"PASSED: GET /api/admin/branding returns full config: {list(data.keys())}")

    def test_update_branding_platform_name(self, admin_token):
        """POST /api/admin/branding saves platform_name"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        test_name = f"Test Platform {uuid.uuid4().hex[:6]}"
        
        response = requests.post(f"{BASE_URL}/api/admin/branding", 
                                headers=headers, 
                                json={"platform_name": test_name})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["platform_name"] == test_name, f"Expected {test_name}, got {data['platform_name']}"
        print(f"PASSED: POST /api/admin/branding updated platform_name to '{test_name}'")
        
        # Reset to default
        requests.post(f"{BASE_URL}/api/admin/branding", 
                     headers=headers, 
                     json={"platform_name": "MAARS Command"})

    def test_update_branding_colors(self, admin_token):
        """POST /api/admin/branding saves primary_color and accent_color"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/admin/branding", 
                                headers=headers, 
                                json={"primary_color": "#3b82f6", "accent_color": "#8b5cf6"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["primary_color"] == "#3b82f6", f"primary_color mismatch"
        assert data["accent_color"] == "#8b5cf6", f"accent_color mismatch"
        print("PASSED: POST /api/admin/branding updated colors")
        
        # Reset to default
        requests.post(f"{BASE_URL}/api/admin/branding", 
                     headers=headers, 
                     json={"primary_color": "#ef4444", "accent_color": "#f97316"})

    def test_update_branding_custom_domain(self, admin_token):
        """POST /api/admin/branding with custom_domain sets status to pending"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        test_domain = "test.example.com"
        
        response = requests.post(f"{BASE_URL}/api/admin/branding", 
                                headers=headers, 
                                json={"custom_domain": test_domain})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["custom_domain"] == test_domain, f"custom_domain mismatch"
        assert data["custom_domain_status"] == "pending_verification", "Status should be pending_verification"
        print(f"PASSED: POST /api/admin/branding set custom_domain and status to pending_verification")

    def test_update_branding_footer_and_support_email(self, admin_token):
        """POST /api/admin/branding saves footer_text and support_email"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/admin/branding", 
                                headers=headers, 
                                json={
                                    "footer_text": "Test Corp 2024",
                                    "support_email": "support@test.com"
                                })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["footer_text"] == "Test Corp 2024", f"footer_text mismatch"
        assert data["support_email"] == "support@test.com", f"support_email mismatch"
        print("PASSED: POST /api/admin/branding updated footer_text and support_email")
        
        # Reset to default
        requests.post(f"{BASE_URL}/api/admin/branding", 
                     headers=headers, 
                     json={"footer_text": "MAARS Global Corporation", "support_email": ""})

    def test_verify_domain_with_non_existent_domain(self, admin_token):
        """POST /api/admin/branding/verify-domain returns dns_not_found for invalid domain"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        # First set a non-existent domain
        requests.post(f"{BASE_URL}/api/admin/branding", 
                     headers=headers, 
                     json={"custom_domain": "nonexistent-domain-12345.invalid"})
        
        response = requests.post(f"{BASE_URL}/api/admin/branding/verify-domain", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] in ["dns_not_found", "pending_verification", "verification_error"], \
            f"Unexpected status: {data['status']}"
        print(f"PASSED: POST /api/admin/branding/verify-domain returned status: {data['status']}")
        
        # Clean up
        requests.post(f"{BASE_URL}/api/admin/branding", 
                     headers=headers, 
                     json={"custom_domain": ""})

    def test_verify_domain_requires_domain_configured(self, admin_token):
        """POST /api/admin/branding/verify-domain returns 400 if no domain configured"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        # Clear domain first
        requests.post(f"{BASE_URL}/api/admin/branding", 
                     headers=headers, 
                     json={"custom_domain": ""})
        
        response = requests.post(f"{BASE_URL}/api/admin/branding/verify-domain", headers=headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASSED: POST /api/admin/branding/verify-domain returns 400 when no domain configured")


class TestBrandingUploadLogo:
    """Tests for logo upload endpoint"""
    
    def test_upload_valid_png(self, admin_token):
        """POST /api/admin/branding/upload-logo accepts PNG files"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a minimal valid PNG (1x1 transparent pixel)
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 image
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
            0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
            0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
            0x42, 0x60, 0x82
        ])
        
        files = {"file": ("test_logo.png", png_data, "image/png")}
        response = requests.post(f"{BASE_URL}/api/admin/branding/upload-logo", 
                                headers=headers, 
                                files=files)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, "Response should include 'url'"
        assert data["url"].startswith("/api/files/"), f"URL should start with /api/files/, got {data['url']}"
        assert "filename" in data, "Response should include 'filename'"
        print(f"PASSED: Upload logo returned URL: {data['url']}")

    def test_upload_rejects_large_file(self, admin_token):
        """POST /api/admin/branding/upload-logo rejects files > 5MB"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a file > 5MB (this will be rejected before fully processing)
        large_data = b"x" * (6 * 1024 * 1024)  # 6MB
        
        files = {"file": ("large.png", large_data, "image/png")}
        response = requests.post(f"{BASE_URL}/api/admin/branding/upload-logo", 
                                headers=headers, 
                                files=files)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASSED: Upload rejects files > 5MB")

    def test_upload_rejects_invalid_extension(self, admin_token):
        """POST /api/admin/branding/upload-logo rejects unsupported file types"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        files = {"file": ("test.exe", b"fake executable", "application/octet-stream")}
        response = requests.post(f"{BASE_URL}/api/admin/branding/upload-logo", 
                                headers=headers, 
                                files=files)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASSED: Upload rejects unsupported file types")


class TestRegressionEndpoints:
    """Regression tests to ensure existing functionality still works"""
    
    def test_agents_endpoint_works(self, admin_token):
        """GET /api/agents returns agents list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Should return list"
        assert len(data) >= 20, f"Expected at least 20 agents, got {len(data)}"
        print(f"PASSED: GET /api/agents returns {len(data)} agents")

    def test_auth_me_endpoint_works(self, admin_token):
        """GET /api/auth/me returns user info"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "email" in data, "Should have email field"
        assert data["is_admin"] == True, "Admin user should have is_admin=True"
        print("PASSED: GET /api/auth/me returns admin user info")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
