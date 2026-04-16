# Logfire Configuration Reference

Complete reference for `logfire.configure()` options.

## Basic Configuration

```python
import logfire

logfire.configure(
    service_name="my-api",           # Required: identifies your service
    service_version="1.0.0",          # Semantic version
    environment="production",         # dev/staging/production
    send_to_logfire=True,             # Send to Logfire platform
    token="your-project-token",       # Auth token (or use env var)
    console=True,                     # Print to console
    min_level="info",                 # Minimum log level
)
```

## Log Levels

Logfire provides 7 log levels (lowest to highest severity):

| Level | Method | Numeric | Use Case |
|-------|--------|---------|----------|
| `trace` | `logfire.trace()` | 1 | Detailed debugging, step-by-step |
| `debug` | `logfire.debug()` | 5 | Development debugging |
| `info` | `logfire.info()` | 9 | Normal operations (default) |
| `notice` | `logfire.notice()` | 10 | Important events |
| `warn` | `logfire.warn()` | 13 | Potential issues |
| `error` | `logfire.error()` | 17 | Errors that don't stop execution |
| `fatal` | `logfire.fatal()` | 21 | Critical failures |

```python
# All log levels
logfire.trace("Step 1 of algorithm", step=1)
logfire.debug("Variable state", data=locals())
logfire.info("User logged in", user_id=123)
logfire.notice("Cache invalidated", reason="manual")
logfire.warn("Rate limit approaching", current=95, limit=100)
logfire.error("API call failed", status=500, retry=True)
logfire.fatal("Database connection lost", host="db.example.com")

# Dynamic log level
logfire.log("warn", "Dynamic level message")

# Exception logging (shortcut for error + traceback)
try:
    risky_operation()
except Exception:
    logfire.exception("Operation failed")  # Includes full traceback
```

### f-string Magic (Python 3.11+)

```python
user_id = 123
status = "active"

# Automatically extracts variable names
logfire.info(f"User {user_id} status: {status}")
# Equivalent to:
logfire.info("User {user_id} status: {status}", user_id=123, status="active")
```

## Environment Variables

Set these instead of passing to `configure()`:

```bash
export LOGFIRE_SERVICE_NAME=my-api
export LOGFIRE_SERVICE_VERSION=1.0.0
export LOGFIRE_ENVIRONMENT=production
export LOGFIRE_TOKEN=your-project-token
```

## Configuration Parameters

### Service Metadata

| Parameter | Type | Description |
|-----------|------|-------------|
| `service_name` | `str` | Service identifier (shown as colored bubble in UI) |
| `service_version` | `str` | Semantic version (shown in tooltip on hover) |
| `environment` | `str` | Deployment environment |

### Output Control

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `send_to_logfire` | `bool` | `True` | Send telemetry to Logfire platform |
| `console` | `bool\|dict` | `True` | Enable console output |
| `min_level` | `str` | `"info"` | Minimum log level: trace, debug, info, warn, error, fatal |

### Authentication

| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | `str` | Write token for Logfire project |

## Console Options

```python
# Disable console completely
logfire.configure(console=False)

# Custom console settings
logfire.configure(
    console={
        "colors": True,
        "include_timestamps": True,
        "verbose": False,
    }
)
```

## Scrubbing Options

```python
from logfire import ScrubbingOptions

logfire.configure(
    scrubbing=ScrubbingOptions(
        # Add custom patterns (combined with defaults)
        extra_patterns=["my_secret_pattern", "api_key"],
        
        # Custom callback for fine-grained control
        callback=my_scrubbing_callback,
    )
)
```

Default patterns automatically scrub: `password`, `secret`, `token`, `key`, `auth`, `credential`, `credit_card`, `ssn`.

## Sampling Options

```python
from logfire import SamplingOptions

# Simple ratio sampling
logfire.configure(sampling=SamplingOptions(head=0.5))  # 50%

# Custom sampler
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, ParentBased

logfire.configure(
    sampling=SamplingOptions(
        head=ParentBased(TraceIdRatioBased(0.1))  # 10% with parent context
    )
)
```

## Metrics Options

```python
from logfire import MetricsOptions

# Enable metrics collection within spans
logfire.configure(
    metrics=MetricsOptions(collect_in_spans=True)
)

# Disable metrics entirely
logfire.configure(metrics=False)
```

## Advanced Options

```python
from logfire import AdvancedOptions
from logfire.testing import TestExporter

exporter = TestExporter()

logfire.configure(
    advanced=AdvancedOptions(
        additional_span_processors=[exporter],
    )
)
```

## Testing Configuration

When running under pytest, Logfire automatically sets `send_to_logfire=False`.

```python
# Explicit test mode
logfire.configure(
    send_to_logfire=False,
    console=True,  # See output during tests
)
```

## Multiple Configurations

For microservices or multi-tenant apps:

```python
import logfire

# Primary configuration
logfire.configure(service_name="main-api")

# Create isolated instance
tenant_logfire = logfire.Logfire(
    service_name="tenant-service",
    environment="production",
)
tenant_logfire.info("Tenant-specific log")
```

## OTLP Export (Vendor-Neutral)

For OpenTelemetry-compatible backends:

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource(attributes={"service.name": "my-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))

exporter = OTLPSpanExporter(endpoint="https://your-otlp-backend/v1/traces")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("operation"):
    pass
```
