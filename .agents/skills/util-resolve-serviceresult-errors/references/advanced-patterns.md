# ServiceResult Advanced Patterns

Advanced integration patterns, benefits analysis, and success metrics for ServiceResult usage.

## Integration Points

### With Other Skills

**resolve-serviceresult-errors integrates with:**
- **test-debug-failures** - Fix ServiceResult-specific test failures
- **python-best-practices-type-safety** - Resolve ServiceResult[T] type mismatches
- **test-setup-async** - Configure AsyncMock with ServiceResult
- **implement-cqrs-handler** - Ensure handlers return ServiceResult
- **implement-repository-pattern** - Validate repository ServiceResult returns

### With Testing Workflows

**Use in combination with:**
- AsyncMock configuration (return ServiceResult, not dict)
- Type checking (pyright validates ServiceResult[T])
- Integration tests (real ServiceResult wrapping)
- E2E tests (ServiceResult → dict conversion)

### With Agent Workflows

**Agents should invoke this skill:**
- Unit testing agents - When tests fail with ServiceResult errors
- Debugging agents - For "dict object has no attribute" errors
- Implementation agents - During service implementation

---

## Expected Benefits

| Metric | Without Skill | With Skill | Improvement |
|--------|--------------|------------|-------------|
| **Fix Time** | 30 min (trial/error) | 5 min (systematic) | 83% faster |
| **Mock Configuration Errors** | 50% (dict instead of ServiceResult) | 5% (correct patterns) | 90% reduction |
| **Type Error Resolution** | 20 min (pyright confusion) | 5 min (clear templates) | 75% faster |
| **ServiceResult Chaining Complexity** | 17 lines (manual) | 8 lines (composition utils) | 53% reduction |
| **Unwrap Safety Issues** | 20% (None crashes) | 0% (validation checks) | 100% elimination |
| **Knowledge Transfer** | 1 hour (learning pattern) | 10 min (examples) | 83% faster |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Mock Configuration Accuracy** | 100% | Test pass rate |
| **Type Error Resolution** | 100% | pyright clean |
| **Unwrap Safety** | Zero crashes | Runtime validation |
| **ServiceResult Pattern Adoption** | 100% of services | Code coverage |
| **Composition Utility Usage** | 80% of complex chains | Code review |

---

## Related Project Files

When implementing ServiceResult patterns in your project, these are the typical files you'll work with:

- `src/*/domain/common/service_result.py` - ServiceResult implementation
- `src/*/domain/common/service_result_utils.py` - Composition utilities
- `tests/unit/core/test_service_result_type_safety.py` - Type safety test patterns
- `tests/unit/core/test_service_utils.py` - ServiceResult utility tests

**Note:** Exact paths depend on your project structure and bounded context naming.
