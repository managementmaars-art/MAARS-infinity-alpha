# Complex Aggregates with State/Merge Functions

Complete examples for using AggregatingMergeTree with State/Merge functions for advanced analytics.

## Pattern Overview

Every aggregate using AggregatingMergeTree follows this three-step pattern:

```
1. View Definition:        Use *State functions      (uniqState, quantileState, etc.)
2. Table Definition:       Use AggregateFunction type
3. Query Execution:        Use *Merge functions      (uniqMerge, quantileMerge, etc.)
```

---

## Example 1: Unique User Counting

**Scenario**: Track unique daily active users without duplicates or recounting

```sql
-- Table definition with AggregateFunction column
CREATE TABLE daily_unique_users (
    date Date,
    unique_users AggregateFunction(uniq, UInt32)
) ENGINE = AggregatingMergeTree()
ORDER BY date;

-- View with State function
CREATE MATERIALIZED VIEW daily_unique_users_mv TO daily_unique_users AS
SELECT
    toDate(timestamp) as date,
    uniqState(user_id) as unique_users
FROM events
GROUP BY date;

-- Query with Merge function
SELECT
    date,
    uniqMerge(unique_users) as total_unique_users
FROM daily_unique_users
WHERE date >= today() - INTERVAL 30 DAY
ORDER BY date DESC;

-- Why this matters:
-- WITHOUT State/Merge: Each INSERT batch creates separate row
--   INSERT 1: 100 unique users → 1 row
--   INSERT 2: 50 unique users (30 overlap) → 2 rows
--   Result: Query needs complex UNION/deduplicate logic
--
-- WITH State/Merge: ClickHouse automatically deduplicates
--   INSERT 1: uniqState({users 1-100})
--   INSERT 2: uniqState({users 71-120})
--   Merge: uniqMerge() → correctly counts unique {1-120} = 120
```

---

## Example 2: Percentile Calculation (Response Time SLAs)

**Scenario**: Track p95 and p99 response times for SLA monitoring

```sql
-- Table with quantile states
CREATE TABLE response_time_sla (
    hour DateTime,
    p50_latency AggregateFunction(quantile(0.50), Float32),
    p95_latency AggregateFunction(quantile(0.95), Float32),
    p99_latency AggregateFunction(quantile(0.99), Float32),
    p999_latency AggregateFunction(quantile(0.999), Float32)
) ENGINE = AggregatingMergeTree()
ORDER BY hour;

-- View aggregates response times
CREATE MATERIALIZED VIEW response_time_sla_mv TO response_time_sla AS
SELECT
    toStartOfHour(timestamp) as hour,
    quantileState(0.50)(response_time_ms) as p50_latency,
    quantileState(0.95)(response_time_ms) as p95_latency,
    quantileState(0.99)(response_time_ms) as p99_latency,
    quantileState(0.999)(response_time_ms) as p999_latency
FROM request_logs
GROUP BY hour;

-- Query for SLA reporting
SELECT
    hour,
    quantileMerge(0.50)(p50_latency) as median_latency,
    quantileMerge(0.95)(p95_latency) as p95_latency,
    quantileMerge(0.99)(p99_latency) as p99_latency,
    quantileMerge(0.999)(p999_latency) as p999_latency,
    -- SLA: p99 must be < 500ms
    if(quantileMerge(0.99)(p99_latency) < 500, 'PASS', 'FAIL') as sla_status
FROM response_time_sla
WHERE hour >= now() - INTERVAL 24 HOUR
ORDER BY hour DESC;
```

**Use Cases**:
- API SLA monitoring (p95, p99 latency targets)
- Database query performance tracking
- Page load time analysis

---

## Example 3: Top Products by Sales

**Scenario**: Always have top 10 products available without complex queries

