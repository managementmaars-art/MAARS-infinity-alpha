"""
Tests for Admin API Keys and Provider functionality
Verifies that all 9 providers are properly configured in the backend
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://multi-agent-business.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"

# Expected 9 providers
ALL_PROVIDERS = ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"]


@pytest.fixture(scope="module")
def admin_token():
    """Get admin JWT token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert data.get("user", {}).get("is_admin") == True, "User is not admin"
    return data["token"]


@pytest.fixture
def api_client(admin_token):
    """Create authenticated requests session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}"
    })
    return session


class TestAdminApiKeys:
    """Tests for GET /api/admin/api-keys endpoint"""
    
    def test_api_keys_endpoint_returns_200(self, api_client):
        """API Keys endpoint should return 200 for admin"""
        response = api_client.get(f"{BASE_URL}/api/admin/api-keys")
        assert response.status_code == 200
        print("GET /api/admin/api-keys returns 200")
    
    def test_api_keys_has_cost_reference(self, api_client):
        """API Keys response should include cost_reference"""
        response = api_client.get(f"{BASE_URL}/api/admin/api-keys")
        data = response.json()
        assert "cost_reference" in data, "cost_reference not in response"
        print("cost_reference found in response")
    
    def test_cost_reference_has_all_9_providers(self, api_client):
        """cost_reference should have all 9 providers"""
        response = api_client.get(f"{BASE_URL}/api/admin/api-keys")
        data = response.json()
        cost_reference = data.get("cost_reference", {})
        
        missing = []
        for provider in ALL_PROVIDERS:
            if provider not in cost_reference:
                missing.append(provider)
        
        assert len(missing) == 0, f"Missing providers in cost_reference: {missing}"
        assert len(cost_reference) >= 9, f"Expected 9 providers, got {len(cost_reference)}"
        print(f"All 9 providers found in cost_reference: {list(cost_reference.keys())}")
    
    def test_each_provider_has_models(self, api_client):
        """Each provider in cost_reference should have models list"""
        response = api_client.get(f"{BASE_URL}/api/admin/api-keys")
        data = response.json()
        cost_reference = data.get("cost_reference", {})
        
        for provider in ALL_PROVIDERS:
            assert provider in cost_reference, f"{provider} not in cost_reference"
            provider_data = cost_reference[provider]
            assert "models" in provider_data, f"{provider} missing 'models' key"
            assert len(provider_data["models"]) > 0, f"{provider} has no models"
            print(f"{provider}: {len(provider_data['models'])} models")
    
    def test_api_keys_has_key_set_flags_for_all_providers(self, api_client):
        """Response should have {provider}_key_set flags for all 9 providers"""
        response = api_client.get(f"{BASE_URL}/api/admin/api-keys")
        data = response.json()
        
        for provider in ALL_PROVIDERS:
            key_set_field = f"{provider}_key_set"
            assert key_set_field in data, f"{key_set_field} not in response"
        print("All 9 providers have _key_set flags in response")


class TestAdminApiUsage:
    """Tests for GET /api/admin/api-usage endpoint"""
    
    def test_api_usage_endpoint_returns_200(self, api_client):
        """API Usage endpoint should return 200 for admin"""
        response = api_client.get(f"{BASE_URL}/api/admin/api-usage")
        assert response.status_code == 200
        print("GET /api/admin/api-usage returns 200")
    
    def test_api_usage_has_providers_key(self, api_client):
        """API Usage response should have providers key"""
        response = api_client.get(f"{BASE_URL}/api/admin/api-usage")
        data = response.json()
        # providers key should exist (may be empty if no keys configured)
        assert "providers" in data or "tracked_usage" in data, "Neither 'providers' nor 'tracked_usage' in response"
        print("API usage response has expected structure")


class TestAppNavigation:
    """Tests for general app navigation"""
    
    def test_landing_page_loads(self):
        """Landing page should return 200"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        print("Landing page returns 200")
    
    def test_login_endpoint_works(self):
        """Login endpoint should authenticate admin"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["is_admin"] == True
        print("Login works, admin user authenticated")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
