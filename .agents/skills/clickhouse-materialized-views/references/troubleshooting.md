# Materialized View Troubleshooting Guide

## Diagnostic Queries

### Check If View Exists and Is Healthy

```sql
-- List all materialized views
SELECT
    name,
    database,
    engine,
    create_table_query
FROM system.tables
WHERE engine = 'MaterializedView';

-- Check specific view
SELECT name, status
FROM system.tables
WHERE name = 'hourly_stats_mv'
  AND engine = 'MaterializedView';
```

### Check View Execution Status

```sql
-- Get recent materialized view execution times
SELECT
    view_name,
    database,
    elapsed,
    query_duration_ms,
    read_rows,
    read_bytes,
    written_rows,
    written_bytes,
    memory_usage,
    exception
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today() - INTERVAL 1 DAY
ORDER BY event_time DESC
LIMIT 100;

-- Show slowest views in last 24 hours
SELECT
    view_name,
    COUNT(*) as executions,
    AVG(elapsed) as avg_elapsed_ms,
    MAX(elapsed) as max_elapsed_ms,
    SUM(read_rows) as total_read_rows
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today() - INTERVAL 1 DAY
GROUP BY view_name
ORDER BY max_elapsed_ms DESC;
```

### Check Destination Table Status

```sql
-- View destination table storage
SELECT
    table,
    formatReadableSize(sum(bytes)) as size,
    sum(rows) as rows,
    count(distinct partition) as partitions
FROM system.parts
WHERE table LIKE '%mv'
  OR table LIKE '.inner.%'
GROUP BY table
ORDER BY sum(bytes) DESC;

-- Check for merges in progress
SELECT
    database,
    table,
    partition,
    is_mutation,
    elapsed
FROM system.mutations
WHERE is_done = 0;
```

---

## Common Issues and Solutions

### Issue 1: View Not Updating

**Symptoms**:
- Inserting data into source table but destination table doesn't change
- View seems inactive

**Diagnosis**:

```sql
-- Check if view exists
SELECT name FROM system.tables
WHERE name = 'hourly_stats_mv' AND engine = 'MaterializedView';

-- Check if view definition is correct
SELECT create_table_query FROM system.tables
WHERE name = 'hourly_stats_mv';

-- Check for errors in recent executions
SELECT
    exception,
    COUNT(*) as count
FROM system.query_log
WHERE query LIKE '%hourly_stats_mv%'
  AND exception != ''
GROUP BY exception;
```

**Solutions**:

**Solution A: Verify source table gets inserts**
```sql
-- Check if data is being inserted into source
SELECT COUNT(*) FROM events WHERE timestamp >= now() - INTERVAL 1 MINUTE;

-- Check insertion logs
SELECT event_time, query, exception
FROM system.query_log
WHERE table = 'events'
  AND type = 'QueryFinish'
  AND query_kind = 'Insert'
  AND event_date = today()
ORDER BY event_time DESC
LIMIT 10;
```

**Solution B: Recreate the view**
```sql
-- Drop and recreate
DROP VIEW hourly_stats_mv;

CREATE MATERIALIZED VIEW hourly_stats_mv TO hourly_stats AS
SELECT
    toStartOfHour(timestamp) as hour,
    product_id,
    COUNT() as sales_count,
    SUM(revenue) as total_revenue
FROM events
GROUP BY hour, product_id;

-- Test with new data
INSERT INTO events VALUES (123, 'test', now(), 99.99);
SELECT COUNT(*) FROM hourly_stats;  -- Should see new row
```

**Solution C: Check destination table permissions**
```sql
-- Verify you can write to destination table
INSERT INTO hourly_stats VALUES (now(), 1, 0, 0);

-- Check table existence
SHOW TABLES WHERE name = 'hourly_stats';

-- Check destination table structure
DESCRIBE hourly_stats;
```

---

### Issue 2: Duplicate Data in Results

**Symptoms**:
- Query returns same data multiple times
- SUM of counts doesn't match actual row count
- Expected: 100 rows with count=50, Actual: 2 rows (count=30, count=20)

**Root Cause**: Using `MergeTree` instead of `SummingMergeTree`

