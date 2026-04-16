# ClickHouse Query Optimization - Real-World Examples

## Example 1: E-Commerce Orders Table - From Slow to Fast

### Scenario
E-commerce platform with 10 billion orders. Initial queries on product filtering are slow (5-10 seconds).

### Initial Schema (Slow)

```sql
CREATE TABLE orders (
    order_id String,
    customer_id UInt32,
    product_id UInt32,
    created_at DateTime,
    status String,
    total_amount Decimal(10, 2)
)
ENGINE = MergeTree()
ORDER BY (customer_id, created_at);  -- Bad: optimized for customer queries only
```

### Problem Analysis

```sql
-- Check slow query
EXPLAIN SELECT COUNT() FROM orders WHERE product_id = 789;

-- Output shows:
-- Partitions: 12/12 (all partitions scanned)
-- Granules: 10000/10000 (all granules scanned)
-- ❌ Full table scan for product_id filter
```

### Optimization Steps

**Step 1: Keep primary key as-is** (customer queries are most common)
```sql
-- Customer queries are fast (uses primary key)
SELECT COUNT() FROM orders WHERE customer_id = 12345;
-- Reads: ~100K rows (0.001% of table)
```

**Step 2: Add data skipping index for product filtering**
```sql
-- Add minmax index for product_id range queries
ALTER TABLE orders ADD INDEX idx_product_id product_id TYPE minmax GRANULARITY 4;

-- Add set index for status filtering
ALTER TABLE orders ADD INDEX idx_status status TYPE set(10) GRANULARITY 4;

-- Verify with EXPLAIN
EXPLAIN SELECT COUNT() FROM orders WHERE product_id = 789;
-- Output now shows:
-- Granules: 150/10000 (only 1.5% scanned - 100x improvement!)
```

**Step 3: Add projection for product-first queries** (e.g., product analytics)
```sql
ALTER TABLE orders ADD PROJECTION proj_by_product (
    SELECT *
    ORDER BY (product_id, created_at)
);

-- Materialize projection (backfill existing data)
ALTER TABLE orders MATERIALIZE PROJECTION proj_by_product;

-- Product queries are now as fast as customer queries
EXPLAIN SELECT COUNT() FROM orders WHERE product_id = 789;
-- Output shows:
-- Uses proj_by_product (sorted by product_id)
-- Granules: 150/10000 (sparse index on projection)
```

**Step 4: Add aggregating projection for product statistics** (pre-compute)
```sql
ALTER TABLE orders ADD PROJECTION proj_product_stats (
    SELECT
        product_id,
        COUNT() as order_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_amount
    GROUP BY product_id
);

ALTER TABLE orders MATERIALIZE PROJECTION proj_product_stats;

-- Instant product statistics
SELECT product_id, order_count, total_revenue
FROM orders
WHERE product_id IN (1, 2, 3);
-- Query now reads pre-aggregated data instead of raw orders
```

### Performance Comparison

| Query | Before | After | Improvement |
|-------|--------|-------|-------------|
| Customer orders (10M) | 50ms | 30ms | 1.7x faster |
| Product orders (10M) | 8000ms | 50ms | 160x faster |
| Product stats (single) | 5000ms | 5ms | 1000x faster |

### Final Schema (Optimized)

```sql
CREATE TABLE orders (
    order_id String,
    customer_id UInt32,
    product_id UInt32,
    created_at DateTime,
    status String,
    total_amount Decimal(10, 2)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (customer_id, created_at);

-- Indexes
ALTER TABLE orders ADD INDEX idx_product_id product_id TYPE minmax GRANULARITY 4;
ALTER TABLE orders ADD INDEX idx_status status TYPE set(10) GRANULARITY 4;

-- Projections
ALTER TABLE orders ADD PROJECTION proj_by_product (
    SELECT * ORDER BY (product_id, created_at)
);

ALTER TABLE orders ADD PROJECTION proj_product_stats (
    SELECT
        product_id,
        COUNT() as order_count,
        SUM(total_amount) as total_revenue
    GROUP BY product_id
);

-- Materialize both
ALTER TABLE orders MATERIALIZE PROJECTION proj_by_product;
ALTER TABLE orders MATERIALIZE PROJECTION proj_product_stats;
```

---

