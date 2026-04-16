# ServiceResult Troubleshooting Guide

Detailed troubleshooting steps for common ServiceResult pattern errors.

## Issue: Test fails with "'dict' object has no attribute 'success'"

**Symptom:** Mock returns dict instead of ServiceResult

**Diagnosis:**
```bash
# Run test to see exact error
uv run pytest tests/path/to/test.py::test_name -v
```

**Fix:**
```python
# ❌ WRONG - Returns dict
mock_service.get_data = AsyncMock(return_value={"items": []})

# ✅ CORRECT - Returns ServiceResult
from project_watch_mcp.domain.common import ServiceResult
mock_service.get_data = AsyncMock(return_value=ServiceResult.ok({"items": []}))
```

**Validation:**
```bash
# Re-run test
uv run pytest tests/path/to/test.py::test_name -v
# Should now pass
```

---

## Issue: "coroutine object has no attribute 'success'"

**Symptom:** AsyncMock not configured correctly

**Root Cause:** Missing `return_value` on AsyncMock

**Fix:**
```python
# ❌ WRONG - AsyncMock without return_value
mock_service.fetch = AsyncMock()

# ✅ CORRECT - AsyncMock with ServiceResult return_value
mock_service.fetch = AsyncMock(
    return_value=ServiceResult.ok(data)
)
```

---

## Issue: Type error "Incompatible types in assignment"

**Symptom:** `ServiceResult[T]` type mismatch

**Diagnosis:**
```bash
uv run pyright src/project_watch_mcp/
```

**Common causes:**

### 1. Wrong generic type
```python
# ❌ WRONG
def process() -> ServiceResult[list[str]]:
    result: ServiceResult[dict] = get_data()
    return result  # Type error!

# ✅ CORRECT
def process() -> ServiceResult[list[str]]:
    result: ServiceResult[dict] = get_data()
    if result.is_failure:
        return ServiceResult.fail(result.error)
    return ServiceResult.ok(list(result.data.keys()))
```

### 2. Missing type annotation
```python
# ❌ WRONG
result = await service.fetch()  # Type unknown

# ✅ CORRECT
result: ServiceResult[dict] = await service.fetch()
```

---

## Issue: "Cannot unwrap None data from successful result"

**Symptom:** Calling `.unwrap()` on ServiceResult with None data

**Root Cause:** ServiceResult.ok(None) cannot be unwrapped

**Fix:**
```python
# ❌ WRONG
result = ServiceResult.ok(None)
value = result.unwrap()  # Raises ValueError!

# ✅ CORRECT - Use unwrap_or
result = ServiceResult.ok(None)
value = result.unwrap_or([])  # Returns default

# ✅ BETTER - Check data before unwrapping
if result.data is not None:
    value = result.unwrap()
else:
    value = default_value
```

---

## Issue: Many sequential ServiceResult checks

**Symptom:** Code has 5+ sequential `if result.success:` checks

**Diagnosis:**
```bash
# Find files with chaining opportunities
grep -r "if.*result.*success" src/ | wc -l
```

**Refactoring opportunity:**
Use composition utilities instead of manual chaining

**See:** Step 4 in main SKILL.md Instructions section for `compose_results()` examples

---

## Validation Process

### Step 1: Error Classification
```bash
# Run test to identify error type
uv run pytest tests/path/to/test.py::test_name -v

# Classify error:
# - 'dict' object has no attribute 'success'
# - coroutine object has no attribute 'success'
# - Incompatible types in assignment
# - Cannot unwrap None data
```

### Step 2: Mock Configuration Fix
```python
# Verify mock returns ServiceResult
from project_watch_mcp.domain.common import ServiceResult

mock_service.method = AsyncMock(
    return_value=ServiceResult.ok(data)
)
```

### Step 3: Type Validation
```bash
# Run pyright to check ServiceResult[T] types
uv run pyright src/

# Fix type mismatches
```

### Step 4: Test Execution
```bash
# Re-run test
uv run pytest tests/path/to/test.py::test_name -v

# Verify:
# ✓ Test passes
# ✓ No type errors
# ✓ ServiceResult pattern enforced
```

### Step 5: Pattern Validation
```bash
# Check for refactoring opportunities
python scripts/find_serviceresult_chains.py --suggest-refactor src/

# Apply composition utilities where beneficial
```
