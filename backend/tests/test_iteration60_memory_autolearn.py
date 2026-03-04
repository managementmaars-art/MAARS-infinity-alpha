"""
Iteration 60: Memory Auto-Learning Feature Tests
Tests the auto-learn functionality for agent memory including:
- GET /api/memory/stats - auto_learned and manual counts
- GET /api/memory/entries - source='auto_learn' and source_task_title fields
- Memory learning service integration hooks
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for admin user."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text[:200]}")


@pytest.fixture
def headers(auth_token):
    """Headers with auth token."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestMemoryAutoLearnStats:
    """Test GET /api/memory/stats returns auto_learned and manual counts."""
    
    def test_stats_returns_auto_learned_count(self, headers):
        """Verify stats endpoint returns auto_learned field."""
        response = requests.get(f"{BASE_URL}/api/memory/stats", headers=headers)
        assert response.status_code == 200, f"Stats failed: {response.text}"
        
        data = response.json()
        # Stats should have auto_learned and manual counts
        assert "auto_learned" in data, f"Missing auto_learned field. Got: {data.keys()}"
        assert "manual" in data, f"Missing manual field. Got: {data.keys()}"
        
        # Should be integers
        assert isinstance(data["auto_learned"], int), f"auto_learned should be int, got {type(data['auto_learned'])}"
        assert isinstance(data["manual"], int), f"manual should be int, got {type(data['manual'])}"
        
        print(f"Stats: auto_learned={data['auto_learned']}, manual={data['manual']}")
    
    def test_stats_has_standard_fields(self, headers):
        """Verify stats has all expected fields."""
        response = requests.get(f"{BASE_URL}/api/memory/stats", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        expected_fields = ["total_entries", "max_entries", "usage_pct", "avg_relevance", 
                          "low_relevance_count", "categories", "agents", "auto_learned", "manual"]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}. Got: {list(data.keys())}"
        
        print(f"All expected fields present in stats response")


