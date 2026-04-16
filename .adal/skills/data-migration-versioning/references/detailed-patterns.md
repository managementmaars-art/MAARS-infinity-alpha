# Detailed Migration Patterns and Reference

## Version Numbering Strategies (Detailed)

### Strategy 1: Semantic Versioning (Recommended for Libraries)

**Format:** `MAJOR.MINOR.PATCH`

**Rules:**
- MAJOR: Breaking changes (incompatible)
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

**Example:**
```json
{"version": "2.1.0"}
```

**When to use:** Libraries, APIs, public data formats

### Strategy 2: Dotted Versioning (Recommended for Applications)

**Format:** `MAJOR.MINOR`

**Rules:**
- MAJOR: Structural changes (may need migration)
- MINOR: Field additions (backward compatible)

**Example:**
```json
{"version": "2.0"}
```

**When to use:** Application data files, configuration files (used in Stream A work)

### Strategy 3: Integer Versioning

**Format:** `1`, `2`, `3`

**Example:**
```json
{"version": 2}
```

**When to use:** Internal formats, simple migrations

### Strategy 4: Date-Based Versioning

**Format:** `YYYY-MM-DD` or `YYYYMMDD`

**Example:**
```json
{"version": "2025-12-21"}
```

**When to use:** Configuration files, data exports, snapshots

## Backward Compatibility Patterns (Detailed)

### Pattern 1: Auto-Convert on Load (Recommended)

**Advantages:**
- Transparent to caller
- No user intervention needed
- Works with read-only files

**Implementation:**
```python
def load_data(path):
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    if version == "1.0":
        # Convert v1.0 to v2.0 structure in memory
        return convert_v1_to_v2(data)
    elif version == "2.0":
        return load_v2(data)
    else:
        raise ValueError(f"Unsupported version: {version}")
```

**When to use:** Most applications (Stream A used this)

### Pattern 2: Explicit Migration Script

**Advantages:**
- One-time operation
- Clear migration event
- User controls timing

**Implementation:**
```bash
# migrate_v1_to_v2.py
for file in *.json:
    data = load_v1(file)
    converted = convert_to_v2(data)
    save_v2(file, converted)
```

**When to use:** Large datasets, breaking changes, user needs notification

### Pattern 3: Dual-Format Support

**Advantages:**
- Supports both versions simultaneously
- Gradual migration
- Rollback possible

**Implementation:**
```python
def save_data(data, path, version="2.0"):
    if version == "1.0":
        save_v1_format(data, path)
    elif version == "2.0":
        save_v2_format(data, path)
```

**When to use:** Transitional periods, multiple clients with different versions

## Auto-Upgrade Timing (Detailed)

### Option 1: On Load (Recommended)

**When:** During `load_layout()` / `load_config()`

**Advantages:**
- Immediate compatibility
- Works with read-only files
- No user action needed

**Disadvantages:**
- File stays in old format until saved

**Example:** Stream A implementation

### Option 2: On First Save

**When:** During first `save()` or `update()` after load

**Advantages:**
- File updated to new format on disk
- Clear migration point

**Disadvantages:**
- File remains old format if never saved

**Example:**
```python
def update_layout(path, results):
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    if version == "1.0":
        # Auto-upgrade to v2.0 on first save
        data["version"] = "2.0"
        data["materials"] = convert_to_v2_materials(results)
        data.pop("material", None)  # Remove old field
        data.pop("result", None)
```

### Option 3: On First Update (Hybrid - Used in Stream A)

**When:** During `update_layout()` (not on load, not on save)

**Advantages:**
- File loads in any format
- Upgrades only when modified
- Preserves original file if read-only

**Disadvantages:**
- More complex logic

**Example:** See `update_multi_material_layout()` in Stream A

### Option 4: Manual Migration Tool

**When:** User runs `migrate.py` script

**Advantages:**
- User controls timing
- Can handle large batches
- Clear migration event

**Disadvantages:**
- Requires user action

## Field Deprecation Workflow (Detailed)

### Step 1: Add Version Field (if missing)

```python
# Before
data = {"material": "18mm", "result": {...}}

# After
data = {"version": "1.0", "material": "18mm", "result": {...}}
```

### Step 2: Add New Fields (v1.1)

```python
# Backward compatible - keep old fields
data = {
    "version": "1.1",
    "material": "18mm",  # Old field - deprecated
    "materials": {"18mm": {...}},  # New field
    "result": {...}  # Old field - deprecated
}
```

### Step 3: Mark Fields as Deprecated (Documentation)

```python
# In code comments or docs
"""
version 1.1: 'material' and 'result' fields deprecated, use 'materials' instead
"""
```

### Step 4: Remove Old Fields (v2.0)

```python
# Breaking change - new major version
data = {
    "version": "2.0",
    "materials": {"18mm": {...}}
}
# 'material' and 'result' fields removed
```

### Step 5: Update Load Function

