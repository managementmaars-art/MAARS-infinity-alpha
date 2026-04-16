# Logfire Pitfalls & Troubleshooting

Common issues and their solutions.

## Configuration Issues

### Missing Service Name

**Symptom**: Spans appear as "unknown_service" in UI, hard to filter.

**Fix**:
```python
# Always set service_name
logfire.configure(service_name="my-api")
```

### Late Instrumentation

**Symptom**: No spans captured for some requests.

**Cause**: Clients/apps created before `configure()` is called.

**Fix**:
```python
import logfire

# 1. Configure FIRST
logfire.configure(service_name="backend")

# 2. Instrument SECOND
logfire.instrument_fastapi()
logfire.instrument_httpx()

# 3. Create clients/apps THIRD
from fastapi import FastAPI
app = FastAPI()
```

### Console Noise in Production

**Symptom**: Stdout polluted with trace output.

**Fix**:
```python
logfire.configure(
    console=False,  # Disable console in production
    send_to_logfire=True,
)
```

## Performance Issues

### High-Cardinality Attributes

**Symptom**: Storage costs explode, slow queries.

**Cause**: Using unbounded values as attributes.

**Bad**:
```python
logfire.info("Request", body=full_request_body)  # Huge, unique
logfire.info("User", email=user_email)            # High cardinality
```

**Good**:
```python
logfire.info("Request", request_id=request_id, size_bytes=len(body))
logfire.info("User", user_id=user_id)  # Use IDs, not raw values
```

### Too Many Spans

**Symptom**: High costs, slow UI, drowning in data.

**Fixes**:
```python
# 1. Enable sampling
logfire.configure(sampling=logfire.SamplingOptions(head=0.1))

# 2. Suppress noisy operations
with logfire.suppress_instrumentation():
    frequent_healthcheck()

# 3. Suppress entire scopes
logfire.suppress_scopes("noisy.library.scope")

# 4. Disable metrics if not needed
logfire.configure(metrics=False)
```

### Memory Growth

**Symptom**: Application memory grows over time.

**Cause**: Unbounded span processors or exporters.

**Fix**:
```python
# Use batch processors (default) with limits
from opentelemetry.sdk.trace.export import BatchSpanProcessor

processor = BatchSpanProcessor(
    exporter,
    max_queue_size=2048,
    max_export_batch_size=512,
)
```

## Tracing Issues

### Missing Child Spans

**Symptom**: Parent span exists but children are missing.

**Cause**: Child operations happen in different thread/context.

**Fix**:
```python
from opentelemetry import trace, context

# Capture current context
current_context = context.get_current()

def background_task():
    # Restore context in new thread
    token = context.attach(current_context)
    try:
        with logfire.span("child_operation"):
            pass
    finally:
        context.detach(token)
```

### Spans Not Appearing

**Symptom**: `logfire.span()` calls produce no output.

**Causes & Fixes**:
1. Not configured: Call `logfire.configure()` first
2. Sampled out: Check sampling settings
3. Suppressed: Check for `suppress_instrumentation()` context
4. Not flushed: Add explicit flush on shutdown

```python
import atexit
from opentelemetry import trace

atexit.register(lambda: trace.get_tracer_provider().force_flush())
```

### Broken Trace Context

**Symptom**: Traces don't connect across services.

**Cause**: Headers not propagated.

**Fix**: Ensure instrumented HTTP clients propagate context:
```python
logfire.instrument_httpx()  # Handles propagation automatically
```

## Scrubbing Issues

### Sensitive Data Leaking

**Symptom**: PII visible in logs.

**Fix**:
```python
logfire.configure(
    scrubbing=logfire.ScrubbingOptions(
        extra_patterns=["email", "phone", "address", "ssn"]
    )
)
```

### Over-Scrubbing

**Symptom**: Non-sensitive data being redacted.

**Fix**:
```python
def scrubbing_callback(match: logfire.ScrubMatch):
    # Whitelist safe fields
    safe_fields = ["password_changed", "reset_password_requested"]
    if any(f in str(match.path) for f in safe_fields):
        return match.value
    return None

logfire.configure(
    scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback)
)
```

## Testing Issues

### Tests Sending Real Data

**Symptom**: Test runs appear in production Logfire.

**Fix**: Logfire auto-disables under pytest, but verify:
```python
logfire.configure(send_to_logfire=False)
```

### Flaky Span Assertions

**Symptom**: Tests randomly fail on span counts.

**Cause**: Background instrumentation creating extra spans.

**Fix**:
```python
def test_specific_operation(capfire: CaptureLogfire):
    capfire.exporter.clear()  # Clear any setup spans
    
    my_operation()
    
    # Filter for specific spans
    my_spans = [s for s in capfire.exporter.exported_spans 
                if "my_operation" in s.name]
    assert len(my_spans) == 1
```

## Integration-Specific Issues

### FastAPI 422 Validation Errors Not Logged

**Symptom**: Pydantic validation failures don't appear.

**Fix**: Use `instrument_fastapi(app)` not just `instrument_fastapi()`:
```python
logfire.instrument_fastapi(app)  # Pass the app instance
```

### SQLAlchemy Queries Not Traced

**Symptom**: Database queries missing from traces.

**Fix**: Instrument the specific engine:
```python
engine = create_engine(url)
logfire.instrument_sqlalchemy(engine=engine)  # Pass engine explicitly
```

### Async Code Not Traced

**Symptom**: Async operations missing from traces.

**Cause**: Context not propagated across async boundaries.

**Fix**: Use async-aware instrumentation:
```python
logfire.instrument_httpx()  # Supports AsyncClient
logfire.instrument_asyncpg()  # Async PostgreSQL
```

## Debug Checklist

When spans aren't appearing:

1. **Check configuration**: `logfire.configure()` called?
2. **Check ordering**: Configure → Instrument → Create clients
3. **Check sampling**: Is `sampling` set too aggressively?
4. **Check suppression**: Inside `suppress_instrumentation()` context?
5. **Check min_level**: Is `min_level` higher than your log level?
6. **Check console**: Is `console=True` for debugging?
7. **Force flush**: Add explicit flush to ensure spans export

```python
# Debug configuration
logfire.configure(
    service_name="debug-service",
    console=True,
    min_level="trace",
    send_to_logfire=True,
)

# Debug logging
logfire.debug("Configuration complete")
```
