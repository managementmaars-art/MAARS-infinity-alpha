"""
Test suite for Martian AI Pricing Control Center feature
Tests: 
- Admin extra credit packages CRUD
- GET /api/plans returns credit_packages from DB
- Admin custom package pricing with credit presets
- Profit margin calculation from real avg cost
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"

class TestAdminCreditPackages:
    """Test admin credit packages endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data.get("user", {}).get("is_admin") == True, "User is not admin"
        return data["token"]
    
    def test_get_credit_packages_returns_list(self, admin_token):
        """GET /api/admin/credit-packages returns list of extra credit packs"""
        response = requests.get(
            f"{BASE_URL}/api/admin/credit-packages",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed to get credit packages: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "packages" in data, "Response should have 'packages' key"
        packages = data["packages"]
        assert isinstance(packages, list), "packages should be a list"
        assert len(packages) > 0, "Should have at least one credit package"
        
        # Verify each package has required fields
        for pkg in packages:
            assert "id" in pkg, "Package missing 'id'"
            assert "credits" in pkg, "Package missing 'credits'"
            assert "price_usd" in pkg, "Package missing 'price_usd'"
            assert "price_bdt" in pkg, "Package missing 'price_bdt'"
            assert "name" in pkg, "Package missing 'name'"
            assert isinstance(pkg["credits"], (int, float)), "credits should be numeric"
            assert isinstance(pkg["price_usd"], (int, float)), "price_usd should be numeric"
            assert isinstance(pkg["price_bdt"], (int, float)), "price_bdt should be numeric"
        
        print(f"Found {len(packages)} credit packages")
    
    def test_post_credit_packages_updates_db(self, admin_token):
        """POST /api/admin/credit-packages saves updated packages to DB"""
        # Get current packages first
        get_response = requests.get(
            f"{BASE_URL}/api/admin/credit-packages",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        original_packages = get_response.json().get("packages", [])
        
        # Update with test data (add a test package)
        test_packages = original_packages + [{
            "id": "credits_test_999",
            "credits": 999,
            "price_usd": 59.99,
            "price_bdt": 6400,
            "name": "TEST 999 Credits"
        }]
        
        response = requests.post(
            f"{BASE_URL}/api/admin/credit-packages",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            json={"packages": test_packages}
        )
        assert response.status_code == 200, f"Failed to update credit packages: {response.text}"
        data = response.json()
        assert "packages" in data, "Response should have 'packages'"
        assert any(p.get("credits") == 999 for p in data["packages"]), "Test package not saved"
        
        # Verify persisted in GET
        verify_response = requests.get(
            f"{BASE_URL}/api/admin/credit-packages",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        verify_data = verify_response.json()
        assert any(p.get("id") == "credits_test_999" for p in verify_data["packages"]), "Test package not persisted"
        
        # Cleanup - restore original packages
        requests.post(
            f"{BASE_URL}/api/admin/credit-packages",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            json={"packages": original_packages}
        )
        print("Credit packages save/update verified successfully")
    
    def test_credit_packages_requires_admin(self):
        """GET /api/admin/credit-packages requires admin auth"""
        response = requests.get(f"{BASE_URL}/api/admin/credit-packages")
        assert response.status_code == 401, "Should require authentication"


class TestPlansEndpointCreditPackages:
    """Test GET /api/plans returns credit_packages from DB"""
    
    def test_plans_returns_credit_packages(self):
        """GET /api/plans returns credit_packages from DB (not hardcoded)"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200, f"Failed to get plans: {response.text}"
        data = response.json()
        
        # Verify credit_packages in response
        assert "credit_packages" in data, "Response should have 'credit_packages'"
        credit_packages = data["credit_packages"]
        assert isinstance(credit_packages, dict), "credit_packages should be dict"
        assert len(credit_packages) > 0, "Should have at least one credit package"
        
        # Verify each package structure (it's a dict with id as key)
        for pkg_id, pkg in credit_packages.items():
            assert "credits" in pkg, f"Package {pkg_id} missing 'credits'"
            assert "price_usd" in pkg, f"Package {pkg_id} missing 'price_usd'"
            assert "price_bdt" in pkg, f"Package {pkg_id} missing 'price_bdt'"
        
        print(f"GET /api/plans returns {len(credit_packages)} credit packages")
    
    def test_plans_returns_custom_package_config(self):
        """GET /api/plans returns custom_package config"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200
        data = response.json()
        
        assert "custom_package" in data, "Response should have 'custom_package'"
        custom = data["custom_package"]
        
        # Verify structure
        assert "per_agent_price_usd" in custom, "Missing per_agent_price_usd"
        assert "per_agent_price_bdt" in custom, "Missing per_agent_price_bdt"
        assert "commander_addon_price_usd" in custom, "Missing commander_addon_price_usd"
        assert "commander_addon_price_bdt" in custom, "Missing commander_addon_price_bdt"
        assert "credit_presets" in custom, "Missing credit_presets"
        
        print(f"GET /api/plans returns custom_package config with {len(custom.get('credit_presets', []))} credit presets")


class TestAdminCustomPackage:
    """Test admin custom package endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_get_custom_package_returns_agent_pricing(self, admin_token):
        """GET /api/admin/custom-package returns agent/commander pricing + credit presets"""
        response = requests.get(
            f"{BASE_URL}/api/admin/custom-package",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed to get custom package: {response.text}"
        data = response.json()
        
        # Verify agent pricing fields
        assert "per_agent_price_usd" in data, "Missing per_agent_price_usd"
        assert "per_agent_price_bdt" in data, "Missing per_agent_price_bdt"
        assert "commander_addon_price_usd" in data, "Missing commander_addon_price_usd"
        assert "commander_addon_price_bdt" in data, "Missing commander_addon_price_bdt"
        
        # Verify credit presets
        assert "credit_presets" in data, "Missing credit_presets"
        presets = data["credit_presets"]
        assert isinstance(presets, list), "credit_presets should be a list"
        
        for preset in presets:
            assert "id" in preset, "Preset missing 'id'"
            assert "credits" in preset, "Preset missing 'credits'"
            assert "price_usd" in preset, "Preset missing 'price_usd'"
            assert "price_bdt" in preset, "Preset missing 'price_bdt'"
        
        print(f"Custom package: agent=${data['per_agent_price_usd']}, commander=${data['commander_addon_price_usd']}, {len(presets)} presets")


class TestAvgCostForProfitMargin:
    """Test avg cost endpoint for profit margin calculation"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_avg_cost_returns_real_data(self, admin_token):
        """GET /api/admin/avg-cost returns avg cost per credit from real usage"""
        response = requests.get(
            f"{BASE_URL}/api/admin/avg-cost",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed to get avg cost: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "avg_cost_per_credit" in data, "Missing avg_cost_per_credit"
        assert "source" in data, "Missing source field"
        
        # Cost should be greater than 0 (either real or default)
        assert data["avg_cost_per_credit"] > 0, "avg_cost_per_credit should be > 0"
        
        print(f"Avg cost per credit: ${data['avg_cost_per_credit']:.6f} (source: {data['source']})")
        if data.get("total_calls"):
            print(f"Based on {data['total_calls']} API calls")


class TestPricingIntegration:
    """Integration test: admin updates credit packages, verify they appear in /api/plans"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_admin_credit_packages_sync_to_plans(self, admin_token):
        """Verify admin credit packages updates appear in GET /api/plans"""
        # Get current packages
        admin_response = requests.get(
            f"{BASE_URL}/api/admin/credit-packages",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        admin_packages = admin_response.json().get("packages", [])
        
        # Get plans endpoint
        plans_response = requests.get(f"{BASE_URL}/api/plans")
        plans_data = plans_response.json()
        plans_packages = plans_data.get("credit_packages", {})
        
        # Verify same count
        assert len(admin_packages) == len(plans_packages), "Package count should match between admin and plans endpoints"
        
        # Verify each admin package exists in plans
        for admin_pkg in admin_packages:
            pkg_id = admin_pkg.get("id")
            assert pkg_id in plans_packages, f"Package {pkg_id} from admin not found in plans"
            plans_pkg = plans_packages[pkg_id]
            assert plans_pkg["credits"] == admin_pkg["credits"], f"Credits mismatch for {pkg_id}"
            assert plans_pkg["price_usd"] == admin_pkg["price_usd"], f"USD price mismatch for {pkg_id}"
        
        print("Admin credit packages correctly sync to /api/plans")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
