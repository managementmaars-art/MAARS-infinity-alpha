"""
Iteration 73: Campaign Builder + Workflow Builder LLM Execution Tests
Tests the two P0 features:
1. Campaign Builder - CRUD + execution endpoints
2. Workflow Builder - Real LLM workflow execution
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "management.maars@marsgc.net"
TEST_PASSWORD = "Admin123!"


class TestAuthSetup:
    """Authentication tests to get token for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        return data["token"]
    
    def test_login_returns_token(self, auth_token):
        """Verify login works and returns token"""
        assert auth_token is not None
        assert len(auth_token) > 10
        print(f"Auth token obtained: {auth_token[:20]}...")


class TestCampaignTemplates:
    """Campaign Template endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL, "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_get_campaign_templates_returns_6(self, auth_token):
        """GET /api/kernel/campaign-templates returns 6 templates"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/campaign-templates", headers=headers)
        
        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list), "Templates should be a list"
        assert len(templates) == 6, f"Expected 6 templates, got {len(templates)}"
        print(f"Campaign templates count: {len(templates)}")
    
    def test_campaign_template_structure(self, auth_token):
        """Verify each template has correct structure (template_id, name, steps, category, color)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/campaign-templates", headers=headers)
        
        assert response.status_code == 200
        templates = response.json()
        
        required_fields = ["template_id", "name", "steps", "category", "color"]
        template_ids_found = []
        
        for template in templates:
            for field in required_fields:
                assert field in template, f"Template missing field: {field}"
            
            # Verify steps is a list with proper structure
            assert isinstance(template["steps"], list), "Steps should be a list"
            assert len(template["steps"]) > 0, f"Template {template['template_id']} has no steps"
            
            template_ids_found.append(template["template_id"])
            print(f"Template: {template['template_id']} - {template['name']} ({len(template['steps'])} steps)")
        
        # Verify expected template_ids
        expected_ids = ["content_marketing", "product_launch", "customer_onboarding", 
                       "sales_outreach", "security_audit", "data_analysis"]
        for expected_id in expected_ids:
            assert expected_id in template_ids_found, f"Missing template: {expected_id}"
    
    def test_template_steps_have_required_fields(self, auth_token):
        """Verify template steps have required fields"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/campaign-templates", headers=headers)
        
        assert response.status_code == 200
        templates = response.json()
        
        step_required_fields = ["order", "title", "agent_role", "agent_network", "default_task"]
        
        for template in templates:
            for step in template["steps"]:
                for field in step_required_fields:
                    assert field in step, f"Step in {template['template_id']} missing: {field}"


