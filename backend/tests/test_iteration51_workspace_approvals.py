"""
Iteration 51 Tests: Workspace Brain (Profile Memory) and Approval Workflows + Tool Call Observability
Tests Phase 1 (Workspace Brain) and Phase 2 (Approval Workflows) features
"""
import pytest
import requests
import os
import uuid

# Get the API URL from environment, same as frontend uses
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    BASE_URL = "https://launch-ready-debug.preview.emergentagent.com"

# Test credentials
TEST_USER_EMAIL = "test@test.com"
TEST_USER_PASSWORD = "test123"
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for test user"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    pytest.skip(f"Auth failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


# =============================================
# Phase 1: Workspace Brain / Profile Memory
# =============================================

class TestWorkspaceProfile:
    """Tests for GET/PUT/DELETE /api/workspace/profile - business profile CRUD"""

    def test_get_workspace_profile_requires_auth(self):
        """GET /api/workspace/profile without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/workspace/profile")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: GET /api/workspace/profile requires auth (401)")

    def test_get_workspace_profile_returns_default_or_existing(self, auth_headers):
        """GET /api/workspace/profile returns default workspace profile or existing data"""
        response = requests.get(f"{BASE_URL}/api/workspace/profile", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify structure - core workspace fields should be present
        # Note: Stored profiles may not have all fields if created before all fields were added
        core_fields = [
            "company_name", "industry", "brand_voice", "products_services",
            "target_audience", "user_id"
        ]
        
        for field in core_fields:
            assert field in data, f"Missing core field: {field}"
        
        # Verify it's a dict with user_id
        assert "user_id" in data, "Response should include user_id"
        assert isinstance(data, dict), "Response should be a dict"
        
        print(f"PASSED: GET /api/workspace/profile returns profile with user_id")
        print(f"  Current company_name: {data.get('company_name', 'empty')}")

    def test_put_workspace_profile_updates_data(self, auth_headers):
        """PUT /api/workspace/profile saves business profile data"""
        # Create unique test data
        test_suffix = str(uuid.uuid4())[:8]
        test_data = {
            "company_name": f"TEST_Company_{test_suffix}",
            "industry": "Technology",
            "brand_voice": "Professional and innovative",
            "products_services": "AI-powered workforce management",
            "target_audience": "Enterprise CTOs and Operations teams",
            "competitors": "Competitor A, Competitor B",
            "unique_value_prop": "End-to-end AI automation",
            "pricing_info": "Starter $99/mo, Pro $299/mo",
            "regions": "Global",
            "website": "https://test-company.com",
            "policies": "24/7 support SLA",
            "timezone": "America/New_York",
            "working_hours": "9:00-18:00",
            "writing_style": "concise",
            "custom_instructions": "Always be helpful and thorough"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/workspace/profile",
            headers=auth_headers,
            json=test_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        
        # Verify by GET
        verify_response = requests.get(f"{BASE_URL}/api/workspace/profile", headers=auth_headers)
        assert verify_response.status_code == 200
        
        verified_data = verify_response.json()
        assert verified_data["company_name"] == test_data["company_name"], "Company name not persisted"
        assert verified_data["industry"] == test_data["industry"], "Industry not persisted"
        assert verified_data["brand_voice"] == test_data["brand_voice"], "Brand voice not persisted"
        
        print(f"PASSED: PUT /api/workspace/profile saves data and persists correctly")
        print(f"  Updated company_name: {verified_data['company_name']}")

    def test_delete_workspace_profile_clears_data(self, auth_headers):
        """DELETE /api/workspace/profile clears profile (user-controlled memory boundary)"""
        response = requests.delete(f"{BASE_URL}/api/workspace/profile", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        
        # Verify profile is cleared - should return default empty values
        verify_response = requests.get(f"{BASE_URL}/api/workspace/profile", headers=auth_headers)
        verified_data = verify_response.json()
        
        # After delete, company_name should be empty (default)
        assert verified_data.get("company_name") == "" or verified_data.get("company_name") is None, \
            f"Expected empty company_name after delete, got: {verified_data.get('company_name')}"
        
        print("PASSED: DELETE /api/workspace/profile clears profile data")


class TestToolLogs:
    """Tests for GET /api/workspace/tool-logs - tool call observability"""

    def test_get_tool_logs_requires_auth(self):
        """GET /api/workspace/tool-logs without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/workspace/tool-logs")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: GET /api/workspace/tool-logs requires auth (401)")

    def test_get_tool_logs_returns_list(self, auth_headers):
        """GET /api/workspace/tool-logs returns logs array and total count"""
        response = requests.get(f"{BASE_URL}/api/workspace/tool-logs", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "logs" in data, "Response should have 'logs' field"
        assert "total" in data, "Response should have 'total' field"
        assert isinstance(data["logs"], list), "logs should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        
        print(f"PASSED: GET /api/workspace/tool-logs returns {len(data['logs'])} logs, total: {data['total']}")

    def test_get_tool_logs_limit_parameter(self, auth_headers):
        """GET /api/workspace/tool-logs?limit=10 respects limit param"""
        response = requests.get(f"{BASE_URL}/api/workspace/tool-logs?limit=10", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert len(data["logs"]) <= 10, f"Expected at most 10 logs, got {len(data['logs'])}"
        
        print(f"PASSED: GET /api/workspace/tool-logs respects limit parameter")


# =============================================
# Phase 2: Approval Workflows
# =============================================

class TestApprovalsCRUD:
    """Tests for full approval workflow: create → list → get → approve → publish → delete"""

    def test_create_approval_requires_auth(self):
        """POST /api/approvals without auth returns 401"""
        response = requests.post(f"{BASE_URL}/api/approvals", json={"title": "Test"})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: POST /api/approvals requires auth (401)")

    def test_list_approvals_requires_auth(self):
        """GET /api/approvals without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/approvals")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: GET /api/approvals requires auth (401)")

    def test_create_approval_creates_draft(self, auth_headers):
        """POST /api/approvals creates approval in draft status"""
        test_suffix = str(uuid.uuid4())[:8]
        approval_data = {
            "type": "social_post",
            "title": f"TEST_SocialPost_{test_suffix}",
            "content": "Check out our new product! #innovation #tech",
            "agent_id": "agent_test",
            "agent_name": "Social Media Manager",
            "metadata": {"platform": "twitter", "scheduled_time": "2025-01-15T10:00:00Z"}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/approvals",
            headers=auth_headers,
            json=approval_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "approval_id" in data, "Response should have approval_id"
        assert data["status"] == "draft", f"Expected status=draft, got {data['status']}"
        assert data["title"] == approval_data["title"], "Title mismatch"
        assert data["type"] == "social_post", "Type mismatch"
        assert data["content"] == approval_data["content"], "Content mismatch"
        assert "created_at" in data, "Should have created_at timestamp"
        
        # Store for later tests
        self.__class__.test_approval_id = data["approval_id"]
        
        print(f"PASSED: POST /api/approvals creates draft approval: {data['approval_id']}")
        return data["approval_id"]

    def test_list_approvals_returns_items(self, auth_headers):
        """GET /api/approvals returns list with pending_count"""
        response = requests.get(f"{BASE_URL}/api/approvals", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "approvals" in data, "Response should have 'approvals' field"
        assert "pending_count" in data, "Response should have 'pending_count' field"
        assert isinstance(data["approvals"], list), "approvals should be a list"
        assert isinstance(data["pending_count"], int), "pending_count should be int"
        
        print(f"PASSED: GET /api/approvals returns {len(data['approvals'])} items, pending: {data['pending_count']}")

    def test_list_approvals_filter_by_status(self, auth_headers):
        """GET /api/approvals?status=draft filters by status"""
        response = requests.get(f"{BASE_URL}/api/approvals?status=draft", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        for item in data["approvals"]:
            assert item["status"] == "draft", f"Expected all draft, got {item['status']}"
        
        print(f"PASSED: GET /api/approvals?status=draft filters correctly ({len(data['approvals'])} drafts)")

    def test_get_single_approval(self, auth_headers):
        """GET /api/approvals/{id} returns single approval"""
        if not hasattr(self.__class__, 'test_approval_id'):
            pytest.skip("No test approval created")
        
        approval_id = self.__class__.test_approval_id
        response = requests.get(f"{BASE_URL}/api/approvals/{approval_id}", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["approval_id"] == approval_id, "Approval ID mismatch"
        assert "title" in data, "Should have title"
        assert "content" in data, "Should have content"
        assert "status" in data, "Should have status"
        
        print(f"PASSED: GET /api/approvals/{approval_id} returns single approval")

    def test_get_nonexistent_approval_returns_404(self, auth_headers):
        """GET /api/approvals/nonexistent returns 404"""
        response = requests.get(f"{BASE_URL}/api/approvals/appr_nonexistent", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASSED: GET /api/approvals/nonexistent returns 404")


class TestApprovalWorkflow:
    """Tests for approval lifecycle: draft → approved → published"""

    @pytest.fixture(autouse=True)
    def setup_approval(self, auth_headers):
        """Create a fresh approval for workflow testing"""
        test_suffix = str(uuid.uuid4())[:8]
        response = requests.post(
            f"{BASE_URL}/api/approvals",
            headers=auth_headers,
            json={
                "type": "email_campaign",
                "title": f"TEST_WorkflowApproval_{test_suffix}",
                "content": "Dear valued customer, we have exciting news...",
                "agent_name": "Email Marketing Agent"
            }
        )
        if response.status_code == 200:
            self.approval_id = response.json()["approval_id"]
        else:
            pytest.skip(f"Could not create test approval: {response.status_code}")

    def test_approve_changes_status_to_approved(self, auth_headers):
        """POST /api/approvals/{id}/approve changes status to approved"""
        response = requests.post(
            f"{BASE_URL}/api/approvals/{self.approval_id}/approve",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert data.get("status") == "approved", f"Expected status=approved, got {data.get('status')}"
        
        # Verify by GET
        verify = requests.get(f"{BASE_URL}/api/approvals/{self.approval_id}", headers=auth_headers)
        verified_data = verify.json()
        assert verified_data["status"] == "approved", "Status not persisted as approved"
        assert "approved_at" in verified_data, "Should have approved_at timestamp"
        
        print(f"PASSED: POST /api/approvals/{self.approval_id}/approve changes status to approved")

    def test_publish_approved_content(self, auth_headers):
        """POST /api/approvals/{id}/publish changes status to published (only if approved)"""
        # First approve it
        requests.post(f"{BASE_URL}/api/approvals/{self.approval_id}/approve", headers=auth_headers)
        
        # Then publish
        response = requests.post(
            f"{BASE_URL}/api/approvals/{self.approval_id}/publish",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert data.get("status") == "published", f"Expected status=published, got {data.get('status')}"
        
        # Verify by GET
        verify = requests.get(f"{BASE_URL}/api/approvals/{self.approval_id}", headers=auth_headers)
        verified_data = verify.json()
        assert verified_data["status"] == "published", "Status not persisted as published"
        assert "published_at" in verified_data, "Should have published_at timestamp"
        
        print(f"PASSED: POST /api/approvals/{self.approval_id}/publish changes status to published")

    def test_cannot_publish_draft_directly(self, auth_headers):
        """POST /api/approvals/{id}/publish on draft returns 400"""
        # Try to publish without approving first (status is still draft)
        response = requests.post(
            f"{BASE_URL}/api/approvals/{self.approval_id}/publish",
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        print("PASSED: Cannot publish draft directly - must approve first (400)")


class TestApprovalReject:
    """Tests for rejection/revision workflow"""

    @pytest.fixture(autouse=True)
    def setup_approval(self, auth_headers):
        """Create a fresh approval for rejection testing"""
        test_suffix = str(uuid.uuid4())[:8]
        response = requests.post(
            f"{BASE_URL}/api/approvals",
            headers=auth_headers,
            json={
                "type": "blog_post",
                "title": f"TEST_RejectApproval_{test_suffix}",
                "content": "This is a draft blog post that needs revision...",
                "agent_name": "Content Writer"
            }
        )
        if response.status_code == 200:
            self.approval_id = response.json()["approval_id"]
        else:
            pytest.skip(f"Could not create test approval: {response.status_code}")

    def test_reject_changes_status_to_revision_requested(self, auth_headers):
        """POST /api/approvals/{id}/reject changes status to revision_requested"""
        response = requests.post(
            f"{BASE_URL}/api/approvals/{self.approval_id}/reject",
            headers=auth_headers,
            json={"reason": "Needs more engaging opening paragraph"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert data.get("status") == "revision_requested", f"Expected status=revision_requested, got {data.get('status')}"
        
        # Verify by GET - check rejection reason is stored
        verify = requests.get(f"{BASE_URL}/api/approvals/{self.approval_id}", headers=auth_headers)
        verified_data = verify.json()
        assert verified_data["status"] == "revision_requested", "Status not persisted"
        assert verified_data.get("rejection_reason") == "Needs more engaging opening paragraph", \
            "Rejection reason not saved"
        
        print(f"PASSED: POST /api/approvals/{self.approval_id}/reject changes status to revision_requested")


class TestApprovalDelete:
    """Tests for approval deletion"""

    def test_delete_approval(self, auth_headers):
        """DELETE /api/approvals/{id} removes the approval"""
        # Create an approval to delete
        test_suffix = str(uuid.uuid4())[:8]
        create_response = requests.post(
            f"{BASE_URL}/api/approvals",
            headers=auth_headers,
            json={"type": "general", "title": f"TEST_DeleteMe_{test_suffix}", "content": "To be deleted"}
        )
        if create_response.status_code != 200:
            pytest.skip("Could not create test approval")
        
        approval_id = create_response.json()["approval_id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/approvals/{approval_id}", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        
        # Verify it's gone
        verify = requests.get(f"{BASE_URL}/api/approvals/{approval_id}", headers=auth_headers)
        assert verify.status_code == 404, f"Expected 404 after delete, got {verify.status_code}"
        
        print(f"PASSED: DELETE /api/approvals/{approval_id} removes approval and returns 404 on GET")

    def test_delete_nonexistent_returns_404(self, auth_headers):
        """DELETE /api/approvals/nonexistent returns 404"""
        response = requests.delete(f"{BASE_URL}/api/approvals/appr_nonexistent", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASSED: DELETE /api/approvals/nonexistent returns 404")


# =============================================
# Cleanup: Restore workspace profile for test user
# =============================================

class TestCleanupAndRestore:
    """Restore test data after tests"""

    def test_restore_workspace_profile(self, auth_headers):
        """Restore workspace profile to original test data"""
        restore_data = {
            "company_name": "TechStartup Inc",
            "industry": "Technology",
            "brand_voice": "Professional and innovative",
            "products_services": "AI solutions",
            "target_audience": "Enterprise",
            "writing_style": "professional"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/workspace/profile",
            headers=auth_headers,
            json=restore_data
        )
        assert response.status_code == 200, f"Failed to restore: {response.status_code}"
        print("PASSED: Restored workspace profile for test user")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
