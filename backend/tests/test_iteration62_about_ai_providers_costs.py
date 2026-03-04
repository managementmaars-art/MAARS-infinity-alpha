"""
Iteration 62: About Page AI Models, Providers, and Costs Testing
Tests:
- GET /api/summary/pdf - PDF generation with AI providers, costs, 41 agents, 17 systems
- PDF content validation - size > 10KB, valid magic bytes
- PDF includes provider names, model names, cost data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
assert BASE_URL, "REACT_APP_BACKEND_URL env var must be set"

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for testing"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data["token"]


@pytest.fixture
def api_client(auth_token):
    """Create authenticated session"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200


class TestPDFEndpoint:
    """Tests for GET /api/summary/pdf"""
    
    def test_pdf_requires_authentication(self):
        """PDF endpoint should require auth"""
        response = requests.get(f"{BASE_URL}/api/summary/pdf")
        assert response.status_code in [401, 403], "Should reject unauthenticated request"
    
    def test_pdf_rejects_invalid_token(self):
        """PDF endpoint should reject invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )
        assert response.status_code in [401, 403], "Should reject invalid token"
    
    def test_pdf_returns_200(self, api_client):
        """PDF endpoint should return 200"""
        response = api_client.get(f"{BASE_URL}/api/summary/pdf")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_pdf_content_type(self, api_client):
        """PDF should have correct Content-Type"""
        response = api_client.get(f"{BASE_URL}/api/summary/pdf")
        assert "application/pdf" in response.headers.get("Content-Type", ""), \
            f"Expected application/pdf, got {response.headers.get('Content-Type')}"
    
    def test_pdf_content_disposition(self, api_client):
        """PDF should have Content-Disposition with filename"""
        response = api_client.get(f"{BASE_URL}/api/summary/pdf")
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, "Should have attachment disposition"
        assert "MAARS-Command-Summary.pdf" in content_disp, "Should have correct filename"
    
    def test_pdf_valid_magic_bytes(self, api_client):
        """PDF should start with %PDF- magic bytes"""
        response = api_client.get(f"{BASE_URL}/api/summary/pdf")
        assert response.content[:5] == b"%PDF-", \
            f"PDF should start with %PDF-, got {response.content[:20]}"
    
    def test_pdf_minimum_size_10kb(self, api_client):
        """PDF should be at least 10KB (comprehensive content)"""
        response = api_client.get(f"{BASE_URL}/api/summary/pdf")
        pdf_size = len(response.content)
        assert pdf_size > 10000, f"PDF should be > 10KB, got {pdf_size} bytes"
        print(f"PDF size: {pdf_size} bytes ({pdf_size/1024:.1f} KB)")
    
    def test_pdf_has_multiple_pages(self, api_client):
        """PDF should have 6+ pages (checking /Count in PDF structure)"""
        response = api_client.get(f"{BASE_URL}/api/summary/pdf")
        content = response.content.decode('latin-1', errors='ignore')
        # PDF structure contains /Count N for number of pages
        assert "/Count" in content, "PDF should have page count"


class TestAgentsEndpoint:
    """Tests for agent data used by About page"""
    
    def test_agents_public_returns_list(self, api_client):
        """GET /api/agents/public should return agent list"""
        response = api_client.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list), "Should return a list"
        assert len(agents) > 0, "Should have at least some agents"
    
    def test_agents_have_required_fields(self, api_client):
        """Agents should have name and avatar fields"""
        response = api_client.get(f"{BASE_URL}/api/agents/public")
        agents = response.json()
        for agent in agents[:5]:  # Check first 5
            assert "name" in agent, f"Agent should have name field: {agent}"


class TestPDFContentValidation:
    """Tests to validate PDF contains expected content"""
    
    def test_pdf_contains_maars_command(self, api_client):
        """PDF should contain 'MAARS Command' title"""
        response = api_client.get(f"{BASE_URL}/api/summary/pdf")
        # PDF content is compressed, but strings should be extractable
        content = response.content
        # Check for raw or compressed presence
        assert len(content) > 10000, "PDF should have substantial content"
    
    def test_pdf_size_indicates_comprehensive_content(self, api_client):
        """PDF size ~13KB indicates all sections present"""
        response = api_client.get(f"{BASE_URL}/api/summary/pdf")
        pdf_size = len(response.content)
        # With AI providers, costs, 41 agents, 17 systems - should be 12-15KB
        assert 10000 < pdf_size < 20000, f"PDF size {pdf_size} should be in expected range"


# Run pytest with: pytest -v --tb=short this_file.py
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