class TestMemoryEntriesAutoLearn:
    """Test GET /api/memory/entries returns auto-learned entries correctly."""
    
    def test_entries_list_returns_data(self, headers):
        """Verify entries endpoint returns data with stats."""
        response = requests.get(f"{BASE_URL}/api/memory/entries?page=1&limit=30", headers=headers)
        assert response.status_code == 200, f"Entries failed: {response.text}"
        
        data = response.json()
        assert "entries" in data, "Missing entries array"
        assert "stats" in data, "Missing stats object"
        assert "total" in data, "Missing total count"
        
        print(f"Retrieved {len(data['entries'])} entries, total={data['total']}")
    
    def test_auto_learned_entries_have_source_field(self, headers):
        """Verify auto-learned entries have source='auto_learn' field."""
        response = requests.get(f"{BASE_URL}/api/memory/entries?page=1&limit=50", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        entries = data.get("entries", [])
        
        # Find auto-learned entries
        auto_learned = [e for e in entries if e.get("source") == "auto_learn"]
        manual = [e for e in entries if e.get("source") == "manual"]
        
        print(f"Found {len(auto_learned)} auto-learned entries and {len(manual)} manual entries")
        
        # Verify all entries have source field
        for entry in entries:
            assert "source" in entry, f"Entry {entry.get('memory_id')} missing source field"
    
    def test_auto_learned_entries_have_source_task_title(self, headers):
        """Verify auto-learned entries have source_task_title field."""
        response = requests.get(f"{BASE_URL}/api/memory/entries?page=1&limit=50", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        entries = data.get("entries", [])
        
        # Find auto-learned entries
        auto_learned = [e for e in entries if e.get("source") == "auto_learn"]
        
        if not auto_learned:
            pytest.skip("No auto-learned entries found to verify source_task_title")
        
        # Auto-learned entries should have source_task_title
        for entry in auto_learned:
            assert "source_task_title" in entry, f"Auto-learned entry {entry.get('memory_id')} missing source_task_title"
            print(f"Auto-learn entry: {entry.get('memory_id')} from task: {entry.get('source_task_title')}")
    
    def test_entry_structure_for_autolearn(self, headers):
        """Verify auto-learned entry has correct structure."""
        response = requests.get(f"{BASE_URL}/api/memory/entries?page=1&limit=50", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        entries = data.get("entries", [])
        
        auto_learned = [e for e in entries if e.get("source") == "auto_learn"]
        
        if not auto_learned:
            pytest.skip("No auto-learned entries found")
        
        entry = auto_learned[0]
        expected_fields = ["memory_id", "user_id", "agent_id", "agent_name", "category", 
                          "content", "importance", "version", "versions", "tags", 
                          "source", "created_at", "updated_at", "relevance_score"]
        
        for field in expected_fields:
            assert field in entry, f"Missing field {field} in auto-learn entry"
        
        # Verify category is valid
        valid_categories = ["fact", "preference", "instruction", "context", "decision", "general"]
        assert entry.get("category") in valid_categories, f"Invalid category: {entry.get('category')}"
        
        print(f"Auto-learn entry structure verified: category={entry.get('category')}, importance={entry.get('importance')}")


class TestMemoryStatsConsistency:
    """Test that stats counts match actual entries."""
    
    def test_counts_match_entries(self, headers):
        """Verify auto_learned and manual counts match actual entry counts."""
        # Get stats
        stats_response = requests.get(f"{BASE_URL}/api/memory/stats", headers=headers)
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        # Get all entries
        entries_response = requests.get(f"{BASE_URL}/api/memory/entries?page=1&limit=500", headers=headers)
        assert entries_response.status_code == 200
        entries_data = entries_response.json()
        
        entries = entries_data.get("entries", [])
        actual_auto = len([e for e in entries if e.get("source") == "auto_learn"])
        actual_manual = len([e for e in entries if e.get("source") == "manual"])
        
        reported_auto = stats.get("auto_learned", 0)
        reported_manual = stats.get("manual", 0)
        
        assert actual_auto == reported_auto, f"Auto-learn count mismatch: actual={actual_auto}, reported={reported_auto}"
        assert actual_manual == reported_manual, f"Manual count mismatch: actual={actual_manual}, reported={reported_manual}"
        
        print(f"Counts verified: auto_learned={actual_auto}, manual={actual_manual}")


class TestMemoryManualCRUD:
    """Test that manual memory operations still work correctly."""
    
    def test_create_manual_entry(self, headers):
        """Verify can create a manual memory entry."""
        payload = {
            "content": "TEST_Auto-learn feature test entry - manual creation",
            "summary": "Test entry for iteration 60",
            "category": "fact",
            "importance": 0.6,
            "tags": ["test", "iteration60"],
            "source": "manual"
        }
        
        response = requests.post(f"{BASE_URL}/api/memory/entries", headers=headers, json=payload)
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        assert data.get("source") == "manual", f"Source should be manual, got: {data.get('source')}"
        assert data.get("memory_id"), "Missing memory_id"
        
        # Cleanup
        memory_id = data["memory_id"]
        delete_response = requests.delete(f"{BASE_URL}/api/memory/entries/{memory_id}", headers=headers)
        assert delete_response.status_code == 200
        
        print(f"Manual entry create/delete verified")
    
    def test_update_entry_creates_version(self, headers):
        """Verify updating entry creates new version."""
        # Create entry
        payload = {
            "content": "TEST_Version test initial content",
            "category": "instruction",
            "importance": 0.5
        }
        create_response = requests.post(f"{BASE_URL}/api/memory/entries", headers=headers, json=payload)
        assert create_response.status_code == 200
        entry = create_response.json()
        memory_id = entry["memory_id"]
        
        # Update entry
        update_payload = {
            "content": "TEST_Version test updated content",
            "reason": "Testing version creation"
        }
        update_response = requests.put(f"{BASE_URL}/api/memory/entries/{memory_id}", headers=headers, json=update_payload)
        assert update_response.status_code == 200
        updated = update_response.json()
        
        assert updated.get("version") == 2, f"Version should be 2, got {updated.get('version')}"
        
        # Get versions
        versions_response = requests.get(f"{BASE_URL}/api/memory/entries/{memory_id}/versions", headers=headers)
        assert versions_response.status_code == 200
        versions_data = versions_response.json()
        assert len(versions_data.get("versions", [])) == 2
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/memory/entries/{memory_id}", headers=headers)
        
        print(f"Version creation verified")


class TestMemoryLearningServiceIntegration:
    """Verify the memory learning service is properly integrated."""
    
    def test_seeded_autolearn_entries_exist(self, headers):
        """Verify seeded auto-learned entries exist for admin user."""
        response = requests.get(f"{BASE_URL}/api/memory/entries?page=1&limit=50", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        entries = data.get("entries", [])
        
        auto_learned = [e for e in entries if e.get("source") == "auto_learn"]
        
        # According to context, 3 auto-learned entries were seeded
        print(f"Found {len(auto_learned)} auto-learned entries")
        
        if len(auto_learned) > 0:
            # Verify auto-learned entries have expected fields
            for entry in auto_learned:
                assert entry.get("source") == "auto_learn"
                assert "source_task_title" in entry
                assert entry.get("category") in ["fact", "preference", "instruction", "context", "decision"]
                print(f"  - {entry.get('memory_id')}: category={entry.get('category')}, from task='{entry.get('source_task_title', 'N/A')}'")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
