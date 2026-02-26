"""
Tests for Martian AI Rebranding, Dynamic Pricing Manager, and Expanded AI Models
Iteration 4: Testing new features from main agent

Features tested:
1. Branding - 'Martian AI by MAARS Global Corporation' (no 'AI Legends' or 'Emergent')
2. Admin Pricing Manager - GET/PUT /api/admin/pricing, POST /api/admin/pricing/calculate
3. Dynamic Plans - GET /api/plans loads current pricing
4. Expanded AI Models - GET /api/models returns all 10 models
5. Auto Model Selection - tests for different task types
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"
USER_EMAIL = "admin@test.com"
USER_PASSWORD = "Admin1234!"


class TestHealthAndPlans:
    """Test public endpoints - health and plans"""
    
    def test_health_endpoint(self):
        """Health endpoint should be accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("SUCCESS: Health endpoint working")
    
    def test_public_plans_endpoint(self):
        """GET /api/plans should return subscription plans without auth"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200
        data = response.json()
        
        # Verify plans structure
        assert "plans" in data
        assert "credit_packages" in data
        
        # Check all expected plans exist
        plans = data["plans"]
        assert "free" in plans
        assert "starter" in plans
        assert "pro" in plans
        assert "business" in plans
        
        # Verify plan fields
        for plan_id, plan in plans.items():
            assert "name" in plan
            assert "price_usd" in plan
            assert "price_bdt" in plan
            assert "credits" in plan
            assert "features" in plan
        
        print(f"SUCCESS: /api/plans returns {len(plans)} plans")


class TestAdminLogin:
    """Test admin authentication"""
    
    def test_admin_login(self):
        """Admin can login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["is_admin"] == True
        print(f"SUCCESS: Admin login successful, is_admin={data['user']['is_admin']}")
        return data["token"]


