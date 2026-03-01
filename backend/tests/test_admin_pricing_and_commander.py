"""
Test suite for Admin Pricing Manager with real cost data and Commander AI delegation
Testing the new features:
1. Admin avg-cost endpoint returns real usage data
2. Pricing calculator uses real cost values
3. Commander delegation returns structured group chat data
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-team-commander.preview.emergentagent.com')

# Admin credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Test admin can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["is_admin"] == True
        assert data["user"]["email"] == ADMIN_EMAIL


class TestAdminAvgCostEndpoint:
    """Tests for the new /api/admin/avg-cost endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_avg_cost_returns_real_usage(self, admin_token):
        """Test that avg-cost endpoint returns real usage data, not hardcoded 0.003"""
        response = requests.get(
            f"{BASE_URL}/api/admin/avg-cost",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "avg_cost_per_credit" in data
        assert "total_calls" in data
        assert "source" in data
        
        # Since there are usage logs, source should be "real_usage"
        # and avg_cost should be different from default 0.003
        if data["total_calls"] > 0:
            assert data["source"] == "real_usage"
            # avg_cost should be positive and reasonable (not 0)
            assert data["avg_cost_per_credit"] > 0
            print(f"Real avg cost: ${data['avg_cost_per_credit']:.6f} from {data['total_calls']} calls")
        else:
            assert data["source"] == "default"
            assert data["avg_cost_per_credit"] == 0.003
    
    def test_avg_cost_requires_admin(self):
        """Test that avg-cost endpoint requires admin access"""
        response = requests.get(f"{BASE_URL}/api/admin/avg-cost")
        assert response.status_code == 401
    
    def test_avg_cost_returns_non_default_value(self, admin_token):
        """Test that avg cost is not the old hardcoded $0.003 when there's usage data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/avg-cost",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        if data["total_calls"] > 0:
            # The real cost should be different from the old default
            assert data["avg_cost_per_credit"] != 0.003, "avg_cost should not be the old hardcoded 0.003"


class TestPricingCalculator:
    """Tests for the pricing calculator with real cost data"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_calculate_pricing_with_real_cost(self, admin_token):
        """Test calculating prices with real cost data"""
        # First get the real avg cost
        avg_cost_resp = requests.get(
            f"{BASE_URL}/api/admin/avg-cost",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        avg_cost_data = avg_cost_resp.json()
        real_cost = avg_cost_data["avg_cost_per_credit"]
        
        # Calculate pricing with real cost
        response = requests.post(
            f"{BASE_URL}/api/admin/pricing/calculate",
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            json={
                "ai_cost_per_credit": real_cost,
                "target_profit_margin": 200,
                "bdt_exchange_rate": 107
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "plan_calculations" in data
        assert "starter" in data["plan_calculations"]
        assert "pro" in data["plan_calculations"]
        assert "business" in data["plan_calculations"]
        
        # Verify starter plan calculation
        starter = data["plan_calculations"]["starter"]
        assert "base_ai_cost_usd" in starter
        assert "recommended_price_usd" in starter
        assert "profit_per_user_usd" in starter
        
        # Verify that base_ai_cost is calculated correctly (500 credits * real_cost)
        expected_base_cost = round(500 * real_cost, 2)
        assert starter["base_ai_cost_usd"] == expected_base_cost
        
        print(f"Starter plan: Cost ${starter['base_ai_cost_usd']}, Recommended ${starter['recommended_price_usd']}")
    
    def test_get_pricing_config(self, admin_token):
        """Test getting current pricing configuration"""
        response = requests.get(
            f"{BASE_URL}/api/admin/pricing",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "plans" in data
        assert "ai_cost_per_credit" in data
        assert "bdt_exchange_rate" in data


class TestCommanderDelegation:
    """Tests for Commander AI delegation structure (code review)"""
    
    def test_commander_exists_in_agents(self):
        """Test that Commander Orion exists in public agents"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        agents = response.json()
        
        commander = next((a for a in agents if a["agent_id"] == "agent_commander"), None)
        assert commander is not None
        assert commander["name"] == "Commander Orion"
        assert commander["is_commander"] == True
        assert "Task Delegation" in commander["capabilities"]


class TestChatPage:
    """Tests for chat page functionality"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_agents_authenticated(self, admin_token):
        """Test getting agents list when authenticated"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) >= 21  # 21 default agents
        
        # Commander should be first
        assert agents[0]["agent_id"] == "agent_commander"
    
    def test_create_chat_with_agent(self, admin_token):
        """Test creating a chat with an agent"""
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            json={"agent_id": "agent_strategist"}
        )
        assert response.status_code == 200
        chat = response.json()
        assert "chat_id" in chat
        assert chat["agent_id"] == "agent_strategist"


class TestLandingPage:
    """Tests for landing page endpoints"""
    
    def test_public_agents_endpoint(self):
        """Test that public agents endpoint works"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) >= 21


class TestAdminStats:
    """Tests for admin statistics"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_get_admin_stats(self, admin_token):
        """Test getting admin statistics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        stats = response.json()
        
        assert "total_users" in stats
        assert "total_chats" in stats
        assert "total_agents" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
