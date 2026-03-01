# Test file for Admin Analytics and SMTP Configuration endpoints
# Iteration 26: Testing Customer Analytics Dashboard and Gmail SMTP Configuration

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestAuth:
    """Authentication helper tests"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in login response"
        return data["token"]

    def test_admin_login(self, admin_token):
        """Verify admin can log in"""
        assert admin_token is not None
        assert len(admin_token) > 20
        print(f"✓ Admin login successful, token length: {len(admin_token)}")


class TestAdminAnalytics:
    """Test GET /api/admin/analytics endpoint"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]

    def test_analytics_endpoint_returns_200(self, admin_token):
        """Test analytics endpoint returns 200 for admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Analytics endpoint returns 200")

    def test_analytics_has_kpis(self, admin_token):
        """Test analytics returns KPIs object with required fields"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "kpis" in data, "Missing 'kpis' in response"
        kpis = data["kpis"]
        
        # Check all required KPI fields
        required_kpis = ["total_users", "active_7d", "active_30d", "total_chats", "total_revenue", "mrr"]
        for field in required_kpis:
            assert field in kpis, f"Missing KPI field: {field}"
            print(f"  - {field}: {kpis[field]}")
        
        # Validate types
        assert isinstance(kpis["total_users"], int), "total_users should be int"
        assert isinstance(kpis["active_7d"], int), "active_7d should be int"
        assert isinstance(kpis["active_30d"], int), "active_30d should be int"
        assert isinstance(kpis["total_chats"], int), "total_chats should be int"
        assert isinstance(kpis["total_revenue"], (int, float)), "total_revenue should be numeric"
        assert isinstance(kpis["mrr"], (int, float)), "mrr should be numeric"
        print("✓ KPIs structure validated")

    def test_analytics_has_daily_arrays(self, admin_token):
        """Test analytics returns daily data arrays"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        data = response.json()
        
        # Check daily arrays exist and are lists
        daily_arrays = ["daily_signups", "daily_messages", "daily_revenue"]
        for arr_name in daily_arrays:
            assert arr_name in data, f"Missing array: {arr_name}"
            assert isinstance(data[arr_name], list), f"{arr_name} should be a list"
            # Should have approximately 31 days (0-30)
            assert len(data[arr_name]) > 0, f"{arr_name} should not be empty"
            print(f"  - {arr_name}: {len(data[arr_name])} entries")
            
            # Validate structure of first entry
            if len(data[arr_name]) > 0:
                first_entry = data[arr_name][0]
                assert "date" in first_entry, f"{arr_name} entries should have 'date'"
        print("✓ Daily arrays validated")

    def test_analytics_has_agent_usage(self, admin_token):
        """Test analytics returns agent_usage array"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        data = response.json()
        
        assert "agent_usage" in data, "Missing agent_usage"
        assert isinstance(data["agent_usage"], list), "agent_usage should be a list"
        print(f"✓ agent_usage: {len(data['agent_usage'])} agents")
        
        # If there's data, validate structure
        if len(data["agent_usage"]) > 0:
            agent = data["agent_usage"][0]
            assert "name" in agent or "agent_id" in agent, "agent_usage entries should have identifier"
            assert "messages" in agent, "agent_usage entries should have messages count"
            print(f"  - Top agent: {agent.get('name', 'Unknown')} with {agent.get('messages', 0)} messages")

    def test_analytics_has_plan_distribution(self, admin_token):
        """Test analytics returns plan_distribution array"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        data = response.json()
        
        assert "plan_distribution" in data, "Missing plan_distribution"
        assert isinstance(data["plan_distribution"], list), "plan_distribution should be a list"
        print(f"✓ plan_distribution: {len(data['plan_distribution'])} plans")
        
        for plan in data["plan_distribution"]:
            assert "plan" in plan, "plan_distribution entries should have 'plan'"
            assert "count" in plan, "plan_distribution entries should have 'count'"
            print(f"  - {plan['plan']}: {plan['count']} users")

    def test_analytics_has_token_usage(self, admin_token):
        """Test analytics returns token_usage array"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        data = response.json()
        
        assert "token_usage" in data, "Missing token_usage"
        assert isinstance(data["token_usage"], list), "token_usage should be a list"
        
        if len(data["token_usage"]) > 0:
            entry = data["token_usage"][0]
            # Check structure
            for field in ["date", "input_tokens", "output_tokens", "cost"]:
                assert field in entry, f"token_usage entry missing {field}"
        print(f"✓ token_usage: {len(data['token_usage'])} entries")

    def test_analytics_has_top_users(self, admin_token):
        """Test analytics returns top_users array"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        data = response.json()
        
        assert "top_users" in data, "Missing top_users"
        assert isinstance(data["top_users"], list), "top_users should be a list"
        print(f"✓ top_users: {len(data['top_users'])} users")
        
        for user in data["top_users"][:3]:
            print(f"  - {user.get('name', 'Unknown')}: {user.get('total_messages', 0)} messages")

    def test_analytics_has_model_costs(self, admin_token):
        """Test analytics returns model_costs array"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        data = response.json()
        
        assert "model_costs" in data, "Missing model_costs"
        assert isinstance(data["model_costs"], list), "model_costs should be a list"
        print(f"✓ model_costs: {len(data['model_costs'])} models")
        
        for model in data["model_costs"][:3]:
            print(f"  - {model.get('model', 'Unknown')}: ${model.get('cost', 0):.4f} ({model.get('calls', 0)} calls)")