## Example 2: User Events Table - Complex Filtering

### Scenario
Analytics platform tracking 100 billion user events. Need to filter on multiple dimensions (country, device type, event type, duration).

### Schema Design

```sql
CREATE TABLE user_events (
    user_id UInt32,
    timestamp DateTime,
    country String,
    device_type String,
    event_type String,
    session_duration UInt32,
    url String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp);  -- Primary key: user-centric
```

### Data Skipping Indexes

```sql
-- Filter on categorical columns (low cardinality)
ALTER TABLE user_events ADD INDEX idx_country country TYPE set(250) GRANULARITY 4;
ALTER TABLE user_events ADD INDEX idx_device_type device_type TYPE set(20) GRANULARITY 4;
ALTER TABLE user_events ADD INDEX idx_event_type event_type TYPE set(50) GRANULARITY 4;

-- Filter on numeric ranges
ALTER TABLE user_events ADD INDEX idx_duration session_duration TYPE minmax GRANULARITY 4;

-- Filter on high-cardinality strings (URLs)
ALTER TABLE user_events ADD INDEX idx_url url TYPE bloom_filter(0.01) GRANULARITY 4;
```

### Query 1: Complex Multi-Column Filter

```sql
-- Without optimization
SELECT
    toDate(timestamp) as date,
    COUNT() as event_count,
    uniq(user_id) as unique_users
FROM user_events
WHERE country = 'US'
  AND device_type = 'mobile'
  AND event_type = 'purchase'
  AND session_duration > 300
  AND timestamp >= '2024-01-01';

-- EXPLAIN shows:
-- Partitions: 12/12 (but timestamp in PREWHERE would help)
-- Granules: 5000/100000 (indexes skip 95% of blocks)

-- With PREWHERE optimization
SELECT
    toDate(timestamp) as date,
    COUNT() as event_count,
    uniq(user_id) as unique_users
FROM user_events
PREWHERE country = 'US'
  AND device_type = 'mobile'
  AND session_duration > 300
  AND timestamp >= '2024-01-01'
WHERE event_type = 'purchase'
GROUP BY date;

-- Faster: Filters small columns first, then reads event_type only for matches
```

### Query 2: URL Substring Search

```sql
-- Find events with specific URL pattern
SELECT
    user_id,
    COUNT() as events,
    topK(5)(event_type) as top_events
FROM user_events
WHERE url LIKE '%checkout%'
  AND timestamp >= '2024-01-01'
GROUP BY user_id
LIMIT 1000;

-- Bloom filter index makes this fast even on high-cardinality URL column
-- ngrambf_v1 would be better for substring search if we add it:
ALTER TABLE user_events ADD INDEX idx_url_ngram url TYPE ngrambf_v1(4, 512, 3, 0) GRANULARITY 1;
```

### Query 3: Top Products by User Segment

```sql
-- Find top products for mobile users in US
SELECT
    product_category,
    COUNT() as purchases,
    uniq(user_id) as unique_buyers
FROM user_events
WHERE country = 'US'
  AND device_type = 'mobile'
  AND event_type = 'purchase'
GROUP BY product_category
ORDER BY purchases DESC
LIMIT 10;

-- Using approximate functions for even faster results
SELECT
    product_category,
    COUNT() as purchases,
    uniq(user_id) as approx_buyers  -- Approximate unique count (10x faster)
FROM user_events SAMPLE 0.1  -- Sample 10% of data (10x faster)
WHERE country = 'US'
  AND device_type = 'mobile'
  AND event_type = 'purchase'
GROUP BY product_category
ORDER BY purchases DESC
LIMIT 10;
```

### Projection for Time-Aggregated Analysis

```sql
-- Pre-aggregate hourly statistics
ALTER TABLE user_events ADD PROJECTION proj_hourly_stats (
    SELECT
        toStartOfHour(timestamp) as hour,
        country,
        device_type,
        event_type,
        COUNT() as event_count,
        uniq(user_id) as unique_users,
        avg(session_duration) as avg_duration
    GROUP BY hour, country, device_type, event_type
);

ALTER TABLE user_events MATERIALIZE PROJECTION proj_hourly_stats;

-- Hourly reports are now instant
SELECT
    hour,
    country,
    event_type,
    event_count,
    unique_users
FROM user_events
WHERE hour >= '2024-01-01 00:00:00'
  AND country = 'US'
GROUP BY hour, event_type
ORDER BY hour DESC
LIMIT 100;

-- Reads from pre-aggregated projection instead of raw events
```