```sql
-- Table with topK state
CREATE TABLE top_products_daily (
    date Date,
    top_10_products AggregateFunction(topK(10), String)
) ENGINE = AggregatingMergeTree()
ORDER BY date;

-- View tracks top products
CREATE MATERIALIZED VIEW top_products_daily_mv TO top_products_daily AS
SELECT
    toDate(timestamp) as date,
    topKState(10)(product_name) as top_10_products
FROM orders
GROUP BY date;

-- Query: Top products
SELECT
    date,
    topKMerge(10)(top_10_products) as top_products
FROM top_products_daily
WHERE date >= today() - INTERVAL 7 DAY
ORDER BY date DESC;

-- Result: Array of top 10 products sorted by frequency
-- ['Product A', 'Product B', 'Product C', ...]
```

**With weighted scoring (revenue)**:

```sql
-- Better: Weight by revenue instead of frequency
CREATE TABLE top_products_by_revenue (
    date Date,
    product_name String,
    order_count UInt64,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, total_revenue DESC);

CREATE MATERIALIZED VIEW top_products_by_revenue_mv TO top_products_by_revenue AS
SELECT
    toDate(timestamp) as date,
    product_name,
    COUNT() as order_count,
    SUM(price * quantity) as total_revenue
FROM orders
GROUP BY date, product_name;

-- Query: Top 10 by revenue
SELECT
    date,
    product_name,
    order_count,
    total_revenue,
    row_number() OVER (PARTITION BY date ORDER BY total_revenue DESC) as rank
FROM top_products_by_revenue
WHERE date >= today() - INTERVAL 7 DAY
  AND rank <= 10
ORDER BY date DESC, total_revenue DESC;
```

---

## Example 4: Multiple Aggregates in One View

**Scenario**: Comprehensive analytics with counts, sums, averages, and percentiles

```sql
-- Table with multiple aggregate types
CREATE TABLE comprehensive_metrics (
    date Date,
    event_count AggregateFunction(count),
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2),
    avg_order_value Decimal(10, 2),
    p95_latency AggregateFunction(quantile(0.95), Float32),
    top_categories AggregateFunction(topK(5), String)
) ENGINE = AggregatingMergeTree()
ORDER BY date;

-- Single view with all metrics
CREATE MATERIALIZED VIEW comprehensive_metrics_mv TO comprehensive_metrics AS
SELECT
    toDate(timestamp) as date,
    countState() as event_count,
    uniqState(user_id) as unique_users,
    SUM(revenue) as total_revenue,
    AVG(revenue) as avg_order_value,
    quantileState(0.95)(response_time) as p95_latency,
    topKState(5)(category) as top_categories
FROM events
GROUP BY date;

-- Comprehensive query
SELECT
    date,
    countMerge(event_count) as total_events,
    uniqMerge(unique_users) as daily_active_users,
    total_revenue,
    avg_order_value,
    quantileMerge(0.95)(p95_latency) as latency_p95,
    topKMerge(5)(top_categories) as top_5_categories,
    ROUND(100.0 * total_revenue / (total_revenue + 10000), 2) as revenue_share
FROM comprehensive_metrics
WHERE date >= today() - INTERVAL 30 DAY
ORDER BY date DESC;
```

---

## Example 5: Group Aggregates (Array Collection)

**Scenario**: Collect all values or top N values per group

