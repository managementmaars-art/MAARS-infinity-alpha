# Reference - ServiceResult Monad Pattern

## Python Utility Scripts

For automated validation and refactoring of ServiceResult code, see these Python examples in the `examples/` directory:
- [find_serviceresult_chains.py](../examples/find_serviceresult_chains.py) - Analyze ServiceResult chaining opportunities and identify refactoring opportunities
- [fix_serviceresult_mocks.py](../examples/fix_serviceresult_mocks.py) - Auto-fix ServiceResult mock errors in test files
- [validate_serviceresult_usage.py](../examples/validate_serviceresult_usage.py) - Validate ServiceResult usage patterns across the codebase

## Understanding the Monad Pattern

ServiceResult implements the **Result/Either monad pattern** from functional programming. This document explains the pattern and why it's used in your_project.

---

## What is a Monad?

A monad is a design pattern for composing operations that might fail, without explicit error checking at each step.

**Key Properties:**

1. **Wrapper Type**: ServiceResult[T] wraps a value of type T
2. **Unit/Return**: `ServiceResult.ok(value)` creates a successful result
3. **Bind/FlatMap**: `compose_results(func, result)` chains operations
4. **Laws**: Monads follow specific mathematical laws (left identity, right identity, associativity)

---

## Why Use ServiceResult?

### Problem: Traditional Error Handling

```python
# ❌ Traditional approach - verbose and error-prone
def process_file(path: str) -> dict | None:
    try:
        content = read_file(path)
        if content is None:
            return None

        parsed = parse_content(content)
        if parsed is None:
            return None

        validated = validate(parsed)
        if validated is None:
            return None

        return validated
    except Exception:
        return None
```

**Issues:**
- None can mean "no data" OR "error occurred" (ambiguous)
- Lost error context (what failed and why?)
- Verbose null checking at every step
- Hard to compose operations

### Solution: ServiceResult Pattern

```python
# ✅ ServiceResult approach - explicit and composable
async def process_file(path: str) -> ServiceResult[dict]:
    result = await read_file(path)

    if result.success:
        result = await compose_results(parse_content, result)

    if result.success:
        result = await compose_results(validate, result)

    return result
```

**Benefits:**
- Explicit success/failure state
- Preserves error messages and context
- Type-safe composition
- Fail-fast by default

---

## Monad Operations

### 1. Unit (Return)

Creates a monad from a value.

```python
# Success
result = ServiceResult.ok({"data": "value"})
# ServiceResult(success=True, data={"data": "value"})

# Failure
result = ServiceResult.fail("Error message")
# ServiceResult(success=False, error="Error message")
```

---

### 2. Bind (FlatMap)

Chains operations that return monads.

```python
from your_project.domain.common.service_result_utils import compose_results

def process(data: str) -> ServiceResult[int]:
    try:
        return ServiceResult.ok(int(data))
    except ValueError:
        return ServiceResult.fail("Invalid integer")

# Chain: read -> process
result = ServiceResult.ok("42")
result = compose_results(process, result)
# result.success = True, result.data = 42

# Failure propagates automatically
result = ServiceResult.ok("invalid")
result = compose_results(process, result)
# result.success = False, result.error = "Invalid integer"
```

**Why "Flat"Map?**

Without flattening, we'd get nested results:
```python
# Without flatMap
result = ServiceResult.ok("42")
nested = ServiceResult.ok(process("42"))  # Wrong!
# nested = ServiceResult(success=True, data=ServiceResult(success=True, data=42))

# With flatMap (compose_results)
result = compose_results(process, ServiceResult.ok("42"))
# result = ServiceResult(success=True, data=42)  # Flattened!
```

---

### 3. Map (Functor)

Transforms the wrapped value without changing the wrapper type.

```python
from your_project.domain.common.service_result_utils import map_result

def double(x: int) -> int:
    return x * 2

result = ServiceResult.ok(21)
doubled = map_result(double, result)
# doubled.success = True, doubled.data = 42

# Map doesn't execute on failure
result = ServiceResult.fail("Error")
doubled = map_result(double, result)
# doubled.success = False, doubled.error = "Error"
# double() was never called!
```

**Difference: Map vs Bind**

```python
# Map: T -> U (returns plain value)
def double(x: int) -> int:
    return x * 2

map_result(double, result)  # ServiceResult[int] -> ServiceResult[int]

# Bind: T -> ServiceResult[U] (returns wrapped value)
def process(x: int) -> ServiceResult[str]:
    return ServiceResult.ok(str(x))

compose_results(process, result)  # ServiceResult[int] -> ServiceResult[str]
```

---

## Monad Laws

ServiceResult follows three fundamental laws:

### 1. Left Identity

`bind(unit(x), f) == f(x)`