class TestCampaignCRUD:
    """Campaign CRUD endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL, "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_get_campaigns_list(self, auth_token):
        """GET /api/kernel/campaigns returns user's campaigns list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/campaigns", headers=headers)
        
        assert response.status_code == 200
        campaigns = response.json()
        assert isinstance(campaigns, list), "Campaigns should be a list"
        print(f"Existing campaigns count: {len(campaigns)}")
    
    def test_create_campaign_with_template(self, auth_token):
        """POST /api/kernel/campaigns with template_id creates a campaign"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create campaign using content_marketing template
        payload = {
            "template_id": "content_marketing",
            "context": "TEST: Testing campaign creation for AI-powered analytics platform"
        }
        response = requests.post(f"{BASE_URL}/api/kernel/campaigns", headers=headers, json=payload)
        
        assert response.status_code == 200, f"Create failed: {response.text}"
        campaign = response.json()
        
        # Verify campaign structure
        assert "campaign_id" in campaign, "Missing campaign_id"
        assert "name" in campaign, "Missing name"
        assert "steps" in campaign, "Missing steps"
        assert campaign["template_id"] == "content_marketing"
        assert campaign["name"] == "Content Marketing Campaign"
        
        # Verify steps have agents auto-assigned
        assert isinstance(campaign["steps"], list)
        assert len(campaign["steps"]) == 5, f"Content marketing should have 5 steps, got {len(campaign['steps'])}"
        
        print(f"Created campaign: {campaign['campaign_id']} - {campaign['name']}")
        return campaign["campaign_id"]
    
    def test_get_campaign_detail(self, auth_token):
        """GET /api/kernel/campaigns/{campaign_id} returns campaign details"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # First create a campaign
        create_response = requests.post(f"{BASE_URL}/api/kernel/campaigns", headers=headers, json={
            "template_id": "data_analysis",
            "context": "TEST: Get campaign detail test"
        })
        assert create_response.status_code == 200
        created = create_response.json()
        campaign_id = created["campaign_id"]
        
        # Get the campaign detail
        response = requests.get(f"{BASE_URL}/api/kernel/campaigns/{campaign_id}", headers=headers)
        assert response.status_code == 200, f"Get failed: {response.text}"
        
        campaign = response.json()
        assert campaign["campaign_id"] == campaign_id
        assert campaign["template_id"] == "data_analysis"
        assert "steps" in campaign
        
        # Verify step structure
        for step in campaign["steps"]:
            assert "order" in step
            assert "title" in step
            assert "agent_role" in step
            assert "status" in step
            print(f"  Step {step['order']}: {step['title']} ({step['status']})")
    
    def test_delete_campaign(self, auth_token):
        """DELETE /api/kernel/campaigns/{campaign_id} deletes a campaign"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create a campaign first
        create_response = requests.post(f"{BASE_URL}/api/kernel/campaigns", headers=headers, json={
            "template_id": "security_audit",
            "context": "TEST: Delete campaign test"
        })
        assert create_response.status_code == 200
        campaign_id = create_response.json()["campaign_id"]
        
        # Delete the campaign
        delete_response = requests.delete(f"{BASE_URL}/api/kernel/campaigns/{campaign_id}", headers=headers)
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        # Verify it's gone
        get_response = requests.get(f"{BASE_URL}/api/kernel/campaigns/{campaign_id}", headers=headers)
        assert get_response.status_code == 404, "Campaign should be deleted"
        
        print(f"Successfully deleted campaign: {campaign_id}")


class TestCampaignExecution:
    """Campaign execution endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL, "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_run_campaign_returns_started(self, auth_token):
        """POST /api/kernel/campaigns/{campaign_id}/run triggers execution and returns status:started"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create a campaign
        create_response = requests.post(f"{BASE_URL}/api/kernel/campaigns", headers=headers, json={
            "template_id": "sales_outreach",
            "context": "TEST: Run campaign test for a B2B SaaS company"
        })
        assert create_response.status_code == 200
        campaign_id = create_response.json()["campaign_id"]
        
        # Run the campaign
        run_response = requests.post(f"{BASE_URL}/api/kernel/campaigns/{campaign_id}/run", headers=headers)
        assert run_response.status_code == 200, f"Run failed: {run_response.text}"
        
        result = run_response.json()
        assert result.get("status") == "started", f"Expected status:started, got {result}"
        assert result.get("campaign_id") == campaign_id
        
        print(f"Campaign run started: {campaign_id}")
    
    def test_run_nonexistent_campaign_returns_404(self, auth_token):
        """Running a non-existent campaign returns 404"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(f"{BASE_URL}/api/kernel/campaigns/nonexistent_id/run", headers=headers)
        assert response.status_code == 404


class TestWorkflowBuilder:
    """Workflow Builder endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL, "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_get_workflows_list(self, auth_token):
        """GET /api/kernel/workflows returns user's workflows"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kernel/workflows", headers=headers)
        
        assert response.status_code == 200
        workflows = response.json()
        assert isinstance(workflows, list)
        print(f"Existing workflows count: {len(workflows)}")
    
    def test_create_workflow(self, auth_token):
        """POST /api/kernel/workflows creates a new workflow"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        payload = {
            "name": "TEST_Workflow_Creation",
            "description": "Test workflow for iteration 73",
            "nodes": [
                {"id": "node_1", "name": "Test Agent", "role": "Analyst", "network": "research_intelligence", "task": "Analyze data"}
            ],
            "edges": []
        }
        response = requests.post(f"{BASE_URL}/api/kernel/workflows", headers=headers, json=payload)
        
        assert response.status_code == 200, f"Create failed: {response.text}"
        workflow = response.json()
        assert "workflow_id" in workflow
        assert workflow["name"] == "TEST_Workflow_Creation"
        
        print(f"Created workflow: {workflow['workflow_id']}")
        return workflow["workflow_id"]
    
    def test_get_workflow_detail(self, auth_token):
        """GET /api/kernel/workflows/{workflow_id} returns workflow details"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create first
        create_response = requests.post(f"{BASE_URL}/api/kernel/workflows", headers=headers, json={
            "name": "TEST_Get_Detail",
            "nodes": [{"id": "n1", "name": "Agent1", "role": "Tester", "task": ""}],
            "edges": []
        })
        assert create_response.status_code == 200
        workflow_id = create_response.json()["workflow_id"]
        
        # Get detail
        get_response = requests.get(f"{BASE_URL}/api/kernel/workflows/{workflow_id}", headers=headers)
        assert get_response.status_code == 200
        
        wf = get_response.json()
        assert wf["workflow_id"] == workflow_id
        assert wf["name"] == "TEST_Get_Detail"
    
    def test_update_workflow(self, auth_token):
        """PUT /api/kernel/workflows/{workflow_id} updates a workflow"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create
        create_response = requests.post(f"{BASE_URL}/api/kernel/workflows", headers=headers, json={
            "name": "TEST_Update_Me",
            "nodes": [],
            "edges": []
        })
        workflow_id = create_response.json()["workflow_id"]
        
        # Update
        update_response = requests.put(f"{BASE_URL}/api/kernel/workflows/{workflow_id}", headers=headers, json={
            "name": "TEST_Updated_Name",
            "description": "Updated description"
        })
        assert update_response.status_code == 200
        
        updated = update_response.json()
        assert updated["name"] == "TEST_Updated_Name"
    
    def test_delete_workflow(self, auth_token):
        """DELETE /api/kernel/workflows/{workflow_id} deletes a workflow"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create
        create_response = requests.post(f"{BASE_URL}/api/kernel/workflows", headers=headers, json={
            "name": "TEST_Delete_Me",
            "nodes": [],
            "edges": []
        })
        workflow_id = create_response.json()["workflow_id"]
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/kernel/workflows/{workflow_id}", headers=headers)
        assert delete_response.status_code == 200
        
        # Verify
        get_response = requests.get(f"{BASE_URL}/api/kernel/workflows/{workflow_id}", headers=headers)
        assert get_response.status_code == 404


