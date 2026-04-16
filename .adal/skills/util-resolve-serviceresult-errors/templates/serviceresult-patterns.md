# ServiceResult Pattern Templates

Quick reference templates for common ServiceResult patterns. Copy-paste and adapt.

---

## Mock Configuration Templates

### Basic Mock Fixture
```python
from unittest.mock import AsyncMock, MagicMock
from project_watch_mcp.domain.common import ServiceResult

@pytest.fixture
def mock_repository():
    repo = MagicMock(spec=RepositoryInterface)
    repo.method_name = AsyncMock(
        return_value=ServiceResult.ok({{DATA}})
    )
    return repo
```

### Mock with Failure Result
```python
@pytest.fixture
def mock_service_error():
    service = MagicMock(spec=ServiceInterface)
    service.method_name = AsyncMock(
        return_value=ServiceResult.fail("{{ERROR_MESSAGE}}")
    )
    return service
```

### Mock with Side Effect (Multiple Calls)
```python
@pytest.fixture
def mock_with_side_effect():
    service = MagicMock(spec=ServiceInterface)
    service.method_name = AsyncMock(side_effect=[
        ServiceResult.ok({{DATA1}}),
        ServiceResult.fail("{{ERROR}}"),
        ServiceResult.ok({{DATA2}}),
    ])
    return service
```

---

## Service Method Templates

### Basic Service Method
```python
async def {{method_name}}(self, {{params}}) -> ServiceResult[{{ReturnType}}]:
    """{{Description}}.

    Args:
        {{param}}: {{Description}}

    Returns:
        ServiceResult containing {{description}} or error
    """
    try:
        result = await self.{{dependency}}.{{method}}({{args}})

        if result.is_failure:
            return ServiceResult.fail(f"{{Context}}: {result.error}")

        return ServiceResult.ok(result.data)

    except Exception as e:
        return ServiceResult.fail(f"{{Operation}} failed: {str(e)}")
```

### Service Method with Validation
```python
async def {{method_name}}(self, {{params}}) -> ServiceResult[{{ReturnType}}]:
    """{{Description}}."""
    # Validate input
    if not {{validation_condition}}:
        return ServiceResult.fail("{{Validation error message}}")

    # Execute operation
    result = await self.{{dependency}}.{{method}}({{args}})

    if result.is_failure:
        return ServiceResult.fail(result.error)

    # Validate output
    if not {{output_validation}}:
        return ServiceResult.fail("{{Output validation error}}")

    return ServiceResult.ok(result.data)
```

### Service Method with Chaining
```python
from project_watch_mcp.domain.common.service_result_utils import compose_results

async def {{method_name}}(self, {{params}}) -> ServiceResult[{{ReturnType}}]:
    """{{Description}}."""
    # Step 1
    result = await self.{{service1}}.{{method1}}({{args}})

    # Step 2 (only if step 1 succeeded)
    if result.success:
        result = await compose_results(
            lambda data: self.{{service2}}.{{method2}}(data),
            result
        )

    # Step 3 (only if step 2 succeeded)
    if result.success:
        result = await compose_results(
            lambda data: self.{{service3}}.{{method3}}(data),
            result
        )

    return result
```

---

## Test Templates

### Basic Test with Mock
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from project_watch_mcp.domain.common import ServiceResult

class Test{{ClassName}}:
    """Test {{class description}}."""

    @pytest.fixture
    def mock_{{dependency}}(self):
        mock = MagicMock(spec={{DependencyClass}})
        mock.{{method}} = AsyncMock(
            return_value=ServiceResult.ok({{expected_data}})
        )
        return mock

    async def test_{{test_name}}(self, mock_{{dependency}}):
        """Test {{description}}."""
        # Arrange
        service = {{ServiceClass}}(mock_{{dependency}})

        # Act
        result = await service.{{method}}({{args}})

        # Assert
        assert result.success
        assert result.data == {{expected_data}}
        mock_{{dependency}}.{{method}}.assert_called_once_with({{args}})
