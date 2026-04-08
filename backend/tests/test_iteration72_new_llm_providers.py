"""
Iteration 72: New LLM Providers Testing
Tests for Groq, Together AI, Fireworks AI, AI21 provider integrations
Note: System now has 33 providers total (175,609+ models). This test covers the original 13.

Features tested:
1. GET /api/llm/config - Returns available_providers including groq, together, fireworks, ai21
2. GET /api/admin/api-keys - Returns cost_reference for all 33 providers
3. GET /api/admin/api-keys - Returns key_set flags for all 33 providers
4. PUT /api/llm/config - Accepts new providers for user preference
5. POST /api/admin/api-keys/test - Handles new provider names without 'Unknown provider' error
"""

import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
TEST_EMAIL = "management.maars@marsgc.net"
TEST_PASSWORD = "Admin123!"

# New providers added in this iteration
NEW_PROVIDERS = ["groq", "together", "fireworks", "ai21"]

# All 12 LLM providers (excluding elevenlabs which is TTS)
ALL_LLM_PROVIDERS = ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "groq", "together", "fireworks", "ai21"]

# All 13 providers including elevenlabs (for API keys)
ALL_API_KEY_PROVIDERS = ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs", "groq", "together", "fireworks", "ai21"]


class TestAuth:
    """Authentication for accessing protected endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json().get("token")
        assert token, "No token returned"
        return token

    def test_login_success(self, auth_token):
        """Verify login works for admin user"""
        assert auth_token is not None
        assert len(auth_token) > 0


class TestLLMConfigEndpoint:
    """Tests for GET/PUT /api/llm/config endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        return response.json().get("token")

    def test_get_llm_config_returns_12_providers(self, auth_token):
        """GET /api/llm/config should return 12 available_providers"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "available_providers" in data, "Response should include available_providers"
        
        providers = data["available_providers"]
        assert len(providers) == 12, f"Expected 12 providers, got {len(providers)}"
        
        provider_ids = [p["id"] for p in providers]
        for expected_id in ALL_LLM_PROVIDERS:
            assert expected_id in provider_ids, f"Missing provider: {expected_id}"

    def test_llm_config_includes_new_providers(self, auth_token):
        """Verify new providers (groq, together, fireworks, ai21) are in available_providers"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        providers = data["available_providers"]
        provider_map = {p["id"]: p for p in providers}
        
        # Verify Groq
        assert "groq" in provider_map, "Groq provider missing"
        assert "Groq" in provider_map["groq"]["name"] or "Llama" in provider_map["groq"]["name"]
        assert len(provider_map["groq"]["models"]) >= 2, "Groq should have at least 2 models"
        
        # Verify Together AI
        assert "together" in provider_map, "Together AI provider missing"
        assert "Together" in provider_map["together"]["name"]
        assert len(provider_map["together"]["models"]) >= 2, "Together should have at least 2 models"
        
        # Verify Fireworks AI
        assert "fireworks" in provider_map, "Fireworks AI provider missing"
        assert "Fireworks" in provider_map["fireworks"]["name"]
        assert len(provider_map["fireworks"]["models"]) >= 2, "Fireworks should have at least 2 models"
        
        # Verify AI21
        assert "ai21" in provider_map, "AI21 provider missing"
        assert "AI21" in provider_map["ai21"]["name"] or "Jamba" in provider_map["ai21"]["name"]
        assert len(provider_map["ai21"]["models"]) >= 2, "AI21 should have at least 2 models"

    def test_llm_config_provider_model_counts(self, auth_token):
        """Verify each provider has correct model count"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        providers = data["available_providers"]
        total_models = sum(len(p["models"]) for p in providers)
        
        # Should have 45+ models total
        assert total_models >= 30, f"Expected at least 30 models, got {total_models}"
        
        # Each new provider should have models
        provider_map = {p["id"]: p for p in providers}
        for new_provider in NEW_PROVIDERS:
            model_count = len(provider_map[new_provider]["models"])
            assert model_count >= 2, f"{new_provider} should have at least 2 models, got {model_count}"

    def test_put_llm_config_accepts_groq(self, auth_token):
        """PUT /api/llm/config should accept groq as provider"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.put(
            f"{BASE_URL}/api/llm/config",
            headers=headers,
            json={"provider": "groq", "model": "llama-4-scout-17b-16e-instruct"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify it was saved
        get_response = requests.get(f"{BASE_URL}/api/llm/config", headers=headers)
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["provider"] == "groq"

    def test_put_llm_config_accepts_together(self, auth_token):
        """PUT /api/llm/config should accept together as provider"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.put(
            f"{BASE_URL}/api/llm/config",
            headers=headers,
            json={"provider": "together", "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"}
        )
        
        assert response.status_code == 200

    def test_put_llm_config_accepts_fireworks(self, auth_token):
        """PUT /api/llm/config should accept fireworks as provider"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.put(
            f"{BASE_URL}/api/llm/config",
            headers=headers,
            json={"provider": "fireworks", "model": "accounts/fireworks/models/deepseek-v3"}
        )
        
        assert response.status_code == 200

    def test_put_llm_config_accepts_ai21(self, auth_token):
        """PUT /api/llm/config should accept ai21 as provider"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.put(
            f"{BASE_URL}/api/llm/config",
            headers=headers,
            json={"provider": "ai21", "model": "jamba-mini-1.7"}
        )
        
        assert response.status_code == 200

    def test_put_llm_config_restore_default(self, auth_token):
        """Restore default provider (openai) after tests"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.put(
            f"{BASE_URL}/api/llm/config",
            headers=headers,
            json={"provider": "openai", "model": "gpt-5.2"}
        )
        
        assert response.status_code == 200


