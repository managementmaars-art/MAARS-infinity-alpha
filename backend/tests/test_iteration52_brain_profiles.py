"""
Iteration 52: Brain Profiles and New Agents Testing
Tests:
- GET /api/agents/public returns 28 agents (21 existing + 7 new)
- GET /api/agents/{agent_id}/brain returns brain profile
- PUT /api/agents/{agent_id}/brain updates brain profile
- DELETE /api/agents/{agent_id}/brain resets to defaults
- GET /api/brain-profiles returns all agent brain profiles
- New agents: cybersecurity, automation, growthhacker, compliance, aioptimizer, operations, revenue
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"

# New agent IDs to verify
NEW_AGENT_IDS = [
    "agent_cybersecurity",
    "agent_automation",
    "agent_growthhacker",
    "agent_compliance",
    "agent_aioptimizer",
    "agent_operations",
    "agent_revenue"
]

@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")

@pytest.fixture(scope="module")
def headers(auth_token):
    """Auth headers for requests"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


# ============== PUBLIC AGENTS ENDPOINT ==============
class TestPublicAgents:
    """Test GET /api/agents/public returns 28 agents"""
    
    def test_public_agents_returns_28_agents(self):
        """Should return 28 agents total (21 existing + 7 new)"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        agents = response.json()
        assert isinstance(agents, list), "Response should be a list"
        assert len(agents) >= 28, f"Expected at least 28 agents, got {len(agents)}"
        print(f"PASSED: /api/agents/public returns {len(agents)} agents")
    
    def test_new_agents_exist_in_public_list(self):
        """Verify all 7 new agents are in the public list"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        
        agents = response.json()
        agent_ids = [a.get("agent_id") for a in agents]
        
        for new_agent_id in NEW_AGENT_IDS:
            assert new_agent_id in agent_ids, f"New agent {new_agent_id} missing from public list"
        print(f"PASSED: All 7 new agents found in public list: {NEW_AGENT_IDS}")
    
    def test_new_agents_have_required_fields(self):
        """Verify new agents have all required fields"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        agents = response.json()
        
        new_agents = [a for a in agents if a.get("agent_id") in NEW_AGENT_IDS]
        
        for agent in new_agents:
            assert agent.get("name"), f"{agent.get('agent_id')} missing name"
            assert agent.get("role"), f"{agent.get('agent_id')} missing role"
            assert agent.get("description"), f"{agent.get('agent_id')} missing description"
            assert agent.get("avatar"), f"{agent.get('agent_id')} missing avatar"
            assert isinstance(agent.get("capabilities"), list), f"{agent.get('agent_id')} missing capabilities list"
            assert agent.get("tools"), f"{agent.get('agent_id')} missing tools"
        print("PASSED: All new agents have required fields (name, role, description, avatar, capabilities, tools)")


# ============== BRAIN PROFILE CRUD ==============
class TestBrainProfileGet:
    """Test GET /api/agents/{agent_id}/brain"""
    
    def test_get_brain_requires_auth(self):
        """Should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/agents/agent_commander/brain")
        assert response.status_code == 401
        print("PASSED: GET /api/agents/agent_commander/brain requires auth")
    
    def test_get_commander_brain_profile(self, headers):
        """Get Commander's brain profile with predefined defaults"""
        response = requests.get(f"{BASE_URL}/api/agents/agent_commander/brain", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        brain = response.json()
        # Commander has predefined brain profile in DEFAULT_BRAIN_PROFILES
        assert brain.get("agent_id") == "agent_commander"
        assert brain.get("autonomy_level") is not None
        assert "memory_scopes" in brain
        assert "kpis" in brain
        assert "escalation_rules" in brain
        assert "communication_style" in brain
        assert "risk_boundaries" in brain
        print(f"PASSED: Commander brain profile has all fields - autonomy_level: {brain.get('autonomy_level')}")
    
    def test_get_new_agent_brain_profile_returns_default(self, headers):
        """New agents without predefined profile get generic default"""
        response = requests.get(f"{BASE_URL}/api/agents/agent_cybersecurity/brain", headers=headers)
        assert response.status_code == 200
        
        brain = response.json()
        # agent_cybersecurity has predefined profile in DEFAULT_BRAIN_PROFILES
        assert brain.get("agent_id") == "agent_cybersecurity"
        assert brain.get("autonomy_level") == 3  # Has predefined profile with level 3
        assert "memory_scopes" in brain
        print(f"PASSED: agent_cybersecurity brain profile returned with autonomy_level: {brain.get('autonomy_level')}")
    
    def test_get_growthhacker_brain_has_predefined_values(self, headers):
        """Growth hacker has predefined brain profile with specific values"""
        response = requests.get(f"{BASE_URL}/api/agents/agent_growthhacker/brain", headers=headers)
        assert response.status_code == 200
        
        brain = response.json()
        assert brain.get("agent_id") == "agent_growthhacker"
        assert brain.get("autonomy_level") == 4  # growthhacker has autonomy 4
        assert "user_acquisition_rate" in brain.get("kpis", []) or "viral_coefficient" in brain.get("kpis", [])
        print(f"PASSED: agent_growthhacker has autonomy_level 4, KPIs: {brain.get('kpis', [])[:3]}")


class TestBrainProfileUpdate:
    """Test PUT /api/agents/{agent_id}/brain"""
    
    def test_update_brain_requires_auth(self):
        """Should return 401 without auth"""
        response = requests.put(f"{BASE_URL}/api/agents/agent_commander/brain", json={"autonomy_level": 4})
        assert response.status_code == 401
        print("PASSED: PUT /api/agents/agent_commander/brain requires auth")
    
    def test_update_brain_autonomy_level(self, headers):
        """Update autonomy_level and verify persistence"""
        # Update
        response = requests.put(
            f"{BASE_URL}/api/agents/agent_marketing/brain",
            headers=headers,
            json={"autonomy_level": 4, "communication_style": "TEST: Data-driven and trendy"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        updated = response.json()
        assert updated.get("autonomy_level") == 4
        assert updated.get("is_custom") == True
        
        # Verify persistence with GET
        get_response = requests.get(f"{BASE_URL}/api/agents/agent_marketing/brain", headers=headers)
        assert get_response.status_code == 200
        persisted = get_response.json()
        assert persisted.get("autonomy_level") == 4
        assert "TEST:" in persisted.get("communication_style", "")
        print("PASSED: Brain profile update persisted - autonomy_level: 4, is_custom: True")
    
    def test_update_brain_kpis_and_escalation_rules(self, headers):
        """Update KPIs and escalation rules"""
        response = requests.put(
            f"{BASE_URL}/api/agents/agent_sales/brain",
            headers=headers,
            json={
                "kpis": ["TEST_deals_closed", "TEST_revenue_generated"],
                "escalation_rules": ["TEST: Escalate if deal value > $50k"]
            }
        )
        assert response.status_code == 200
        
        brain = response.json()
        assert "TEST_deals_closed" in brain.get("kpis", [])
        assert any("TEST:" in r for r in brain.get("escalation_rules", []))
        print("PASSED: KPIs and escalation_rules updated successfully")
    
    def test_update_brain_memory_scopes(self, headers):
        """Update memory scopes"""
        response = requests.put(
            f"{BASE_URL}/api/agents/agent_finance/brain",
            headers=headers,
            json={"memory_scopes": ["working", "long_term", "domain"]}
        )
        assert response.status_code == 200
        
        brain = response.json()
        assert set(brain.get("memory_scopes", [])) == {"working", "long_term", "domain"}
        print("PASSED: memory_scopes updated to ['working', 'long_term', 'domain']")
    
    def test_update_brain_risk_boundaries(self, headers):
        """Update risk boundaries"""
        response = requests.put(
            f"{BASE_URL}/api/agents/agent_legal/brain",
            headers=headers,
            json={
                "risk_boundaries": {
                    "max_budget_authority": 500,
                    "can_approve_external_comms": False
                }
            }
        )
        assert response.status_code == 200
        
        brain = response.json()
        rb = brain.get("risk_boundaries", {})
        assert rb.get("max_budget_authority") == 500
        assert rb.get("can_approve_external_comms") == False
        print("PASSED: risk_boundaries updated successfully")
    
    def test_update_brain_approval_required_toggle(self, headers):
        """Update approval_required toggle"""
        # Enable approval
        response = requests.put(
            f"{BASE_URL}/api/agents/agent_socialmedia/brain",
            headers=headers,
            json={"approval_required": True}
        )
        assert response.status_code == 200
        assert response.json().get("approval_required") == True
        
        # Disable approval
        response2 = requests.put(
            f"{BASE_URL}/api/agents/agent_socialmedia/brain",
            headers=headers,
            json={"approval_required": False}
        )
        assert response2.status_code == 200
        assert response2.json().get("approval_required") == False
        print("PASSED: approval_required toggle works correctly")


class TestBrainProfileDelete:
    """Test DELETE /api/agents/{agent_id}/brain"""
    
    def test_delete_brain_requires_auth(self):
        """Should return 401 without auth"""
        response = requests.delete(f"{BASE_URL}/api/agents/agent_marketing/brain")
        assert response.status_code == 401
        print("PASSED: DELETE /api/agents/agent_marketing/brain requires auth")
    
    def test_delete_brain_resets_to_defaults(self, headers):
        """Delete should reset brain profile to defaults"""
        # First update something
        requests.put(
            f"{BASE_URL}/api/agents/agent_analyst/brain",
            headers=headers,
            json={"autonomy_level": 5, "communication_style": "TEST: Super analytical"}
        )
        
        # Now delete
        response = requests.delete(f"{BASE_URL}/api/agents/agent_analyst/brain", headers=headers)
        assert response.status_code == 200
        assert response.json().get("success") == True
        
        # Verify it's back to default (is_custom should be False)
        get_response = requests.get(f"{BASE_URL}/api/agents/agent_analyst/brain", headers=headers)
        brain = get_response.json()
        assert brain.get("is_custom", True) == False or "is_custom" not in brain
        print("PASSED: DELETE resets brain profile to defaults")


# ============== LIST ALL BRAIN PROFILES ==============
class TestBrainProfilesList:
    """Test GET /api/brain-profiles"""
    
    def test_brain_profiles_requires_auth(self):
        """Should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/brain-profiles")
        assert response.status_code == 401
        print("PASSED: GET /api/brain-profiles requires auth")
    
    def test_brain_profiles_returns_all_agents(self, headers):
        """Should return profiles for all 28 agents"""
        response = requests.get(f"{BASE_URL}/api/brain-profiles", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        profiles = data.get("profiles", [])
        assert len(profiles) >= 28, f"Expected at least 28 profiles, got {len(profiles)}"
        print(f"PASSED: /api/brain-profiles returns {len(profiles)} agent profiles")
    
    def test_brain_profiles_include_new_agents(self, headers):
        """All 7 new agents should be in brain profiles list"""
        response = requests.get(f"{BASE_URL}/api/brain-profiles", headers=headers)
        profiles = response.json().get("profiles", [])
        
        profile_ids = [p.get("agent_id") for p in profiles]
        for new_agent_id in NEW_AGENT_IDS:
            assert new_agent_id in profile_ids, f"{new_agent_id} missing from brain profiles"
        print(f"PASSED: All 7 new agents found in brain profiles")
    
    def test_brain_profiles_have_correct_metadata(self, headers):
        """Each profile should have agent metadata and brain fields"""
        response = requests.get(f"{BASE_URL}/api/brain-profiles", headers=headers)
        profiles = response.json().get("profiles", [])
        
        for p in profiles[:5]:  # Check first 5
            assert p.get("agent_id"), "Missing agent_id"
            assert p.get("agent_name"), "Missing agent_name"
            assert p.get("agent_role"), "Missing agent_role"
            assert "autonomy_level" in p, "Missing autonomy_level"
            assert "is_custom" in p, "Missing is_custom"
        print("PASSED: Brain profiles have correct metadata (agent_id, agent_name, agent_role, autonomy_level, is_custom)")


# ============== CLEANUP TEST DATA ==============
class TestCleanup:
    """Clean up test data created during tests"""
    
    def test_cleanup_test_brain_profiles(self, headers):
        """Reset any brain profiles modified during testing"""
        agents_to_reset = ["agent_marketing", "agent_sales", "agent_finance", "agent_legal", "agent_socialmedia"]
        
        for agent_id in agents_to_reset:
            requests.delete(f"{BASE_URL}/api/agents/{agent_id}/brain", headers=headers)
        
        print(f"PASSED: Cleaned up test brain profiles for {len(agents_to_reset)} agents")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
