# Logfire Advanced Patterns

Sampling, scrubbing, suppression, testing, and custom configurations.

## Sampling Strategies

### Simple Ratio Sampling

```python
import logfire

# Sample 50% of traces randomly
logfire.configure(sampling=logfire.SamplingOptions(head=0.5))

# Sample 10% of traces
logfire.configure(sampling=logfire.SamplingOptions(head=0.1))
```

### Custom Sampler

```python
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_OFF,
    ALWAYS_ON,
    ParentBased,
    Sampler,
    TraceIdRatioBased,
)
import logfire


class MySampler(Sampler):
    def should_sample(self, parent_context, trace_id, name, *args, **kwargs):
        if name == "healthcheck":
            sampler = ALWAYS_OFF  # Never sample healthchecks
        elif name.startswith("internal/"):
            sampler = TraceIdRatioBased(0.01)  # 1% for internal
        elif name.startswith("api/"):
            sampler = TraceIdRatioBased(0.5)  # 50% for API
        else:
            sampler = ALWAYS_ON  # Sample everything else
        
        return sampler.should_sample(parent_context, trace_id, name, *args, **kwargs)

    def get_description(self):
        return "MySampler"


logfire.configure(
    sampling=logfire.SamplingOptions(
        head=ParentBased(MySampler())  # Respect parent sampling decisions
    )
)
```

### Disable Metrics

```python
# Reduce volume by disabling aggregate metrics
logfire.configure(metrics=False)
```

## Sensitive Data Scrubbing

### Default Scrubbing

Logfire automatically scrubs common patterns: `password`, `secret`, `token`, `key`, `auth`, `credential`, `credit_card`, `ssn`.

### Add Custom Patterns

```python
import logfire

logfire.configure(
    scrubbing=logfire.ScrubbingOptions(
        extra_patterns=["api_key", "private_key", "my_secret"]
    )
)

# These will be scrubbed
logfire.info("Request", data={
    "api_key": "sk-12345",  # → [REDACTED]
    "user": "alice",        # Kept
})
```

### Custom Scrubbing Callback

```python
import logfire

def scrubbing_callback(match: logfire.ScrubMatch):
    # Don't scrub known safe fields
    if match.path == ("attributes", "password_reset_requested"):
        return match.value  # Return original value
    
    # Custom redaction format
    if "email" in str(match.path):
        return "[EMAIL REDACTED]"
    
    return None  # Use default scrubbing

logfire.configure(
    scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback)
)
```

### OTel Collector Scrubbing

For server-side scrubbing:

```yaml
processors:
  attributes:
    actions:
      - key: session_id
        action: update
        value: "SCRUBBED"
      - pattern: "password"
        action: delete
  
  redaction:
    allow_all_keys: true
    blocked_values:
      - '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'  # Emails

pipelines:
  traces:
    processors: [attributes, redaction]
```

## Suppression

### Suppress by Scope

Suppress all spans/metrics from a specific OpenTelemetry scope:

```python
import logfire

logfire.configure()

# Suppress noisy BigQuery auto-instrumentation
logfire.suppress_scopes("google.cloud.bigquery.opentelemetry_tracing")

# Suppress multiple scopes
logfire.suppress_scopes(
    "google.cloud.bigquery.opentelemetry_tracing",
    "some.other.noisy.scope",
)
```

### Suppress Code Block

Suppress instrumentation for specific code:

```python
import logfire
import httpx

logfire.configure()
logfire.instrument_httpx()

client = httpx.Client()

# This request IS traced
client.get("https://api.example.com/users")

# This request is NOT traced
with logfire.suppress_instrumentation():
    client.get("https://internal-healthcheck.local")
    client.get("https://another-internal-service.local")

# Tracing resumes here
client.get("https://api.example.com/orders")
```

Use cases:
- Health check endpoints
- Internal service calls
- High-frequency polling
- Debug/test requests

## Testing

### Pytest Fixture

```python
import logfire
from logfire.testing import CaptureLogfire


def test_order_processing(capfire: CaptureLogfire):
    process_order("ORD-123")
    
    spans = capfire.exporter.exported_spans
    
    # Verify span was created
    assert len(spans) >= 1
    
    # Verify span attributes
    order_span = next(s for s in spans if "order" in s.name.lower())
    assert order_span.attributes["order_id"] == "ORD-123"
    
    # Clean up
    capfire.exporter.clear()


def test_multiple_operations(capfire: CaptureLogfire):
    logfire.info("First operation")
    assert len(capfire.exporter.exported_spans) == 1
    
    logfire.info("Second operation")
    assert len(capfire.exporter.exported_spans) == 2
    
    capfire.exporter.clear()
    assert len(capfire.exporter.exported_spans) == 0
```

### Manual Test Setup

```python
import logfire
from logfire.testing import TestExporter

def setup_test_logfire():
    exporter = TestExporter()
    logfire.configure(
        send_to_logfire=False,
        advanced=logfire.AdvancedOptions(
            additional_span_processors=[exporter]
        )
    )
    return exporter

# In tests
exporter = setup_test_logfire()
my_function()
assert len(exporter.exported_spans) == 1
```

### Automatic Test Mode

Logfire automatically sets `send_to_logfire=False` when running under pytest.

## LLM Cost Tracking

```python
import logfire
from pydantic_ai import Agent

# Enable metrics collection within spans
logfire.configure(metrics=logfire.MetricsOptions(collect_in_spans=True))
logfire.instrument_pydantic_ai()

agent = Agent("gpt-4o")

with logfire.span("batch_processing"):
    # Token usage and costs are aggregated in parent span
    agent.run_sync("Question 1")
    agent.run_sync("Question 2")
    agent.run_sync("Question 3")
```

## Distributed Tracing

### Multi-Service Setup

Service A (API):

```python
import logfire

logfire.configure(service_name="api-gateway")
logfire.instrument_fastapi()
logfire.instrument_httpx()
```

Service B (Backend):

```python
import logfire

logfire.configure(service_name="order-service")
logfire.instrument_fastapi()
logfire.instrument_sqlalchemy()
```

Trace context propagates automatically via HTTP headers.

### Manual Context Propagation

```python
from opentelemetry import trace
from opentelemetry.propagate import inject, extract

# Inject context into headers
headers = {}
inject(headers)
# headers now contains: {"traceparent": "00-..."}

# Extract context from headers
context = extract(incoming_headers)
with trace.get_tracer(__name__).start_as_current_span("child", context=context):
    pass
```

## Custom Span Processors

```python
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.sdk.trace.export import ReadableSpan
import logfire


class MyProcessor(SpanProcessor):
    def on_start(self, span, parent_context):
        # Add custom attribute to all spans
        span.set_attribute("custom.processor", "active")
    
    def on_end(self, span: ReadableSpan):
        if span.status.is_ok:
            print(f"Span {span.name} completed successfully")
    
    def shutdown(self):
        pass
    
    def force_flush(self, timeout_millis=30000):
        return True


logfire.configure(
    advanced=logfire.AdvancedOptions(
        additional_span_processors=[MyProcessor()]
    )
)
```

## Baggage Propagation

```python
from opentelemetry import baggage
from opentelemetry.context import attach, detach

# Set baggage (propagates across services)
ctx = baggage.set_baggage("tenant_id", "acme-corp")
token = attach(ctx)

try:
    # All spans in this context have access to tenant_id
    with logfire.span("tenant_operation"):
        tenant = baggage.get_baggage("tenant_id")
        logfire.info("Processing for tenant", tenant_id=tenant)
finally:
    detach(token)
```