```sql
-- Table with groupArray state
CREATE TABLE user_product_history (
    user_id UInt32,
    products_viewed AggregateFunction(groupArray, String),
    products_purchased AggregateFunction(groupArray, String)
) ENGINE = AggregatingMergeTree()
ORDER BY user_id;

-- View collects products by user
CREATE MATERIALIZED VIEW user_product_history_mv TO user_product_history AS
SELECT
    user_id,
    groupArrayState(if(event_type = 'view', product_name, NULL)) as products_viewed,
    groupArrayState(if(event_type = 'purchase', product_name, NULL)) as products_purchased
FROM events
GROUP BY user_id;

-- Query: Get user browsing and purchase history
SELECT
    user_id,
    uniq(arrayConcat(
        arrayFilter(x -> x != 'None', products_viewed),
        products_purchased
    )) as distinct_products_viewed_or_purchased,
    arrayConcat(
        products_viewed,
        products_purchased
    ) as full_history
FROM user_product_history
WHERE user_id = 12345
LIMIT 1;

-- Limited array (prevent unbounded growth)
CREATE TABLE top_purchased_products_by_user (
    user_id UInt32,
    top_10_products AggregateFunction(groupArraySorted(10), String)
) ENGINE = AggregatingMergeTree()
ORDER BY user_id;

CREATE MATERIALIZED VIEW top_purchased_products_mv TO top_purchased_products_by_user AS
SELECT
    user_id,
    groupArraySortedState(10)(product_name) as top_10_products
FROM events
WHERE event_type = 'purchase'
GROUP BY user_id;

-- Query
SELECT
    user_id,
    groupArraySortedMerge(10)(top_10_products) as favorite_products
FROM top_purchased_products_by_user
LIMIT 100;
```

---

## Example 6: Statistical Aggregates

**Scenario**: Track variance and standard deviation for data quality monitoring

```sql
-- Table with statistical measures
CREATE TABLE price_statistics (
    date Date,
    category String,
    count_values AggregateFunction(count),
    sum_values Decimal(18, 2),
    avg_value Decimal(10, 2),
    stddev Decimal(10, 4),
    variance Decimal(10, 4)
) ENGINE = AggregatingMergeTree()
ORDER BY (date, category);

-- View calculates statistics
CREATE MATERIALIZED VIEW price_statistics_mv TO price_statistics AS
SELECT
    toDate(timestamp) as date,
    category,
    countState() as count_values,
    SUM(price) as sum_values,
    AVG(price) as avg_value,
    stddevPopState(price) as stddev,
    varPopState(price) as variance
FROM products
GROUP BY date, category;

-- Query: Data quality checks
SELECT
    date,
    category,
    countMerge(count_values) as num_products,
    avg_value,
    stddevPopMerge(stddev) as price_stddev,
    varPopMerge(variance) as price_variance,
    -- Alert if variance too high
    if(varPopMerge(variance) > 1000, 'HIGH_VARIANCE', 'NORMAL') as quality_flag
FROM price_statistics
WHERE date >= today() - INTERVAL 7 DAY
ORDER BY date DESC, quality_flag DESC;
```

---

## Example 7: Combining Multiple Quantiles Efficiently

**Scenario**: Calculate multiple percentiles without running separate aggregations

```sql
-- Table with multiple quantiles
CREATE TABLE latency_percentiles (
    service_name String,
    period DateTime,
    percentile_values AggregateFunction(quantiles(0.50, 0.75, 0.90, 0.95, 0.99, 0.999), Float32)
) ENGINE = AggregatingMergeTree()
ORDER BY (service_name, period);

-- View with all percentiles
CREATE MATERIALIZED VIEW latency_percentiles_mv TO latency_percentiles AS
SELECT
    service_name,
    toStartOfMinute(timestamp) as period,
    quantilesState(0.50, 0.75, 0.90, 0.95, 0.99, 0.999)(latency_ms) as percentile_values
FROM request_logs
GROUP BY service_name, period;

-- Query: All percentiles at once
SELECT
    service_name,
    period,
    quantilesMerge(0.50, 0.75, 0.90, 0.95, 0.99, 0.999)(percentile_values) as percentiles,
    percentiles[1] as p50,
    percentiles[2] as p75,
    percentiles[3] as p90,
    percentiles[4] as p95,
    percentiles[5] as p99,
    percentiles[6] as p999
FROM latency_percentiles
WHERE service_name = 'api_gateway'
  AND period >= now() - INTERVAL 1 HOUR
ORDER BY period DESC
LIMIT 100;
```

---

## Example 8: Real-World: E-Commerce Analytics

**Scenario**: Complete e-commerce pipeline with multiple aggregate types