```python
def load(path):
    version = data.get("version", "1.0")

    if version in ["1.0", "1.1"]:
        # Support both old versions
        return load_legacy(data)
    elif version == "2.0":
        return load_v2(data)
```

## Language-Specific Patterns (Detailed)

### Python

**Using dataclasses:**
```python
from dataclasses import dataclass, asdict

@dataclass
class LayoutV2:
    version: str = "2.0"
    materials: dict[str, Any]

    def to_dict(self):
        return asdict(self)
```

**Using Pydantic:**
```python
from pydantic import BaseModel

class LayoutV2(BaseModel):
    version: str = "2.0"
    materials: dict[str, Any]

    def to_dict(self):
        return self.model_dump()
```

### JavaScript/TypeScript

```typescript
interface LayoutV1 {
  version: "1.0";
  material: string;
  result: Result;
}

interface LayoutV2 {
  version: "2.0";
  materials: Record<string, { result: Result }>;
}

function loadLayout(path: string): LayoutV2 {
  const data = JSON.parse(fs.readFileSync(path, 'utf8'));

  if (data.version === "1.0") {
    // Auto-convert
    return {
      version: "2.0",
      materials: {
        [data.material]: { result: data.result }
      }
    };
  }

  return data as LayoutV2;
}
```

### Go

```go
type LayoutV1 struct {
    Version  string `json:"version"`
    Material string `json:"material"`
    Result   Result `json:"result"`
}

type LayoutV2 struct {
    Version   string              `json:"version"`
    Materials map[string]Material `json:"materials"`
}

func LoadLayout(path string) (*LayoutV2, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }

    // Try v2 first
    var v2 LayoutV2
    if err := json.Unmarshal(data, &v2); err == nil && v2.Version == "2.0" {
        return &v2, nil
    }

    // Fall back to v1
    var v1 LayoutV1
    if err := json.Unmarshal(data, &v1); err != nil {
        return nil, err
    }

    // Convert v1 → v2
    return &LayoutV2{
        Version: "2.0",
        Materials: map[string]Material{
            v1.Material: {Result: v1.Result},
        },
    }, nil
}
```

### Rust

```rust
#[derive(Serialize, Deserialize)]
#[serde(tag = "version")]
enum Layout {
    #[serde(rename = "1.0")]
    V1 {
        material: String,
        result: Result,
    },
    #[serde(rename = "2.0")]
    V2 {
        materials: HashMap<String, Material>,
    },
}

fn load_layout(path: &Path) -> Result<LayoutV2> {
    let data = fs::read_to_string(path)?;
    let layout: Layout = serde_json::from_str(&data)?;

    match layout {
        Layout::V1 { material, result } => {
            let mut materials = HashMap::new();
            materials.insert(material, Material { result });
            Ok(LayoutV2 { version: "2.0".into(), materials })
        }
        Layout::V2 { materials } => {
            Ok(LayoutV2 { version: "2.0".into(), materials })
        }
    }
}
```

## Advanced Migration Scenarios

### Scenario 1: Multi-Version Jump (v1.0 → v3.0)

```python
def load_with_multi_version_support(path):
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    # Cascade conversions
    if version == "1.0":
        data = convert_v1_to_v2(data)
        version = "2.0"

    if version == "2.0":
        data = convert_v2_to_v3(data)
        version = "3.0"

    if version == "3.0":
        return load_v3(data)

    raise ValueError(f"Unsupported version: {version}")
```

### Scenario 2: Parallel Version Branches

```python
# Support multiple active versions
def load_layout(path):
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    # Legacy branch (v1.x)
    if version.startswith("1."):
        return load_v1_branch(data)

    # Current branch (v2.x)
    elif version.startswith("2."):
        return load_v2_branch(data)

    # Future branch (v3.x)
    elif version.startswith("3."):
        return load_v3_branch(data)
```

### Scenario 3: Conditional Field Migration

```python
def convert_v1_to_v2(data):
    """Convert with conditional field handling."""
    result = {"version": "2.0"}

    # Required field migration
    result["materials"] = {
        data["material"]: {"result": data["result"]}
    }

    # Optional field preservation
    if "created_at" in data:
        result["created_at"] = data["created_at"]

    if "metadata" in data:
        result["metadata"] = data["metadata"]

    return result
```

## Testing Strategies (Detailed)

### Comprehensive Test Matrix