---

## Example 3: Time-Series Data - Retention and Performance

### Scenario
IoT platform collecting 1 trillion events per year. Need to:
- Keep latest 90 days of data hot
- Archive older data to cold storage
- Fast queries on recent data

### Schema with Retention

```sql
CREATE TABLE iot_events (
    device_id UInt64,
    timestamp DateTime,
    metric_name String,
    value Float32,
    quality UInt8
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)  -- Monthly partitions
ORDER BY (device_id, timestamp)
SETTINGS index_granularity = 8192
TTL timestamp + INTERVAL 90 DAY;  -- Auto-delete old data

-- Add indexes
ALTER TABLE iot_events ADD INDEX idx_metric_name metric_name TYPE set(100) GRANULARITY 4;
ALTER TABLE iot_events ADD INDEX idx_quality quality TYPE minmax GRANULARITY 4;
```

### Queries on Hot Data (Fast)

```sql
-- Device time-series (primary key + partition)
SELECT
    timestamp,
    metric_name,
    value
FROM iot_events
WHERE device_id = 12345
  AND timestamp >= '2024-01-01'  -- Within 90-day window
ORDER BY timestamp DESC
LIMIT 1000;

-- EXPLAIN shows:
-- Partitions: 4/4 (only 4 recent partitions)
-- Granules: 50/1000 (sparse index is very selective)
```

### Automatic Cleanup

```sql
-- TTL removes old partitions automatically during merges
-- Monitor TTL progress:
SELECT
    partition,
    modification_time,
    CASE
        WHEN modification_time + INTERVAL 90 DAY < now() THEN 'Marked for deletion'
        ELSE 'Active'
    END as status
FROM system.parts
WHERE table = 'iot_events'
ORDER BY partition DESC;

-- Manually trigger cleanup if needed
ALTER TABLE iot_events UPDATE timestamp = now() WHERE 1 = 0;
-- This forces a merge cycle and TTL evaluation
```

---

## Example 4: Avoiding Common Pitfalls

### Pitfall 1: SELECT * Performance

```sql
-- Bad: Reads all 50 columns
SELECT * FROM events WHERE timestamp >= '2024-01-01' LIMIT 1000;
-- 500MB transferred

-- Good: Read only needed columns
SELECT timestamp, user_id, event_type FROM events WHERE timestamp >= '2024-01-01' LIMIT 1000;
-- 5MB transferred (100x faster)
```

### Pitfall 2: GROUP BY on High-Cardinality Column

```sql
-- Bad: Groups on millions of unique URLs (memory explosion)
SELECT url, COUNT() FROM events GROUP BY url LIMIT 1000;

-- Good: Use approximate topK
SELECT topK(1000)(url) FROM events;

-- Or:
SELECT url, COUNT() FROM events GROUP BY url ORDER BY COUNT() DESC LIMIT 1000;
-- ClickHouse can push LIMIT into GROUP BY for memory optimization
```

### Pitfall 3: Missing Primary Key Prefix

```sql
-- Table: ORDER BY (country, user_id, timestamp)

-- ❌ Slow: Missing country prefix
SELECT * FROM events WHERE user_id = 12345;
-- Sparse index can't help, full table scan

-- ✅ Fix 1: Use primary key prefix
SELECT * FROM events WHERE country = 'US' AND user_id = 12345;

-- ✅ Fix 2: Add data skipping index
ALTER TABLE events ADD INDEX idx_user_id user_id TYPE minmax GRANULARITY 4;
```

### Pitfall 4: Not Using FINAL with ReplacingMergeTree

```sql
-- Table uses ReplacingMergeTree for soft deletes
CREATE TABLE orders (
    order_id String,
    status String,
    timestamp DateTime,
    version UInt32
)
ENGINE = ReplacingMergeTree(version)
ORDER BY order_id;

-- ❌ Bad: May return old versions until parts merge
SELECT * FROM orders WHERE order_id = '12345';

-- ✅ Good: FINAL ensures deduplicated results
SELECT * FROM orders FINAL WHERE order_id = '12345';
```

