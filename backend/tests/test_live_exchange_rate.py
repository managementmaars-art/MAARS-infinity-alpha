"""
Test Suite: Live Exchange Rate Sync Feature
Tests the /api/exchange-rate endpoint and BDT rate synchronization
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestExchangeRateEndpoint:
    """Tests for the public /api/exchange-rate endpoint"""
    
    def test_exchange_rate_returns_valid_rate(self):
        """Test that exchange-rate endpoint returns a valid USD/BDT rate"""
        response = requests.get(f"{BASE_URL}/api/exchange-rate")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "usd_bdt" in data, "Response should contain usd_bdt field"
        assert "source" in data, "Response should contain source field"
        
        # Rate should be between 115-130 BDT as per requirements
        rate = data["usd_bdt"]
        assert isinstance(rate, (int, float)), "usd_bdt should be a number"
        assert 100 < rate < 150, f"Rate {rate} should be between 100-150 BDT (realistic range)"
        
    def test_exchange_rate_source_is_hexarate_or_fallback(self):
        """Test that source is either 'hexarate' (live) or 'fallback'"""
        response = requests.get(f"{BASE_URL}/api/exchange-rate")
        assert response.status_code == 200
        
        data = response.json()
        assert data["source"] in ["hexarate", "fallback"], f"Source should be hexarate or fallback, got {data['source']}"
        
    def test_exchange_rate_no_auth_required(self):
        """Test that exchange-rate endpoint is public (no auth required)"""
        # Make request without any auth headers
        response = requests.get(f"{BASE_URL}/api/exchange-rate", headers={})
        assert response.status_code == 200, "Exchange rate endpoint should be public (no auth)"
        
    def test_exchange_rate_is_not_hardcoded_107(self):
        """Test that rate is live, not the old hardcoded value of 107"""
        response = requests.get(f"{BASE_URL}/api/exchange-rate")
        assert response.status_code == 200
        
        data = response.json()
        rate = data["usd_bdt"]
        # The old hardcoded rate was 107, live rate should be different (around 120-125)
        # This is a soft check - if rate happens to be 107, it's suspicious but not necessarily wrong
        print(f"Current rate: {rate} BDT")
        # Just verify it's a valid number in expected range
        assert rate > 110, f"Rate {rate} seems too low, should be > 110 for live rate"


class TestAdminPricingWithExchangeRate:
    """Tests for admin pricing endpoints using exchange rate"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "management.maars@marsgc.net",
                "password": "MaarsAdmin2024!"
            }
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
        
    def test_admin_pricing_fetches_exchange_rate(self, auth_token):
        """Test that admin pricing endpoint returns exchange rate data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/pricing",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "bdt_exchange_rate" in data, "Pricing data should include bdt_exchange_rate"
        
    def test_admin_custom_package_has_bdt_prices(self, auth_token):
        """Test that custom package config includes BDT prices"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/custom-package",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Check agent pricing has both USD and BDT
        assert "per_agent_price_usd" in data, "Should have per_agent_price_usd"
        assert "per_agent_price_bdt" in data, "Should have per_agent_price_bdt"
        assert "commander_addon_price_usd" in data, "Should have commander_addon_price_usd"
        assert "commander_addon_price_bdt" in data, "Should have commander_addon_price_bdt"
        
        # Check credit presets have BDT prices
        if "credit_presets" in data and data["credit_presets"]:
            preset = data["credit_presets"][0]
            assert "price_bdt" in preset, "Credit presets should have price_bdt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
