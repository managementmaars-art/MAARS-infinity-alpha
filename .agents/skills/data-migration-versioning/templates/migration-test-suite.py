"""Template for testing data format migrations.

This template provides comprehensive tests for v1.0 → v2.0 migrations including:
- Load v1.0 files (backward compatibility)
- Load v2.0 files (new format)
- Auto-upgrade v1.0 → v2.0
- Data preservation during upgrade
- Field cleanup after upgrade
- Round-trip save → load
- Edge cases (empty, large files, etc.)

Usage:
1. Copy this file to your tests directory
2. Update format definitions (V1_FORMAT, V2_FORMAT)
3. Implement load/save functions for your data
4. Run: pytest test_migration.py -v
"""

import json
import tempfile
from pathlib import Path
from typing import Any

# ============================================================================
# Configuration - Update These for Your Data Format
# ============================================================================

# Version constants
VERSION_V1 = "1.0"
VERSION_V2 = "2.0"

# Example v1.0 format
V1_FORMAT = {
    "version": VERSION_V1,
    "item": "Item A",
    "data": {"value": 100}
}

# Example v2.0 format
V2_FORMAT = {
    "version": VERSION_V2,
    "items": {
        "Item A": {"data": {"value": 100}},
        "Item B": {"data": {"value": 200}}
    }
}

# ============================================================================
# Load/Save Functions - Implement These for Your Data
# ============================================================================

def load_data(path: Path) -> tuple[dict[str, Any], dict]:
    """Load data from file (supports v1.0 and v2.0).

    Returns:
        Tuple of (data_dict, config_dict)
    """
    with open(path) as f:
        file_data = json.load(f)

    version = file_data.get("version", VERSION_V1)

    if version == VERSION_V1:
        # Convert v1.0 to v2.0 structure in memory
        item_name = file_data.get("item", "Unknown")
        data = {item_name: file_data["data"]}
        config = {"version": version}
        return data, config

    elif version == VERSION_V2:
        # Load v2.0 format
        data = file_data["items"]
        config = {"version": version}
        return data, config

    else:
        raise ValueError(f"Unsupported version: {version}")


def save_data(data: dict[str, Any], path: Path, version: str = VERSION_V2) -> None:
    """Save data to file in v2.0 format."""
    file_data = {
        "version": version,
        "items": data
    }

    with open(path, 'w') as f:
        json.dump(file_data, f, indent=2)


def update_data(path: Path, data: dict[str, Any]) -> None:
    """Update existing file, auto-upgrade v1.0 → v2.0 if needed."""
    with open(path) as f:
        file_data = json.load(f)

    version = file_data.get("version", VERSION_V1)

    if version == VERSION_V1:
        # Auto-upgrade to v2.0 - save ALL items
        file_data["version"] = VERSION_V2
        file_data["items"] = data  # All items from data dict

        # Remove old v1.0 fields
        file_data.pop("item", None)
        file_data.pop("data", None)

    elif version == VERSION_V2:
        # Update existing v2.0 structure
        file_data["items"] = data

    with open(path, 'w') as f:
        json.dump(file_data, f, indent=2)


# ============================================================================
# Tests
# ============================================================================

