"""
Iteration 66: MAARS Command Pricing Page Update Tests
Tests that the plans API returns updated data: 41 AI agents, 9 LLM providers, 17 core systems, etc.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_backend_health(self):
        """Backend health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("PASS: Backend health check")
    
    def test_plans_endpoint_accessible(self):
        """Plans endpoint is public (no auth required)"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200
        print("PASS: Plans endpoint accessible")


class TestPlansAPIStructure:
    """Test GET /api/plans returns correct structure"""
    
    def test_plans_returns_all_plan_tiers(self):
        """Plans API returns free, starter, pro, business tiers"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200
        data = response.json()
        
        assert "plans" in data
        plans = data["plans"]
        
        expected_tiers = ["free", "starter", "pro", "business"]
        for tier in expected_tiers:
            assert tier in plans, f"Missing tier: {tier}"
        
        print(f"PASS: All 4 plan tiers present: {list(plans.keys())}")
    
    def test_plans_have_required_fields(self):
        """Each plan has required fields: name, price_usd, price_bdt, credits, features"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plans = data["plans"]
        
        required_fields = ["name", "price_usd", "price_bdt", "credits", "features", "max_agents"]
        
        for tier, plan in plans.items():
            for field in required_fields:
                assert field in plan, f"Plan '{tier}' missing field: {field}"
        
        print("PASS: All plans have required fields")
    
    def test_custom_package_config_present(self):
        """Plans API returns custom_package config"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        
        assert "custom_package" in data
        custom = data["custom_package"]
        
        assert "per_agent_price_usd" in custom
        assert "credit_presets" in custom
        
        print("PASS: Custom package config present")
    
    def test_credit_packages_present(self):
        """Plans API returns credit packages"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        
        assert "credit_packages" in data
        packages = data["credit_packages"]
        
        assert len(packages) >= 1
        print(f"PASS: Credit packages present: {len(packages)} packages")


class TestFreePlanFeatures:
    """Test Free plan has correct updated features"""
    
    def test_free_plan_max_agents_3(self):
        """Free plan allows 3 agents (not 1)"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["free"]
        
        assert plan["max_agents"] == 3
        print(f"PASS: Free plan max_agents = {plan['max_agents']}")
    
    def test_free_plan_has_ai_agents_feature(self):
        """Free plan features mention '3 AI agents' (not employees)"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["free"]
        
        features_text = " ".join(plan["features"]).lower()
        
        assert "3 ai agents" in features_text or "3 ai agent" in features_text
        assert "employee" not in features_text
        
        print(f"PASS: Free plan features: {plan['features']}")


class TestStarterPlanFeatures:
    """Test Starter plan has correct updated features"""
    
    def test_starter_plan_max_agents_10(self):
        """Starter plan allows 10 agents"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["starter"]
        
        assert plan["max_agents"] == 10
        print(f"PASS: Starter plan max_agents = {plan['max_agents']}")
    
    def test_starter_plan_has_ai_agents_feature(self):
        """Starter plan features mention '10 AI agents' (not employees)"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["starter"]
        
        features_text = " ".join(plan["features"]).lower()
        
        assert "10 ai agents" in features_text or "10 ai agent" in features_text
        assert "employee" not in features_text
        
        print(f"PASS: Starter plan features: {plan['features']}")
    
    def test_starter_plan_has_llm_providers(self):
        """Starter plan mentions LLM providers"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["starter"]
        
        features_text = " ".join(plan["features"]).lower()
        
        assert "llm provider" in features_text
        print("PASS: Starter plan mentions LLM providers")


