# SRP Validation Usage Examples

## Example 1: Validate Entire Codebase

```bash
# Default: thorough validation of src/
Skill(command: "single-responsibility-principle")
```

**Expected Output**: Full report with all violation types, confidence scores, fix guidance.

---

## Example 2: Fast Pre-Commit Check

```bash
# Quick validation before commit
Skill(command: "single-responsibility-principle --level=fast")
```

**Expected Output**: Naming patterns + basic size metrics only (5-10s).

---

## Example 3: Validate Specific Service

```bash
# Deep analysis of specific file
Skill(command: "single-responsibility-principle --path=src/application/services/indexing_service.py --level=full")
```

**Expected Output**: Comprehensive analysis including actor identification, cohesion metrics.

---

## Example 4: JSON Output for CI/CD

```bash
# Machine-readable output
Skill(command: "single-responsibility-principle --level=thorough --format=json")
```

**Expected Output**:

```json
{
  "summary": {
    "files_analyzed": 45,
    "classes_analyzed": 78,
    "violations": 12,
    "passed": 66,
    "pass_rate": 0.846
  },
  "violations": [
    {
      "level": "critical",
      "type": "god_class",
      "file": "src/services/user_service.py",
      "line": 45,
      "class": "UserService",
      "metrics": {
        "lines": 450,
        "methods": 23,
        "params": 9,
        "atfd": 8,
        "wmc": 52,
        "tcc": 0.28
      },
      "confidence": 0.85,
      "fix": "Split into UserServicePersistence, UserServiceValidator, UserServiceCoordinator",
      "effort_hours": [4, 6]
    }
  ]
}
```

---

## Quick Start Example

```bash
# Validate entire codebase (thorough level)
Skill(command: "single-responsibility-principle")

# Validate specific directory
Skill(command: "single-responsibility-principle --path=src/services/")

# Fast validation (pre-commit)
Skill(command: "single-responsibility-principle --level=fast")

# Full validation with JSON output
Skill(command: "single-responsibility-principle --level=full --format=json")
```
