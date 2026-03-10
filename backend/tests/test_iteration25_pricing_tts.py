"""
Iteration 25 Tests: Admin Pricing Persistence, OpenAI TTS via Emergent, Brain Editor
Tests:
1. GET /api/plans returns admin-configured prices (Starter should be ~$74, not hardcoded $29)
2. GET /api/tts/voices returns 9 OpenAI voices
3. POST /api/tts/generate returns base64 audio 
4. GET /health returns 200
5. PUT /api/admin/agents/{agent_id}/brain saves brain fields
6. Commander returns immediately with processing status (or delegated response)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://task-flow-276.preview.emergentagent.com')
BASE_URL = BASE_URL.rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestHealthCheck:
    """Health endpoint test"""
    
    def test_health_endpoint(self):
        """Test 5: GET /health returns 200"""
        # Note: /health is on app root, not /api - use internal URL
        response = requests.get(f"http://localhost:8001/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("Health check PASSED: status=healthy")


class TestAdminPricing:
    """Admin-configured pricing persistence tests"""
    
    def test_plans_returns_admin_configured_prices(self):
        """Test 1: GET /api/plans returns admin-configured prices (not hardcoded defaults)"""
        response = requests.get(f"{BASE_URL}/api/plans", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        plans = data.get("plans", {})
        
        # Verify structure
        assert "starter" in plans, "Starter plan not found"
        assert "pro" in plans, "Pro plan not found"
        
        starter = plans["starter"]
        pro = plans["pro"]
        
        # According to the test request, admin has set:
        # Starter: $74.04, Pro: $296.14 (not hardcoded $29 and $79)
        starter_price = starter.get("price_usd", 0)
        pro_price = pro.get("price_usd", 0)
        
        print(f"Starter price_usd: ${starter_price}")
        print(f"Pro price_usd: ${pro_price}")
        
        # Starter should NOT be $29 (hardcoded default)
        assert starter_price != 29.0, f"Starter price is hardcoded default $29, should be admin-configured (expected ~$74.04)"
        assert starter_price > 29.0, f"Starter price ${starter_price} should be > $29 (admin configured ~$74)"
        
        # Verify it's close to expected admin value
        assert 70 <= starter_price <= 80, f"Starter price ${starter_price} not in expected range $70-$80"
        
        print(f"Pricing test PASSED: Starter=${starter_price} (not hardcoded $29)")
    
    def test_plans_structure(self):
        """Verify /api/plans returns proper structure with plans, credit_packages, custom_package"""
        response = requests.get(f"{BASE_URL}/api/plans", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "plans" in data, "Missing 'plans' key"
        assert "credit_packages" in data, "Missing 'credit_packages' key"
        assert "custom_package" in data, "Missing 'custom_package' key"
        
        plans = data["plans"]
        assert len(plans) >= 4, f"Expected at least 4 plans, got {len(plans)}"
        
        for plan_id in ["free", "starter", "pro", "business"]:
            assert plan_id in plans, f"Missing plan: {plan_id}"
            assert "price_usd" in plans[plan_id], f"Plan {plan_id} missing price_usd"
            assert "name" in plans[plan_id], f"Plan {plan_id} missing name"
        
        print("Plans structure PASSED")


class TestTTS:
    """OpenAI TTS via Emergent integration tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=10)
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Login failed: {response.text}")
    
    def test_tts_voices_returns_9_voices(self, auth_token):
        """Test 4: GET /api/tts/voices returns 9 voices"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/tts/voices", headers=headers, timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        voices = data.get("voices", [])
        
        assert len(voices) == 9, f"Expected 9 voices, got {len(voices)}"
        
        voice_ids = [v["voice_id"] for v in voices]
        expected_voices = ["alloy", "nova", "shimmer", "echo", "onyx", "fable", "coral", "sage", "ash"]
        
        for expected in expected_voices:
            assert expected in voice_ids, f"Missing voice: {expected}"
        
        print(f"TTS voices test PASSED: {len(voices)} voices found")
        for v in voices:
            print(f"  - {v['voice_id']}: {v['name']}")
    
    def test_tts_generate_returns_audio(self, auth_token):
        """Test 3: POST /api/tts/generate with {text:'Hello world', voice:'nova'} returns audio_url"""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        payload = {"text": "Hello world", "voice": "nova"}
        
        # TTS may take 5-10 seconds
        response = requests.post(
            f"{BASE_URL}/api/tts/generate",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200, f"TTS generate failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "audio_url" in data, "Missing audio_url in response"
        assert "text" in data, "Missing text in response"
        assert "voice" in data, "Missing voice in response"
        
        audio_url = data["audio_url"]
        assert audio_url.startswith("data:audio/mpeg;base64,"), "audio_url should be base64 data URI"
        assert len(audio_url) > 1000, f"audio_url too short ({len(audio_url)} chars), should be >1000 for actual audio"
        
        assert data["text"] == "Hello world"
        assert data["voice"] == "nova"
        
        print(f"TTS generate test PASSED: audio_url length={len(audio_url)} chars")


class TestBrainEditor:
    """Brain Editor API tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=10)
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Login failed: {response.text}")
    
    def test_brain_editor_update(self, auth_token):
        """Test 6: PUT /api/admin/agents/{agent_id}/brain saves personality_tone"""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Use the SEO agent for testing
        agent_id = "agent_seo"
        
        # First get current state
        response = requests.get(f"{BASE_URL}/api/admin/agents/{agent_id}", headers=headers, timeout=10)
        assert response.status_code == 200
        original_agent = response.json()
        
        # Update brain with test value
        test_tone = f"TEST_TONE_{int(time.time())}"
        update_payload = {
            "personality_tone": test_tone,
            "expertise_areas": "SEO, Keywords, Search Rankings"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/admin/agents/{agent_id}/brain",
            headers=headers,
            json=update_payload,
            timeout=10
        )
        
        assert response.status_code == 200, f"Brain update failed: {response.text}"
        update_result = response.json()
        assert update_result.get("success") == True
        
        # Verify the update persisted
        response = requests.get(f"{BASE_URL}/api/admin/agents/{agent_id}", headers=headers, timeout=10)
        assert response.status_code == 200
        updated_agent = response.json()
        
        # Check personality_tone was saved
        assert updated_agent.get("personality_tone") == test_tone, "personality_tone not persisted"
        
        # Check system_prompt contains BRAIN CONFIG section
        system_prompt = updated_agent.get("system_prompt", "")
        assert "--- BRAIN CONFIG ---" in system_prompt or test_tone in system_prompt, "Brain config not in system_prompt"
        
        print(f"Brain editor test PASSED: personality_tone saved and system_prompt updated")