```sql
-- Problem demonstration
CREATE TABLE stats (...) ENGINE = MergeTree() ORDER BY (date, product_id);

CREATE MATERIALIZED VIEW stats_mv TO stats AS
SELECT date, product_id, COUNT() as sales FROM events GROUP BY date, product_id;

-- INSERT 1: 30 sales on 2024-01-01 for product 1
-- INSERT 2: 20 sales on 2024-01-01 for product 1
-- Result: TWO rows (30 and 20) instead of ONE row (50)

SELECT date, product_id, sales FROM stats WHERE date = '2024-01-01';
-- Returns: [2024-01-01, 1, 30] and [2024-01-01, 1, 20]
```

**Solution 1: Change destination to SummingMergeTree**

```sql
-- Step 1: Drop the view
DROP VIEW stats_mv;

-- Step 2: Create new destination with SummingMergeTree
CREATE TABLE stats_v2 (
    date Date,
    product_id UInt32,
    sales UInt64
) ENGINE = SummingMergeTree()
ORDER BY (date, product_id);

-- Step 3: Copy existing data
INSERT INTO stats_v2 SELECT date, product_id, SUM(sales) FROM stats GROUP BY date, product_id;

-- Step 4: Recreate view
CREATE MATERIALIZED VIEW stats_mv TO stats_v2 AS
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as sales
FROM events
GROUP BY date, product_id;

-- Step 5: Drop old table
DROP TABLE stats;
```

