"""
Iteration 55: Testing MAARS Command P1 Features
- Quality Control & Failure Recovery (GET /api/quality/dashboard, POST /api/quality/review, POST /api/quality/retry)
- LLM Router (GET /api/router/stats, POST /api/router/analyze)
- Content Generator (GET /api/content/types, POST /api/content/generate, GET /api/content/history, DELETE /api/content/{id})
- Collaboration Engine enhanced with auto-detection during project execution
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication for API access"""
    
    def test_login_success(self):
        """Login with admin credentials to get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data or "user_id" in data, "No token or user_id in response"
        return data


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for all tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "management.maars@marsgc.net",
        "password": "admin123"
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    pytest.skip("Authentication failed")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


# ============== QUALITY CONTROL DASHBOARD ==============
class TestQualityDashboard:
    """Test Quality Dashboard API - GET /api/quality/dashboard"""
    
    def test_quality_dashboard_returns_metrics(self, auth_headers):
        """GET /api/quality/dashboard returns total_reviews, pass_rate, escalated_tasks, recovered_tasks, recent_reviews"""
        response = requests.get(f"{BASE_URL}/api/quality/dashboard", headers=auth_headers)
        assert response.status_code == 200, f"Quality dashboard failed: {response.text}"
        data = response.json()
        
        # Check all required fields
        assert "total_reviews" in data, "Missing total_reviews"
        assert "pass_count" in data, "Missing pass_count"
        assert "pass_rate" in data, "Missing pass_rate"
        assert "escalated_tasks" in data, "Missing escalated_tasks"
        assert "recovered_tasks" in data, "Missing recovered_tasks"
        assert "recent_reviews" in data, "Missing recent_reviews"
        assert "avg_score" in data, "Missing avg_score"
        
        # Validate types
        assert isinstance(data["total_reviews"], int), "total_reviews should be int"
        assert isinstance(data["pass_rate"], (int, float)), "pass_rate should be numeric"
        assert isinstance(data["recent_reviews"], list), "recent_reviews should be list"
        
        print(f"Dashboard: {data['total_reviews']} reviews, {data['pass_rate']}% pass rate")
    
    def test_quality_dashboard_recent_reviews_structure(self, auth_headers):
        """Recent reviews should have review_id, score, verdict, summary fields"""
        response = requests.get(f"{BASE_URL}/api/quality/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        if data["recent_reviews"]:
            review = data["recent_reviews"][0]
            assert "review_id" in review, "Missing review_id in recent review"
            assert "score" in review or "verdict" in review, "Missing score or verdict"
            print(f"Recent review sample: {review.get('review_id')}, score={review.get('score')}, verdict={review.get('verdict')}")


# ============== QUALITY REVIEW ==============
class TestQualityReview:
    """Test Quality Review API - POST /api/quality/review"""
    
    def test_quality_review_requires_task_id(self, auth_headers):
        """POST /api/quality/review requires task_id"""
        response = requests.post(f"{BASE_URL}/api/quality/review", headers=auth_headers, json={})
        assert response.status_code == 400, "Should fail without task_id"
    
    def test_quality_review_task_not_found(self, auth_headers):
        """POST /api/quality/review returns 404 for non-existent task"""
        response = requests.post(f"{BASE_URL}/api/quality/review", headers=auth_headers, json={
            "task_id": "nonexistent_task_12345"
        })
        assert response.status_code == 404, f"Should return 404 for non-existent task: {response.text}"
    
    def test_quality_review_task_needs_result(self, auth_headers):
        """POST /api/quality/review requires task to have a result"""
        # First, create a task without result
        task_response = requests.post(f"{BASE_URL}/api/tasks", headers=auth_headers, json={
            "title": "TEST_Iteration55_NoResult_Task",
            "description": "A task without result for testing",
            "priority": "medium"
        })
        
        if task_response.status_code == 200:
            task_data = task_response.json()
            task_id = task_data.get("task_id")
            
            # Try to review task without result
            review_response = requests.post(f"{BASE_URL}/api/quality/review", headers=auth_headers, json={
                "task_id": task_id
            })
            # Should fail because task has no result
            assert review_response.status_code == 400, f"Should fail for task without result: {review_response.text}"


# ============== QUALITY RETRY ==============
class TestQualityRetry:
    """Test Quality Retry API - POST /api/quality/retry"""
    
    def test_quality_retry_requires_task_id(self, auth_headers):
        """POST /api/quality/retry requires task_id"""
        response = requests.post(f"{BASE_URL}/api/quality/retry", headers=auth_headers, json={})
        assert response.status_code == 400, "Should fail without task_id"
    
    def test_quality_retry_task_not_found(self, auth_headers):
        """POST /api/quality/retry returns 404 for non-existent task"""
        response = requests.post(f"{BASE_URL}/api/quality/retry", headers=auth_headers, json={
            "task_id": "nonexistent_task_retry_12345"
        })
        assert response.status_code == 404, f"Should return 404: {response.text}"


# ============== LLM ROUTER STATS ==============
class TestRouterStats:
    """Test LLM Router Stats API - GET /api/router/stats"""
    
    def test_router_stats_returns_metrics(self, auth_headers):
        """GET /api/router/stats returns model_usage, complexity_distribution, task_type_distribution"""
        response = requests.get(f"{BASE_URL}/api/router/stats", headers=auth_headers)
        assert response.status_code == 200, f"Router stats failed: {response.text}"
        data = response.json()
        
        # Check all required fields
        assert "model_usage" in data, "Missing model_usage"
        assert "complexity_distribution" in data, "Missing complexity_distribution"
        assert "task_type_distribution" in data, "Missing task_type_distribution"
        assert "total_routed_calls" in data, "Missing total_routed_calls"
        assert "total_credits_used" in data, "Missing total_credits_used"
        
        # Validate types
        assert isinstance(data["model_usage"], list), "model_usage should be list"
        assert isinstance(data["complexity_distribution"], dict), "complexity_distribution should be dict"
        assert isinstance(data["total_routed_calls"], int), "total_routed_calls should be int"
        
        print(f"Router stats: {data['total_routed_calls']} calls, {data['total_credits_used']} credits")
    
    def test_router_stats_model_usage_structure(self, auth_headers):
        """Model usage should have model, provider, count fields"""
        response = requests.get(f"{BASE_URL}/api/router/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        if data["model_usage"]:
            usage = data["model_usage"][0]
            assert "model" in usage, "Missing model in model_usage"
            assert "count" in usage, "Missing count in model_usage"
            print(f"Model usage sample: {usage.get('model')}, count={usage.get('count')}")


# ============== LLM ROUTER ANALYZE ==============
class TestRouterAnalyze:
    """Test LLM Router Analyze API - POST /api/router/analyze"""
    
    def test_router_analyze_requires_content(self, auth_headers):
        """POST /api/router/analyze requires content"""
        response = requests.post(f"{BASE_URL}/api/router/analyze", headers=auth_headers, json={})
        assert response.status_code == 400, "Should fail without content"
    
    def test_router_analyze_simple_task_economy_tier(self, auth_headers):
        """Simple tasks should route to economy tier"""
        response = requests.post(f"{BASE_URL}/api/router/analyze", headers=auth_headers, json={
            "content": "Hello, how are you today?",
            "agent_role": ""
        })
        assert response.status_code == 200, f"Router analyze failed: {response.text}"
        data = response.json()
        
        assert "provider" in data, "Missing provider"
        assert "model" in data, "Missing model"
        assert "classification" in data, "Missing classification"
        
        classification = data.get("classification", {})
        assert classification.get("tier") == "economy", f"Simple task should be economy tier, got: {classification.get('tier')}"
        print(f"Simple task routed to: {data.get('provider')}/{data.get('model')}, tier={classification.get('tier')}")
    
    def test_router_analyze_complex_coding_premium_tier(self, auth_headers):
        """Complex coding tasks should route to premium tier"""
        response = requests.post(f"{BASE_URL}/api/router/analyze", headers=auth_headers, json={
            "content": "Implement a complex algorithm to optimize database query performance. Analyze the current code, refactor for efficiency, add proper error handling, and deploy the solution. Include comprehensive unit tests and documentation.",
            "agent_role": "Senior Developer"
        })
        assert response.status_code == 200, f"Router analyze failed: {response.text}"
        data = response.json()
        
        classification = data.get("classification", {})
        assert classification.get("tier") == "premium", f"Complex coding task should be premium tier, got: {classification.get('tier')}"
        print(f"Complex task routed to: {data.get('provider')}/{data.get('model')}, tier={classification.get('tier')}")
    
    def test_router_analyze_returns_complexity_signals(self, auth_headers):
        """Router analyze should return complexity signals"""
        response = requests.post(f"{BASE_URL}/api/router/analyze", headers=auth_headers, json={
            "content": "Write a marketing email for our new product launch",
            "agent_role": "Marketing"
        })
        assert response.status_code == 200
        data = response.json()
        
        classification = data.get("classification", {})
        assert "signals" in classification, "Missing signals in classification"
        assert "primary_type" in classification, "Missing primary_type in classification"
        print(f"Task signals: {classification.get('signals')}, primary_type={classification.get('primary_type')}")


# ============== CONTENT TYPES ==============
class TestContentTypes:
    """Test Content Types API - GET /api/content/types"""
    
    def test_content_types_returns_8_types(self, auth_headers):
        """GET /api/content/types returns 8 content types"""
        response = requests.get(f"{BASE_URL}/api/content/types", headers=auth_headers)
        assert response.status_code == 200, f"Content types failed: {response.text}"
        data = response.json()
        
        assert "types" in data, "Missing types"
        assert isinstance(data["types"], list), "types should be list"
        assert len(data["types"]) == 8, f"Should have 8 content types, got: {len(data['types'])}"
        
        # Check structure
        for t in data["types"]:
            assert "id" in t, "Type missing id"
            assert "label" in t, "Type missing label"
            assert "description" in t, "Type missing description"
        
        type_ids = [t["id"] for t in data["types"]]
        expected_types = ["marketing_copy", "social_post", "email_campaign", "blog_article", "ad_copy", "press_release", "brand_guidelines", "custom"]
        for expected in expected_types:
            assert expected in type_ids, f"Missing content type: {expected}"
        
        print(f"Content types: {type_ids}")


# ============== CONTENT GENERATION ==============
class TestContentGenerate:
    """Test Content Generate API - POST /api/content/generate"""
    
    def test_content_generate_requires_prompt(self, auth_headers):
        """POST /api/content/generate requires prompt"""
        response = requests.post(f"{BASE_URL}/api/content/generate", headers=auth_headers, json={
            "content_type": "marketing_copy"
        })
        assert response.status_code == 400, "Should fail without prompt"
    
    def test_content_generate_social_post(self, auth_headers):
        """POST /api/content/generate creates social media content"""
        response = requests.post(f"{BASE_URL}/api/content/generate", headers=auth_headers, json={
            "content_type": "social_post",
            "prompt": "TEST_Iteration55: Write a LinkedIn post announcing a new AI feature that helps businesses automate their workflows",
            "length": "short"
        }, timeout=60)  # Allow 60 seconds for LLM
        
        assert response.status_code == 200, f"Content generate failed: {response.text}"
        data = response.json()
        
        assert "content_id" in data, "Missing content_id"
        assert "content" in data, "Missing content"
        assert "content_type" in data, "Missing content_type"
        assert data["content_type"] == "social_post", f"Wrong content type: {data.get('content_type')}"
        assert len(data["content"]) > 50, "Content too short"
        
        print(f"Generated social post: {data['content'][:100]}...")
        return data.get("content_id")
    
    def test_content_generate_with_blueprint(self, auth_headers):
        """POST /api/content/generate can use a style blueprint"""
        # First, check if any blueprints exist
        history_response = requests.get(f"{BASE_URL}/api/reference/history", headers=auth_headers)
        if history_response.status_code == 200:
            history_data = history_response.json()
            items = history_data.get("items", [])
            
            if items:
                blueprint_id = items[0].get("ref_id")
                
                # Generate content with blueprint
                response = requests.post(f"{BASE_URL}/api/content/generate", headers=auth_headers, json={
                    "content_type": "marketing_copy",
                    "blueprint_id": blueprint_id,
                    "prompt": "TEST_Iteration55_Blueprint: Create a product description for our AI-powered assistant",
                    "length": "medium"
                }, timeout=60)
                
                assert response.status_code == 200, f"Content with blueprint failed: {response.text}"
                data = response.json()
                
                assert data.get("blueprint_id") == blueprint_id, "Blueprint ID not preserved"
                print(f"Generated content with blueprint: {data['content'][:100]}...")


# ============== CONTENT HISTORY ==============
class TestContentHistory:
    """Test Content History API - GET /api/content/history"""
    
    def test_content_history_returns_items(self, auth_headers):
        """GET /api/content/history returns generated content"""
        response = requests.get(f"{BASE_URL}/api/content/history", headers=auth_headers)
        assert response.status_code == 200, f"Content history failed: {response.text}"
        data = response.json()
        
        assert "items" in data, "Missing items"
        assert isinstance(data["items"], list), "items should be list"
        print(f"Content history: {len(data['items'])} items")
    
    def test_content_history_item_structure(self, auth_headers):
        """Content history items should have content_id, content, content_type, created_at"""
        response = requests.get(f"{BASE_URL}/api/content/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        if data["items"]:
            item = data["items"][0]
            assert "content_id" in item, "Missing content_id"
            assert "content" in item, "Missing content"
            assert "content_type" in item, "Missing content_type"
            assert "created_at" in item, "Missing created_at"


# ============== CONTENT DELETE ==============
class TestContentDelete:
    """Test Content Delete API - DELETE /api/content/{content_id}"""
    
    def test_content_delete_not_found(self, auth_headers):
        """DELETE /api/content/{id} returns 404 for non-existent content"""
        response = requests.delete(f"{BASE_URL}/api/content/nonexistent_id_12345", headers=auth_headers)
        assert response.status_code == 404, f"Should return 404: {response.text}"
    
    def test_content_delete_success(self, auth_headers):
        """DELETE /api/content/{id} deletes content successfully"""
        # First generate content to delete
        gen_response = requests.post(f"{BASE_URL}/api/content/generate", headers=auth_headers, json={
            "content_type": "custom",
            "prompt": "TEST_Iteration55_Delete: This content will be deleted",
            "length": "short"
        }, timeout=60)
        
        if gen_response.status_code == 200:
            content_id = gen_response.json().get("content_id")
            
            # Delete it
            del_response = requests.delete(f"{BASE_URL}/api/content/{content_id}", headers=auth_headers)
            assert del_response.status_code == 200, f"Delete failed: {del_response.text}"
            
            # Verify deletion
            history_response = requests.get(f"{BASE_URL}/api/content/history", headers=auth_headers)
            if history_response.status_code == 200:
                items = history_response.json().get("items", [])
                content_ids = [item.get("content_id") for item in items]
                assert content_id not in content_ids, "Content should be deleted"
            
            print(f"Successfully deleted content: {content_id}")


# ============== SIDEBAR NAVIGATION ==============
class TestSidebarNavigation:
    """Test Content Generator appears in sidebar navigation"""
    
    def test_dashboard_layout_includes_content_generator(self, auth_headers):
        """DashboardLayout should include Content Generator nav item"""
        # This is a frontend check - we verify the API routes exist
        response = requests.get(f"{BASE_URL}/api/content/types", headers=auth_headers)
        assert response.status_code == 200, "Content types API must be accessible for Content Generator page"
        
        response = requests.get(f"{BASE_URL}/api/content/history", headers=auth_headers)
        assert response.status_code == 200, "Content history API must be accessible for Content Generator page"


# ============== EXISTING FEATURES STILL WORK ==============
class TestExistingFeatures:
    """Verify existing features still work"""
    
    def test_activity_monitor_still_works(self, auth_headers):
        """Activity Monitor API should still work"""
        response = requests.get(f"{BASE_URL}/api/activity/live", headers=auth_headers)
        assert response.status_code == 200, "Activity Monitor broken"
        data = response.json()
        assert "agent_activity" in data
    
    def test_vibe_coding_still_works(self, auth_headers):
        """Vibe Coding API should still work"""
        response = requests.get(f"{BASE_URL}/api/vibe/projects", headers=auth_headers)
        assert response.status_code == 200, "Vibe Coding broken"
        data = response.json()
        assert "items" in data
    
    def test_reference_intelligence_still_works(self, auth_headers):
        """Reference Intelligence API should still work"""
        response = requests.get(f"{BASE_URL}/api/reference/history", headers=auth_headers)
        assert response.status_code == 200, "Reference Intelligence broken"
        data = response.json()
        assert "items" in data
    
    def test_llm_config_still_works(self, auth_headers):
        """LLM Config API should still work"""
        response = requests.get(f"{BASE_URL}/api/llm/config", headers=auth_headers)
        assert response.status_code == 200, "LLM Config broken"
        data = response.json()
        assert "provider" in data
        assert "available_providers" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