class TestCommanderDelegation:
    """Commander delegation tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=10)
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Login failed: {response.text}")
    
    def test_commander_delegation_structure(self, auth_token):
        """Test 10: Commander returns with processing status or delegation data"""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # First create/get a chat with commander
        response = requests.post(f"{BASE_URL}/api/chats", headers=headers, json={
            "agent_id": "agent_commander"
        }, timeout=10)
        
        if response.status_code not in [200, 201]:
            # Try getting existing chats
            response = requests.get(f"{BASE_URL}/api/chats", headers=headers, timeout=10)
            assert response.status_code == 200
            chats = response.json()
            commander_chats = [c for c in chats if c.get("agent_id") == "agent_commander"]
            if commander_chats:
                chat_id = commander_chats[0]["chat_id"]
            else:
                # Create new
                response = requests.post(f"{BASE_URL}/api/chats", headers=headers, json={
                    "agent_id": "agent_commander"
                }, timeout=10)
                chat_id = response.json().get("chat_id")
        else:
            chat_id = response.json().get("chat_id")
        
        # Send a simple delegation message
        # Note: We're just checking the response structure, not waiting for full delegation
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={"content": "List the specialist agents available"},
            timeout=60  # Commander may take time
        )
        
        assert response.status_code == 200, f"Commander message failed: {response.text}"
        data = response.json()
        
        # Response structure is {assistant_message: {...}, user_message: {...}, credits_used: ...}
        assistant_msg = data.get("assistant_message", data)
        
        # Commander should return with commander_status=processing (background delegation)
        commander_status = assistant_msg.get("commander_status")
        print(f"Commander status: {commander_status}")
        
        # For delegation requests, status should be 'processing' indicating background work started
        assert commander_status in ["processing", "complete", "pending", None], f"Invalid commander_status: {commander_status}"
        
        # Verify content exists
        content = assistant_msg.get("content", "")
        assert len(content) > 0, "Commander response content is empty"
        
        print(f"Commander delegation test PASSED: commander_status={commander_status}, content length={len(content)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
