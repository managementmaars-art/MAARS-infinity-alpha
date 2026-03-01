"""
Iteration 40: Model-Aware Credit System Tests
Tests credit costs per model, credit tiers, and credits deducted in chat responses
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"

class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Test admin login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["is_admin"] == True
        print(f"✓ Admin login successful, is_admin={data['user']['is_admin']}")

@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for authenticated requests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Auth failed: {response.text}")
    return response.json()["token"]

@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestModelsEndpoint:
    """Test /api/models endpoint returns models with credit information"""
    
    def test_models_endpoint_returns_models(self, auth_headers):
        """Test GET /api/models returns model list with credits field"""
        response = requests.get(f"{BASE_URL}/api/models", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "models" in data, "Response should contain 'models' key"
        assert "credit_tiers" in data, "Response should contain 'credit_tiers' key"
        
        models = data["models"]
        assert len(models) >= 20, f"Expected at least 20 models, got {len(models)}"
        print(f"✓ /api/models returned {len(models)} models")
        
    def test_models_have_credits_field(self, auth_headers):
        """Verify each model has a 'credits' field"""
        response = requests.get(f"{BASE_URL}/api/models", headers=auth_headers)
        assert response.status_code == 200
        
        models = response.json()["models"]
        for model in models:
            assert "credits" in model, f"Model {model.get('name', 'unknown')} missing 'credits' field"
            assert isinstance(model["credits"], int), f"Credits should be int for {model['name']}"
            assert model["credits"] >= 1, f"Credits should be >= 1 for {model['name']}"
        
        print(f"✓ All {len(models)} models have valid 'credits' field")
    
    def test_credit_tiers_structure(self, auth_headers):
        """Verify credit_tiers contains expected tiers"""
        response = requests.get(f"{BASE_URL}/api/models", headers=auth_headers)
        assert response.status_code == 200
        
        tiers = response.json()["credit_tiers"]
        expected_tiers = ["economy", "fast", "flagship", "premium", "image_gen", "video_gen"]
        
        for tier in expected_tiers:
            assert tier in tiers, f"Missing tier: {tier}"
            assert "credits" in tiers[tier], f"Tier {tier} missing 'credits' field"
            
        # Verify specific credit values
        assert tiers["economy"]["credits"] == 1, "Economy tier should be 1 credit"
        assert tiers["fast"]["credits"] == 2, "Fast tier should be 2 credits"
        assert tiers["flagship"]["credits"] == 3, "Flagship tier should be 3 credits"
        assert tiers["premium"]["credits"] == 5, "Premium tier should be 5 credits"
        assert tiers["image_gen"]["credits"] == 5, "Image gen should be +5 credits"
        assert tiers["video_gen"]["credits"] == 10, "Video gen should be +10 credits"
        
        print(f"✓ credit_tiers structure verified with correct values")
        
    def test_specific_model_credits(self, auth_headers):
        """Verify specific models have correct credit costs"""
        response = requests.get(f"{BASE_URL}/api/models", headers=auth_headers)
        assert response.status_code == 200
        
        models = {m["model"]: m for m in response.json()["models"]}
        
        # Economy models (1 credit)
        assert models.get("gpt-4o-mini", {}).get("credits") == 1, "GPT-4o-mini should be 1 credit"
        assert models.get("claude-haiku-4-5-20250929", {}).get("credits") == 1, "Claude Haiku should be 1 credit"
        
        # Fast models (2 credits)
        assert models.get("gpt-4o", {}).get("credits") == 2, "GPT-4o should be 2 credits"
        
        # Flagship models (3 credits)
        assert models.get("gpt-5.2", {}).get("credits") == 3, "GPT-5.2 should be 3 credits"
        
        # Premium models (5 credits)
        assert models.get("claude-opus-4-5-20251101", {}).get("credits") == 5, "Claude Opus should be 5 credits"
        
        print("✓ Specific model credit costs verified")


class TestCreditDeductionEconomy:
    """Test credit deduction for economy tier models"""
    
    def test_economy_model_deduction(self, auth_headers):
        """Send message with gpt-4o-mini, verify credits_deducted=1"""
        # First create a chat
        chat_resp = requests.post(f"{BASE_URL}/api/chats", 
            headers=auth_headers,
            json={"agent_id": "agent_secretary"}
        )
        assert chat_resp.status_code == 200, f"Failed to create chat: {chat_resp.text}"
        chat_id = chat_resp.json()["chat_id"]
        
        # Send message with economy model
        msg_resp = requests.post(f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=auth_headers,
            json={
                "content": "Hello, just testing credit deduction",
                "model_provider": "openai",
                "model_name": "gpt-4o-mini"
            }
        )
        assert msg_resp.status_code == 200, f"Failed to send message: {msg_resp.text}"
        data = msg_resp.json()
        
        assert "credits_deducted" in data, "Response should contain credits_deducted"
        assert data["credits_deducted"] == 1, f"Expected 1 credit deducted for economy model, got {data['credits_deducted']}"
        
        print(f"✓ Economy model (gpt-4o-mini) correctly deducted {data['credits_deducted']} credit")


class TestCreditDeductionFlagship:
    """Test credit deduction for flagship tier models"""
    
    def test_flagship_model_deduction(self, auth_headers):
        """Send message with gpt-5.2, verify credits_deducted=3"""
        # Create a chat
        chat_resp = requests.post(f"{BASE_URL}/api/chats", 
            headers=auth_headers,
            json={"agent_id": "agent_secretary"}
        )
        assert chat_resp.status_code == 200, f"Failed to create chat: {chat_resp.text}"
        chat_id = chat_resp.json()["chat_id"]
        
        # Send message with flagship model
        msg_resp = requests.post(f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=auth_headers,
            json={
                "content": "Hello, testing flagship model credit",
                "model_provider": "openai",
                "model_name": "gpt-5.2"
            }
        )
        assert msg_resp.status_code == 200, f"Failed to send message: {msg_resp.text}"
        data = msg_resp.json()
        
        assert "credits_deducted" in data, "Response should contain credits_deducted"
        assert data["credits_deducted"] == 3, f"Expected 3 credits deducted for flagship model, got {data['credits_deducted']}"
        
        print(f"✓ Flagship model (gpt-5.2) correctly deducted {data['credits_deducted']} credits")


class TestImageGenerationCredits:
    """Test credit deduction for image generation (text + image extra)"""
    
    def test_image_generation_credits(self, auth_headers):
        """Send 'draw a logo' to agent_graphics, verify credits_deducted=8 (3+5)"""
        # Create a chat with the graphics agent
        chat_resp = requests.post(f"{BASE_URL}/api/chats", 
            headers=auth_headers,
            json={"agent_id": "agent_graphics"}
        )
        assert chat_resp.status_code == 200, f"Failed to create chat: {chat_resp.text}"
        chat_id = chat_resp.json()["chat_id"]
        
        # Send message requesting image generation - wait longer for image gen
        msg_resp = requests.post(f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=auth_headers,
            json={
                "content": "draw a simple red circle for testing",
                "model_provider": "openai",
                "model_name": "gpt-5.2"
            },
            timeout=60  # Image gen can take 10-20 seconds
        )
        assert msg_resp.status_code == 200, f"Failed to send message: {msg_resp.text}"
        data = msg_resp.json()
        
        # Check credits deducted (should be 8 = 3 text + 5 image)
        assert "credits_deducted" in data, "Response should contain credits_deducted"
        
        # If image was generated, credits should be 8
        if data.get("generated_image"):
            assert data["credits_deducted"] == 8, f"Expected 8 credits for image gen (3 text + 5 image), got {data['credits_deducted']}"
            print(f"✓ Image generation correctly deducted {data['credits_deducted']} credits (3 text + 5 image)")
            print(f"✓ Generated image URL present: {bool(data.get('generated_image'))}")
        else:
            # Image wasn't generated - just text response
            print(f"⚠ Image not generated, only text credits deducted: {data['credits_deducted']}")
            assert data["credits_deducted"] >= 3, "At minimum 3 credits should be deducted for text"


class TestNanoBanana2LandingPage:
    """Test that Nano Banana 2 appears in the landing page models section"""
    
    def test_nano_banana_2_in_models_list(self, auth_headers):
        """Check that Nano Banana 2 appears in the /api/models endpoint"""
        response = requests.get(f"{BASE_URL}/api/models", headers=auth_headers)
        assert response.status_code == 200
        
        models = response.json()["models"]
        nano_banana = next((m for m in models if "nano banana" in m.get("name", "").lower()), None)
        
        assert nano_banana is not None, "Nano Banana 2 should be in the models list"
        assert nano_banana["category"] == "image_gen", "Nano Banana 2 should be in image_gen category"
        assert nano_banana["credits"] == 5, "Nano Banana 2 should cost 5 credits"
        
        print(f"✓ Nano Banana 2 found in models: {nano_banana}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