```sql
-- Source events
CREATE TABLE ecommerce_events (
    timestamp DateTime,
    user_id UInt32,
    event_type String,
    product_id UInt32,
    category String,
    price Decimal(10, 2),
    quantity UInt32
) ENGINE = MergeTree()
ORDER BY (timestamp, user_id);

-- Comprehensive daily analytics
CREATE TABLE daily_ecommerce_analytics (
    date Date,
    -- Counts and totals
    event_count AggregateFunction(count),
    unique_visitors AggregateFunction(uniq, UInt32),
    view_count UInt64,
    cart_count UInt64,
    purchase_count UInt64,

    -- Revenue
    total_revenue Decimal(18, 2),
    avg_purchase_value Decimal(10, 2),

    -- Performance
    p95_session_duration AggregateFunction(quantile(0.95), Float32),

    -- Product insights
    unique_products_viewed UInt64,
    top_5_products AggregateFunction(topK(5), String)
) ENGINE = AggregatingMergeTree()
ORDER BY date;

-- Single comprehensive view
CREATE MATERIALIZED VIEW daily_ecommerce_analytics_mv TO daily_ecommerce_analytics AS
SELECT
    toDate(timestamp) as date,
    countState() as event_count,
    uniqState(user_id) as unique_visitors,
    countIf(event_type = 'view') as view_count,
    countIf(event_type = 'cart_add') as cart_count,
    countIf(event_type = 'purchase') as purchase_count,
    sumIf(price * quantity, event_type = 'purchase') as total_revenue,
    avgIf(price * quantity, event_type = 'purchase') as avg_purchase_value,
    quantileState(0.95)(CAST(timestamp as Float32) % 1000) as p95_session_duration,
    COUNT(DISTINCT IF(event_type = 'view', product_id, NULL)) as unique_products_viewed,
    topKState(5)(IF(event_type = 'purchase', product_id, NULL)) as top_5_products
FROM ecommerce_events
GROUP BY date;

-- Comprehensive dashboard query
SELECT
    date,
    countMerge(event_count) as total_events,
    uniqMerge(unique_visitors) as daily_active_users,
    view_count,
    cart_count,
    purchase_count,
    ROUND(100.0 * purchase_count / view_count, 2) as view_to_purchase_rate,
    ROUND(100.0 * cart_count / view_count, 2) as view_to_cart_rate,
    total_revenue,
    avg_purchase_value,
    quantileMerge(0.95)(p95_session_duration) as p95_session_time,
    unique_products_viewed,
    topKMerge(5)(top_5_products) as top_products,

    -- Derived metrics
    ROUND(total_revenue / uniqMerge(unique_visitors), 2) as revenue_per_user,
    ROUND(purchase_count / uniqMerge(unique_visitors), 2) as purchases_per_user
FROM daily_ecommerce_analytics
WHERE date >= today() - INTERVAL 30 DAY
ORDER BY date DESC;
```

---

## Example 9: Chaining Views with State Functions

**Scenario**: Multi-level aggregation preserving State functions through levels