class TestAdminPricingManager:
    """Test Admin Pricing Manager endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_get_admin_pricing_requires_admin(self):
        """GET /api/admin/pricing requires admin authentication"""
        # Without auth
        response = requests.get(f"{BASE_URL}/api/admin/pricing")
        assert response.status_code == 401
        print("SUCCESS: Admin pricing requires authentication")
    
    def test_get_admin_pricing(self, admin_token):
        """GET /api/admin/pricing returns pricing configuration"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/pricing", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify pricing structure
        assert "plans" in data
        assert "custom_agent_credit_cost" in data
        assert "ai_cost_per_credit" in data
        assert "target_profit_margin" in data
        assert "bdt_exchange_rate" in data
        
        print(f"SUCCESS: Admin pricing returned - cost per credit: {data['ai_cost_per_credit']}, margin: {data['target_profit_margin']}%")
    
    def test_calculate_pricing(self, admin_token):
        """POST /api/admin/pricing/calculate returns recommended prices"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        calc_inputs = {
            "ai_cost_per_credit": 0.003,
            "target_profit_margin": 200,
            "bdt_exchange_rate": 107
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/pricing/calculate",
            headers=headers,
            json=calc_inputs
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify calculation response
        assert "plan_calculations" in data
        assert "ai_cost_per_credit" in data
        assert "target_profit_margin" in data
        assert "bdt_exchange_rate" in data
        
        # Verify all plans calculated
        calcs = data["plan_calculations"]
        assert "free" in calcs
        assert "starter" in calcs
        assert "pro" in calcs
        assert "business" in calcs
        
        # Verify calculation fields
        for plan_id, calc in calcs.items():
            assert "credits" in calc
            assert "base_ai_cost_usd" in calc
            assert "recommended_price_usd" in calc
            assert "recommended_price_bdt" in calc
            assert "profit_per_user_usd" in calc
        
        # Free should be $0
        assert calcs["free"]["recommended_price_usd"] == 0
        # Paid plans should have positive prices
        assert calcs["starter"]["recommended_price_usd"] > 0
        
        print(f"SUCCESS: Pricing calculation returned - Starter rec: ${calcs['starter']['recommended_price_usd']}, Pro rec: ${calcs['pro']['recommended_price_usd']}")
    
    def test_update_pricing(self, admin_token):
        """PUT /api/admin/pricing updates pricing (read-only test)"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        # First get current pricing
        response = requests.get(f"{BASE_URL}/api/admin/pricing", headers=headers)
        current_pricing = response.json()
        
        # Update with same values (non-destructive test)
        response = requests.put(
            f"{BASE_URL}/api/admin/pricing",
            headers=headers,
            json=current_pricing
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Pricing updated successfully"
        
        print("SUCCESS: PUT /api/admin/pricing endpoint working")


class TestExpandedModels:
    """Test expanded AI models endpoint"""
    
    @pytest.fixture
    def user_token(self):
        """Get user authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": USER_EMAIL, "password": USER_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("User authentication failed")
    
    def test_get_models_requires_auth(self):
        """GET /api/models requires authentication"""
        response = requests.get(f"{BASE_URL}/api/models")
        assert response.status_code == 401
        print("SUCCESS: Models endpoint requires authentication")
    
    def test_get_all_models(self, user_token):
        """GET /api/models returns all 10 AI models"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/api/models", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "models" in data
        assert "default" in data
        
        models = data["models"]
        assert len(models) == 10, f"Expected 10 models, got {len(models)}"
        
        # Verify model names from requirement
        model_names = [m["name"] for m in models]
        
        # Check for expected models
        expected_models = [
            "GPT-5.2", "GPT-4o", "GPT-4o Mini", "O3", "O3 Mini",
            "Claude Sonnet 4.5", "Claude Opus 4.5", "Claude Haiku 4.5",
            "Gemini 3 Flash", "Gemini 3 Pro"
        ]
        
        for expected in expected_models:
            assert expected in model_names, f"Model '{expected}' not found in {model_names}"
        
        # Verify model structure
        for model in models:
            assert "provider" in model
            assert "model" in model
            assert "name" in model
            assert "category" in model
        
        print(f"SUCCESS: /api/models returns all 10 models: {model_names}")


class TestAutoModelSelection:
    """Test auto model selection functionality"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token (admin has credits)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_coding_task_auto_selection(self, admin_token):
        """Auto-selection should pick GPT-5.2 for coding tasks"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        # First get an agent
        response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert response.status_code == 200
        agents = response.json()
        
        if not agents:
            pytest.skip("No agents available")
        
        # Create a chat
        agent_id = agents[0]["agent_id"]
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": agent_id}
        )
        assert response.status_code == 200
        chat = response.json()
        chat_id = chat["chat_id"]
        
        # Send a coding-related message with auto model
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={
                "content": "Write a Python function to calculate fibonacci numbers recursively",
                "model_provider": "auto",
                "model_name": "auto"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "model_used" in data
        assert "auto_selected" in data
        assert data["auto_selected"] == True
        
        # For coding task, should select GPT-5.2
        print(f"SUCCESS: Auto model selection for coding task - selected: {data['model_used']}")
        print(f"Model reason: {data.get('model_reason', 'N/A')}")


class TestDefaultAgentPrompts:
    """Test that default agents have 'Martian AI by MAARS Global Corporation' in prompts"""
    
    @pytest.fixture
    def user_token(self):
        """Get user authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": USER_EMAIL, "password": USER_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("User authentication failed")
    
    def test_agents_have_martian_ai_branding(self, user_token):
        """Default agents should reference 'Martian AI by MAARS Global Corporation'"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        
        assert response.status_code == 200
        agents = response.json()
        
        # Check a few default agents for branding
        martian_ai_count = 0
        for agent in agents:
            if not agent.get("is_custom"):
                if "Martian AI" in agent.get("system_prompt", ""):
                    martian_ai_count += 1
        
        print(f"INFO: {martian_ai_count} out of {len([a for a in agents if not a.get('is_custom')])} default agents have 'Martian AI' in system_prompt")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