class TestDataMigration:
    """Comprehensive test suite for data format migration."""

    def test_load_v2_format(self):
        """Test loading v2.0 file (new format)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)
            json.dump(V2_FORMAT, f)

        try:
            data, config = load_data(path)

            assert len(data) == 2, "Should load 2 items"
            assert "Item A" in data, "Item A should be present"
            assert "Item B" in data, "Item B should be present"
            assert data["Item A"]["data"]["value"] == 100
            assert data["Item B"]["data"]["value"] == 200
        finally:
            path.unlink()

    def test_load_v1_format_backward_compatibility(self):
        """Test loading v1.0 file (backward compatibility)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)
            json.dump(V1_FORMAT, f)

        try:
            data, config = load_data(path)

            assert len(data) == 1, "Should load 1 item from v1.0 file"
            assert "Item A" in data, "Item A should be present"
            assert data["Item A"]["value"] == 100
        finally:
            path.unlink()

    def test_v1_to_v2_auto_upgrade(self):
        """Test v1.0 → v2.0 auto-upgrade on update.

        CRITICAL TEST: This catches the partial preservation bug!
        """
        # Create v1.0 file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)
            json.dump(V1_FORMAT, f)

        try:
            # Load v1.0 file (should have 1 item)
            data, _ = load_data(path)
            assert len(data) == 1, "V1.0 file should have 1 item"
            assert "Item A" in data

            # Add new item (simulates user adding data)
            data["Item B"] = {"data": {"value": 200}}

            # Update (triggers v1.0 → v2.0 upgrade)
            update_data(path, data)

            # Verify file upgraded to v2.0
            with open(path) as f:
                upgraded = json.load(f)

            assert upgraded["version"] == VERSION_V2, "Should upgrade to v2.0"
            assert "items" in upgraded, "Should have 'items' field"
            assert len(upgraded["items"]) == 2, "Should preserve BOTH items (not just original)"
            assert "Item A" in upgraded["items"], "Original item should be preserved"
            assert "Item B" in upgraded["items"], "New item should be preserved"

            # Verify old v1.0 fields removed
            assert "item" not in upgraded, "Old 'item' field should be removed"
            assert "data" not in upgraded, "Old 'data' field should be removed (top-level)"

        finally:
            path.unlink()

    def test_round_trip_v2(self):
        """Test save → load → verify (round-trip test)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)

        try:
            # Create data
            original_data = {
                "Item A": {"data": {"value": 100}},
                "Item B": {"data": {"value": 200}},
                "Item C": {"data": {"value": 300}}
            }

            # Save
            save_data(original_data, path)

            # Load
            loaded_data, _ = load_data(path)

            # Verify all data preserved
            assert len(loaded_data) == 3, "Should preserve all 3 items"
            assert loaded_data == original_data, "Data should match exactly"

        finally:
            path.unlink()

    def test_multiple_updates_preserve_data(self):
        """Test multiple update cycles preserve all data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)
            json.dump(V2_FORMAT, f)

        try:
            # Update 1: Modify existing item
            data, _ = load_data(path)
            data["Item A"]["data"]["value"] = 150
            update_data(path, data)

            # Update 2: Add new item
            data, _ = load_data(path)
            data["Item C"] = {"data": {"value": 300}}
            update_data(path, data)

            # Verify all items present
            final_data, _ = load_data(path)
            assert len(final_data) == 3, "Should have 3 items after updates"
            assert final_data["Item A"]["data"]["value"] == 150, "Modified value preserved"
            assert "Item C" in final_data, "New item preserved"

        finally:
            path.unlink()

    def test_empty_v2_file(self):
        """Test loading empty v2.0 file (edge case)."""
        empty_v2 = {
            "version": VERSION_V2,
            "items": {}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)
            json.dump(empty_v2, f)

        try:
            data, _ = load_data(path)
            assert len(data) == 0, "Empty file should return empty dict"
        finally:
            path.unlink()

    def test_large_file_performance(self):
        """Test performance with large number of items."""
        import time

        # Create file with 1000 items
        large_data = {
            f"Item {i}": {"data": {"value": i}}
            for i in range(1000)
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)

        try:
            # Save
            start = time.time()
            save_data(large_data, path)
            save_time = time.time() - start

            # Load
            start = time.time()
            loaded_data, _ = load_data(path)
            load_time = time.time() - start

            assert len(loaded_data) == 1000, "Should load all 1000 items"
            assert save_time < 1.0, f"Save should be fast (<1s), took {save_time:.2f}s"
            assert load_time < 1.0, f"Load should be fast (<1s), took {load_time:.2f}s"

        finally:
            path.unlink()

    def test_unsupported_version_error(self):
        """Test that unsupported versions raise clear errors."""
        unsupported = {
            "version": "99.0",
            "items": {}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)
            json.dump(unsupported, f)

        try:
            try:
                load_data(path)
                assert False, "Should raise ValueError for unsupported version"
            except ValueError as e:
                assert "Unsupported version" in str(e), "Error should mention unsupported version"
                assert "99.0" in str(e), "Error should mention specific version"
        finally:
            path.unlink()

    def test_missing_version_defaults_to_v1(self):
        """Test that files without version field default to v1.0."""
        no_version = {
            "item": "Item A",
            "data": {"value": 100}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)
            json.dump(no_version, f)

        try:
            data, _ = load_data(path)

            # Should treat as v1.0 and convert
            assert len(data) == 1, "Should load 1 item (v1.0 format)"
            assert "Item A" in data
        finally:
            path.unlink()

    def test_partial_preservation_bug_prevented(self):
        """CRITICAL: Test that partial preservation bug is prevented.

        This is the exact bug found in Stream A:
        - Load v1.0 file with Item A
        - Add Item B
        - Update file
        - BUG: Only Item A saved, Item B lost
        - FIX: All items saved
        """
        # Create v1.0 file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = Path(f.name)
            json.dump(V1_FORMAT, f)

        try:
            # Load v1.0
            data, _ = load_data(path)

            # Add multiple new items
            data["Item B"] = {"data": {"value": 200}}
            data["Item C"] = {"data": {"value": 300}}
            data["Item D"] = {"data": {"value": 400}}

            # Update
            update_data(path, data)

            # Re-load and verify ALL items present
            reloaded, _ = load_data(path)

            assert len(reloaded) == 4, "ALL items must be preserved (not just original)"
            assert "Item A" in reloaded, "Original item preserved"
            assert "Item B" in reloaded, "New item B preserved"
            assert "Item C" in reloaded, "New item C preserved"
            assert "Item D" in reloaded, "New item D preserved"

            # This test MUST fail if partial preservation bug exists

        finally:
            path.unlink()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
