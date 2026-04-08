---
name: tinybird-analytics
description: "Tinybird data pipelines, endpoints, Kafka ingestion, Python SDK, real-time analytics API"
---

# Tinybird Analytics

Real-time analytics with Tinybird: building data sources, transformation pipes, publishing API endpoints, Kafka ingestion, and the Python SDK for programmatic control.

## Core Concepts

```
Data Sources  → Raw tables (append-only or replacing)
Pipes         → SQL transformations (chain of nodes)
Endpoints     → Published pipes as HTTP APIs
Events API    → HTTP ingestion of JSON events
Kafka Sources → Streaming ingestion from Kafka topics
```

## CLI Setup and Project Structure

```bash
# Install CLI
pip install tinybird-cli

# Authenticate
tb auth --token $TINYBIRD_ADMIN_TOKEN

# Initialize project
tb init --project my-analytics

# Project layout
my-analytics/
├── datasources/
│   ├── events.datasource
│   ├── users.datasource
│   └── kafka_events.datasource
├── pipes/
│   ├── events_mv.pipe          # Materialized view
│   ├── daily_stats.pipe        # Transformation
│   └── api_events.pipe         # Published endpoint
└── .tinyenv                    # Environment config

# Deploy all resources
tb push --force

# Deploy specific file
tb push datasources/events.datasource

# Run endpoint locally
tb sql "SELECT * FROM events LIMIT 10"
```

## Data Sources

```sql
-- datasources/events.datasource
DESCRIPTION >
    Raw event stream from the product

SCHEMA >
    `event_id`    String,
    `tenant_id`   LowCardinality(String),
    `user_id`     String,
    `event_type`  LowCardinality(String),
    `properties`  String `json:$.properties`,
    `revenue`     Nullable(Float64),
    `session_id`  String,
    `timestamp`   DateTime64(3) `timeformat:auto`

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(timestamp)"
ENGINE_SORTING_KEY "tenant_id, event_type, timestamp, user_id"
ENGINE_TTL "timestamp + INTERVAL 2 YEAR"

-- datasources/users.datasource
DESCRIPTION >
    User dimension table (replacing merge tree for upserts)

SCHEMA >
    `user_id`    String,
    `tenant_id`  LowCardinality(String),
    `email`      String,
    `name`       String,
    `plan`       LowCardinality(String),
    `created_at` DateTime
    `updated_at` DateTime

ENGINE "ReplacingMergeTree"
ENGINE_SORTING_KEY "tenant_id, user_id"
ENGINE_VER "updated_at"
```

## Kafka Data Source

```sql
-- datasources/kafka_events.datasource
DESCRIPTION >
    Real-time events from Kafka

KAFKA_CONNECTION_NAME my_kafka_connection
KAFKA_TOPIC events-production
KAFKA_GROUP_ID tinybird-consumer
KAFKA_AUTO_OFFSET_RESET latest
KAFKA_BOOTSTRAP_SERVERS kafka1:9092,kafka2:9092,kafka3:9092

SCHEMA >
    `event_id`   String `json:$.event_id`,
    `tenant_id`  String `json:$.tenant_id`,
    `user_id`    String `json:$.user_id`,
    `event_type` String `json:$.event_type`,
    `payload`    String `json:$.payload`,
    `timestamp`  DateTime64(3) `json:$.timestamp` `timeformat:auto`

ENGINE MergeTree
ENGINE_PARTITION_KEY toYYYYMM(timestamp)
ENGINE_SORTING_KEY tenant_id, event_type, timestamp
```

## Pipes and Materialized Views

