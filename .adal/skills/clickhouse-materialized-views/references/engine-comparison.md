# ClickHouse Destination Table Engines for Materialized Views

## Quick Comparison

| Engine | Use Case | Auto Aggregation | Best For |
|--------|----------|------------------|----------|
| **SummingMergeTree** | Simple aggregates | COUNT, SUM, AVG | Hourly/daily metrics, sales totals |
| **AggregatingMergeTree** | Complex aggregates | uniq, quantile, topK | Unique counts, percentiles, top-K |
| **ReplacingMergeTree** | Entity updates | No (deduplicates on version) | User profiles, state snapshots |
| **MergeTree** | Raw events | No | Event audit, raw data retention |

---

## SummingMergeTree

**When**: Simple aggregates (COUNT, SUM, AVG, MIN, MAX)

**How it works**:
- Automatically sums numeric columns during background merges
- Keeps only the latest version of each key
- No need to SUM in queries

**Table Definition**:
```sql
CREATE TABLE hourly_sales (
    hour DateTime,
    product_id UInt32,
    sales_count UInt64,
    total_revenue Decimal(18, 2)
)
ENGINE = SummingMergeTree()
ORDER BY (hour, product_id);
```

**Materialized View**:
```sql
CREATE MATERIALIZED VIEW hourly_sales_mv TO hourly_sales AS
SELECT
    toStartOfHour(timestamp) as hour,
    product_id,
    COUNT() as sales_count,
    SUM(price * quantity) as total_revenue
FROM orders
GROUP BY hour, product_id;
```

**Query Behavior**:
```sql
-- INSERT 1: 10 orders for product_id=1 at hour=2024-01-15 10:00
-- INSERT 2: 5 orders for product_id=1 at hour=2024-01-15 10:00
-- After background merge: ONE row with sales_count=15 (automatically summed)

SELECT hour, product_id, sales_count
FROM hourly_sales
WHERE hour >= today();
-- Result: 2024-01-15 10:00:00 | 1 | 15 (merged automatically)
```

**Columns Summed**:
- UInt8-64, Int8-64, Float32-64 (numeric types)
- Decimal types
- Arrays (element-wise sum)

**Columns Not Summed** (replaced, not summed):
- String, DateTime, Date, Enum types
- Arrays of non-numeric types
- Specified in ENGINE settings

**Columns Not Summed Example**:
```sql
CREATE TABLE product_stats (
    date Date,
    product_id UInt32,
    product_name String,        -- NOT summed, replaced
    total_sales UInt64,         -- Summed
    avg_price Decimal(10, 2)    -- Summed (careful: becomes meaningless)
)
ENGINE = SummingMergeTree()
ORDER BY (date, product_id);
-- product_name will be replaced, not concatenated
```

**Pros**:
- Simple and efficient
- No special query syntax needed
- Handles most common aggregation needs

**Cons**:
- Only works with specific numeric aggregates
- Cannot handle complex aggregates (uniq, quantile)
- Need to decide which columns to sum at table creation

---

## AggregatingMergeTree

**When**: Complex aggregates (uniq, quantile, topK, or multiple aggregation types)

**How it works**:
- Stores intermediate aggregation states (not final values)
- Merges states during background processes
- Query with Merge functions to get final values

**Table Definition with State Columns**:
```sql
CREATE TABLE user_analytics (
    date Date,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue AggregateFunction(sum, Decimal(18, 2)),
    p95_latency AggregateFunction(quantile(0.95), Float32)
)
ENGINE = AggregatingMergeTree()
ORDER BY date;
```

**Materialized View with State Functions**:
```sql
CREATE MATERIALIZED VIEW user_analytics_mv TO user_analytics AS
SELECT
    toDate(timestamp) as date,
    uniqState(user_id) as unique_users,
    sumState(revenue) as total_revenue,
    quantileState(0.95)(response_time) as p95_latency
FROM events
GROUP BY date;
```

**Query with Merge Functions**:
```sql
SELECT
    date,
    uniqMerge(unique_users) as total_unique_users,
    sumMerge(total_revenue) as total_revenue,
    quantileMerge(0.95)(p95_latency) as latency_p95
FROM user_analytics
GROUP BY date
ORDER BY date;
```

**How It Works Internally**:
```
INSERT 1: uniqState({1, 2, 3}) → State A
INSERT 2: uniqState({3, 4, 5}) → State B
Background Merge: uniqMerge(A, B) → State C ({1, 2, 3, 4, 5})
Query: uniqMerge(C) → Final value: 5
```

**State/Merge Function Pairs**:
```sql
-- Basic Aggregates
countState() / countMerge()
sumState(x) / sumMerge()
avgState(x) / avgMerge()
minState(x) / minMerge()
maxState(x) / maxMerge()

-- Approximate Unique Counting
uniqState(x) / uniqMerge()
uniqExactState(x) / uniqExactMerge()
uniqCombinedState(x) / uniqCombinedMerge()

-- Percentiles
quantileState(0.95)(x) / quantileMerge(0.95)()
quantilesDeterministicState(0.95, 0.99)(x) / quantilesDeterministicMerge()

-- Top-K Elements
topKState(10)(x) / topKMerge(10)()

-- Other Aggregates
groupArrayState(x) / groupArrayMerge()
stddevPopState(x) / stddevPopMerge()
```

**⚠️ Important**: Use `AggregateFunction` type for all aggregate columns

**Pros**:
- Handles complex aggregates accurately
- Deduplication for approximate functions (uniq)
- Efficient state storage

**Cons**:
- Requires State/Merge function pairs in views and queries
- More complex setup than SummingMergeTree
- Must use AggregateFunction column type

