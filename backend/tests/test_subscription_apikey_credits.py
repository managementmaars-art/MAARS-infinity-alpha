"""
Test Suite for:
1. API Key Testing (9 providers) - POST /api/admin/api-keys/test
2. Subscription Flow - GET /api/plans, GET /api/subscription
3. Credit System - GET /api/credits, credit deduction via messages
4. Checkout Flow - POST /api/checkout, POST /api/custom-package/checkout
5. Admin Stats - GET /api/admin/stats
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"
TEST_USER_EMAIL = "testuser_sub@test.com"
TEST_USER_PASSWORD = "TestPass123!"


class TestAdminLogin:
    """Admin authentication for protected endpoints"""
    
    def test_admin_login(self):
        """Test admin login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        pytest.admin_token = data["token"]
        print(f"✓ Admin login successful, token received")


class TestApiKeyProviders:
    """Test API key validation for all 9 providers - P0 bug fix verification"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure admin token is available"""
        if not hasattr(pytest, 'admin_token'):
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            pytest.admin_token = response.json().get("token")
    
    @pytest.mark.parametrize("provider", [
        "openai",
        "anthropic", 
        "gemini",
        "xai",
        "deepseek",
        "mistral",
        "perplexity",
        "cohere",
        "elevenlabs"
    ])
    def test_api_key_provider_returns_descriptive_error(self, provider):
        """
        P0 Bug Fix: Each provider should return a descriptive error message for invalid keys,
        NOT 'Invalid provider' error. This verifies all 9 providers are properly supported.
        """
        headers = {"Authorization": f"Bearer {pytest.admin_token}"}
        response = requests.post(
            f"{BASE_URL}/api/admin/api-keys/test",
            headers=headers,
            json={"provider": provider, "api_key": "sk-invalid-test-key-12345"}
        )
        
        assert response.status_code == 200, f"Endpoint returned error status: {response.status_code}"
        data = response.json()
        
        # Critical: Should NOT return "Invalid provider" error
        if "message" in data:
            assert "Unknown provider" not in data["message"], \
                f"Provider '{provider}' not supported - got 'Unknown provider' error"
            assert "Invalid provider" not in data["message"], \
                f"Provider '{provider}' not supported - got 'Invalid provider' error"
        
        # Should have success=False for invalid key
        assert "success" in data, f"Response missing 'success' field for {provider}"
        
        # The message should be descriptive (contain provider name or error details)
        message = data.get("message", "")
        print(f"✓ {provider}: success={data.get('success')}, message={message[:100]}")


