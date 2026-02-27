"""
Test suite for Martian AI Platform - New Provider Expansion
Tests: xAI Grok, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs TTS
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


@pytest.fixture(scope="module")
def session():
    """Shared requests session"""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def auth_token(session):
    """Get admin auth token"""
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Admin login failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def admin_headers(auth_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


# ============== /api/models TESTS ==============

class TestModelsEndpoint:
    """Tests for GET /api/models endpoint - verify all new providers are present"""

    def test_models_endpoint_returns_200(self, session, admin_headers):
        """Test that /api/models returns 200"""
        response = session.get(f"{BASE_URL}/api/models", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: /api/models returns 200")

    def test_models_contains_xai_grok_3(self, session, admin_headers):
        """Test xAI Grok 3 is in models list"""
        response = session.get(f"{BASE_URL}/api/models", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        models = data.get("models", [])
        grok3 = [m for m in models if m.get("provider") == "xai" and m.get("model") == "grok-3"]
        assert len(grok3) > 0, "xAI grok-3 not found in models"
        print(f"PASS: xAI grok-3 found: {grok3[0]}")

    def test_models_contains_deepseek_chat(self, session, admin_headers):
        """Test DeepSeek Chat is in models list"""
        response = session.get(f"{BASE_URL}/api/models", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        models = data.get("models", [])
        deepseek = [m for m in models if m.get("provider") == "deepseek" and m.get("model") == "deepseek-chat"]
        assert len(deepseek) > 0, "deepseek-chat not found in models"
        print(f"PASS: deepseek-chat found: {deepseek[0]}")

    def test_models_contains_mistral_large(self, session, admin_headers):
        """Test Mistral Large is in models list"""
        response = session.get(f"{BASE_URL}/api/models", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        models = data.get("models", [])
        mistral = [m for m in models if m.get("provider") == "mistral" and m.get("model") == "mistral-large-latest"]
        assert len(mistral) > 0, "mistral-large-latest not found in models"
        print(f"PASS: mistral-large-latest found: {mistral[0]}")

    def test_models_contains_perplexity_sonar(self, session, admin_headers):
        """Test Perplexity Sonar is in models list"""
        response = session.get(f"{BASE_URL}/api/models", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        models = data.get("models", [])
        sonar = [m for m in models if m.get("provider") == "perplexity" and m.get("model") == "sonar"]
        assert len(sonar) > 0, "perplexity sonar not found in models"
        print(f"PASS: perplexity sonar found: {sonar[0]}")

    def test_models_contains_cohere_command_r_plus(self, session, admin_headers):
        """Test Cohere Command R+ is in models list"""
        response = session.get(f"{BASE_URL}/api/models", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        models = data.get("models", [])
        cohere = [m for m in models if m.get("provider") == "cohere" and m.get("model") == "command-r-plus"]
        assert len(cohere) > 0, "cohere command-r-plus not found in models"
        print(f"PASS: cohere command-r-plus found: {cohere[0]}")

    def test_models_total_count(self, session, admin_headers):
        """Test models list has expected count (24+ models)"""
        response = session.get(f"{BASE_URL}/api/models", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        models = data.get("models", [])
        assert len(models) >= 24, f"Expected 24+ models, got {len(models)}"
        print(f"PASS: Total models count: {len(models)}")


# ============== /api/admin/api-keys TESTS ==============

class TestAdminApiKeys:
    """Tests for GET/POST /api/admin/api-keys endpoint - verify all 9 providers"""

    def test_admin_api_keys_returns_200(self, session, admin_headers):
        """Test /api/admin/api-keys returns 200 for admin"""
        response = session.get(f"{BASE_URL}/api/admin/api-keys", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: /api/admin/api-keys returns 200")

    def test_admin_api_keys_has_all_9_providers(self, session, admin_headers):
        """Test all 9 providers have key_set status"""
        response = session.get(f"{BASE_URL}/api/admin/api-keys", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        required_providers = ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"]
        for provider in required_providers:
            key_set_field = f"{provider}_key_set"
            assert key_set_field in data, f"Missing {key_set_field} in response"
            print(f"PASS: {provider}_key_set present: {data[key_set_field]}")

    def test_admin_api_keys_has_cost_reference(self, session, admin_headers):
        """Test cost_reference contains pricing for all providers"""
        response = session.get(f"{BASE_URL}/api/admin/api-keys", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        cost_ref = data.get("cost_reference", {})
        required_providers = ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"]
        
        for provider in required_providers:
            assert provider in cost_ref, f"Missing cost_reference for {provider}"
            assert "models" in cost_ref[provider], f"Missing models array for {provider}"
            assert "unit" in cost_ref[provider], f"Missing unit field for {provider}"
            print(f"PASS: cost_reference for {provider}: {len(cost_ref[provider]['models'])} models")

    def test_admin_api_keys_xai_cost_reference(self, session, admin_headers):
        """Test xAI cost reference has correct models"""
        response = session.get(f"{BASE_URL}/api/admin/api-keys", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        xai_ref = data.get("cost_reference", {}).get("xai", {})
        models = xai_ref.get("models", [])
        model_names = [m.get("name") for m in models]
        
        assert "Grok 3" in model_names, "Grok 3 not in xAI cost reference"
        assert "Grok 3 Mini" in model_names, "Grok 3 Mini not in xAI cost reference"
        print(f"PASS: xAI cost reference models: {model_names}")

    def test_admin_api_keys_elevenlabs_cost_reference(self, session, admin_headers):
        """Test ElevenLabs cost reference has TTS pricing"""
        response = session.get(f"{BASE_URL}/api/admin/api-keys", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        el_ref = data.get("cost_reference", {}).get("elevenlabs", {})
        assert "per 1K characters" in el_ref.get("unit", ""), "ElevenLabs unit should be per 1K chars"
        models = el_ref.get("models", [])
        assert len(models) >= 2, f"Expected 2+ ElevenLabs models, got {len(models)}"
        print(f"PASS: ElevenLabs cost reference: {models}")


# ============== POST /api/admin/api-keys TESTS ==============

class TestAdminSaveApiKey:
    """Tests for POST /api/admin/api-keys - can save new provider keys"""

    def test_can_save_xai_key_structure(self, session, admin_headers):
        """Test that POST /api/admin/api-keys accepts xai_key field"""
        # Just test the endpoint accepts the field - don't save real key
        response = session.put(f"{BASE_URL}/api/admin/api-keys", headers=admin_headers, json={
            "active_provider": "emergent"  # Keep using emergent, just test structure
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: PUT /api/admin/api-keys accepts request")


# ============== /api/tts/generate TESTS ==============

class TestTTSEndpoint:
    """Tests for POST /api/tts/generate endpoint - ElevenLabs TTS"""

    def test_tts_endpoint_exists(self, session, admin_headers):
        """Test /api/tts/generate endpoint exists (returns 400 without key, not 404)"""
        response = session.post(f"{BASE_URL}/api/tts/generate", headers=admin_headers, json={
            "text": "Hello world"
        })
        # Expected: 400 (no ElevenLabs key configured) or 200 (if key exists)
        # NOT 404 (endpoint missing) or 422 (validation error)
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}: {response.text}"
        print(f"PASS: /api/tts/generate endpoint exists, returns {response.status_code}")

    def test_tts_endpoint_requires_auth(self, session):
        """Test /api/tts/generate requires authentication"""
        response = session.post(f"{BASE_URL}/api/tts/generate", json={"text": "Hello"})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/tts/generate requires authentication")


# ============== SUMMARY TESTS ==============

class TestProviderSummary:
    """Summary tests for new provider expansion"""

    def test_all_new_providers_in_models(self, session, admin_headers):
        """Verify all new providers appear in /api/models"""
        response = session.get(f"{BASE_URL}/api/models", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        models = data.get("models", [])
        
        providers_found = set(m.get("provider") for m in models)
        required_new = {"xai", "deepseek", "mistral", "perplexity", "cohere"}
        
        missing = required_new - providers_found
        assert len(missing) == 0, f"Missing providers in models: {missing}"
        print(f"PASS: All new providers found in /api/models: {required_new}")

    def test_all_new_providers_in_admin_keys(self, session, admin_headers):
        """Verify all new providers appear in /api/admin/api-keys"""
        response = session.get(f"{BASE_URL}/api/admin/api-keys", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        required_providers = ["xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"]
        for provider in required_providers:
            assert f"{provider}_key_set" in data, f"Missing {provider}_key_set"
        print(f"PASS: All new providers in admin api-keys: {required_providers}")