---

## Example 5: Query Profiling Workflow

### Identify Slow Query

```sql
-- Find queries slower than 1 second
SELECT
    query,
    query_duration_ms,
    read_rows,
    read_bytes,
    partitions_read,
    result_rows
FROM system.query_log
WHERE query_duration_ms > 1000
  AND type = 'QueryFinish'
  AND database = 'default'
ORDER BY query_duration_ms DESC
LIMIT 5;

-- Sample slow query found:
-- "SELECT count() FROM orders WHERE product_id = 789"
-- Duration: 5000ms
-- Read rows: 10000000000
-- Read bytes: 40GB
```

### Analyze with EXPLAIN

```sql
EXPLAIN SELECT count() FROM orders WHERE product_id = 789;

-- Output shows:
-- Primary key: (customer_id, created_at, order_id)
-- Filter: product_id = 789
-- Partitions: 12/12
-- ❌ Full partition scan (product_id not in primary key)
```

### Implement Optimization

```sql
-- Check table statistics
SELECT
    sum(bytes) as total_bytes,
    count() as part_count,
    sum(rows) as total_rows
FROM system.parts
WHERE table = 'orders';

-- Add data skipping index
ALTER TABLE orders ADD INDEX idx_product_id product_id TYPE minmax GRANULARITY 4;

-- Wait for index application (background process)
-- or force merge:
-- ALTER TABLE orders FINAL;
```

### Verify Improvement

```sql
-- Re-run with EXPLAIN
EXPLAIN SELECT count() FROM orders WHERE product_id = 789;

-- Output shows:
-- Granules: 150/10000 (sparse index helps!)

-- Check actual performance
SELECT count() FROM orders WHERE product_id = 789;
-- Duration: 50ms (100x improvement!)

-- Verify in query log
SELECT
    query_duration_ms,
    read_rows,
    read_bytes
FROM system.query_log
WHERE query LIKE '%product_id = 789%'
ORDER BY event_time DESC
LIMIT 1;

-- Results:
-- Duration: 50ms (was 5000ms)
-- Read rows: 10M (was 10B)
-- Improvement: 100x faster, 1000x fewer rows read
```

---

## Example 6: Projection Transparency and Optimization

### Query 1: Customer Perspective

```sql
-- Main table sorted by customer
SELECT * FROM orders WHERE customer_id = 12345;

-- EXPLAIN shows:
-- Uses main table (sorted by customer_id)
-- Reads: ~100K rows
```

### Query 2: Product Perspective

```sql
-- Without projection
SELECT * FROM orders WHERE product_id = 789;

-- EXPLAIN shows:
-- Full partition scan (product_id not in primary key)
-- Reads: 10B rows ❌

-- With projection added
ALTER TABLE orders ADD PROJECTION proj_by_product (
    SELECT * ORDER BY (product_id, created_at)
);
ALTER TABLE orders MATERIALIZE PROJECTION proj_by_product;

-- EXPLAIN shows:
-- Uses proj_by_product (automatically selected!)
-- Reads: ~1M rows ✅
```

### Query 3: Time Perspective with Aggregation

```sql
-- Daily sales report
SELECT
    toDate(created_at) as date,
    count() as orders,
    sum(total_amount) as revenue
FROM orders
WHERE created_at >= '2024-01-01'
GROUP BY date
ORDER BY date;

-- Add aggregating projection
ALTER TABLE orders ADD PROJECTION proj_daily_stats (
    SELECT
        toDate(created_at) as date,
        count() as orders,
        sum(total_amount) as revenue
    GROUP BY date
);
ALTER TABLE orders MATERIALIZE PROJECTION proj_daily_stats;

-- Query automatically reads pre-aggregated data
-- Duration: 5ms (was 500ms reading raw orders)
```

### Monitoring Projection Usage

```sql
-- Check which projections are being used
SELECT
    query,
    used_projection,
    query_duration_ms
FROM system.query_log
WHERE database = 'default'
  AND used_projection IS NOT NULL
ORDER BY event_time DESC
LIMIT 10;

-- Check projection size and maintenance cost
SELECT
    name as projection_name,
    count() as part_count,
    sum(bytes) as total_bytes
FROM system.projection_parts
WHERE table = 'orders'
GROUP BY name;
```