```sql
-- Level 1: Minute-level aggregation (raw from events)
CREATE TABLE minute_metrics (
    minute DateTime,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2),
    p95_latency AggregateFunction(quantile(0.95), Float32)
) ENGINE = AggregatingMergeTree()
ORDER BY minute;

CREATE MATERIALIZED VIEW minute_metrics_mv TO minute_metrics AS
SELECT
    toStartOfMinute(timestamp) as minute,
    uniqState(user_id) as unique_users,
    SUM(revenue) as total_revenue,
    quantileState(0.95)(response_time) as p95_latency
FROM events
GROUP BY minute;

-- Level 2: Hour-level aggregation (from minute metrics)
CREATE TABLE hour_metrics (
    hour DateTime,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2),
    p95_latency AggregateFunction(quantile(0.95), Float32)
) ENGINE = AggregatingMergeTree()
ORDER BY hour;

CREATE MATERIALIZED VIEW hour_metrics_mv TO hour_metrics AS
SELECT
    toStartOfHour(minute) as hour,
    uniqMerge(unique_users) as unique_users,  -- Merge minute-level states
    SUM(total_revenue) as total_revenue,
    quantileMerge(0.95)(p95_latency) as p95_latency  -- Merge quantile states
FROM minute_metrics
GROUP BY hour;

-- Level 3: Day-level aggregation (from hour metrics)
CREATE TABLE day_metrics (
    date Date,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2),
    p95_latency AggregateFunction(quantile(0.95), Float32)
) ENGINE = AggregatingMergeTree()
ORDER BY date;

CREATE MATERIALIZED VIEW day_metrics_mv TO day_metrics AS
SELECT
    toDate(hour) as date,
    uniqMerge(unique_users) as unique_users,  -- Further merge
    SUM(total_revenue) as total_revenue,
    quantileMerge(0.95)(p95_latency) as p95_latency
FROM hour_metrics
GROUP BY date;

-- Query: Combine all levels
SELECT
    date,
    uniqMerge(unique_users) as daily_unique_users,
    total_revenue,
    quantileMerge(0.95)(p95_latency) as daily_p95_latency
FROM day_metrics
WHERE date >= today() - INTERVAL 90 DAY
ORDER BY date DESC;
```

**Benefits**:
- Raw events processed only once (for minute aggregation)
- Hour metrics computed from pre-aggregated minutes (90% less data)
- Day metrics computed from hours (further 60x reduction)
- All while maintaining accuracy of complex aggregates

---

## Common Patterns and Anti-Patterns

### Pattern 1: Use State in Views, Merge in Queries

```sql
-- ✅ CORRECT
CREATE MATERIALIZED VIEW correct_mv AS
SELECT uniqState(user_id) FROM events GROUP BY date;

SELECT uniqMerge(users) FROM correct_mv;

-- ❌ WRONG - Using State in queries
SELECT uniqState(users) FROM correct_mv;  -- Nests state, incorrect result
```

### Pattern 2: Mixed Aggregates Need Proper Types

```sql
-- ✅ CORRECT - AggregatingMergeTree for complex aggregates
CREATE TABLE metrics (
    date Date,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2)
) ENGINE = AggregatingMergeTree();

CREATE MATERIALIZED VIEW metrics_mv TO metrics AS
SELECT
    toDate(timestamp) as date,
    uniqState(user_id) as unique_users,
    SUM(revenue) as total_revenue  -- Regular SUM, not sumState
FROM events
GROUP BY date;

-- ❌ WRONG - Can't mix State and regular sums in AggregatingMergeTree
CREATE TABLE metrics_wrong (
    date Date,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue AggregateFunction(sum, Decimal)  -- Wrong!
) ENGINE = AggregatingMergeTree();
```

### Pattern 3: Include Non-Aggregated Columns

```sql
-- ✅ CORRECT - Include grouping dimensions
CREATE TABLE analytics (
    date Date,
    product_id UInt32,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2)
) ENGINE = AggregatingMergeTree()
ORDER BY (date, product_id);

-- ❌ WRONG - Missing grouping dimension in ORDER BY
CREATE TABLE analytics_wrong (
    date Date,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2)
) ENGINE = AggregatingMergeTree()
ORDER BY date;  -- Missing product_id
```

---

## Troubleshooting State/Merge Aggregates

```sql
-- Check if aggregate functions are working
SELECT
    uniqMerge(uniqState(1))  -- Should work: 1
    uniqMerge(uniqState(1), uniqState(2));  -- Should work: 2 unique

-- Verify table schema
DESCRIBE table_name;  -- Check AggregateFunction columns exist

-- Test with sample data
INSERT INTO test_table VALUES ('2024-01-15', uniqState(1), uniqState(2), uniqState(3));
SELECT uniqMerge(col1) FROM test_table;

-- Monitor view execution
SELECT
    view_name,
    COUNT(*) as executions,
    MAX(elapsed) as slowest_ms
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today()
GROUP BY view_name
ORDER BY slowest_ms DESC;
```