```python
import pytest
from pathlib import Path

class TestMigration:
    """Comprehensive migration test suite."""

    def test_load_v1_format(self, tmp_path):
        """Verify v1.0 files load without errors."""
        v1_file = tmp_path / "test_v1.json"
        v1_file.write_text(json.dumps({
            "version": "1.0",
            "material": "18mm",
            "result": {"sheets_used": 2}
        }))

        results, config = load_layout(v1_file)
        assert len(results) == 1
        assert "18mm" in results

    def test_load_v2_format(self, tmp_path):
        """Verify v2.0 files load correctly."""
        v2_file = tmp_path / "test_v2.json"
        v2_file.write_text(json.dumps({
            "version": "2.0",
            "materials": {
                "18mm": {"result": {"sheets_used": 2}},
                "6mm": {"result": {"sheets_used": 1}}
            }
        }))

        results, config = load_layout(v2_file)
        assert len(results) == 2
        assert "18mm" in results
        assert "6mm" in results

    def test_v1_to_v2_upgrade_preserves_all_data(self, tmp_path):
        """Critical test: Verify ALL materials preserved during upgrade."""
        v1_file = tmp_path / "test_upgrade.json"
        v1_file.write_text(json.dumps({
            "version": "1.0",
            "material": "18mm",
            "result": {"sheets_used": 2}
        }))

        # Load v1 (auto-converts)
        results, config = load_layout(v1_file)

        # Add new material
        results["6mm"] = create_result(sheets_used=1)

        # Update (should upgrade to v2.0)
        update_layout(v1_file, results)

        # Verify upgrade
        upgraded_data = json.loads(v1_file.read_text())
        assert upgraded_data["version"] == "2.0"
        assert "materials" in upgraded_data
        assert len(upgraded_data["materials"]) == 2
        assert "18mm" in upgraded_data["materials"]
        assert "6mm" in upgraded_data["materials"]

    def test_old_fields_removed_after_upgrade(self, tmp_path):
        """Verify deprecated fields are cleaned up."""
        v1_file = tmp_path / "test_cleanup.json"
        v1_file.write_text(json.dumps({
            "version": "1.0",
            "material": "18mm",
            "result": {"sheets_used": 2}
        }))

        results, config = load_layout(v1_file)
        update_layout(v1_file, results)

        upgraded_data = json.loads(v1_file.read_text())
        assert "material" not in upgraded_data
        assert "result" not in upgraded_data

    def test_metadata_preservation(self, tmp_path):
        """Verify metadata survives migration."""
        v1_file = tmp_path / "test_metadata.json"
        v1_file.write_text(json.dumps({
            "version": "1.0",
            "material": "18mm",
            "result": {"sheets_used": 2},
            "created_at": "2025-01-22",
            "author": "test-user"
        }))

        results, config = load_layout(v1_file)
        update_layout(v1_file, results)

        upgraded_data = json.loads(v1_file.read_text())
        assert upgraded_data.get("created_at") == "2025-01-22"
        assert upgraded_data.get("author") == "test-user"

    def test_unsupported_version_error(self, tmp_path):
        """Verify clear error for unsupported versions."""
        future_file = tmp_path / "test_future.json"
        future_file.write_text(json.dumps({
            "version": "99.0",
            "unknown_field": "value"
        }))

        with pytest.raises(ValueError, match="Unsupported.*99.0"):
            load_layout(future_file)

    def test_round_trip_v2(self, tmp_path):
        """Verify save → load preserves data."""
        v2_file = tmp_path / "test_roundtrip.json"

        # Create data
        results = {
            "18mm": create_result(sheets_used=2),
            "6mm": create_result(sheets_used=1)
        }

        # Save
        save_layout(v2_file, results)

        # Load
        loaded_results, config = load_layout(v2_file)

        # Verify
        assert len(loaded_results) == 2
        assert loaded_results["18mm"].sheets_used == 2
        assert loaded_results["6mm"].sheets_used == 1
```

## Troubleshooting Guide (Detailed)

### Issue: "Old files won't load after migration"

**Symptoms:**
- FileNotFoundError or KeyError when loading v1 files
- "Unsupported version" errors

**Diagnosis:**
```python
# Check version detection
data = json.loads(path.read_text())
print(f"Detected version: {data.get('version', 'MISSING')}")
```

**Solution:**
```python
# Always support old versions
if version == "1.0":
    return load_v1(data)
```

### Issue: "Data lost during migration"

**Symptoms:**
- Some materials/entities missing after upgrade
- Only original item preserved

**Diagnosis:**
```python
# Before update
print(f"Materials before: {list(results.keys())}")

# After update
upgraded = json.loads(path.read_text())
print(f"Materials after: {list(upgraded['materials'].keys())}")
```

**Solution:**
```python
# Iterate through ALL items, not just original
for mat_name, result in results.items():
    materials_data[mat_name] = {"result": result.to_dict()}
```

### Issue: "Version detection fails"

**Symptoms:**
- Files always treated as v1.0
- Upgrade happens repeatedly

**Diagnosis:**
```python
# Check file structure
with open(path) as f:
    print(json.dumps(json.load(f), indent=2))
```

**Solution:**
```python
# Use explicit version check with default
version = data.get("version", "1.0")
```

### Issue: "Orphaned fields remain after migration"

**Symptoms:**
- Both old and new fields present in v2.0 files
- File size larger than expected

**Diagnosis:**
```python
# Check for deprecated fields
deprecated = ["material", "result"]
present = [field for field in deprecated if field in data]
if present:
    print(f"Warning: Deprecated fields found: {present}")
```

**Solution:**
```python
# Explicitly remove old fields
data.pop("material", None)
data.pop("result", None)
```