```

### Test Error Handling
```python
async def test_{{test_name}}_error_handling(self, mock_{{dependency}}):
    """Test error handling when {{condition}}."""
    # Arrange - Mock returns error
    mock_{{dependency}}.{{method}} = AsyncMock(
        return_value=ServiceResult.fail("{{error_message}}")
    )
    service = {{ServiceClass}}(mock_{{dependency}})

    # Act
    result = await service.{{method}}({{args}})

    # Assert
    assert result.is_failure
    assert "{{error_message}}" in result.error
```

### Test Validation Error
```python
async def test_{{test_name}}_validation_error(self):
    """Test validation error when {{condition}}."""
    # Arrange
    service = {{ServiceClass}}({{dependencies}})
    invalid_input = {{invalid_value}}

    # Act
    result = await service.{{method}}(invalid_input)

    # Assert
    assert result.is_failure
    assert "{{validation_error_message}}" in result.error
```

---

## Composition Templates

### Map Over Result
```python
from project_watch_mcp.domain.common.service_result_utils import map_result

def {{transform_function}}(data: {{InputType}}) -> {{OutputType}}:
    return {{transformation}}

async def {{method_name}}(self) -> ServiceResult[{{OutputType}}]:
    result = await self.{{service}}.{{method}}()
    return map_result({{transform_function}}, result)
```

### Chain Multiple Results
```python
from project_watch_mcp.domain.common.service_result_utils import chain_results

async def {{method_name}}(self) -> ServiceResult[list]:
    result1 = await self.{{service1}}.{{method}}()
    result2 = await self.{{service2}}.{{method}}()
    result3 = await self.{{service3}}.{{method}}()

    return chain_results(result1, result2, result3)
```

### Collect List of Results
```python
from project_watch_mcp.domain.common.service_result_utils import collect_results

async def {{method_name}}(self, items: list[{{ItemType}}]) -> ServiceResult[list[{{ResultType}}]]:
    results = []
    for item in items:
        result = await self.{{service}}.{{method}}(item)
        results.append(result)

    return collect_results(results)
```

### Parallel Processing
```python
import asyncio
from project_watch_mcp.domain.common.service_result_utils import collect_results

async def {{method_name}}(self, items: list[{{ItemType}}]) -> ServiceResult[list[{{ResultType}}]]:
    # Execute all operations in parallel
    tasks = [
        self.{{service}}.{{method}}(item)
        for item in items
    ]

    # Wait for all to complete
    results = await asyncio.gather(*tasks)

    # Collect and return
    return collect_results(results)
```

### Recovery Pattern
```python
from project_watch_mcp.domain.common.service_result_utils import recover_result

async def {{method_name}}(self) -> ServiceResult[{{Type}}]:
    result = await self.{{service}}.{{method}}()

    return recover_result(
        result,
        lambda error: ServiceResult.ok({{default_value}})
    )
```

---

## Integration Test Templates

### Integration Test with Real Dependencies
```python
import pytest
from project_watch_mcp.domain.common import ServiceResult

@pytest.mark.integration
class Test{{ClassName}}Integration:
    """Integration tests for {{class}}."""

    @pytest.fixture
    async def service(self, {{real_dependencies}}):
        """Create service with real dependencies."""
        return {{ServiceClass}}({{dependencies}})

    async def test_{{test_name}}_integration(self, service):
        """Test {{description}} with real dependencies."""
        # Act
        result = await service.{{method}}({{args}})

        # Assert
        assert result.success
        assert {{validation_of_result_data}}
```

---

## Error Handling Templates

### Try-Catch with ServiceResult
```python
async def {{method_name}}(self, {{params}}) -> ServiceResult[{{Type}}]:
    """{{Description}}."""
    try:
        # Risky operation
        data = await self.{{dependency}}.{{method}}({{args}})
        return ServiceResult.ok(data)

    except {{SpecificException}} as e:
        return ServiceResult.fail(f"{{Operation}} failed: {str(e)}")

    except Exception as e:
        return ServiceResult.fail(f"Unexpected error: {str(e)}")