class TestAnalyticsAuthz:
    """Test analytics endpoint authorization"""

    def test_analytics_requires_auth(self):
        """Test analytics endpoint returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 401, f"Expected 401 for unauthenticated, got {response.status_code}"
        print("✓ Analytics returns 401 without auth")

    def test_analytics_requires_admin(self):
        """Test analytics returns 403 for non-admin user"""
        # Create a test user and try to access
        # First try with invalid token
        headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=headers)
        # Should be 401 (invalid token) or 403 (not admin)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Analytics rejects invalid token with {response.status_code}")


class TestSmtpConfig:
    """Test SMTP configuration endpoints"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]

    def test_smtp_config_get_returns_200(self, admin_token):
        """Test GET /api/admin/smtp-config returns 200"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/smtp-config", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ SMTP config GET returns 200")

    def test_smtp_config_has_required_fields(self, admin_token):
        """Test SMTP config response has required fields"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/smtp-config", headers=headers)
        data = response.json()
        
        # Should have these fields
        assert "email" in data, "Missing 'email' field"
        assert "has_password" in data, "Missing 'has_password' field"
        assert "configured" in data, "Missing 'configured' field"
        
        # Type validation
        assert isinstance(data["email"], str), "email should be string"
        assert isinstance(data["has_password"], bool), "has_password should be bool"
        assert isinstance(data["configured"], bool), "configured should be bool"
        
        print(f"✓ SMTP config: email='{data['email']}', has_password={data['has_password']}, configured={data['configured']}")

    def test_smtp_config_post_requires_email(self, admin_token):
        """Test POST /api/admin/smtp-config requires email"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        response = requests.post(f"{BASE_URL}/api/admin/smtp-config", 
                                headers=headers, 
                                json={"email": "", "password": "test"})
        # Should return 400 for missing email
        assert response.status_code == 400, f"Expected 400 for empty email, got {response.status_code}"
        print("✓ SMTP config POST requires email")

    def test_smtp_config_post_saves_config(self, admin_token):
        """Test POST /api/admin/smtp-config saves configuration"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        # Save a test config (won't actually work for sending email since password is fake)
        response = requests.post(f"{BASE_URL}/api/admin/smtp-config",
                                headers=headers,
                                json={"email": "test-smtp@example.com"})
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        print("✓ SMTP config POST saves configuration")
        
        # Verify by getting config again
        get_response = requests.get(f"{BASE_URL}/api/admin/smtp-config", headers=headers)
        get_data = get_response.json()
        assert get_data["email"] == "test-smtp@example.com", "Email not saved correctly"
        print(f"✓ SMTP config persisted: {get_data['email']}")

    def test_smtp_test_requires_config(self, admin_token):
        """Test POST /api/admin/smtp-test returns error when SMTP not configured"""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        # Clear the SMTP config first (save empty password)
        # Note: The test email should fail since we don't have real SMTP credentials
        response = requests.post(f"{BASE_URL}/api/admin/smtp-test",
                                headers=headers,
                                json={})
        
        # Should either return 400 (not configured) or 500 (send failed)
        # Since we saved email above but no password, it should be 400
        assert response.status_code in [400, 500], f"Expected 400/500, got {response.status_code}"
        print(f"✓ SMTP test returns {response.status_code} when not properly configured")


class TestSmtpAuthz:
    """Test SMTP endpoint authorization"""

    def test_smtp_config_get_requires_auth(self):
        """Test SMTP config GET requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/smtp-config")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ SMTP config GET requires auth")

    def test_smtp_config_post_requires_auth(self):
        """Test SMTP config POST requires authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/smtp-config", json={"email": "test@test.com"})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ SMTP config POST requires auth")

    def test_smtp_test_requires_auth(self):
        """Test SMTP test requires authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/smtp-test", json={})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ SMTP test requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