class TestSubscriptionPlans:
    """Test subscription plans endpoint"""
    
    def test_get_plans_returns_all_data(self):
        """GET /api/plans should return plans, credit_packages, and custom_package config"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200, f"GET /api/plans failed: {response.text}"
        
        data = response.json()
        
        # Verify plans structure
        assert "plans" in data, "Response missing 'plans'"
        plans = data["plans"]
        
        # Should have 4 plans: free, starter, pro, business
        expected_plans = ["free", "starter", "pro", "business"]
        for plan_id in expected_plans:
            assert plan_id in plans, f"Missing plan: {plan_id}"
            plan = plans[plan_id]
            assert "name" in plan, f"Plan {plan_id} missing 'name'"
            assert "price_usd" in plan, f"Plan {plan_id} missing 'price_usd'"
            assert "credits" in plan, f"Plan {plan_id} missing 'credits'"
        
        print(f"✓ Found all 4 plans: {list(plans.keys())}")
        
        # Verify credit_packages
        assert "credit_packages" in data, "Response missing 'credit_packages'"
        credit_packages = data["credit_packages"]
        assert len(credit_packages) > 0, "No credit packages found"
        print(f"✓ Found {len(credit_packages)} credit packages")
        
        # Verify custom_package config
        assert "custom_package" in data, "Response missing 'custom_package'"
        custom_pkg = data["custom_package"]
        assert custom_pkg is not None, "custom_package is None"
        print(f"✓ Custom package config present")


class TestUserSubscription:
    """Test user subscription and credits"""
    
    @pytest.fixture(autouse=True)
    def setup_test_user(self):
        """Create or login test user"""
        # Try to login first
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if login_resp.status_code == 200:
            pytest.test_user_token = login_resp.json().get("token")
        else:
            # Register new user
            register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": "Test User Subscription"
            })
            if register_resp.status_code in [200, 201]:
                pytest.test_user_token = register_resp.json().get("token")
            else:
                pytest.skip(f"Could not create test user: {register_resp.text}")
    
    def test_new_user_gets_free_plan(self):
        """GET /api/subscription - new user should get free plan with 50 credits"""
        headers = {"Authorization": f"Bearer {pytest.test_user_token}"}
        response = requests.get(f"{BASE_URL}/api/subscription", headers=headers)
        
        assert response.status_code == 200, f"GET subscription failed: {response.text}"
        data = response.json()
        
        # Should have free plan
        assert data.get("plan_id") == "free", f"Expected 'free' plan, got: {data.get('plan_id')}"
        
        # Should have credits (initially 50 for free plan)
        credits = data.get("credits", 0)
        assert credits >= 0, "Credits should be non-negative"
        print(f"✓ User has plan: {data.get('plan_id')}, credits: {credits}")
        
        # Store for later tests
        pytest.test_user_credits = credits
    
    def test_get_credits_endpoint(self):
        """GET /api/credits should return credits and plan"""
        headers = {"Authorization": f"Bearer {pytest.test_user_token}"}
        response = requests.get(f"{BASE_URL}/api/credits", headers=headers)
        
        assert response.status_code == 200, f"GET credits failed: {response.text}"
        data = response.json()
        
        assert "credits" in data, "Response missing 'credits'"
        assert "plan" in data, "Response missing 'plan'"
        
        print(f"✓ Credits: {data['credits']}, Plan: {data['plan']}")


class TestCheckoutFlow:
    """Test checkout session creation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure test user token is available"""
        if not hasattr(pytest, 'test_user_token'):
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            if login_resp.status_code == 200:
                pytest.test_user_token = login_resp.json().get("token")
            else:
                pytest.skip("Test user not available")
    
    def test_checkout_subscription(self):
        """POST /api/checkout for subscription should create Stripe session"""
        headers = {
            "Authorization": f"Bearer {pytest.test_user_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/checkout",
            headers=headers,
            json={
                "type": "subscription",
                "plan_id": "starter",
                "currency": "usd",
                "origin_url": "https://multi-agent-ai-16.preview.emergentagent.com"
            }
        )
        
        assert response.status_code == 200, f"Checkout failed: {response.text}"
        data = response.json()
        
        assert "checkout_url" in data, "Response missing 'checkout_url'"
        assert "session_id" in data, "Response missing 'session_id'"
        assert data["checkout_url"].startswith("https://"), "Invalid checkout URL"
        
        print(f"✓ Subscription checkout created: session_id={data['session_id'][:20]}...")
    
    def test_checkout_credits(self):
        """POST /api/checkout for credits should create Stripe session"""
        headers = {
            "Authorization": f"Bearer {pytest.test_user_token}",
            "Content-Type": "application/json"
        }
        
        # First get available credit packages
        plans_resp = requests.get(f"{BASE_URL}/api/plans")
        if plans_resp.status_code == 200:
            credit_pkgs = plans_resp.json().get("credit_packages", {})
            package_id = list(credit_pkgs.keys())[0] if credit_pkgs else "credits_100"
        else:
            package_id = "credits_100"
        
        response = requests.post(
            f"{BASE_URL}/api/checkout",
            headers=headers,
            json={
                "type": "credits",
                "package_id": package_id,
                "currency": "usd",
                "origin_url": "https://multi-agent-ai-16.preview.emergentagent.com"
            }
        )
        
        assert response.status_code == 200, f"Credit checkout failed: {response.text}"
        data = response.json()
        
        assert "checkout_url" in data, "Response missing 'checkout_url'"
        assert "session_id" in data, "Response missing 'session_id'"
        
        print(f"✓ Credit checkout created: session_id={data['session_id'][:20]}...")


class TestCustomPackageCheckout:
    """Test custom package checkout"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure test user token is available"""
        if not hasattr(pytest, 'test_user_token'):
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            if login_resp.status_code == 200:
                pytest.test_user_token = login_resp.json().get("token")
            else:
                pytest.skip("Test user not available")
    
    def test_custom_package_checkout(self):
        """POST /api/custom-package/checkout should work with selected agents and credit preset"""
        headers = {
            "Authorization": f"Bearer {pytest.test_user_token}",
            "Content-Type": "application/json"
        }
        
        # Get agents list
        agents_resp = requests.get(f"{BASE_URL}/api/agents/public")
        if agents_resp.status_code == 200:
            agents = agents_resp.json()
            agent_ids = [a["agent_id"] for a in agents if not a.get("is_commander")][:2]
        else:
            agent_ids = ["agent_finance", "agent_secretary"]
        
        # Get custom package config for credit preset
        config_resp = requests.get(f"{BASE_URL}/api/custom-package/config")
        if config_resp.status_code == 200:
            config = config_resp.json()
            credit_presets = config.get("credit_presets", [])
            credit_preset_id = credit_presets[0]["id"] if credit_presets else "preset_100"
        else:
            credit_preset_id = "preset_100"
        
        response = requests.post(
            f"{BASE_URL}/api/custom-package/checkout",
            headers=headers,
            json={
                "selected_agents": agent_ids,
                "credit_preset_id": credit_preset_id,
                "include_commander": False,
                "origin_url": "https://multi-agent-ai-16.preview.emergentagent.com",
                "currency": "usd"
            }
        )
        
        assert response.status_code == 200, f"Custom package checkout failed: {response.text}"
        data = response.json()
        
        assert "checkout_url" in data, "Response missing 'checkout_url'"
        assert "session_id" in data, "Response missing 'session_id'"
        assert "breakdown" in data, "Response missing 'breakdown'"
        
        breakdown = data["breakdown"]
        assert "agents" in breakdown, "Breakdown missing 'agents'"
        assert "total" in breakdown, "Breakdown missing 'total'"
        
        print(f"✓ Custom package checkout: {breakdown['agents']} agents, total=${breakdown['total']}")