```python
from your_project.domain.common.service_result_utils import compose_results

def add_ten(x: int) -> ServiceResult[int]:
    return ServiceResult.ok(x + 10)

# Left side: bind(unit(5), add_ten)
left = compose_results(add_ten, ServiceResult.ok(5))

# Right side: add_ten(5)
right = add_ten(5)

# They should be equal
assert left == right
# Both: ServiceResult(success=True, data=15)
```

---

### 2. Right Identity

`bind(m, unit) == m`

```python
result = ServiceResult.ok(42)

# Binding with unit should return the same monad
identity_result = compose_results(
    lambda x: ServiceResult.ok(x),
    result
)

assert identity_result == result
```

---

### 3. Associativity

`bind(bind(m, f), g) == bind(m, lambda x: bind(f(x), g))`

```python
def add_ten(x: int) -> ServiceResult[int]:
    return ServiceResult.ok(x + 10)

def double(x: int) -> ServiceResult[int]:
    return ServiceResult.ok(x * 2)

m = ServiceResult.ok(5)

# Left side: bind(bind(m, add_ten), double)
left = compose_results(add_ten, m)
left = compose_results(double, left)

# Right side: bind(m, lambda x: bind(add_ten(x), double))
right = compose_results(
    lambda x: compose_results(double, add_ten(x)),
    m
)

assert left == right
# Both: ServiceResult(success=True, data=30)
# (5 + 10) * 2 = 30
```

---

## Practical Examples

### Example 1: Railway-Oriented Programming

Think of ServiceResult as a railway track with two rails:
- **Success rail**: Operations continue
- **Failure rail**: Operations skip to the end

```python
async def index_file(path: Path) -> ServiceResult[dict]:
    # All on success rail
    result = await read_file(path)           # May switch to failure rail
    if result.success:
        result = await parse_content(result.data)   # May switch to failure rail
    if result.success:
        result = await validate(result.data)        # May switch to failure rail
    if result.success:
        result = await store(result.data)           # May switch to failure rail

    # Once on failure rail, stays there
    return result
```

**Visual:**
```
Success: read -> parse -> validate -> store -> success
                ↓
Failure:        parse_error -> SKIP -> SKIP -> failure
```

---

### Example 2: Collecting Multiple Results

```python
from your_project.domain.common.service_result_utils import collect_results

async def process_files(paths: list[Path]) -> ServiceResult[list[dict]]:
    results = []
    for path in paths:
        result = await process_file(path)
        results.append(result)

    # Fails if ANY result failed (fail-fast)
    return collect_results(results)
```

---

### Example 3: Partial Success with Partition

```python
from your_project.domain.common.service_result_utils import partition_results

async def process_batch(items: list[str]) -> dict:
    results = [await process_item(item) for item in items]

    # Separate successes from failures
    successes, failures = partition_results(results)

    return {
        "processed": successes,
        "errors": failures
    }
```

---

## Comparison with Other Patterns

### Option/Maybe Monad

```python
# Option monad (Rust, Haskell)
Some(value) | None

# ServiceResult (more explicit)
ServiceResult.ok(value) | ServiceResult.fail(error)
```

ServiceResult is **more informative** because it preserves error context.

---

### Either Monad

```python
# Either monad (Haskell)
Right(value) | Left(error)

# ServiceResult (equivalent)
ServiceResult.ok(value) | ServiceResult.fail(error)
```

ServiceResult **is an Either monad** with explicit naming.

---

### Exception-Based Error Handling

```python
# Exceptions (traditional)
try:
    result = risky_operation()
except Exception as e:
    # Error handling

# ServiceResult (functional)
result = risky_operation()  # Returns ServiceResult
if result.is_failure:
    # Error handling
```

**ServiceResult advantages:**
- Explicit in function signature
- Forces error handling (type system)
- No hidden control flow
- Easier to test

---

## Type Safety Benefits

### 1. Explicit Error Types

```python
# ❌ Exception-based - what exceptions?
async def get_user(id: str) -> User:
    # Could raise DatabaseError, ValidationError, NetworkError, etc.
    # Caller doesn't know from signature!
    pass

# ✅ ServiceResult-based - explicit failure possibility
async def get_user(id: str) -> ServiceResult[User]:
    # Signature says: "This can fail, handle it!"
    pass
```

---

### 2. Compile-Time Safety (with mypy/pyright)

```python
result = await get_user("123")

# ❌ Type error - accessing data without checking success
user = result.data
# Error: Object possibly None

# ✅ Type-safe - narrow type with success check
if result.success:
    user = result.data  # Type system knows data is not None
    print(user.name)
```

---

### 3. Generic Type Preservation

```python
# Generic function maintains type
from typing import TypeVar

T = TypeVar("T")

def wrap_result(value: T) -> ServiceResult[T]:
    return ServiceResult.ok(value)

# Type checker knows:
int_result: ServiceResult[int] = wrap_result(42)
str_result: ServiceResult[str] = wrap_result("hello")
```

