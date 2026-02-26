"""
Iteration 5 Tests: Commander AI Agent + Audio (STT/TTS) + ElevenLabs API Key
Tests for new features added:
- Commander AI agent in agents list
- Audio endpoints (speech-to-text, text-to-speech)
- ElevenLabs API key in admin panel
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestCommanderAIAgent:
    """Tests for Commander AI agent (agent_commander)"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["token"]

    def test_commander_agent_exists_in_agents_list(self, admin_token):
        """Commander AI agent should exist with id 'agent_commander'"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        agents = response.json()
        
        # Find Commander agent
        commander = next((a for a in agents if a["agent_id"] == "agent_commander"), None)
        assert commander is not None, "agent_commander not found in agents list"
        print(f"Commander agent found: {commander['name']}")

    def test_commander_agent_has_correct_details(self, admin_token):
        """Commander AI agent should have correct name, role, and capabilities"""
        response = requests.get(
            f"{BASE_URL}/api/agents/agent_commander",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        commander = response.json()
        
        # Verify core fields
        assert commander["name"] == "Commander Orion", f"Expected 'Commander Orion', got {commander['name']}"
        assert commander["role"] == "Commander", f"Expected role 'Commander', got {commander['role']}"
        assert "is_commander" in commander or commander.get("agent_id") == "agent_commander"
        
        # Check avatar is set
        assert commander.get("avatar"), "Commander should have an avatar"
        
        # Check capabilities
        capabilities = commander.get("capabilities", [])
        assert len(capabilities) > 0, "Commander should have capabilities"
        expected_caps = ["Task Delegation", "Strategic Planning", "Team Orchestration"]
        for cap in expected_caps:
            assert cap in capabilities, f"Expected capability '{cap}' not found"
        
        print(f"Commander details verified: {commander['name']} - {commander['role']}")
        print(f"Capabilities: {capabilities}")

    def test_commander_agent_is_first_in_default_order(self, admin_token):
        """Commander AI should appear as one of the top agents"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        agents = response.json()
        
        # Find Commander's position
        for i, agent in enumerate(agents):
            if agent["agent_id"] == "agent_commander":
                print(f"Commander found at position {i}")
                assert i < 5, f"Commander should be near top, found at position {i}"
                break


class TestAudioEndpoints:
    """Tests for audio endpoints (STT/TTS)"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["token"]

    def test_stt_endpoint_exists(self, admin_token):
        """Speech-to-text endpoint should exist at /api/audio/speech-to-text"""
        # Send an empty request to check endpoint exists
        response = requests.post(
            f"{BASE_URL}/api/audio/speech-to-text",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should return 422 (missing file) not 404
        assert response.status_code in [400, 422], f"STT endpoint should exist, got {response.status_code}: {response.text}"
        print(f"STT endpoint exists, returns {response.status_code} when no file provided")

    def test_tts_endpoint_exists(self, admin_token):
        """Text-to-speech endpoint should exist at /api/audio/text-to-speech"""
        response = requests.post(
            f"{BASE_URL}/api/audio/text-to-speech",
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            json={"text": "Hello world"}
        )
        # Should return 400 (no ElevenLabs key configured) - this is expected!
        assert response.status_code == 400, f"TTS endpoint should return 400 without ElevenLabs key, got {response.status_code}"
        
        data = response.json()
        assert "ElevenLabs API key not configured" in data.get("detail", ""), f"Expected 'ElevenLabs API key not configured' error, got: {data}"
        print(f"TTS endpoint exists and correctly returns error when no ElevenLabs key: {data['detail']}")

    def test_tts_requires_text_parameter(self, admin_token):
        """TTS endpoint should require text parameter"""
        response = requests.post(
            f"{BASE_URL}/api/audio/text-to-speech",
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            json={}
        )
        # Should return 400 or 422 for missing text
        assert response.status_code in [400, 422], f"Expected 400/422 for missing text, got {response.status_code}"
        print(f"TTS correctly validates text parameter: {response.status_code}")


class TestAdminElevenLabsKey:
    """Tests for ElevenLabs API key in admin panel"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["token"]

    def test_admin_api_keys_returns_elevenlabs_field(self, admin_token):
        """GET /api/admin/api-keys should return elevenlabs_key fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/api-keys",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check elevenlabs fields exist
        assert "elevenlabs_key" in data, "elevenlabs_key field missing from API keys response"
        assert "elevenlabs_key_set" in data, "elevenlabs_key_set field missing from API keys response"
        
        print(f"ElevenLabs key fields present in API keys response:")
        print(f"  elevenlabs_key: {data['elevenlabs_key']}")
        print(f"  elevenlabs_key_set: {data['elevenlabs_key_set']}")

    def test_admin_can_save_elevenlabs_key(self, admin_token):
        """Admin should be able to save ElevenLabs key via PUT /api/admin/api-keys"""
        # Test that endpoint accepts elevenlabs_key (we'll send a fake key)
        response = requests.put(
            f"{BASE_URL}/api/admin/api-keys",
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            json={
                "elevenlabs_key": "",  # Empty to not break anything
                "active_provider": "emergent"
            }
        )
        assert response.status_code == 200, f"Failed to save API keys: {response.text}"
        print("ElevenLabs key can be saved via admin API keys endpoint")

    def test_elevenlabs_key_test_endpoint(self, admin_token):
        """Test endpoint for ElevenLabs key should exist"""
        response = requests.post(
            f"{BASE_URL}/api/admin/api-keys/test",
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            json={"provider": "elevenlabs", "api_key": "fake-key-for-test"}
        )
        # Should return 200 with success=False or similar
        assert response.status_code == 200, f"Test endpoint failed: {response.status_code}"
        data = response.json()
        # The key is fake, so it should fail validation
        assert "success" in data, "Test endpoint should return success field"
        print(f"ElevenLabs key test endpoint works: success={data.get('success')}")


class TestAuthenticationAndAccess:
    """Test authentication requirements for new endpoints"""

    def test_stt_requires_auth(self):
        """STT endpoint should require authentication"""
        response = requests.post(f"{BASE_URL}/api/audio/speech-to-text")
        assert response.status_code == 401, f"STT should require auth, got {response.status_code}"
        print("STT endpoint correctly requires authentication")

    def test_tts_requires_auth(self):
        """TTS endpoint should require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/audio/text-to-speech",
            json={"text": "Hello"}
        )
        assert response.status_code == 401, f"TTS should require auth, got {response.status_code}"
        print("TTS endpoint correctly requires authentication")

    def test_admin_api_keys_requires_admin(self):
        """Admin API keys endpoint should require admin authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/api-keys")
        assert response.status_code == 401, f"Admin endpoint should require auth, got {response.status_code}"
        print("Admin API keys endpoint correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
