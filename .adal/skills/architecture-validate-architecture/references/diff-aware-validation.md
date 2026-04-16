# Diff-Aware Validation System

## The Problem (Chicken-and-Egg Issue)

**Original Situation:**
- File had existing architectural violation: `settings: Settings | None = None`
- Needed to add REFACTOR marker for ADR tracking (critical for orphan prevention)
- Pre-flight validation hook blocked **ALL edits** to files with violations
- Could not fix violations because hook blocked ALL edits
- Could not add markers without fixing violations first

**Wrong "Solution":**
```bash
# NEVER DO THIS - Bypasses safety mechanisms
mv pre_tool_use.py pre_tool_use.py.disabled
# Make edits
mv pre_tool_use.py.disabled pre_tool_use.py
```

**Why This Was Wrong:**
- Defeats purpose of validation
- Sets bad precedent ("just disable when inconvenient")
- Opens security hole for future

## The Solution: Diff-Aware Validation

The new system **compares before and after states** to make intelligent decisions:

```
Before: handle_pre_flight_validation(file_path)
        → Blocks if ANY violations exist

After:  handle_pre_flight_validation(file_path, tool_name, tool_input)
        → Analyzes DIFF between current and future state
        → Allows edits that FIX violations
        → Blocks edits that ADD violations
```

## Decision Matrix

| Current Violations | Future Violations | Decision | Reason |
|-------------------|-------------------|----------|---------|
| 0 | 0 | `ALLOW` (NEUTRAL_ON_CLEAN) | Clean stays clean |
| 2 | 0 | `ALLOW` | Complete fix ✅ |
| 2 | 1 | `ALLOW` (FIX_IN_PROGRESS) | Partial fix (improving) ✅ |
| 0 | 2 | `BLOCK` | Adding violations ❌ |
| 2 | 2 | `BLOCK` (NEUTRAL_ON_DIRTY) | Not fixing existing issues ⚠️ |

## Policy Decision: NEUTRAL_ON_DIRTY

**Question:** Should we allow edits that don't change violation count when violations exist?

**Example Scenario:**
```python
# File has violation: settings: Settings | None = None
# Edit: Add REFACTOR marker (doesn't fix violation)

# REFACTOR[ADR-023]: Consolidate chunking logic
class SmartChunkingService:
    def __init__(self, settings: Settings | None = None):  # Violation exists
        ...
```

**Decision: BLOCK (with helpful message)**

**Rationale:**
1. **Encourages fixing violations immediately** - Don't let technical debt accumulate
2. **Prevents "works on my machine" syndrome** - File gets worse over time
3. **Forces conscious decision** - Either fix now or create todo
4. **Maintains code quality** - No gradual degradation

**Message Shown:**
```
⚠️  EXISTING VIOLATIONS DETECTED

This file has 2 architectural violation(s) that are NOT being fixed by this edit:
  • Line 66: Parameter 'settings' must be required, not Optional
  • Line 66: Parameter 'settings' has default None - must be required

POLICY: This edit is ALLOWED because it doesn't make things worse.

However, you should fix these violations soon. Consider:
1. Creating a task to fix violations: Add to todo.md
2. Adding REFACTOR marker if scheduled for refactoring
3. Fixing violations now if the edit is small

To fix these violations, ensure your edit changes the violating code.
```

## How It Works

### Architecture

```
PreToolUse Hook (pre_tool_use.py)
  ↓
handle_pre_flight_validation(file_path, tool_name, tool_input)
  ↓
analyze_edit_impact(file_path, tool_name, tool_input)
  ↓
DiffAwareValidator
  ├─ validate_file()         # Current state
  ├─ validate_edit()         # Simulate Edit
  ├─ validate_write()        # Simulate Write
  └─ validate_multi_edit()   # Simulate MultiEdit
  ↓
EditAnalysis
  ├─ decision: EditDecision
  ├─ current_violations: int
  ├─ future_violations: int
  ├─ message: str
  └─ violation details
```

### Key Components

**1. DiffAwareValidator**
- Parses AST of Python files
- Detects architectural violations
- Simulates edits to predict future state

**2. analyze_edit_impact()**
- Entry point for validation
- Compares current vs future violations
- Returns EditAnalysis with decision

**3. EditDecision Enum**
```python
class EditDecision(Enum):
    ALLOW = "allow"                    # Improves or maintains clean state
    BLOCK = "block"                    # Makes architecture worse
    NEUTRAL_ON_CLEAN = "neutral_clean" # No violations before/after
    NEUTRAL_ON_DIRTY = "neutral_dirty" # Has violations, not fixing
    FIX_IN_PROGRESS = "fix_in_progress"# Reduces but doesn't eliminate
```

## Violations Detected