```sql
-- pipes/events_mv.pipe
DESCRIPTION >
    Materialized view: pre-aggregate hourly event counts

NODE hourly_agg
SQL >
    SELECT
        tenant_id,
        event_type,
        toStartOfHour(timestamp)  AS hour,
        count()                   AS event_count,
        uniqExact(user_id)        AS unique_users,
        uniqExact(session_id)     AS sessions,
        sumIf(revenue, revenue IS NOT NULL) AS revenue
    FROM events
    GROUP BY tenant_id, event_type, hour

TYPE MATERIALIZED_VIEW
DATASOURCE hourly_events_mv

-- pipes/daily_stats.pipe
DESCRIPTION >
    Daily statistics by tenant and event type

NODE daily_rollup
SQL >
    SELECT
        tenant_id,
        toDate(hour)  AS date,
        event_type,
        sum(event_count)   AS events,
        max(unique_users)  AS unique_users,
        sum(revenue)       AS revenue
    FROM hourly_events_mv
    WHERE
        tenant_id = {{String(tenant_id, 'default', description="Tenant identifier")}}
        AND date >= {{Date(start_date, '2026-01-01', description="Start date (YYYY-MM-DD)")}}
        AND date <= {{Date(end_date, '2026-12-31', description="End date (YYYY-MM-DD)")}}
    GROUP BY tenant_id, date, event_type
    ORDER BY date DESC, events DESC

-- pipes/api_events.pipe
DESCRIPTION >
    Published endpoint: real-time event analytics

NODE filter
SQL >
    SELECT *
    FROM events
    WHERE
        tenant_id = {{String(tenant_id, required=True, description="Tenant ID")}}
        AND event_type IN {{Array(event_types, 'String', description="Event types to filter")}}
        AND timestamp >= NOW() - INTERVAL {{Int32(hours, 24, description="Lookback hours")}} HOUR

NODE aggregate
SQL >
    SELECT
        event_type,
        toStartOfHour(timestamp) AS hour,
        count()            AS count,
        uniqExact(user_id) AS unique_users,
        sum(revenue)       AS total_revenue
    FROM filter
    GROUP BY event_type, hour
    ORDER BY hour DESC

TYPE ENDPOINT
```

## Python SDK

```python
import tinybird
from tinybird.client import TinybirdClient
import pandas as pd
import httpx
import json
from datetime import datetime, timedelta

# Initialize client
tb = TinybirdClient(token=os.environ["TINYBIRD_TOKEN"])

# Ingest events via Events API
def ingest_events(events: list[dict]) -> dict:
    """Ingest events to Tinybird data source."""
    ndjson = "\n".join(json.dumps(e) for e in events)
    response = httpx.post(
        "https://api.tinybird.co/v0/events",
        params={"name": "events", "wait": "true"},
        headers={"Authorization": f"Bearer {os.environ['TINYBIRD_TOKEN']}"},
        content=ndjson,
        headers={"Content-Type": "application/x-ndjson"},
    )
    response.raise_for_status()
    return response.json()

# Batch ingest from DataFrame
def ingest_dataframe(df: pd.DataFrame, datasource: str) -> dict:
    """Ingest a pandas DataFrame to Tinybird."""
    ndjson = df.to_json(orient="records", lines=True, date_format="iso")
    response = httpx.post(
        f"https://api.tinybird.co/v0/events",
        params={"name": datasource},
        headers={
            "Authorization": f"Bearer {os.environ['TINYBIRD_TOKEN']}",
            "Content-Type": "application/x-ndjson",
        },
        content=ndjson,
    )
    response.raise_for_status()
    return response.json()

# Query endpoint
def query_endpoint(
    endpoint: str,
    params: dict,
    token: str | None = None,
) -> pd.DataFrame:
    """Call a published Tinybird endpoint and return DataFrame."""
    response = httpx.get(
        f"https://api.tinybird.co/v0/pipes/{endpoint}.json",
        params=params,
        headers={"Authorization": f"Bearer {token or os.environ['TINYBIRD_TOKEN']}"},
        timeout=30.0,
    )
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data["data"])

# Example: fetch daily stats
df = query_endpoint("daily_stats", {
    "tenant_id": "acme",
    "start_date": "2026-01-01",
    "end_date": "2026-01-31",
})

# Run SQL against any datasource
def run_sql(query: str) -> pd.DataFrame:
    response = httpx.get(
        "https://api.tinybird.co/v0/sql",
        params={"q": query, "format": "JSON"},
        headers={"Authorization": f"Bearer {os.environ['TINYBIRD_TOKEN']}"},
    )
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data["data"])
```