---

## Common Anti-Patterns

### ❌ Anti-Pattern 1: Ignoring Failure

```python
result = await operation()
# Assuming success without checking
data = result.data  # Could be None!
```

**✅ Fix:**
```python
result = await operation()
if result.is_failure:
    return ServiceResult.fail(result.error)
data = result.data  # Safe now
```

---

### ❌ Anti-Pattern 2: Converting to Exception

```python
result = await operation()
if result.is_failure:
    raise Exception(result.error)  # Defeats the purpose!
```

**✅ Fix:**
```python
result = await operation()
return result  # Keep it as ServiceResult
```

---

### ❌ Anti-Pattern 3: Nested ServiceResults

```python
def outer() -> ServiceResult[ServiceResult[int]]:
    inner_result = get_number()
    return ServiceResult.ok(inner_result)  # Wrong!
```

**✅ Fix:**
```python
def outer() -> ServiceResult[int]:
    return get_number()  # Already a ServiceResult
```

---

## Performance Considerations

### Memory Overhead

ServiceResult adds minimal overhead:
- 3 fields: success (bool), data (T), error (str | None), metadata (dict)
- ~40 bytes per instance (vs ~24 bytes for bare value)

**Negligible for typical use cases.**

---

### Composition Performance

```python
# Sequential composition
result = step1()
if result.success:
    result = step2(result.data)
if result.success:
    result = step3(result.data)

# vs

# Using compose_results (same performance)
result = step1()
result = compose_results(step2, result)
result = compose_results(step3, result)
```

Composition utilities have **zero performance penalty** - they're just syntactic sugar.

---

### Async Performance

```python
# Parallel execution with ServiceResult
import asyncio
from your_project.domain.common.service_result_utils import collect_results

async def process_parallel(items: list[str]) -> ServiceResult[list[dict]]:
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return collect_results(results)
```

ServiceResult **doesn't block parallelism** - it's just a return type wrapper.

---

## Testing ServiceResult Code

### Unit Testing

```python
import pytest
from your_project.domain.common import ServiceResult

def test_success_case():
    result = ServiceResult.ok({"value": 42})

    assert result.success
    assert result.data == {"value": 42}
    assert result.error is None

def test_failure_case():
    result = ServiceResult.fail("Operation failed")

    assert result.is_failure
    assert result.error == "Operation failed"
    assert result.data is None

def test_composition():
    from your_project.domain.common.service_result_utils import map_result

    def double(x: int) -> int:
        return x * 2

    result = ServiceResult.ok(21)
    doubled = map_result(double, result)

    assert doubled.success
    assert doubled.data == 42
```

---

### Property-Based Testing (Monad Laws)

```python
from hypothesis import given, strategies as st
from your_project.domain.common import ServiceResult
from your_project.domain.common.service_result_utils import compose_results

@given(st.integers())
def test_left_identity(x: int):
    """Left identity law: bind(unit(x), f) == f(x)"""
    def add_ten(n: int) -> ServiceResult[int]:
        return ServiceResult.ok(n + 10)

    left = compose_results(add_ten, ServiceResult.ok(x))
    right = add_ten(x)

    assert left == right

@given(st.integers())
def test_right_identity(x: int):
    """Right identity law: bind(m, unit) == m"""
    m = ServiceResult.ok(x)
    identity = compose_results(lambda v: ServiceResult.ok(v), m)

    assert identity == m
```

---

## Further Reading

### Academic Papers
- "Monads for Functional Programming" - Philip Wadler
- "Railway Oriented Programming" - Scott Wlaschin

### Language Implementations
- **Rust**: `Result<T, E>` type
- **Haskell**: `Either a b` monad
- **Scala**: `Try[T]` and `Either[A, B]`
- **F#**: Result type with computation expressions

### Related Patterns
- **Option/Maybe**: Handles null/None (subset of Result)
- **Try**: Specialized for exception handling
- **Validation**: Accumulates errors instead of fail-fast

---

## Summary

**ServiceResult is a monad that:**
1. ✅ Wraps success/failure explicitly
2. ✅ Preserves error context
3. ✅ Enables type-safe composition
4. ✅ Forces error handling
5. ✅ Follows mathematical laws
6. ✅ Integrates with async/await
7. ✅ Has zero runtime overhead

**Use it for:**
- Service layer operations
- Repository methods
- Command/Query handlers
- Any operation that can fail

**Don't use it for:**
- Programming errors (use assertions/exceptions)
- Truly exceptional conditions (use exceptions)
- Simple getters (use direct return)

---

**Key Takeaway**: ServiceResult transforms error handling from an afterthought into a first-class, type-safe, composable part of your domain model.
