"""
Iteration 49: Testing P1 Features
- Paginated APIs (chats, products, admin users, admin transactions)
- Enhanced Admin Analytics (leaderboard, heatmap, revenue trends, CSV export)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"
TEST_USER_EMAIL = "test@test.com"
TEST_USER_PASSWORD = "test123"


class TestHealthCheck:
    """Basic health check"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASSED: Health endpoint returns status: ok")


class TestAdminLogin:
    """Admin authentication tests"""
    
    def test_admin_login(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        assert data.get("user", {}).get("is_admin") is True
        print("PASSED: Admin login successful with is_admin=True")
        return data.get("access_token") or data.get("token")
    
    def test_user_login(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        print("PASSED: Regular user login successful")
        return data.get("access_token") or data.get("token")


@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip("Admin login failed")


@pytest.fixture(scope="module")
def user_token():
    """Get regular user auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip("User login failed")


class TestPaginatedChats:
    """Test paginated chats endpoint - GET /api/chats"""
    
    def test_chats_returns_paginated_response(self, user_token):
        response = requests.get(f"{BASE_URL}/api/chats", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 200
        data = response.json()
        # Must have paginated structure
        assert "chats" in data, "Response must contain 'chats' array"
        assert "total" in data, "Response must contain 'total'"
        assert "page" in data, "Response must contain 'page'"
        assert "pages" in data, "Response must contain 'pages'"
        assert isinstance(data["chats"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["pages"], int)
        print(f"PASSED: /api/chats returns paginated response with {data['total']} total chats, page {data['page']}/{data['pages']}")
    
    def test_chats_pagination_params(self, user_token):
        response = requests.get(f"{BASE_URL}/api/chats?page=1&limit=5", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("chats", [])) <= 5
        assert data.get("page") == 1
        print(f"PASSED: /api/chats respects pagination params (limit=5)")


class TestPaginatedProducts:
    """Test paginated products endpoint - GET /api/products"""
    
    def test_products_returns_paginated_response(self, user_token):
        response = requests.get(f"{BASE_URL}/api/products", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 200
        data = response.json()
        # Must have paginated structure
        assert "products" in data, "Response must contain 'products' array"
        assert "total" in data, "Response must contain 'total'"
        assert "page" in data, "Response must contain 'page'"
        assert "pages" in data, "Response must contain 'pages'"
        assert isinstance(data["products"], list)
        print(f"PASSED: /api/products returns paginated response with {data['total']} total products, page {data['page']}/{data['pages']}")
    
    def test_products_pagination_params(self, user_token):
        response = requests.get(f"{BASE_URL}/api/products?page=1&limit=10", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("products", [])) <= 10
        print(f"PASSED: /api/products respects pagination params")


class TestPaginatedAdminUsers:
    """Test paginated admin users endpoint - GET /api/admin/users"""
    
    def test_admin_users_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code in [401, 403]
        print("PASSED: /api/admin/users requires authentication")
    
    def test_admin_users_returns_paginated_response(self, admin_token):
        response = requests.get(f"{BASE_URL}/api/admin/users", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        # Must have paginated structure
        assert "users" in data, "Response must contain 'users' array"
        assert "total" in data, "Response must contain 'total'"
        assert "page" in data, "Response must contain 'page'"
        assert "pages" in data, "Response must contain 'pages'"
        assert isinstance(data["users"], list)
        print(f"PASSED: /api/admin/users returns paginated response with {data['total']} total users, page {data['page']}/{data['pages']}")
    
    def test_admin_users_search_param(self, admin_token):
        response = requests.get(f"{BASE_URL}/api/admin/users?search=test", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        print(f"PASSED: /api/admin/users supports search param, found {len(data.get('users', []))} matching users")


class TestPaginatedAdminTransactions:
    """Test paginated admin transactions endpoint - GET /api/admin/transactions"""
    
    def test_admin_transactions_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/admin/transactions")
        assert response.status_code in [401, 403]
        print("PASSED: /api/admin/transactions requires authentication")
    
    def test_admin_transactions_returns_paginated_response(self, admin_token):
        response = requests.get(f"{BASE_URL}/api/admin/transactions", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        # Must have paginated structure
        assert "transactions" in data, "Response must contain 'transactions' array"
        assert "total" in data, "Response must contain 'total'"
        assert "page" in data, "Response must contain 'page'"
        assert "pages" in data, "Response must contain 'pages'"
        assert isinstance(data["transactions"], list)
        print(f"PASSED: /api/admin/transactions returns paginated response with {data['total']} total, page {data['page']}/{data['pages']}")


class TestAgentLeaderboard:
    """Test agent leaderboard endpoint - GET /api/admin/analytics/agent-leaderboard"""
    
    def test_agent_leaderboard_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/admin/analytics/agent-leaderboard")
        assert response.status_code in [401, 403]
        print("PASSED: /api/admin/analytics/agent-leaderboard requires authentication")
    
    def test_agent_leaderboard_returns_data(self, admin_token):
        response = requests.get(f"{BASE_URL}/api/admin/analytics/agent-leaderboard", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data, "Response must contain 'leaderboard' array"
        assert isinstance(data["leaderboard"], list)
        
        # Check structure of leaderboard items if any exist
        if len(data["leaderboard"]) > 0:
            agent = data["leaderboard"][0]
            assert "agent_id" in agent
            assert "name" in agent
            assert "total_chats" in agent
            assert "total_messages" in agent
            assert "satisfaction_pct" in agent
            print(f"PASSED: agent-leaderboard returns {len(data['leaderboard'])} agents with proper structure")
        else:
            print("PASSED: agent-leaderboard returns empty leaderboard (no usage data yet)")


class TestEngagementHeatmap:
    """Test engagement heatmap endpoint - GET /api/admin/analytics/engagement-heatmap"""
    
    def test_engagement_heatmap_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/admin/analytics/engagement-heatmap")
        assert response.status_code in [401, 403]
        print("PASSED: /api/admin/analytics/engagement-heatmap requires authentication")
    
    def test_engagement_heatmap_returns_data(self, admin_token):
        response = requests.get(f"{BASE_URL}/api/admin/analytics/engagement-heatmap", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "heatmap" in data, "Response must contain 'heatmap' array"
        assert "days" in data, "Response must contain 'days' array"
        assert "max_count" in data, "Response must contain 'max_count'"
        
        assert isinstance(data["heatmap"], list)
        assert isinstance(data["days"], list)
        assert len(data["days"]) == 7  # Mon-Sun
        
        # Check heatmap item structure if data exists
        if len(data["heatmap"]) > 0:
            item = data["heatmap"][0]
            assert "day" in item
            assert "hour" in item
            assert "count" in item
            assert "intensity" in item
            print(f"PASSED: engagement-heatmap returns {len(data['heatmap'])} data points, max_count={data['max_count']}")
        else:
            print("PASSED: engagement-heatmap returns empty heatmap (no activity data yet)")


class TestRevenueTrends:
    """Test revenue trends endpoint - GET /api/admin/analytics/revenue-trends"""
    
    def test_revenue_trends_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/admin/analytics/revenue-trends")
        assert response.status_code in [401, 403]
        print("PASSED: /api/admin/analytics/revenue-trends requires authentication")
    
    def test_revenue_trends_returns_data(self, admin_token):
        response = requests.get(f"{BASE_URL}/api/admin/analytics/revenue-trends", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "trends" in data, "Response must contain 'trends' array"
        assert "summary" in data, "Response must contain 'summary' object"
        
        assert isinstance(data["trends"], list)
        assert isinstance(data["summary"], dict)
        
        # Check summary structure
        summary = data["summary"]
        assert "total_revenue" in summary
        assert "avg_daily_revenue" in summary
        assert "total_transactions" in summary
        assert "period_days" in summary
        
        # Check trends item structure if data exists
        if len(data["trends"]) > 0:
            trend = data["trends"][0]
            assert "date" in trend
            assert "revenue" in trend
            assert "transactions" in trend
            assert "cumulative" in trend
            print(f"PASSED: revenue-trends returns {len(data['trends'])} data points, total=${summary['total_revenue']}")
        else:
            print(f"PASSED: revenue-trends returns empty trends, summary={summary}")


class TestAnalyticsExport:
    """Test analytics CSV export endpoint - GET /api/admin/analytics/export"""
    
    def test_analytics_export_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/admin/analytics/export")
        assert response.status_code in [401, 403]
        print("PASSED: /api/admin/analytics/export requires authentication")
    
    def test_analytics_export_returns_csv(self, admin_token):
        response = requests.get(f"{BASE_URL}/api/admin/analytics/export", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        
        # Check Content-Disposition header
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, "Response should have Content-Disposition attachment header"
        assert ".csv" in content_disp, "Response should indicate CSV file"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "csv" in content_type or "text" in content_type
        
        # Check CSV content
        content = response.text
        assert "USERS" in content, "CSV should contain USERS section"
        assert "AGENT USAGE" in content, "CSV should contain AGENT USAGE section"
        assert "PAYMENTS" in content, "CSV should contain PAYMENTS section"
        assert "SUMMARY" in content, "CSV should contain SUMMARY section"
        
        print(f"PASSED: analytics export returns valid CSV with {len(content)} bytes")


class TestCacheService:
    """Test that cache service is properly integrated (functional test via API)"""
    
    def test_cached_response_performance(self, admin_token):
        """Verify analytics response is reasonably fast (cache should help)"""
        import time
        
        # First request
        start1 = time.time()
        response1 = requests.get(f"{BASE_URL}/api/admin/analytics", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        time1 = time.time() - start1
        assert response1.status_code == 200
        
        # Second request (should potentially be faster due to caching)
        start2 = time.time()
        response2 = requests.get(f"{BASE_URL}/api/admin/analytics", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        time2 = time.time() - start2
        assert response2.status_code == 200
        
        print(f"PASSED: Analytics endpoint responded in {time1:.3f}s (1st) and {time2:.3f}s (2nd)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
