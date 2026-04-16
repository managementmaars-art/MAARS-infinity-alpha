# Data Migration Patterns Reference

Common patterns for migrating data formats with version control.

---

## Pattern 1: Auto-Convert on Load

**When:** Most common pattern for application data files

**Advantages:**
- Transparent to users
- Works with read-only files
- No user intervention needed

**Implementation:**
```python
def load_data(path):
    data = read_file(path)
    version = data.get("version", "1.0")

    if version == "1.0":
        return convert_v1_to_v2(data)  # Auto-convert
    elif version == "2.0":
        return load_v2(data)
    else:
        raise ValueError(f"Unsupported version: {version}")
```

**Use cases:**
- JSON config files
- User preferences
- Application state files
- **Used in Stream A cutlist optimizer**

---

## Pattern 2: Auto-Upgrade on First Save

**When:** Want to update files on disk, not just in memory

**Advantages:**
- File format updated permanently
- Clear migration point (when user saves)

**Implementation:**
```python
def update_data(path, data):
    existing = read_file(path)
    version = existing.get("version", "1.0")

    if version == "1.0":
        # Upgrade to v2.0
        new_data = {
            "version": "2.0",
            "items": convert_to_v2_structure(data)
        }
        # Remove old fields
        new_data.pop("old_field", None)
        write_file(path, new_data)

    elif version == "2.0":
        write_file(path, data)
```

**Use cases:**
- User-editable files
- Configuration files
- **Used in Stream A for update_layout()**

---

## Pattern 3: Explicit Migration Script

**When:** Large datasets, breaking changes, or user needs notification

**Advantages:**
- One-time batch operation
- User controls timing
- Can generate migration report

**Implementation:**
```bash
#!/bin/bash
# migrate_v1_to_v2.sh

for file in data/*.json; do
    python -c "
import json
from pathlib import Path

path = Path('$file')
data = json.loads(path.read_text())

if data.get('version', '1.0') == '1.0':
    # Convert to v2.0
    converted = convert_v1_to_v2(data)
    path.write_text(json.dumps(converted, indent=2))
    print(f'Migrated: {path.name}')
"
done
```

**Use cases:**
- Database migrations
- Large file collections
- Breaking changes requiring user notification

---

## Pattern 4: Dual-Format Support

**When:** Gradual migration or supporting multiple client versions

**Advantages:**
- Supports both versions simultaneously
- Gradual rollout
- Rollback possible

**Implementation:**
```python
def save_data(data, path, target_version="2.0"):
    if target_version == "1.0":
        # Downgrade to v1.0 for legacy clients
        write_v1_format(path, downgrade_to_v1(data))
    elif target_version == "2.0":
        write_v2_format(path, data)
```

**Use cases:**
- APIs with multiple client versions
- Transitional periods
- Backward compatibility requirements

---

## Pattern 5: Versioned Loaders with Factory

**When:** Multiple versions, complex migrations

**Implementation:**
```python
class DataLoaderFactory:
    @staticmethod
    def get_loader(version: str):
        loaders = {
            "1.0": DataLoaderV1,
            "2.0": DataLoaderV2,
            "3.0": DataLoaderV3,
        }

        if version not in loaders:
            raise ValueError(f"Unsupported version: {version}")

        return loaders[version]

def load_data(path):
    data = read_file(path)
    version = data.get("version", "1.0")

    loader = DataLoaderFactory.get_loader(version)
    return loader().load(data)
```

**Use cases:**
- Many versions to support
- Complex migration logic
- Clean separation of concerns

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Partial Preservation

**Problem:** Only saving subset of data during migration

```python
# ❌ BAD: Only saves original item
def upgrade_v1_to_v2(path, data):
    original_item = get_original_item(path)
    new_data = {"items": {original_item: data[original_item]}}
    # NEW ITEMS LOST!
```

**Fix:**
```python
# ✅ GOOD: Save ALL items
def upgrade_v1_to_v2(path, data):
    new_data = {
        "items": {item_name: item_data for item_name, item_data in data.items()}
    }
```

### ❌ Anti-Pattern 2: Missing Version Field

**Problem:** No way to detect format

```python
# ❌ BAD: No version field
data = {"config": {...}}
```