```

### Nested Error Propagation
```python
async def {{method_name}}(self, {{params}}) -> ServiceResult[{{Type}}]:
    """{{Description}}."""
    # Call service that returns ServiceResult
    result = await self.{{service}}.{{method}}({{args}})

    if result.is_failure:
        # Add context to error
        return ServiceResult.fail(
            f"{{Context}}: {result.error}",
            code=result.metadata.get("code")
        )

    # Process successful result
    processed = {{process_data}}(result.data)
    return ServiceResult.ok(processed)
```

---

## Type-Safe Patterns

### Generic Service Method
```python
from typing import TypeVar

T = TypeVar("T")

async def {{method_name}}(
    self,
    data: T,
    processor: Callable[[T], ServiceResult[U]]
) -> ServiceResult[U]:
    """Process data with type safety."""
    try:
        return processor(data)
    except Exception as e:
        return ServiceResult.fail(f"Processing failed: {str(e)}")
```

### Protocol-Based Mock
```python
from typing import Protocol
from project_watch_mcp.domain.common import ServiceResult

class {{ProtocolName}}(Protocol):
    """Protocol for {{description}}."""

    async def {{method}}(self, {{params}}) -> ServiceResult[{{Type}}]:
        ...

@pytest.fixture
def mock_{{protocol_name}}() -> {{ProtocolName}}:
    mock = MagicMock(spec={{ProtocolName}})
    mock.{{method}} = AsyncMock(
        return_value=ServiceResult.ok({{data}})
    )
    return mock
```

---

## Quick Fixes

### Fix "dict has no attribute success"
```python
# ❌ BEFORE
return_value = {"key": "value"}

# ✅ AFTER
return_value = ServiceResult.ok({"key": "value"})
```

### Fix "coroutine object has no attribute success"
```python
# ❌ BEFORE
mock.method = AsyncMock()

# ✅ AFTER
mock.method = AsyncMock(return_value=ServiceResult.ok(data))
```

### Fix "Cannot unwrap None data"
```python
# ❌ BEFORE
value = result.unwrap()

# ✅ AFTER
value = result.unwrap_or(default_value)
```

### Fix Type Mismatch
```python
# ❌ BEFORE
def process() -> ServiceResult[list[str]]:
    result: ServiceResult[dict] = get_data()
    return result  # Type error!

# ✅ AFTER
def process() -> ServiceResult[list[str]]:
    result: ServiceResult[dict] = get_data()
    if result.is_failure:
        return ServiceResult.fail(result.error)
    items = list(result.data.keys())
    return ServiceResult.ok(items)
```

---

## Usage Notes

1. **Replace placeholders** in {{double_braces}} with your actual values
2. **Import ServiceResult** from `project_watch_mcp.domain.common`
3. **Use AsyncMock** for async methods, MagicMock for sync methods
4. **Always wrap** mock return values in ServiceResult.ok() or ServiceResult.fail()
5. **Check success** before accessing result.data
6. **Use composition utilities** for complex chains instead of manual checking

---

**Quick Command Reference:**

```python
# Import
from project_watch_mcp.domain.common import ServiceResult
from project_watch_mcp.domain.common.service_result_utils import (
    compose_results,
    map_result,
    chain_results,
    collect_results,
    flatten_results,
    recover_result,
    partition_results,
)

# Create success
ServiceResult.ok(data)
ServiceResult.ok(data, metadata_key=value)

# Create failure
ServiceResult.fail("error message")
ServiceResult.fail("error", code=500)

# Check result
result.success / result.is_success
result.is_failure
result.data
result.error

# Safe unwrap
result.unwrap_or(default)
result.unwrap_or_raise()

# Composition
compose_results(func, result)  # flatMap
map_result(func, result)       # map
chain_results(*results)        # combine multiple
collect_results(results)       # list to single result
```