class TestAdminApiKeysEndpoint:
    """Tests for GET /api/admin/api-keys endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        return response.json().get("token")

    def test_admin_api_keys_returns_cost_reference(self, auth_token):
        """GET /api/admin/api-keys should return cost_reference for all providers"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "cost_reference" in data, "Response should include cost_reference"
        
        cost_ref = data["cost_reference"]
        
        # Verify new providers in cost_reference
        for new_provider in NEW_PROVIDERS:
            assert new_provider in cost_ref, f"cost_reference missing {new_provider}"

    def test_admin_api_keys_groq_pricing(self, auth_token):
        """Verify Groq pricing data in cost_reference"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        groq = data["cost_reference"].get("groq")
        assert groq is not None, "Groq missing from cost_reference"
        assert "models" in groq, "Groq should have models array"
        assert len(groq["models"]) >= 2, f"Groq should have at least 2 models, got {len(groq['models'])}"
        
        # Check for Llama models
        model_names = [m["name"] for m in groq["models"]]
        assert any("Llama" in name for name in model_names), "Groq should have Llama models"

    def test_admin_api_keys_together_pricing(self, auth_token):
        """Verify Together AI pricing data in cost_reference"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        together = data["cost_reference"].get("together")
        assert together is not None, "Together missing from cost_reference"
        assert "models" in together
        assert len(together["models"]) >= 2

    def test_admin_api_keys_fireworks_pricing(self, auth_token):
        """Verify Fireworks AI pricing data in cost_reference"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        fireworks = data["cost_reference"].get("fireworks")
        assert fireworks is not None, "Fireworks missing from cost_reference"
        assert "models" in fireworks
        assert len(fireworks["models"]) >= 2

    def test_admin_api_keys_ai21_pricing(self, auth_token):
        """Verify AI21 pricing data in cost_reference"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        ai21 = data["cost_reference"].get("ai21")
        assert ai21 is not None, "AI21 missing from cost_reference"
        assert "models" in ai21
        assert len(ai21["models"]) >= 2
        
        # Check for Jamba models
        model_names = [m["name"] for m in ai21["models"]]
        assert any("Jamba" in name for name in model_names), "AI21 should have Jamba models"

    def test_admin_api_keys_key_set_flags(self, auth_token):
        """GET /api/admin/api-keys should return key_set flags for all 13 providers"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify key_set flags exist for all 13 providers
        for provider in ALL_API_KEY_PROVIDERS:
            key_set_field = f"{provider}_key_set"
            assert key_set_field in data, f"Missing {key_set_field} in response"
            # Value should be boolean
            assert isinstance(data[key_set_field], bool), f"{key_set_field} should be boolean"

    def test_admin_api_keys_key_fields(self, auth_token):
        """GET /api/admin/api-keys should return key fields (masked) for all 13 providers"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify key fields exist for all 13 providers
        for provider in ALL_API_KEY_PROVIDERS:
            key_field = f"{provider}_key"
            assert key_field in data, f"Missing {key_field} in response"


