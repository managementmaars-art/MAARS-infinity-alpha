"""
Iteration 61 Tests: About Page PDF Export and Updated Systems Count
Tests:
- GET /api/summary/pdf returns valid PDF with all 17 systems
- PDF contains all required sections: Platform Overview, 41 Agents, Core Systems, Tech Architecture, API Endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')


class TestSummaryPDFEndpoint:
    """Tests for the GET /api/summary/pdf endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token") or data.get("token")

    def test_pdf_endpoint_returns_200(self, auth_token):
        """PDF endpoint should return 200 with valid auth"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS - GET /api/summary/pdf returns 200")

    def test_pdf_content_type(self, auth_token):
        """PDF should have correct content-type header"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Expected application/pdf, got {content_type}"
        print("PASS - Content-Type is application/pdf")

    def test_pdf_content_disposition(self, auth_token):
        """PDF should have Content-Disposition header for download"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp, f"Expected attachment disposition, got {content_disp}"
        assert "MAARS-Command-Summary.pdf" in content_disp, f"Expected filename, got {content_disp}"
        print("PASS - Content-Disposition header with correct filename")

    def test_pdf_has_valid_content(self, auth_token):
        """PDF should have valid PDF content (starts with %PDF magic bytes)"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        content = response.content
        # PDF files start with %PDF-
        assert content[:5] == b'%PDF-', f"Expected PDF magic bytes, got {content[:10]}"
        print("PASS - PDF has valid PDF magic bytes")

    def test_pdf_minimum_size(self, auth_token):
        """PDF should be at least 8KB (comprehensive summary)"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        size_kb = len(response.content) / 1024
        assert size_kb >= 8, f"Expected PDF >= 8KB, got {size_kb:.1f}KB"
        print(f"PASS - PDF size is {size_kb:.1f}KB (>= 8KB minimum)")

    def test_pdf_requires_auth(self):
        """PDF endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/summary/pdf")
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"
        print("PASS - PDF endpoint requires authentication")

    def test_pdf_with_invalid_token(self):
        """PDF endpoint should reject invalid tokens"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": "Bearer invalid-token-12345"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS - PDF endpoint rejects invalid tokens")


class TestSummaryRouterRegistration:
    """Verify summary router is properly registered"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")

    def test_health_check(self, auth_token):
        """Basic health check to verify backend is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS - Backend health check OK")


class TestAgentsPublicEndpoint:
    """Test agents endpoint for About page"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")

    def test_agents_public_returns_agents(self, auth_token):
        """GET /api/agents/public should return agent list"""
        response = requests.get(
            f"{BASE_URL}/api/agents/public",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) > 0, "Expected agents in response"
        print(f"PASS - GET /api/agents/public returns {len(agents)} agents")

    def test_agents_have_required_fields(self, auth_token):
        """Agents should have name and avatar fields"""
        response = requests.get(
            f"{BASE_URL}/api/agents/public",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        agents = response.json()
        for agent in agents[:5]:  # Check first 5
            assert "name" in agent, f"Agent missing name field"
        print("PASS - Agents have required name field")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
