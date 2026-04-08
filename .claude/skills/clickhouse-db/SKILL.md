---
name: clickhouse-db
description: ClickHouse SQL, aggregating merge trees, materialized views, Python client, time series analytics
---

# ClickHouse Database

Production ClickHouse usage: table design with MergeTree family, materialized views for pre-aggregation, the Python `clickhouse-connect` client, and time-series analytics patterns.

## Python Client Setup

```python
import clickhouse_connect
from clickhouse_connect.driver.client import Client
import os

# Connection with connection pooling
client: Client = clickhouse_connect.get_client(
    host=os.environ["CH_HOST"],
    port=int(os.environ.get("CH_PORT", "8443")),
    username=os.environ["CH_USER"],
    password=os.environ["CH_PASSWORD"],
    database=os.environ.get("CH_DATABASE", "default"),
    secure=True,
    verify=True,
    compress=True,
    query_retries=2,
    connect_timeout=10,
    send_receive_timeout=300,
)

# Test connection
result = client.command("SELECT version()")
print(f"Connected to ClickHouse {result}")
```

## Table Design: MergeTree Variants

```sql
-- Events table: ReplicatedMergeTree for HA, partitioned by date
CREATE TABLE IF NOT EXISTS events
(
    event_id     UUID            DEFAULT generateUUIDv4(),
    tenant_id    LowCardinality(String),
    event_type   LowCardinality(String),
    user_id      String,
    session_id   String,
    properties   Map(String, String),
    revenue      Nullable(Decimal64(2)),
    duration_ms  UInt32,
    created_at   DateTime64(3, 'UTC') DEFAULT now64(),
    date         Date MATERIALIZED toDate(created_at)
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events', '{replica}')
PARTITION BY toYYYYMM(date)
ORDER BY (tenant_id, event_type, created_at, user_id)
TTL created_at + INTERVAL 2 YEAR DELETE
SETTINGS
    index_granularity = 8192,
    merge_with_ttl_timeout = 86400;

-- Aggregating MergeTree for pre-aggregated summaries
CREATE TABLE IF NOT EXISTS daily_revenue_agg
(
    tenant_id    LowCardinality(String),
    product_id   String,
    date         Date,
    revenue      AggregateFunction(sum, Decimal64(2)),
    order_count  AggregateFunction(count, UInt64),
    unique_users AggregateFunction(uniqHLL12, String)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (tenant_id, product_id, date);

-- SummingMergeTree for simple counters
CREATE TABLE IF NOT EXISTS page_views
(
    tenant_id LowCardinality(String),
    page      String,
    date      Date,
    views     UInt64,
    uniq      UInt64
)
ENGINE = SummingMergeTree((views, uniq))
PARTITION BY toYYYYMM(date)
ORDER BY (tenant_id, page, date);
```

## Materialized Views

```sql
-- Materialized view feeding into AggregatingMergeTree
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_revenue
TO daily_revenue_agg
AS
SELECT
    tenant_id,
    JSONExtractString(properties, 'product_id') AS product_id,
    toDate(created_at)                          AS date,
    sumState(revenue)                           AS revenue,
    countState()                                AS order_count,
    uniqHLL12State(user_id)                     AS unique_users
FROM events
WHERE event_type = 'purchase' AND revenue IS NOT NULL
GROUP BY tenant_id, product_id, date;

-- Query the materialized view with Merge functions
SELECT
    product_id,
    date,
    sumMerge(revenue)          AS total_revenue,
    countMerge(order_count)    AS orders,
    uniqHLL12Merge(unique_users) AS unique_buyers
FROM daily_revenue_agg
WHERE tenant_id = 'acme' AND date >= today() - 30
GROUP BY product_id, date
ORDER BY date DESC, total_revenue DESC
LIMIT 100;

-- Chained materialized view for hourly -> daily rollups
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hourly_events
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMMDD(hour)
ORDER BY (tenant_id, event_type, hour)
AS
SELECT
    tenant_id,
    event_type,
    toStartOfHour(created_at) AS hour,
    count()                   AS event_count,
    uniqExact(user_id)        AS unique_users,
    sum(duration_ms)          AS total_duration_ms
FROM events
GROUP BY tenant_id, event_type, hour;
```

## Time Series Analytics

```sql
-- Retention analysis with arrays
WITH
    cohort AS (
        SELECT user_id, toDate(min(created_at)) AS cohort_date
        FROM events
        WHERE event_type = 'signup'
        GROUP BY user_id
    ),
    activity AS (
        SELECT user_id, toDate(created_at) AS activity_date
        FROM events
        GROUP BY user_id, activity_date
    )
SELECT
    cohort_date,
    count(DISTINCT c.user_id)                                                          AS cohort_size,
    countIf(DISTINCT c.user_id, dateDiff('day', c.cohort_date, a.activity_date) = 7)  AS day7_retained,
    countIf(DISTINCT c.user_id, dateDiff('day', c.cohort_date, a.activity_date) = 30) AS day30_retained
FROM cohort c
JOIN activity a USING (user_id)
WHERE c.cohort_date >= today() - 90
GROUP BY cohort_date
ORDER BY cohort_date;

-- Funnel analysis
SELECT
    countIf(step >= 1) AS step1_signup,
    countIf(step >= 2) AS step2_onboarded,
    countIf(step >= 3) AS step3_first_purchase,
    countIf(step >= 4) AS step4_repeat_purchase,
    round(countIf(step >= 2) / countIf(step >= 1) * 100, 2) AS signup_to_onboard_pct
FROM (
    SELECT
        user_id,
        windowFunnel(7 * 86400)(
            created_at,
            event_type = 'signup',
            event_type = 'onboarding_complete',
            event_type = 'first_purchase',
            event_type = 'second_purchase'
        ) AS step
    FROM events
    WHERE created_at >= now() - INTERVAL 30 DAY
    GROUP BY user_id
);

-- Moving average with window functions
SELECT
    date,
    revenue,
    avg(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS revenue_7d_avg,
    sum(revenue) OVER (PARTITION BY toYYYYMM(date) ORDER BY date) AS revenue_mtd
FROM (
    SELECT date, sumMerge(revenue) AS revenue
    FROM daily_revenue_agg
    WHERE tenant_id = 'acme' AND date >= today() - 90
    GROUP BY date
)
ORDER BY date;
```