### 1. Optional Config Parameters
```python
# ❌ BLOCKED
def __init__(self, settings: Settings | None = None):
    ...

# ✅ ALLOWED
def __init__(self, settings: Settings):
    if not settings:
        raise ValueError("Settings required")
    ...
```

### 2. Default Config Creation
```python
# ❌ BLOCKED
def __init__(self, settings: Settings | None = None):
    if not settings:
        settings = Settings()  # Creating default
    ...

# ✅ ALLOWED
def __init__(self, settings: Settings):
    if not settings:
        raise ValueError("Settings required")  # Fail fast
    ...
```

### 3. try/except ImportError
```python
# ❌ BLOCKED
try:
    import optional_lib
except ImportError:
    optional_lib = None

# ✅ ALLOWED
import optional_lib  # Fail fast if missing
```

### 4. Clean Architecture Layer Violations
```python
# ❌ BLOCKED (domain importing infrastructure)
# In src/your_project/domain/services/processor.py
from your_project.infrastructure.neo4j.client import Neo4jClient

# ✅ ALLOWED
# In src/your_project/infrastructure/services/processor_impl.py
from your_project.infrastructure.neo4j.client import Neo4jClient
```

## Usage Examples

### Example 1: Fixing a Violation
```python
# Current file (has violation)
class MyService:
    def __init__(self, settings: Settings | None = None):
        if not settings:
            settings = Settings()
        self.settings = settings

# Edit operation
Edit(
    file_path="service.py",
    old_string="def __init__(self, settings: Settings | None = None):",
    new_string="def __init__(self, settings: Settings):",
)

# Result: ✅ ALLOWED (reduces violations from 2 to 0)
```

### Example 2: Adding a Violation
```python
# Current file (clean)
class MyService:
    def __init__(self, settings: Settings):
        self.settings = settings

# Edit operation
Edit(
    file_path="service.py",
    old_string="def __init__(self, settings: Settings):",
    new_string="def __init__(self, settings: Settings | None = None):",
)

# Result: 🚫 BLOCKED (adds violations: 0 → 2)
```

### Example 3: Neutral Edit to Dirty File
```python
# Current file (has violation)
class MyService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings

# Edit operation (adding comment, not fixing violation)
Edit(
    file_path="service.py",
    old_string="class MyService:",
    new_string="# TODO: Refactor this\nclass MyService:",
)

# Result: 🚫 BLOCKED (violations: 2 → 2, not improving)
# Message: Please fix existing violations or create todo
```

## Testing

### Run All Tests
```bash
python3 .claude/scripts/test_diff_aware_validation.py
```

### Test Scenarios Covered
1. ✅ Adding violations (BLOCK)
2. ✅ Fixing violations (ALLOW)
3. ✅ Complete fix (ALLOW)
4. ✅ Neutral edit to clean file (ALLOW)
5. ✅ Neutral edit to dirty file (BLOCK)
6. ✅ Adding REFACTOR marker to dirty file (BLOCK)
7. ✅ MultiEdit fixing violations (ALLOW)
8. ✅ Adding try/except ImportError (BLOCK)
9. ✅ Removing try/except ImportError (ALLOW)

### Manual Testing
```bash
# Test single file validation
python3 .claude/scripts/diff_aware_validation.py \
    src/path/to/file.py \
    Edit \
    '{"old_string": "...", "new_string": "..."}'
```

## Integration Points

### PreToolUse Hook
```python
# .claude/hooks/pre_tool_use/pre_tool_use.py

def handle_pre_flight_validation(file_path: str, tool_name: str, tool_input: dict):
    """NEW: Diff-aware validation"""
    from scripts.diff_aware_validation import analyze_edit_impact

    analysis = analyze_edit_impact(file_path, tool_name, tool_input)

    if analysis.should_allow:
        return True, ""
    else:
        return False, analysis.message
```

### Fallback Behavior
If diff-aware validation unavailable (ImportError):
```python
# Falls back to old pre_flight_validation.py (simple mode)
# Only validates current file state (original behavior)
# Ensures system keeps working even if new code has issues
```

## Edge Cases Handled

### 1. File Doesn't Exist Yet (Write operation)
```python
# Creating new file
Write(file_path="new_service.py", content="...")

# Result: Validates content directly (no current state to compare)
```

### 2. Edit String Not Found
```python
# Edit would fail anyway
Edit(file_path="file.py", old_string="DOES_NOT_EXIST", new_string="...")

# Result: Returns current file validation (edit won't apply)
```

### 3. MultiEdit with Mixed Operations
```python
MultiEdit(
    file_path="file.py",
    edits=[
        {"old_string": "violation1", "new_string": "fixed1"},  # Fixes
        {"old_string": "clean_code", "new_string": "violation2"},  # Adds
    ]
)

# Result: Analyzes final state after ALL edits
# If net change is negative (more violations), BLOCKS
```