**Fix:**
```python
# ✅ GOOD: Always include version
data = {"version": "1.0", "config": {...}}
```

### ❌ Anti-Pattern 3: Breaking Changes Without Backward Compatibility

**Problem:** Old files can't be loaded

```python
# ❌ BAD: Only supports new format
def load_data(path):
    data = read_file(path)
    return data["items"]  # Crashes on v1.0 files
```

**Fix:**
```python
# ✅ GOOD: Support both formats
def load_data(path):
    data = read_file(path)
    version = data.get("version", "1.0")

    if version == "1.0":
        return {data["item"]: data["data"]}  # Convert
    elif version == "2.0":
        return data["items"]
```

### ❌ Anti-Pattern 4: Orphaned Fields

**Problem:** Old fields remain after migration

```python
# ❌ BAD: Old fields remain
data["version"] = "2.0"
data["items"] = {...}
# "item" and "data" still present (orphaned)
```

**Fix:**
```python
# ✅ GOOD: Clean up old fields
data["version"] = "2.0"
data["items"] = {...}
data.pop("item", None)
data.pop("data", None)
```

### ❌ Anti-Pattern 5: Silent Failures

**Problem:** Unsupported versions return empty data

```python
# ❌ BAD: Silent failure
def load_data(path):
    data = read_file(path)
    version = data.get("version", "1.0")

    if version == "1.0":
        return load_v1(data)
    elif version == "2.0":
        return load_v2(data)
    else:
        return {}  # Silent failure!
```

**Fix:**
```python
# ✅ GOOD: Explicit error
def load_data(path):
    data = read_file(path)
    version = data.get("version", "1.0")

    if version == "1.0":
        return load_v1(data)
    elif version == "2.0":
        return load_v2(data)
    else:
        raise ValueError(
            f"Unsupported version: {version} (expected 1.0 or 2.0)"
        )
```

---

## Checklist for Safe Migrations

- [ ] Version field present in all formats
- [ ] Backward compatibility maintained (can load old formats)
- [ ] Auto-upgrade strategy documented
- [ ] Old fields cleaned up after migration
- [ ] Round-trip tests exist (save → load → verify)
- [ ] ALL entities preserved during upgrade (not just first)
- [ ] Migration path tested for all previous versions
- [ ] Clear error messages for unsupported versions
- [ ] Documentation updated with migration guide
- [ ] Performance tested with large files
- [ ] Edge cases handled (empty files, missing fields)

---

## Real-World Examples

### Example 1: Stream A Cutlist Optimizer (Python + JSON)

**Migration:** v1.0 (single material) → v2.0 (multi-material)

**Pattern used:** Auto-convert on load + Auto-upgrade on first update

**Files:**
- `src/cutlist_optimizer/layout_io.py`
- See `examples/json-v1-to-v2.md` for complete implementation

**Key lesson:** Partial preservation bug caught during testing

### Example 2: Database Schema Migration (SQL)

**Migration:** Add new column with default value

**Pattern used:** Explicit migration script

```sql
-- Migration: v1 → v2
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
UPDATE metadata SET version = '2.0';
```

### Example 3: Configuration File Migration (YAML)

**Migration:** Flatten nested structure

**Before (v1.0):**
```yaml
version: "1.0"
database:
  connection:
    host: localhost
    port: 5432
```

**After (v2.0):**
```yaml
version: "2.0"
database:
  host: localhost
  port: 5432
```

**Pattern used:** Auto-convert on load with validation

---

## Tools and Libraries

### Python
- **JSON Schema:** Validate format compliance
- **Pydantic:** Type-safe data models with versioning
- **Alembic:** Database migration tool

### JavaScript/TypeScript
- **Zod:** Schema validation with versioning
- **JSON Schema:** Format validation
- **TypeORM:** Database migrations

### Go
- **golang-migrate:** Database migration tool
- **go-structconv:** Struct conversion utilities

### Rust
- **Serde:** Serialization with versioning support
- **diesel:** Database migration framework

---

## Further Reading

- [Semantic Versioning](https://semver.org/) - Version numbering standard
- [JSON Schema](https://json-schema.org/) - Schema validation
- [Database Migration Best Practices](https://martinfowler.com/articles/evodb.html)
- Stream A implementation: `examples/json-v1-to-v2.md`