class TestWorkflowExecution:
    """Workflow execution endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL, "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_run_workflow(self, auth_token):
        """POST /api/kernel/workflows/{workflow_id}/run starts workflow execution"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create workflow with task
        create_response = requests.post(f"{BASE_URL}/api/kernel/workflows", headers=headers, json={
            "name": "TEST_Run_Workflow",
            "nodes": [
                {"id": "n1", "name": "Analyst", "role": "Research Analyst", "network": "research_intelligence", "task": "Summarize testing best practices in 2 sentences."}
            ],
            "edges": []
        })
        assert create_response.status_code == 200
        workflow_id = create_response.json()["workflow_id"]
        
        # Run workflow
        run_response = requests.post(f"{BASE_URL}/api/kernel/workflows/{workflow_id}/run", headers=headers)
        assert run_response.status_code == 200, f"Run failed: {run_response.text}"
        
        run = run_response.json()
        assert "run_id" in run
        assert run["status"] in ["running", "completed", "failed"]
        
        print(f"Workflow run: {run['run_id']} - status: {run['status']}")
    
    def test_get_workflow_runs(self, auth_token):
        """GET /api/kernel/workflows/{workflow_id}/runs returns run history"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create workflow
        create_response = requests.post(f"{BASE_URL}/api/kernel/workflows", headers=headers, json={
            "name": "TEST_Get_Runs",
            "nodes": [{"id": "n1", "name": "Agent", "role": "Test", "task": ""}],
            "edges": []
        })
        workflow_id = create_response.json()["workflow_id"]
        
        # Get runs
        runs_response = requests.get(f"{BASE_URL}/api/kernel/workflows/{workflow_id}/runs", headers=headers)
        assert runs_response.status_code == 200
        
        runs = runs_response.json()
        assert isinstance(runs, list)


class TestAuthRequired:
    """Verify endpoints require authentication"""
    
    def test_campaign_templates_requires_auth(self):
        """Campaign templates endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/campaign-templates")
        assert response.status_code == 401
    
    def test_campaigns_requires_auth(self):
        """Campaigns list endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/campaigns")
        assert response.status_code == 401
    
    def test_workflows_requires_auth(self):
        """Workflows endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/kernel/workflows")
        assert response.status_code == 401


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL, "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_cleanup_test_campaigns(self, auth_token):
        """Delete TEST_ prefixed campaigns"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get all campaigns
        response = requests.get(f"{BASE_URL}/api/kernel/campaigns", headers=headers)
        campaigns = response.json()
        
        deleted = 0
        for c in campaigns:
            # Delete campaigns created in tests (by context containing TEST:)
            if c.get("context", "").startswith("TEST:"):
                requests.delete(f"{BASE_URL}/api/kernel/campaigns/{c['campaign_id']}", headers=headers)
                deleted += 1
        
        print(f"Cleaned up {deleted} test campaigns")
    
    def test_cleanup_test_workflows(self, auth_token):
        """Delete TEST_ prefixed workflows"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get all workflows
        response = requests.get(f"{BASE_URL}/api/kernel/workflows", headers=headers)
        workflows = response.json()
        
        deleted = 0
        for wf in workflows:
            if wf.get("name", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/kernel/workflows/{wf['workflow_id']}", headers=headers)
                deleted += 1
        
        print(f"Cleaned up {deleted} test workflows")