## Python Bulk Insert Pattern

```python
import pandas as pd
from datetime import datetime
from typing import Any

def insert_events(events: list[dict[str, Any]], batch_size: int = 10_000) -> int:
    """Bulk insert events with batching."""
    if not events:
        return 0

    # Prepare data in columnar format for efficiency
    df = pd.DataFrame(events)
    df["created_at"] = pd.to_datetime(df["created_at"])

    total_inserted = 0
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i + batch_size]
        client.insert_df(
            table="events",
            df=batch,
            database="analytics",
            column_names=list(batch.columns),
            settings={"async_insert": 1, "wait_for_async_insert": 0},
        )
        total_inserted += len(batch)

    return total_inserted

def query_to_df(sql: str, parameters: dict | None = None) -> pd.DataFrame:
    """Execute a query and return as DataFrame."""
    result = client.query(
        sql,
        parameters=parameters,
        settings={"max_execution_time": 60, "max_memory_usage": 4_000_000_000},
    )
    return pd.DataFrame(result.result_rows, columns=result.column_names)

# Example usage
df = query_to_df("""
    SELECT
        event_type,
        toStartOfHour(created_at) AS hour,
        count()                   AS events,
        uniqExact(user_id)        AS users
    FROM events
    WHERE tenant_id = {tenant_id:String}
      AND created_at >= {start:DateTime}
      AND created_at < {end:DateTime}
    GROUP BY event_type, hour
    ORDER BY hour, events DESC
""", parameters={
    "tenant_id": "acme",
    "start": datetime(2026, 1, 1),
    "end": datetime(2026, 2, 1),
})
```

## Schema Migration Pattern

```python
MIGRATIONS = [
    {
        "version": 1,
        "description": "Create events table",
        "up": """
            CREATE TABLE IF NOT EXISTS events (...)
            ENGINE = MergeTree()
            PARTITION BY toYYYYMM(date)
            ORDER BY (tenant_id, created_at);
        """,
    },
    {
        "version": 2,
        "description": "Add revenue column",
        "up": "ALTER TABLE events ADD COLUMN IF NOT EXISTS revenue Nullable(Decimal64(2)) AFTER duration_ms",
    },
    {
        "version": 3,
        "description": "Add covering index for user queries",
        "up": """
            ALTER TABLE events
            ADD INDEX idx_user_id (user_id) TYPE bloom_filter(0.01) GRANULARITY 4
        """,
    },
]

def run_migrations(client: Client):
    client.command("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version UInt32,
            applied_at DateTime DEFAULT now()
        ) ENGINE = ReplacingMergeTree(applied_at)
        ORDER BY version
    """)

    applied = {row[0] for row in client.query("SELECT version FROM schema_migrations").result_rows}

    for migration in MIGRATIONS:
        if migration["version"] not in applied:
            print(f"Applying migration {migration['version']}: {migration['description']}")
            client.command(migration["up"])
            client.command(f"INSERT INTO schema_migrations (version) VALUES ({migration['version']})")
```

## Best Practices

- Choose the right engine: `MergeTree` for raw data, `AggregatingMergeTree` for pre-aggregates, `SummingMergeTree` for counters, `ReplacingMergeTree` for deduplication
- Always define `ORDER BY` to match your most common `WHERE` and `GROUP BY` patterns — it's the primary key
- Use `LowCardinality(String)` for columns with < 10,000 distinct values (e.g., tenant_id, event_type)
- Partition by month (`toYYYYMM(date)`) for time-series data; this enables partition-level operations
- Use `Nullable` sparingly — it has overhead; prefer sentinel values (0, '') where possible
- Use `async_insert` for high-throughput ingestion from many small writers
- Use `FINAL` keyword on `ReplacingMergeTree` queries, or query the max version explicitly
- Monitor with `system.query_log`, `system.merges`, and `system.parts` tables
- Set `max_execution_time` on user queries to prevent runaway analytics queries
- Use Bloom filter indexes on high-cardinality string columns for faster point lookups

## Models to Use

- **Default**: `claude-sonnet-4-5` — SQL design, materialized views, Python client
- **Analytics architecture**: `claude-opus-4-5` — complex funnel analysis, multi-tenant design, performance tuning
- **Quick snippets**: `claude-haiku-3-5` — aggregation queries, schema DDL, migration scripts