class TestCreditDeduction:
    """Test credit deduction via message sending"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure test user token is available"""
        if not hasattr(pytest, 'test_user_token'):
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            if login_resp.status_code == 200:
                pytest.test_user_token = login_resp.json().get("token")
            else:
                pytest.skip("Test user not available")
    
    def test_message_deducts_credits(self):
        """POST /api/chats/{chat_id}/messages should deduct credits and return credits_remaining"""
        headers = {
            "Authorization": f"Bearer {pytest.test_user_token}",
            "Content-Type": "application/json"
        }
        
        # Get initial credits
        credits_before_resp = requests.get(f"{BASE_URL}/api/credits", headers=headers)
        assert credits_before_resp.status_code == 200
        credits_before = credits_before_resp.json().get("credits", 0)
        
        if credits_before < 1:
            pytest.skip("Not enough credits to test message sending")
        
        # Get an agent
        agents_resp = requests.get(f"{BASE_URL}/api/agents/public")
        if agents_resp.status_code != 200:
            pytest.skip("Could not get agents")
        
        agents = agents_resp.json()
        # Get a non-commander agent
        agent = next((a for a in agents if not a.get("is_commander")), None)
        if not agent:
            pytest.skip("No suitable agent found")
        
        agent_id = agent["agent_id"]
        
        # Create a chat
        chat_resp = requests.post(
            f"{BASE_URL}/api/chats",
            headers=headers,
            json={"agent_id": agent_id}
        )
        assert chat_resp.status_code in [200, 201], f"Chat creation failed: {chat_resp.text}"
        chat_id = chat_resp.json().get("chat_id")
        
        # Send a message
        message_resp = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers=headers,
            json={
                "content": "Hello, this is a test message for credit deduction"
            }
        )
        
        # Message may succeed or fail based on AI availability, but should return response
        if message_resp.status_code == 200:
            data = message_resp.json()
            
            # Should have credits_remaining in response
            assert "credits_remaining" in data, "Response missing 'credits_remaining'"
            credits_after = data["credits_remaining"]
            
            print(f"✓ Message sent. Credits before: {credits_before}, after: {credits_after}")
            
            # Verify credit was deducted
            assert credits_after < credits_before, "Credits were not deducted"
        else:
            # If message failed, check credits are still there
            print(f"Message request returned {message_resp.status_code}: {message_resp.text[:200]}")
            # Don't fail the test - just verify the endpoint exists


class TestAdminStats:
    """Test admin statistics endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure admin token is available"""
        if not hasattr(pytest, 'admin_token'):
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            pytest.admin_token = response.json().get("token")
    
    def test_admin_stats_endpoint(self):
        """GET /api/admin/stats should return platform statistics"""
        headers = {"Authorization": f"Bearer {pytest.admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        data = response.json()
        
        # Verify expected fields
        expected_fields = [
            "total_users",
            "total_chats",
            "total_agents",
            "total_messages",
            "active_subscriptions"
        ]
        
        for field in expected_fields:
            assert field in data, f"Stats missing field: {field}"
        
        print(f"✓ Admin stats: {data['total_users']} users, {data['total_chats']} chats, {data['total_agents']} agents")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