class TestProPlanFeatures:
    """Test Pro plan has correct updated features"""
    
    def test_pro_plan_max_agents_25(self):
        """Pro plan allows 25 agents"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["pro"]
        
        assert plan["max_agents"] == 25
        print(f"PASS: Pro plan max_agents = {plan['max_agents']}")
    
    def test_pro_plan_includes_commander(self):
        """Pro plan includes Commander Orion"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["pro"]
        
        assert plan.get("includes_commander") == True
        
        features_text = " ".join(plan["features"]).lower()
        assert "commander orion" in features_text
        
        print("PASS: Pro plan includes Commander Orion")
    
    def test_pro_plan_has_autonomous_orchestration(self):
        """Pro plan has autonomous orchestration feature"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["pro"]
        
        features_text = " ".join(plan["features"]).lower()
        assert "autonomous orchestration" in features_text
        
        print("PASS: Pro plan has autonomous orchestration")
    
    def test_pro_plan_has_quality_control(self):
        """Pro plan has quality control feature"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["pro"]
        
        features_text = " ".join(plan["features"]).lower()
        assert "quality control" in features_text
        
        print("PASS: Pro plan has quality control")
    
    def test_pro_plan_has_memory_governance(self):
        """Pro plan has memory governance feature"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["pro"]
        
        features_text = " ".join(plan["features"]).lower()
        assert "memory governance" in features_text
        
        print("PASS: Pro plan has memory governance")
    
    def test_pro_plan_has_activity_monitor(self):
        """Pro plan has real-time activity monitor"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["pro"]
        
        features_text = " ".join(plan["features"]).lower()
        assert "activity monitor" in features_text or "real-time" in features_text
        
        print("PASS: Pro plan has activity monitor")
    
    def test_pro_plan_has_9_llm_providers(self):
        """Pro plan mentions 9 LLM providers"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["pro"]
        
        features_text = " ".join(plan["features"]).lower()
        assert "9 llm" in features_text or "all 9" in features_text
        
        print("PASS: Pro plan mentions 9 LLM providers")


class TestBusinessPlanFeatures:
    """Test Business plan has correct updated features"""
    
    def test_business_plan_max_agents_41(self):
        """Business plan allows 41 agents (not 20)"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["business"]
        
        assert plan["max_agents"] == 41
        print(f"PASS: Business plan max_agents = {plan['max_agents']}")
    
    def test_business_plan_features_41_ai_agents(self):
        """Business plan features say 'All 41 AI agents' (not 20 employees)"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["business"]
        
        features_text = " ".join(plan["features"]).lower()
        
        # Should have 41 AI agents
        assert "41 ai agents" in features_text or "all 41" in features_text
        
        # Should NOT have old text
        assert "20 ai" not in features_text
        assert "employee" not in features_text
        
        print(f"PASS: Business plan features: {plan['features'][:3]}...")
    
    def test_business_plan_includes_commander(self):
        """Business plan includes Commander Orion"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["business"]
        
        assert plan.get("includes_commander") == True
        
        features_text = " ".join(plan["features"]).lower()
        assert "commander orion" in features_text
        
        print("PASS: Business plan includes Commander Orion")
    
    def test_business_plan_has_17_core_systems(self):
        """Business plan mentions 17 core systems"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["business"]
        
        features_text = " ".join(plan["features"]).lower()
        assert "17 core systems" in features_text or "all 17" in features_text
        
        print("PASS: Business plan mentions 17 core systems")
    
    def test_business_plan_has_9_llm_providers(self):
        """Business plan mentions 9 LLM providers"""
        response = requests.get(f"{BASE_URL}/api/plans")
        data = response.json()
        plan = data["plans"]["business"]
        
        features_text = " ".join(plan["features"]).lower()
        assert "9 llm" in features_text or "all 9" in features_text
        
        print("PASS: Business plan mentions 9 LLM providers")


class TestSubscriptionEndpoint:
    """Test authenticated subscription endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "management.maars@marsgc.net", "password": "admin123"}
        )
        if response.status_code != 200:
            pytest.skip("Cannot login - skipping auth tests")
        return response.json().get("token")
    
    def test_subscription_requires_auth(self):
        """Subscription endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/subscription")
        assert response.status_code == 401
        print("PASS: Subscription endpoint requires auth")
    
    def test_subscription_returns_plan_info(self, auth_token):
        """Authenticated user can get subscription info"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/subscription", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "plan_id" in data
        assert "credits" in data
        
        print(f"PASS: Subscription returns plan_id={data['plan_id']}, credits={data['credits']}")
    
    def test_admin_user_has_business_plan(self, auth_token):
        """Admin user should have Business plan"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/subscription", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Admin should have business plan
        assert data["plan_id"] == "business"
        
        print(f"PASS: Admin user has Business plan")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