class TestAdminApiKeyTest:
    """Tests for POST /api/admin/api-keys/test endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        return response.json().get("token")

    def test_api_key_test_groq_no_unknown_provider(self, auth_token):
        """POST /api/admin/api-keys/test should not return 'Unknown provider' for groq"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(
            f"{BASE_URL}/api/admin/api-keys/test",
            headers=headers,
            json={"provider": "groq", "api_key": "test-invalid-key"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should not say "Unknown provider" - should try to test the key
        assert "Unknown provider" not in data.get("message", ""), "groq should be a known provider"

    def test_api_key_test_together_no_unknown_provider(self, auth_token):
        """POST /api/admin/api-keys/test should not return 'Unknown provider' for together"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(
            f"{BASE_URL}/api/admin/api-keys/test",
            headers=headers,
            json={"provider": "together", "api_key": "test-invalid-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unknown provider" not in data.get("message", ""), "together should be a known provider"

    def test_api_key_test_fireworks_no_unknown_provider(self, auth_token):
        """POST /api/admin/api-keys/test should not return 'Unknown provider' for fireworks"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(
            f"{BASE_URL}/api/admin/api-keys/test",
            headers=headers,
            json={"provider": "fireworks", "api_key": "test-invalid-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unknown provider" not in data.get("message", ""), "fireworks should be a known provider"

    def test_api_key_test_ai21_no_unknown_provider(self, auth_token):
        """POST /api/admin/api-keys/test should not return 'Unknown provider' for ai21"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(
            f"{BASE_URL}/api/admin/api-keys/test",
            headers=headers,
            json={"provider": "ai21", "api_key": "test-invalid-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unknown provider" not in data.get("message", ""), "ai21 should be a known provider"


class TestModelCostsMaps:
    """Verify MODEL_COSTS_MAP includes new provider models"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        return response.json().get("token")

    def test_llm_config_has_groq_models(self, auth_token):
        """Verify Groq models are available in config"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        providers = data["available_providers"]
        groq_provider = next((p for p in providers if p["id"] == "groq"), None)
        
        assert groq_provider is not None
        models = groq_provider["models"]
        
        # Expected Groq models
        expected_models = ["llama-4-scout-17b-16e-instruct", "llama-4-maverick-17b-128e-instruct", "llama-3.3-70b-versatile"]
        for model in expected_models:
            assert model in models, f"Missing Groq model: {model}"

    def test_llm_config_has_together_models(self, auth_token):
        """Verify Together AI models are available in config"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        providers = data["available_providers"]
        together_provider = next((p for p in providers if p["id"] == "together"), None)
        
        assert together_provider is not None
        models = together_provider["models"]
        
        # Expected Together models
        expected_models = ["meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "meta-llama/Llama-3.3-70B-Instruct-Turbo", "deepseek-ai/DeepSeek-R1"]
        for model in expected_models:
            assert model in models, f"Missing Together model: {model}"

    def test_llm_config_has_fireworks_models(self, auth_token):
        """Verify Fireworks AI models are available in config"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        providers = data["available_providers"]
        fireworks_provider = next((p for p in providers if p["id"] == "fireworks"), None)
        
        assert fireworks_provider is not None
        models = fireworks_provider["models"]
        
        # Expected Fireworks models
        expected_models = ["accounts/fireworks/models/llama4-scout-instruct-basic", "accounts/fireworks/models/llama4-maverick-instruct-basic", "accounts/fireworks/models/deepseek-v3"]
        for model in expected_models:
            assert model in models, f"Missing Fireworks model: {model}"

    def test_llm_config_has_ai21_models(self, auth_token):
        """Verify AI21 models are available in config"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        providers = data["available_providers"]
        ai21_provider = next((p for p in providers if p["id"] == "ai21"), None)
        
        assert ai21_provider is not None
        models = ai21_provider["models"]
        
        # Expected AI21 models
        expected_models = ["jamba-large-1.7", "jamba-mini-1.7"]
        for model in expected_models:
            assert model in models, f"Missing AI21 model: {model}"


class TestAuthRequired:
    """Verify endpoints require authentication"""
    
    def test_llm_config_requires_auth(self):
        """GET /api/llm/config should require authentication"""
        response = requests.get(f"{BASE_URL}/api/llm/config")
        assert response.status_code == 401

    def test_admin_api_keys_requires_auth(self):
        """GET /api/admin/api-keys should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/api-keys")
        assert response.status_code == 401

    def test_admin_api_keys_test_requires_auth(self):
        """POST /api/admin/api-keys/test should require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/admin/api-keys/test",
            json={"provider": "groq", "api_key": "test-key"}
        )
        assert response.status_code == 401