**Mixing Aggregate Types**:
```sql
-- Can't mix SummingMergeTree (automatic summing) with AggregatingMergeTree
-- Choose one or the other for your destination table

-- Option 1: Use SummingMergeTree for simple aggregates
CREATE TABLE simple_stats (...) ENGINE = SummingMergeTree() ...
-- Use COUNT(), SUM() in view

-- Option 2: Use AggregatingMergeTree for complex aggregates
CREATE TABLE complex_stats (...) ENGINE = AggregatingMergeTree() ...
-- Use uniqState(), quantileState() in view
```

---

## ReplacingMergeTree

**When**: Need to update/replace existing rows (entity state tracking)

**How it works**:
- Maintains a version column to determine latest record
- Replaces old versions with new versions during merges
- Use FINAL to force deduplication in queries

**Table Definition with Version**:
```sql
CREATE TABLE user_profiles (
    user_id UInt32,
    username String,
    email String,
    update_time DateTime,
    _version UInt64  -- Version column
)
ENGINE = ReplacingMergeTree(_version)
ORDER BY user_id;
```

**Materialized View from Update Stream**:
```sql
-- Kafka topic: user_profile_updates
CREATE MATERIALIZED VIEW user_profiles_mv TO user_profiles AS
SELECT
    JSONExtractInt(message, 'user_id') as user_id,
    JSONExtractString(message, 'username') as username,
    JSONExtractString(message, 'email') as email,
    now() as update_time,
    JSONExtractInt(message, 'version') as _version
FROM kafka_updates;
```

**Query Behavior Without FINAL**:
```sql
SELECT user_id, username, email
FROM user_profiles
WHERE user_id = 123;
-- Result: May have multiple versions, must GROUP BY and take MAX(_version)
```

**Query Behavior With FINAL**:
```sql
SELECT user_id, username, email
FROM user_profiles FINAL
WHERE user_id = 123;
-- Result: Latest version only (forces merging before query)
-- ⚠️ FINAL is expensive for large tables, avoid in production queries
```

**Recommended Query Pattern**:
```sql
SELECT
    user_id,
    username,
    email,
    argMax(update_time, _version) as last_update
FROM user_profiles
WHERE user_id = 123
GROUP BY user_id
ORDER BY user_id;
```

**Pros**:
- Handles entity updates efficiently
- Maintains version history
- Automatic deduplication by version

**Cons**:
- Requires version column management
- FINAL queries are expensive
- GROUP BY + argMax pattern needed for consistent reads

---

## MergeTree (Plain)

**When**: Need raw event retention, audit logs, or data without aggregation

**How it works**:
- No automatic aggregation
- No deduplication
- Stores all versions of rows
- Optimized for read-heavy workloads

**Table Definition**:
```sql
CREATE TABLE event_log (
    timestamp DateTime,
    user_id UInt32,
    event_type String,
    payload String
)
ENGINE = MergeTree()
ORDER BY (user_id, timestamp);
```

**Materialized View**:
```sql
-- Copy raw events from Kafka with transformation
CREATE MATERIALIZED VIEW event_log_mv TO event_log AS
SELECT
    now() as timestamp,
    JSONExtractInt(message, 'user_id') as user_id,
    JSONExtractString(message, 'event_type') as event_type,
    message as payload
FROM kafka_events;
```

**Pros**:
- Simple, straightforward
- Preserves all data
- Good for audit trails and historical records

**Cons**:
- Large storage footprint
- No automatic deduplication
- Requires manual aggregation in queries

---

## Choosing the Right Engine

**Decision Tree**:

```
Do you need to aggregate data?
├─ No → Use MergeTree
│       (Store raw events, audit logs)
│
└─ Yes
   ├─ Using only SUM, COUNT, AVG, MIN, MAX?
   │  └─ Use SummingMergeTree
   │     (Hourly/daily sales, simple metrics)
   │
   ├─ Using uniq, quantile, topK, or mixed aggregates?
   │  └─ Use AggregatingMergeTree
   │     (Unique users, percentiles, complex analytics)
   │
   └─ Need to track entity state/updates?
      └─ Use ReplacingMergeTree
         (User profiles, entity snapshots)
```

---

## Real-World Example: Multi-Level Dashboard

```sql
-- Level 1: Raw events (MergeTree)
CREATE TABLE events (
    timestamp DateTime,
    user_id UInt32,
    event_type String,
    revenue Decimal(10, 2)
) ENGINE = MergeTree() ORDER BY (timestamp, user_id);

-- Level 2: Hourly aggregates (SummingMergeTree for simple metrics)
CREATE TABLE hourly_metrics (
    hour DateTime,
    event_count UInt64,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree() ORDER BY hour;

CREATE MATERIALIZED VIEW hourly_metrics_mv TO hourly_metrics AS
SELECT
    toStartOfHour(timestamp) as hour,
    COUNT() as event_count,
    SUM(revenue) as total_revenue
FROM events
GROUP BY hour;

-- Level 3: Daily unique user analytics (AggregatingMergeTree for complex aggregates)
CREATE TABLE daily_user_analytics (
    date Date,
    unique_users AggregateFunction(uniq, UInt32),
    avg_revenue AggregateFunction(avg, Decimal(18, 2))
) ENGINE = AggregatingMergeTree() ORDER BY date;

CREATE MATERIALIZED VIEW daily_user_analytics_mv TO daily_user_analytics AS
SELECT
    toDate(timestamp) as date,
    uniqState(user_id) as unique_users,
    avgState(revenue) as avg_revenue
FROM events
GROUP BY date;

-- Query pattern combines engine strengths
SELECT
    toStartOfDay(hour) as day,
    SUM(total_revenue) as daily_revenue,
    uniqMerge(unique_users) as daily_active_users
FROM hourly_metrics
FULL OUTER JOIN daily_user_analytics USING (date)
GROUP BY day
ORDER BY day DESC;
```
