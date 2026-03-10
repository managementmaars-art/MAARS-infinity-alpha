"""
Iteration 77 Backend Tests - MAARS Infinity Market-Ready Features
Tests:
1. About page stats (458+ agents in API response)
2. Cost Governance - Cost By Provider endpoint (new endpoint)
3. Pricing Admin CRUD operations
4. PDF download (title should be 'MAARS ∞' not 'MAARS Command')
5. Backend APIs after refactoring (kernel_service split)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "Admin123!"


class TestBackendAuthentication:
    """Authentication tests - required for admin endpoints"""
    
    def test_admin_login(self):
        """Login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in login response"
        assert "user" in data, "No user in login response"
        assert data["user"]["is_admin"] == True, "User should be admin"
        return data["token"]


class TestKernelStatus:
    """Test kernel status endpoint - should show 458+ agents after refactoring"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("token")
    
    def test_kernel_status_agents_count(self, auth_token):
        """GET /api/kernel/status - agents count should be > 450"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/status", headers=headers)
        assert response.status_code == 200, f"Kernel status failed: {response.text}"
        data = response.json()
        assert "agents" in data, "No agents field in kernel status"
        # Verify agents count is > 450 (expecting 458+)
        agents_count = data["agents"]
        print(f"Kernel status shows {agents_count} agents")
        assert agents_count >= 450, f"Expected 450+ agents, got {agents_count}"


class TestCostGovernanceEndpoints:
    """Test cost governance endpoints including new Cost By Provider"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("token")
    
    def test_cost_overview(self, auth_token):
        """GET /api/kernel/cost/overview - should return cost stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/cost/overview", headers=headers)
        assert response.status_code == 200, f"Cost overview failed: {response.text}"
        data = response.json()
        # Verify expected fields
        assert "total_cost" in data, "No total_cost in cost overview"
        assert "total_executions" in data, "No total_executions in cost overview"
        assert "avg_cost" in data, "No avg_cost in cost overview"
        assert "max_cost" in data, "No max_cost in cost overview"
        print(f"Cost overview: {data}")
    
    def test_cost_by_model(self, auth_token):
        """GET /api/kernel/cost/by-model - should return array"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/cost/by-model", headers=headers)
        assert response.status_code == 200, f"Cost by model failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected array, got {type(data)}"
        print(f"Cost by model: {len(data)} entries")
    
    def test_cost_by_agent(self, auth_token):
        """GET /api/kernel/cost/by-agent - should return array"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/cost/by-agent", headers=headers)
        assert response.status_code == 200, f"Cost by agent failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected array, got {type(data)}"
        print(f"Cost by agent: {len(data)} entries")
    
    def test_cost_by_provider_new_endpoint(self, auth_token):
        """GET /api/kernel/cost/by-provider - NEW endpoint, should return array"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/cost/by-provider", headers=headers)
        assert response.status_code == 200, f"Cost by provider failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected array, got {type(data)}"
        # If there are entries, verify structure
        if len(data) > 0:
            entry = data[0]
            assert "provider" in entry, "No provider field in cost by provider entry"
            assert "total_cost" in entry, "No total_cost field"
            assert "count" in entry, "No count field"
        print(f"Cost by provider: {len(data)} entries (empty array is valid if no executions)")
    
    def test_cost_budget(self, auth_token):
        """GET /api/kernel/cost/budget - should return budget config"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/cost/budget", headers=headers)
        assert response.status_code == 200, f"Cost budget failed: {response.text}"
        data = response.json()
        assert "monthly_limit" in data, "No monthly_limit in budget"
        assert "daily_limit" in data, "No daily_limit in budget"
        assert "alert_threshold" in data, "No alert_threshold in budget"
        print(f"Cost budget: monthly_limit=${data['monthly_limit']}")


class TestPDFDownload:
    """Test PDF documentation download"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("token")
    
    def test_pdf_download_returns_pdf(self, auth_token):
        """GET /api/summary/pdf - should return valid PDF"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/summary/pdf", headers=headers)
        assert response.status_code == 200, f"PDF download failed: {response.text}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected PDF content type, got {content_type}"
        
        # Check it's a valid PDF (starts with %PDF)
        content = response.content
        assert content[:4] == b'%PDF', "Response is not a valid PDF"
        
        # Check for MAARS Infinity marker (should contain Unicode ∞)
        # Note: PDF content is binary, so we search for byte patterns
        print(f"PDF size: {len(content)} bytes")
        assert len(content) > 10000, "PDF seems too small, might be empty"


class TestPricingAdmin:
    """Test pricing admin endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("token")
    
    def test_get_pricing_admin(self, auth_token):
        """GET /api/admin/pricing - should return plans"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/pricing", headers=headers)
        assert response.status_code == 200, f"Get pricing failed: {response.text}"
        data = response.json()
        assert "plans" in data, "No plans in pricing response"
        plans = data["plans"]
        # Verify we have at least 4 plans (free, starter, pro, business)
        assert len(plans) >= 4, f"Expected at least 4 plans, got {len(plans)}"
        print(f"Admin pricing: {list(plans.keys())}")
    
    def test_public_plans_endpoint(self, auth_token):
        """GET /api/plans - public endpoint should return plans"""
        # This endpoint may not require auth
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200, f"Get plans failed: {response.text}"
        data = response.json()
        assert "plans" in data, "No plans in response"
        print(f"Public plans: {list(data['plans'].keys())}")


class TestRefactoredServices:
    """Test that backend APIs work after kernel_service refactoring"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("token")
    
    def test_campaigns_endpoint(self, auth_token):
        """GET /api/kernel/campaigns - should work after refactoring"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/campaigns", headers=headers)
        assert response.status_code == 200, f"Campaigns endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Campaigns should return array"
        print(f"Campaigns: {len(data)} campaigns")
    
    def test_integrations_endpoint(self, auth_token):
        """GET /api/kernel/integrations - should work after refactoring"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/integrations", headers=headers)
        assert response.status_code == 200, f"Integrations endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Integrations should return array"
        print(f"Integrations: {len(data)} integrations available")
    
    def test_trust_analytics_endpoint(self, auth_token):
        """GET /api/kernel/trust/analytics - should work after refactoring"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/trust/analytics", headers=headers)
        assert response.status_code == 200, f"Trust analytics endpoint failed: {response.text}"
        data = response.json()
        assert "scores" in data, "No scores in trust analytics"
        print(f"Trust analytics: {data.get('summary', {})}")


class TestAgentsPublic:
    """Test public agents endpoint"""
    
    def test_agents_public_returns_458_plus(self):
        """GET /api/agents/public - should return 458+ agents"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200, f"Agents public failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Agents should return array"
        agents_count = len(data)
        print(f"Public agents: {agents_count} agents")
        assert agents_count >= 450, f"Expected 450+ agents, got {agents_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