**Solution 2: Query with manual aggregation (if can't change engine)**

```sql
-- Workaround until you migrate to SummingMergeTree
SELECT date, product_id, SUM(sales) as total_sales
FROM stats
GROUP BY date, product_id
ORDER BY date, product_id;
```

**Solution 3: Force deduplication with FINAL (temporary fix)**

```sql
-- Forces merging before query (expensive!)
SELECT * FROM stats FINAL;
```

---

### Issue 3: High Memory Usage

**Symptoms**:
- Server memory usage spikes during inserts
- Out-of-memory errors
- Slow system performance

**Root Cause**: Large GROUP BY cardinality (millions of unique combinations)

```sql
-- Example: Per-user, per-minute stats = too high cardinality
CREATE MATERIALIZED VIEW user_minute_stats AS
SELECT
    toStartOfMinute(timestamp) as minute,
    user_id,
    COUNT() as events
FROM events
GROUP BY minute, user_id;  -- Could be millions of combinations!
```

**Diagnosis**:

```sql
-- Check memory usage by view
SELECT
    view_name,
    SUM(memory_usage) as total_memory,
    MAX(memory_usage) as peak_memory
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today() - INTERVAL 1 DAY
GROUP BY view_name
ORDER BY peak_memory DESC;

-- Check GROUP BY cardinality
SELECT
    COUNT(DISTINCT (toStartOfHour(timestamp), user_id)) as unique_combinations
FROM events
WHERE timestamp >= now() - INTERVAL 1 HOUR;
```

**Solutions**:

**Solution A: Reduce GROUP BY cardinality**
```sql
-- Instead of per-user stats:
-- GROUP BY user_id, toStartOfMinute(timestamp)  -- Too high cardinality

-- Use per-segment stats:
CREATE TABLE user_segment_stats (
    hour DateTime,
    user_segment String,
    event_count UInt64
) ENGINE = SummingMergeTree()
ORDER BY (hour, user_segment);

CREATE MATERIALIZED VIEW user_segment_stats_mv TO user_segment_stats AS
SELECT
    toStartOfHour(timestamp) as hour,
    CASE
        WHEN revenue > 1000 THEN 'vip'
        WHEN revenue > 100 THEN 'regular'
        ELSE 'casual'
    END as user_segment,
    COUNT() as event_count
FROM events
GROUP BY hour, user_segment;  -- Much lower cardinality
```

**Solution B: Add WHERE filter to reduce data volume**
```sql
-- Instead of processing all events:
CREATE MATERIALIZED VIEW paid_events_stats AS
SELECT
    toStartOfHour(timestamp) as hour,
    event_type,
    COUNT() as count
FROM events
WHERE event_type IN ('purchase', 'subscription')  -- Filter in view
GROUP BY hour, event_type;
```

**Solution C: Adjust Kafka block size (if using Kafka)**
```sql
-- In Kafka table settings:
CREATE TABLE kafka_source (...)
ENGINE = Kafka()
SETTINGS kafka_max_block_size = 1000;  -- Reduce from default 65536
```

**Solution D: Split into multiple views**
```sql
-- Instead of one complex view, use multiple simpler ones:

-- View 1: Hourly aggregates
CREATE MATERIALIZED VIEW hourly_stats_mv AS
SELECT
    toStartOfHour(timestamp) as hour,
    product_id,
    COUNT() as count
FROM events
GROUP BY hour, product_id;

-- View 2: Product stats (aggregate from hourly)
CREATE MATERIALIZED VIEW product_stats_mv AS
SELECT
    product_id,
    SUM(count) as total_count
FROM hourly_stats
GROUP BY product_id;
```

---

### Issue 4: Slow Materialized View Execution

**Symptoms**:
- View takes 5+ seconds to process each insert batch
- CPU usage spikes during inserts
- Inserts are slow

**Root Cause**: Complex aggregation logic or subqueries in view definition

```sql
-- Example: Complex nested subquery
CREATE MATERIALIZED VIEW slow_stats AS
SELECT
    date,
    product_id,
    COUNT() as sales,
    -- Complex subquery makes this slow
    (SELECT SUM(quantity) FROM orders o WHERE o.product_id = orders.product_id) as total_quantity
FROM orders
GROUP BY date, product_id;
```

**Diagnosis**:

```sql
-- Check which views are slowest
SELECT
    view_name,
    database,
    COUNT(*) as executions,
    AVG(elapsed) as avg_elapsed_ms,
    MAX(elapsed) as max_elapsed_ms,
    AVG(memory_usage) as avg_memory
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today()
GROUP BY view_name, database
ORDER BY max_elapsed_ms DESC
LIMIT 10;

-- Get the actual slow query
SELECT
    event_time,
    query,
    elapsed,
    memory_usage
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND query LIKE '%slow_stats%'
ORDER BY elapsed DESC
LIMIT 5;
```

**Solutions**:

**Solution A: Simplify aggregation logic**
```sql
-- Remove subqueries
-- Before: Complex nested query
-- After: Simple GROUP BY

CREATE MATERIALIZED VIEW fast_stats AS
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as sales,
    SUM(quantity) as total_quantity
FROM orders
GROUP BY date, product_id;
```

**Solution B: Add WHERE filter to reduce data processed**
```sql
CREATE MATERIALIZED VIEW purchase_stats AS
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as purchases,
    SUM(amount) as total_amount
FROM orders
WHERE event_type = 'purchase'  -- Filter early
GROUP BY date, product_id;
```

**Solution C: Use chained views instead of complex single view**
```sql
-- Level 1: Basic hourly aggregation
CREATE TABLE hourly_raw (
    hour DateTime,
    product_id UInt32,
    count UInt64
) ENGINE = SummingMergeTree() ORDER BY (hour, product_id);

CREATE MATERIALIZED VIEW hourly_raw_mv TO hourly_raw AS
SELECT
    toStartOfHour(timestamp) as hour,
    product_id,
    COUNT() as count
FROM orders
GROUP BY hour, product_id;

-- Level 2: Daily stats from hourly (faster than from raw)
CREATE TABLE daily_stats (
    date Date,
    product_id UInt32,
    count UInt64
) ENGINE = SummingMergeTree() ORDER BY (date, product_id);

CREATE MATERIALIZED VIEW daily_stats_mv TO daily_stats AS
SELECT
    toDate(hour) as date,
    product_id,
    SUM(count) as count
FROM hourly_raw
GROUP BY date, product_id;
```

**Solution D: Check for missing indexes on GROUP BY columns**
```sql
-- Ensure GROUP BY columns are first in ORDER BY
DESCRIBE orders;

-- Should see:
-- timestamp DateTime
-- product_id UInt32
-- price Decimal

-- If using GROUP BY product_id, timestamp
-- Ensure ORDER BY (product_id, timestamp) or similar
```

---

### Issue 5: Backfill/Repopulation Failed

**Symptoms**:
- Created view with POPULATE but it's taking too long
- View doesn't have historical data
- Need to populate view with existing data

**Diagnosis**:

```sql
-- Check if POPULATE completed
SELECT
    database,
    table,
    total_rows
FROM system.tables
WHERE name = 'destination_table';

-- Check for stuck mutations/merges
SELECT
    database,
    table,
    command,
    create_time,
    elapsed
FROM system.mutations
WHERE is_done = 0;
```

**Solutions**:

**Solution A: Cancel POPULATE and backfill manually**
```sql
-- If POPULATE is stuck/slow, you can cancel and backfill manually

-- Step 1: Drop the view
DROP VIEW slow_populate_mv;

-- Step 2: Manually backfill destination table
INSERT INTO destination_table
SELECT
    -- Your aggregation query
    toDate(timestamp) as date,
    product_id,
    COUNT() as count
FROM source_table
WHERE timestamp < '2024-01-01'  -- Only historical data
GROUP BY date, product_id;

-- Step 3: Recreate view (without POPULATE) for future data
CREATE MATERIALIZED VIEW slow_populate_mv TO destination_table AS
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as count
FROM source_table
GROUP BY date, product_id;
```

**Solution B: Incremental backfill**
```sql
-- Fill one day at a time instead of all at once
INSERT INTO destination_table
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as count
FROM source_table
WHERE toDate(timestamp) = '2024-01-01'
GROUP BY date, product_id;

INSERT INTO destination_table
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as count
FROM source_table
WHERE toDate(timestamp) = '2024-01-02'
GROUP BY date, product_id;

-- Continue for each day...
```

**Solution C: Batch backfill with batching script**
```sql
-- Use batch size to control memory usage
-- Backfill 100K rows at a time
INSERT INTO destination_table
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as count
FROM source_table
WHERE timestamp BETWEEN '2024-01-01' AND '2024-01-01 23:59:59'
GROUP BY date, product_id;
-- Repeat for each time window
```

---

### Issue 6: View Data Inconsistency

**Symptoms**:
- Query same data twice, get different results
- Duplicates in results
- Partial data visible intermittently

**Root Cause**: Background merges not completed

```sql
-- Check if view is up-to-date
SELECT
    database,
    table,
    count(*) as num_parts,
    sum(rows) as total_rows
FROM system.parts
WHERE table = '.inner.hourly_stats_mv'
  AND active = 1;

-- Multiple parts = merging not complete
-- Should eventually consolidate to 1 part
```

**Solutions**:

**Solution A: Force merge**
```sql
-- Complete all pending merges
OPTIMIZE TABLE destination_table;

-- Or force merge with replication:
OPTIMIZE TABLE destination_table FINAL;
```

**Solution B: Use FINAL in queries (temporary)**
```sql
-- Forces merge before query (slow, avoid in production)
SELECT * FROM destination_table FINAL;
```

**Solution C: Wait for background merge**
```sql
-- ClickHouse will eventually merge parts
-- Check merge progress:
SELECT
    database,
    table,
    partition,
    elapsed
FROM system.mutations
ORDER BY elapsed DESC;
```

---

## Monitoring and Maintenance

### Create Monitoring Queries

```sql
-- Check view health hourly
SELECT
    now() as check_time,
    view_name,
    COUNT(*) as total_executions,
    SUM(if(exception != '', 1, 0)) as failures,
    AVG(elapsed) as avg_elapsed_ms,
    MAX(memory_usage) as peak_memory
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today()
  AND event_time > now() - INTERVAL 1 HOUR
GROUP BY view_name
ORDER BY failures DESC;
```

### Set Up Alerts

```sql
-- Alert if view hasn't executed in 1 hour
SELECT
    view_name,
    MAX(event_time) as last_execution,
    now() - MAX(event_time) as time_since_execution
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today() - INTERVAL 1 DAY
GROUP BY view_name
HAVING time_since_execution > INTERVAL 1 HOUR
ORDER BY time_since_execution DESC;

-- Alert if view has high failure rate
SELECT
    view_name,
    COUNT(*) as total,
    SUM(if(exception != '', 1, 0)) as failures,
    failures / total as failure_rate
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today()
GROUP BY view_name
HAVING failure_rate > 0.05
ORDER BY failure_rate DESC;
```

### Regular Maintenance

```sql
-- Weekly: Check for slow views
SELECT
    view_name,
    COUNT(*) as executions,
    MAX(elapsed) as slowest_ms,
    AVG(elapsed) as avg_ms
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today() - INTERVAL 7 DAY
GROUP BY view_name
ORDER BY slowest_ms DESC;

-- Monthly: Optimize destination tables
OPTIMIZE TABLE destination_table FINAL;
```
