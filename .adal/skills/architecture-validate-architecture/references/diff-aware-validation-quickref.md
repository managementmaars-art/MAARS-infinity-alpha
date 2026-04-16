# Diff-Aware Validation - Quick Reference

## What Changed

**Before:** Hook blocked ALL edits to files with violations
**After:** Hook analyzes DIFF and allows edits that FIX violations

## Decision Matrix

```
┌─────────────────┬─────────────────┬──────────────────────────┐
│ Current Violations │ Future Violations │ Decision              │
├─────────────────┼─────────────────┼──────────────────────────┤
│ 0               │ 0               │ ✅ ALLOW (clean)         │
│ 2               │ 0               │ ✅ ALLOW (fixed all)     │
│ 2               │ 1               │ ✅ ALLOW (improving)     │
│ 0               │ 2               │ ❌ BLOCK (adding)        │
│ 2               │ 2               │ ⚠️  BLOCK (not fixing)   │
└─────────────────┴─────────────────┴──────────────────────────┘
```

## Quick Examples

### ✅ Allowed: Fixing a Violation
```python
# Before
def __init__(self, settings: Settings | None = None):
    ...

# After (Edit)
def __init__(self, settings: Settings):
    ...

# Result: ALLOWED (reduces violations)
```

### ❌ Blocked: Adding a Violation
```python
# Before
def __init__(self, settings: Settings):
    ...

# After (Edit)
def __init__(self, settings: Settings | None = None):
    ...

# Result: BLOCKED (adds violations)
```

### ⚠️ Blocked: Not Fixing Existing Issues
```python
# Before (has violation)
def __init__(self, settings: Settings | None = None):
    ...

# Edit: Add comment (doesn't fix violation)
# TODO: Refactor this

# Result: BLOCKED (violations: 2 → 2)
# Message: Please fix existing violations first
```

## What to Do When Blocked

### Scenario: "File has violations but edit doesn't add any"

**Message:**
```
⚠️  EXISTING VIOLATIONS DETECTED
This file has 2 violation(s) not being fixed by this edit.
```

**Options:**
1. **Fix violations now** - Make edit that reduces violation count
2. **Create todo** - Add task to ./todo.md for later fix
3. **Explain** - Comment why violations can't be fixed yet

### Scenario: "Edit adds new violations"

**Message:**
```
🚫 Edit ADDS violations (0 → 2)
  • Parameter 'settings' must be required, not Optional
```

**Solution:**
- Change edit to NOT add violations
- Follow architectural patterns (see CLAUDE.md)

## Testing

### Run All Tests
```bash
python3 .claude/scripts/test_diff_aware_validation.py
```

### Test Single File
```bash
python3 .claude/scripts/diff_aware_validation.py \
    src/path/file.py \
    Edit \
    '{"old_string": "old", "new_string": "new"}'
```

## Common Violations

### 1. Optional Config Parameters
```python
❌ def __init__(self, settings: Settings | None = None)
✅ def __init__(self, settings: Settings)
```

### 2. Default Config Creation
```python
❌ if not settings: settings = Settings()
✅ if not settings: raise ValueError("Settings required")
```

### 3. try/except ImportError
```python
❌ try: import X except ImportError: X = None
✅ import X  # Fail fast
```

## Files Affected

- **Validated:** `src/your_project/**/*.py`
- **Skipped:** Tests (`tests/**/*.py`)
- **Skipped:** Non-Python files

## Troubleshooting

### "Hook blocks my fix!"
- Check that edit actually reduces violations
- Run test: `python3 .claude/scripts/test_diff_aware_validation.py`

### "Hook allows violation!"
- Check if file is in `src/your_project/`
- Check if file is a test (tests skipped)
- Run validation manually to see decision

## Integration

Hook automatically uses diff-aware validation (v3.0).
No configuration needed.

Falls back to old behavior if new code unavailable.

## Documentation

- **Full guide:** `diff-aware-validation.md`
- **Implementation:** `.claude/scripts/diff_aware_validation.py`
- **Tests:** `.claude/scripts/test_diff_aware_validation.py`
- **Hook:** `.claude/hooks/pre_tool_use/pre_tool_use.py`