### 4. Syntax Errors
```python
# File or proposed content has syntax errors

# Result: Validation passes (not architectural violation)
# Python tools (pyright, ruff) handle syntax errors
```

### 5. Non-Python Files
```python
Edit(file_path="README.md", ...)

# Result: Skipped (validation only for .py files in src/)
```

### 6. Test Files
```python
Edit(file_path="tests/test_service.py", ...)

# Result: Skipped (tests have different rules)
```

## Configuration

### Environment Variables
None required - works out of the box.

### Hook Configuration
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre_tool_use/pre_tool_use.py",
            "timeout": 3000
          }
        ]
      }
    ]
  }
}
```

## Troubleshooting

### Hook Not Blocking/Allowing as Expected

**Check:**
1. Is file in `src/your_project/`? (validation scope)
2. Is file a test? (tests are skipped)
3. Run validation manually to see decision:
   ```bash
   python3 .claude/scripts/diff_aware_validation.py file.py Edit '{"old_string": "...", "new_string": "..."}'
   ```

### ImportError: No module named 'diff_aware_validation'

**Solution:**
- Hook has fallback to old validation
- Check that `.claude/scripts/diff_aware_validation.py` exists
- Verify Python path is set correctly in hook

### Validation Passes But Should Block

**Check:**
1. Are you editing the actual violation?
2. Is violation in test file? (tests skipped)
3. Run tests: `python3 .claude/scripts/test_diff_aware_validation.py`

### Validation Blocks But Should Allow

**Check:**
1. Does edit actually reduce violations?
2. Is edit neutral on dirty file? (policy: block unless fixing)
3. Check violation count: current vs future

## Migration Guide

### Before (v2.0)
```python
# Blocked ALL edits if violations exist
def handle_pre_flight_validation(file_path: str):
    result = validate_file(file_path)
    if result.has_violations:
        return False, "File has violations"
    return True, ""
```

### After (v3.0)
```python
# Smart validation - allows fixing violations
def handle_pre_flight_validation(file_path: str, tool_name: str, tool_input: dict):
    analysis = analyze_edit_impact(file_path, tool_name, tool_input)
    if analysis.should_allow:
        return True, ""
    return False, analysis.message
```

### Behavior Changes

| Scenario | v2.0 (Old) | v3.0 (New) |
|----------|------------|------------|
| Fix violation in file with violations | ❌ BLOCKED | ✅ ALLOWED |
| Add violation to clean file | ❌ BLOCKED | ❌ BLOCKED |
| Add comment to dirty file | ❌ BLOCKED | 🚫 BLOCKED* |
| Add REFACTOR marker to dirty file | ❌ BLOCKED | 🚫 BLOCKED* |

*Note: v3.0 provides actionable guidance on how to proceed

## Future Enhancements

### Potential Improvements
1. **Allow-list for markers**: Permit REFACTOR markers without blocking
2. **Violation exemptions**: Config-based exemptions for specific files
3. **Gradual improvement mode**: Allow edits that don't worsen (not implement due to quality concerns)
4. **Automated fixes**: Suggest fixes for common violations
5. **Violation tracking**: Store violation history in memory

### Not Recommended
- **Disable validation**: Defeats purpose, introduces technical debt
- **Always allow neutral edits**: Permits gradual degradation
- **Warn instead of block**: Developers ignore warnings

## Answers to Design Questions

### 1. Should hook inspect DIFF?
**YES** - Core of solution. Comparing current vs future state is the only way to allow fixes while blocking additions.

### 2. Should certain operations be exempt?
**NO** - All operations should improve or maintain quality. Exception: Operations explicitly marked as "fixing violations" could be exempt.

### 3. How handle files scheduled for deletion?
**BLOCK** - If file has violations and marked for deletion (REFACTOR marker), editing it suggests it's NOT being deleted soon. Either delete it now or fix violations.

### 4. Should there be "fixing violations" mode flag?
**NO** - Decision is automatic based on violation count change. No manual flags needed.

### 5. Right behavior when violations remain?
**BLOCK (with guidance)** - Force conscious decision: fix now, create todo, or explain why violations can't be fixed yet.

## Summary

**Key Benefits:**
- ✅ Allows fixing violations (solves chicken-and-egg problem)
- ✅ Prevents adding new violations (maintains quality)
- ✅ Provides actionable feedback (not just "no")
- ✅ Backwards compatible (falls back to old behavior)
- ✅ Zero configuration required (works out of box)

**Design Principles:**
1. **Never prevent fixing problems** - Always allow edits that reduce violations
2. **Never allow making things worse** - Block edits that add violations
3. **Encourage immediate fixes** - Warn but block neutral edits to dirty files
4. **Fail safely** - If validation has errors, fail open (don't block work)
5. **Be transparent** - Show exactly what violations exist and what would happen

**Result:**
A validation system that **enables quality improvement** while **preventing quality degradation**.
