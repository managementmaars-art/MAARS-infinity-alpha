# Logfire Metrics Reference

Complete guide to creating and using custom metrics with Logfire.

## Metric Types

Logfire supports three metric types aligned with OpenTelemetry:

| Type | Description | Use Case |
|------|-------------|----------|
| **Counter** | Monotonically increasing value | Request counts, errors, events |
| **Gauge** | Current value that can go up/down | Temperature, queue size, active users |
| **Histogram** | Distribution of values | Latency, request size, response times |

## Counter

Tracks cumulative values that only increase (or reset on restart).

```python
import logfire

logfire.configure()

# Create counter
request_counter = logfire.metric_counter(
    "http.requests.total",
    unit="1",
    description="Total HTTP requests received"
)

# Increment by 1
request_counter.add(1)

# Increment with attributes (labels)
request_counter.add(1, {
    "endpoint": "/api/users",
    "method": "GET",
    "status_code": 200
})

# Increment by custom amount
request_counter.add(5, {"batch": "true"})
```

### Counter Examples

```python
# Exception counter
exception_counter = logfire.metric_counter(
    "exceptions.caught",
    unit="1",
    description="Number of exceptions caught"
)

try:
    risky_operation()
except Exception as e:
    exception_counter.add(1, {"exception_type": type(e).__name__})
    logfire.exception("Operation failed")

# Message counter
messages_sent = logfire.metric_counter("messages.sent", unit="1")

def send_message(channel: str):
    # ... send message
    messages_sent.add(1, {"channel": channel})
```

## Gauge

Tracks current value that can increase or decrease.

```python
import logfire

logfire.configure()

# Create gauge
temperature = logfire.metric_gauge(
    "temperature",
    unit="°C",
    description="Current temperature reading"
)

# Set current value
temperature.set(23.5)

# Set with attributes
temperature.set(25.0, {"location": "server_room", "sensor": "A1"})

# Update over time
def update_temperature(value: float, location: str):
    temperature.set(value, {"location": location})
```

### Gauge Examples

```python
# Active connections
active_connections = logfire.metric_gauge(
    "connections.active",
    unit="1",
    description="Current active connections"
)

def on_connect(client_id: str):
    # Logic to get current count
    current = get_connection_count()
    active_connections.set(current)

# Queue size
queue_size = logfire.metric_gauge("queue.size", unit="1")

def process_queue():
    while True:
        queue_size.set(len(pending_items))
        item = pending_items.pop()
        process(item)

# Memory usage
memory_usage = logfire.metric_gauge("memory.used", unit="bytes")

def report_memory():
    import psutil
    memory_usage.set(psutil.Process().memory_info().rss)
```

## Histogram

Tracks distribution of values for statistical analysis.

```python
import logfire
import time

logfire.configure()

# Create histogram
latency = logfire.metric_histogram(
    "http.request.duration",
    unit="ms",
    description="HTTP request latency distribution"
)

# Record a value
latency.record(45.2)

# Record with attributes
latency.record(123.5, {
    "endpoint": "/api/users",
    "method": "GET"
})

# Timing pattern
def timed_operation():
    start = time.time()
    try:
        perform_work()
    finally:
        duration_ms = (time.time() - start) * 1000
        latency.record(duration_ms)
```

### Histogram Examples

```python
# Response size
response_size = logfire.metric_histogram(
    "http.response.size",
    unit="bytes",
    description="HTTP response body size"
)

def send_response(data: bytes):
    response_size.record(len(data))
    return data

# Database query time
query_duration = logfire.metric_histogram(
    "db.query.duration",
    unit="ms",
    description="Database query execution time"
)

async def execute_query(sql: str):
    start = time.time()
    result = await db.execute(sql)
    query_duration.record(
        (time.time() - start) * 1000,
        {"table": extract_table_name(sql)}
    )
    return result

# File processing
file_size = logfire.metric_histogram("file.processed.size", unit="bytes")

def process_file(path: str):
    size = os.path.getsize(path)
    file_size.record(size, {"extension": path.split(".")[-1]})
    # ... process file
```

## System Metrics

Automatically collect system-level metrics:

```python
import logfire

logfire.configure()

# Collect all system metrics
logfire.instrument_system_metrics()

# Selective collection
logfire.instrument_system_metrics(
    metrics={"system.cpu.utilization": None},
    base=None  # Only collect explicitly specified
)

# Collect with exclusions
logfire.instrument_system_metrics(
    metrics={"system.disk.operations": ["read"]},  # Only reads
    base="full"  # Start with all metrics
)
```

### Available System Metrics

| Metric | Description |
|--------|-------------|
| `system.cpu.utilization` | CPU usage percentage |
| `system.memory.usage` | Memory usage |
| `system.memory.utilization` | Memory usage percentage |
| `system.disk.io` | Disk I/O bytes |
| `system.disk.operations` | Disk operations count |
| `system.network.io` | Network I/O bytes |
| `process.cpu.utilization` | Process CPU usage |
| `process.memory.usage` | Process memory usage |

## Metrics in Spans

Aggregate metrics within span context:

```python
import logfire
from pydantic_ai import Agent

# Enable metrics collection in spans
logfire.configure(
    metrics=logfire.MetricsOptions(collect_in_spans=True)
)
logfire.instrument_pydantic_ai()

agent = Agent("gpt-4o")

# Token usage aggregated in parent span
with logfire.span("batch_processing"):
    agent.run_sync("Question 1")
    agent.run_sync("Question 2")
    agent.run_sync("Question 3")
    # Parent span shows total tokens/costs
```

## Disable Metrics

```python
# Disable all metrics
logfire.configure(metrics=False)

# Keep traces, disable only aggregate metrics from integrations
logfire.configure(
    metrics=logfire.MetricsOptions(
        include_metrics=False
    )
)
```

## Best Practices

### Naming Conventions

```python
# Good: hierarchical, lowercase, dots as separators
logfire.metric_counter("http.requests.total")
logfire.metric_histogram("db.query.duration")
logfire.metric_gauge("cache.size.bytes")

# Bad: inconsistent, unclear
logfire.metric_counter("RequestCount")
logfire.metric_histogram("time")
```

### Cardinality Control

```python
# Good: bounded attribute values
request_counter.add(1, {
    "method": "GET",           # Limited set
    "status_class": "2xx",     # Grouped status codes
    "endpoint_pattern": "/api/users/{id}"  # Pattern, not actual ID
})

# Bad: unbounded attribute values (causes storage explosion)
request_counter.add(1, {
    "user_id": user_id,        # Unique per user
    "request_id": request_id,  # Unique per request
    "full_path": "/api/users/12345"  # Contains variable data
})
```

### Units

Use standard units:

| Unit | Description |
|------|-------------|
| `1` | Dimensionless count |
| `ms` | Milliseconds |
| `s` | Seconds |
| `bytes` | Bytes |
| `%` | Percentage (0-100) |
| `°C` | Celsius |