## Real-time Dashboard Endpoint Pattern

```sql
-- pipes/realtime_dashboard.pipe
DESCRIPTION >
    Real-time analytics dashboard endpoint with multiple metrics

NODE current_window
DESCRIPTION "Events in the last N minutes"
SQL >
    SELECT
        event_type,
        count()            AS events,
        uniqExact(user_id) AS users,
        avg(
            if(has(JSONExtractKeys(properties), 'duration_ms'),
               JSONExtractInt(properties, 'duration_ms'), 0)
        )                  AS avg_duration_ms
    FROM events
    WHERE
        tenant_id = {{String(tenant_id, required=True)}}
        AND timestamp >= NOW() - INTERVAL {{Int32(minutes, 60)}} MINUTE
    GROUP BY event_type
    ORDER BY events DESC

NODE comparison_window
DESCRIPTION "Same window from previous period for comparison"
SQL >
    SELECT
        event_type,
        count()            AS events_prev,
        uniqExact(user_id) AS users_prev
    FROM events
    WHERE
        tenant_id = {{String(tenant_id, required=True)}}
        AND timestamp >= NOW() - INTERVAL {{Int32(minutes, 60) * 2}} MINUTE
        AND timestamp  < NOW() - INTERVAL {{Int32(minutes, 60)}} MINUTE
    GROUP BY event_type

NODE final
SQL >
    SELECT
        c.event_type,
        c.events,
        c.users,
        c.avg_duration_ms,
        c.events - p.events_prev                           AS events_delta,
        if(p.events_prev > 0,
           round((c.events - p.events_prev) / p.events_prev * 100, 1),
           0)                                              AS events_pct_change
    FROM current_window c
    LEFT JOIN comparison_window p USING (event_type)
    ORDER BY c.events DESC

TYPE ENDPOINT
```

## CI/CD Integration

```bash
# .github/workflows/tinybird.yml — deploy on push to main
- name: Deploy Tinybird resources
  env:
    TINYBIRD_TOKEN: ${{ secrets.TINYBIRD_ADMIN_TOKEN }}
  run: |
    pip install tinybird-cli
    cd tinybird/
    tb auth --token $TINYBIRD_TOKEN
    tb push --force --yes
    # Run regression tests
    tb test run

# tb test in .tinybird/tests/
# Checks that endpoints return expected shape and values
```

## Best Practices

- Use `LowCardinality(String)` for columns with < 10,000 distinct values (tenant_id, event_type, plan)
- Design sorting keys to match your most common `WHERE` and `GROUP BY` — this is the primary index
- Use materialized views for pre-aggregation — queries on MVs can be 100x faster than raw event tables
- Ingest via the Events API with `wait=true` for synchronous confirmation; omit for higher throughput
- Use `ReplacingMergeTree` data sources for dimension tables that need upsert semantics
- Create separate read tokens per tenant with row-level security using `tenant_id` JWT claims
- Use `ENDPOINT` type pipes with typed parameters — they provide automatic documentation and validation
- Test endpoints with `tb test` before deploying to production — validate schema and value ranges
- Monitor quarantined data: `SELECT * FROM events_quarantine` to catch ingestion schema mismatches
- Use `toStartOfHour` / `toStartOfDay` in materialized views to enable efficient time-range queries

## Models to Use

- **Default**: `claude-sonnet-4-5` — SQL pipes, data source definitions, Python ingestion
- **Analytics architecture**: `claude-opus-4-5` — complex multi-step pipes, real-time dashboard design, schema optimization
- **Quick snippets**: `claude-haiku-3-5` — simple SQL aggregations, endpoint parameters, ingestion scripts
