# Materialized View Aggregation Patterns

Complete SQL examples for common real-world aggregation patterns.

## 1. Simple Aggregation: Daily Sales

**Scenario**: Aggregate daily sales by product

```sql
-- Source table
CREATE TABLE orders (
    order_id UInt64,
    timestamp DateTime,
    product_id UInt32,
    quantity UInt32,
    price Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY (timestamp, product_id);

-- Destination: Daily aggregates
CREATE TABLE daily_sales (
    date Date,
    product_id UInt32,
    order_count UInt64,
    total_quantity UInt64,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, product_id);

-- Materialized view
CREATE MATERIALIZED VIEW daily_sales_mv TO daily_sales AS
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as order_count,
    SUM(quantity) as total_quantity,
    SUM(price * quantity) as total_revenue
FROM orders
GROUP BY date, product_id;

-- Test
INSERT INTO orders VALUES (1, now(), 100, 5, 29.99);
INSERT INTO orders VALUES (2, now(), 100, 3, 29.99);

SELECT * FROM daily_sales;
-- Result: 2024-01-15 | 100 | 2 | 8 | 149.95
```

---

## 2. Multi-Dimensional Aggregation: By Product, Region, Category

**Scenario**: Sales metrics across multiple dimensions

```sql
-- Source with dimensions
CREATE TABLE sales_events (
    timestamp DateTime,
    product_id UInt32,
    product_name String,
    category String,
    region String,
    quantity UInt32,
    price Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY (timestamp, product_id, category, region);

-- Destination: Multi-dimensional aggregates
CREATE TABLE sales_by_dimensions (
    date Date,
    product_id UInt32,
    product_name String,
    category String,
    region String,
    order_count UInt64,
    total_quantity UInt64,
    total_revenue Decimal(18, 2),
    avg_price Decimal(10, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, category, region, product_id);

-- View
CREATE MATERIALIZED VIEW sales_by_dimensions_mv TO sales_by_dimensions AS
SELECT
    toDate(timestamp) as date,
    product_id,
    product_name,
    category,
    region,
    COUNT() as order_count,
    SUM(quantity) as total_quantity,
    SUM(price * quantity) as total_revenue,
    AVG(price) as avg_price
FROM sales_events
GROUP BY date, product_id, product_name, category, region;

-- Query: Sales by category and region
SELECT
    date,
    category,
    region,
    SUM(order_count) as orders,
    SUM(total_revenue) as revenue
FROM sales_by_dimensions
WHERE date >= today() - INTERVAL 7 DAY
GROUP BY date, category, region
ORDER BY date DESC, revenue DESC;
```

---

## 3. Conditional Aggregation: User Segments

**Scenario**: Segment users by activity level in real-time

```sql
-- Source: User events
CREATE TABLE user_events (
    timestamp DateTime,
    user_id UInt32,
    event_type String,
    session_duration UInt32,
    revenue Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY (timestamp, user_id);

-- Destination: User segments
CREATE TABLE user_segments (
    date Date,
    high_activity_users UInt64,      -- 5+ events
    medium_activity_users UInt64,    -- 2-4 events
    low_activity_users UInt64,       -- 1 event
    purchase_active_users UInt64,    -- Users with purchases
    total_unique_users UInt64
) ENGINE = SummingMergeTree()
ORDER BY date;

-- View with conditional aggregation
CREATE MATERIALIZED VIEW user_segments_mv TO user_segments AS
SELECT
    toDate(timestamp) as date,
    countIf(user_id IN (
        SELECT user_id
        FROM user_events
        WHERE toDate(timestamp) = toDate(user_events.timestamp)
        GROUP BY user_id
        HAVING COUNT(*) >= 5
    )) as high_activity_users,
    countIf(user_id IN (
        SELECT user_id
        FROM user_events
        WHERE toDate(timestamp) = toDate(user_events.timestamp)
        GROUP BY user_id
        HAVING COUNT(*) BETWEEN 2 AND 4
    )) as medium_activity_users,
    countIf(user_id IN (
        SELECT user_id
        FROM user_events
        WHERE toDate(timestamp) = toDate(user_events.timestamp)
        GROUP BY user_id
        HAVING COUNT(*) = 1
    )) as low_activity_users,
    countIf(event_type = 'purchase') as purchase_active_users,
    uniq(user_id) as total_unique_users
FROM user_events
GROUP BY date;
```

**Simpler approach with pre-aggregated user activity**:

```sql
-- First aggregation: Count events per user per day
CREATE TABLE daily_user_activity (
    date Date,
    user_id UInt32,
    event_count UInt64,
    has_purchase UInt8,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, user_id);

CREATE MATERIALIZED VIEW daily_user_activity_mv TO daily_user_activity AS
SELECT
    toDate(timestamp) as date,
    user_id,
    COUNT() as event_count,
    max(if(event_type = 'purchase', 1, 0)) as has_purchase,
    SUM(if(event_type = 'purchase', revenue, 0)) as total_revenue
FROM user_events
GROUP BY date, user_id;

-- Second aggregation: Segment users
CREATE TABLE user_segments_v2 (
    date Date,
    segment String,
    user_count UInt64,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, segment);

CREATE MATERIALIZED VIEW user_segments_v2_mv TO user_segments_v2 AS
SELECT
    date,
    CASE
        WHEN event_count >= 5 THEN 'high_activity'
        WHEN event_count BETWEEN 2 AND 4 THEN 'medium_activity'
        WHEN has_purchase = 1 THEN 'purchaser'
        ELSE 'low_activity'
    END as segment,
    COUNT(*) as user_count,
    SUM(total_revenue) as total_revenue
FROM daily_user_activity
GROUP BY date, segment;

-- Query segments
SELECT segment, user_count, total_revenue
FROM user_segments_v2
WHERE date = today()
ORDER BY user_count DESC;
```

---

## 4. Top-K Aggregation: Top Products by Revenue

**Scenario**: Track top 10 products by daily revenue

```sql
-- Using AggregatingMergeTree with topK
CREATE TABLE top_products_daily (
    date Date,
    top_10_products AggregateFunction(topK(10), String)
) ENGINE = AggregatingMergeTree()
ORDER BY date;

CREATE MATERIALIZED VIEW top_products_daily_mv TO top_products_daily AS
SELECT
    toDate(timestamp) as date,
    topKState(10)(product_name) as top_10_products
FROM orders
GROUP BY date;

-- Query: Get top products
SELECT
    date,
    topKMerge(10)(top_10_products) as top_products
FROM top_products_daily
WHERE date >= today() - INTERVAL 7 DAY
ORDER BY date DESC;
```

**With revenue weighting**:

```sql
-- More practical: Top products weighted by revenue
CREATE TABLE top_products_by_revenue (
    date Date,
    product_id UInt32,
    product_name String,
    order_count UInt64,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, total_revenue DESC, product_id);

CREATE MATERIALIZED VIEW top_products_by_revenue_mv TO top_products_by_revenue AS
SELECT
    toDate(timestamp) as date,
    product_id,
    product_name,
    COUNT() as order_count,
    SUM(price * quantity) as total_revenue
FROM orders
GROUP BY date, product_id, product_name;

-- Query: Top 10
SELECT
    date,
    product_id,
    product_name,
    order_count,
    total_revenue
FROM top_products_by_revenue
WHERE date >= today() - INTERVAL 1 DAY
ORDER BY date DESC, total_revenue DESC
LIMIT 10;
```

---

## 5. Real-Time Dashboard Metrics

**Scenario**: Pre-aggregate all dashboard metrics in one view

```sql
-- Dashboard metrics aggregation
CREATE TABLE dashboard_metrics (
    hour DateTime,
    total_events UInt64,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2),
    purchases UInt64,
    avg_order_value Decimal(10, 2),
    p95_response_time AggregateFunction(quantile(0.95), Float32)
) ENGINE = AggregatingMergeTree()
ORDER BY hour;

-- View with all metrics
CREATE MATERIALIZED VIEW dashboard_metrics_mv TO dashboard_metrics AS
SELECT
    toStartOfHour(timestamp) as hour,
    COUNT() as total_events,
    uniqState(user_id) as unique_users,
    SUM(revenue) as total_revenue,
    countIf(event_type = 'purchase') as purchases,
    AVG(if(event_type = 'purchase', revenue, NULL)) as avg_order_value,
    quantileState(0.95)(response_time) as p95_response_time
FROM events
GROUP BY hour;

-- Dashboard query (instant)
SELECT
    hour,
    total_events,
    uniqMerge(unique_users) as unique_users,
    total_revenue,
    purchases,
    avg_order_value,
    quantileMerge(0.95)(p95_response_time) as p95_latency,
    purchases / total_events * 100 as conversion_rate
FROM dashboard_metrics
WHERE hour >= now() - INTERVAL 24 HOUR
ORDER BY hour DESC;
```

---

## 6. Time-Series Downsampling

**Scenario**: Keep high-resolution data recent, low-resolution data old

```sql
-- 1-minute resolution (last 7 days)
CREATE TABLE metrics_1min (
    minute DateTime,
    metric_name String,
    avg_value Float32,
    max_value Float32,
    min_value Float32
) ENGINE = SummingMergeTree()
ORDER BY (metric_name, minute);

CREATE MATERIALIZED VIEW metrics_1min_mv TO metrics_1min AS
SELECT
    toStartOfMinute(timestamp) as minute,
    metric_name,
    AVG(value) as avg_value,
    MAX(value) as max_value,
    MIN(value) as min_value
FROM raw_metrics
WHERE timestamp >= now() - INTERVAL 7 DAY
GROUP BY minute, metric_name;

-- 1-hour resolution (older data)
CREATE TABLE metrics_1hour (
    hour DateTime,
    metric_name String,
    avg_value Float32,
    max_value Float32,
    min_value Float32
) ENGINE = SummingMergeTree()
ORDER BY (metric_name, hour);

CREATE MATERIALIZED VIEW metrics_1hour_mv TO metrics_1hour AS
SELECT
    toStartOfHour(timestamp) as hour,
    metric_name,
    AVG(value) as avg_value,
    MAX(value) as max_value,
    MIN(value) as min_value
FROM raw_metrics
WHERE timestamp < now() - INTERVAL 7 DAY
GROUP BY hour, metric_name;

-- Query combines both resolutions
SELECT minute as time, avg_value FROM metrics_1min
WHERE minute >= now() - INTERVAL 7 DAY
UNION ALL
SELECT hour as time, avg_value FROM metrics_1hour
WHERE hour < now() - INTERVAL 7 DAY
ORDER BY time DESC;
```

---

## 7. Funnel Analysis

**Scenario**: Track conversion funnel stages (view → add to cart → purchase)

```sql
-- User funnel events
CREATE TABLE user_funnel_events (
    timestamp DateTime,
    user_id UInt32,
    event_stage String  -- 'view', 'cart', 'purchase'
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp);

-- Funnel aggregation
CREATE TABLE funnel_analysis (
    date Date,
    stage String,
    unique_users AggregateFunction(uniq, UInt32),
    event_count UInt64
) ENGINE = AggregatingMergeTree()
ORDER BY (date, stage);

CREATE MATERIALIZED VIEW funnel_analysis_mv TO funnel_analysis AS
SELECT
    toDate(timestamp) as date,
    event_stage as stage,
    uniqState(user_id) as unique_users,
    COUNT() as event_count
FROM user_funnel_events
GROUP BY date, event_stage;

-- Query: Funnel conversion rates
SELECT
    date,
    uniqMerge(unique_users) as users,
    event_count,
    ROUND(100.0 * event_count / (
        SELECT SUM(event_count)
        FROM funnel_analysis
        WHERE date = funnel_analysis.date
          AND stage = 'view'
    ), 2) as percent_of_views
FROM funnel_analysis
WHERE date >= today() - INTERVAL 30 DAY
ORDER BY date DESC,
    CASE WHEN stage = 'view' THEN 1
         WHEN stage = 'cart' THEN 2
         WHEN stage = 'purchase' THEN 3
    END;
```

---

## 8. Chained Views: Hour → Day → Month

**Scenario**: Build hierarchical aggregations to reduce computation

```sql
-- Level 1: Raw events
CREATE TABLE events (...) ENGINE = MergeTree() ORDER BY (timestamp, product_id);

-- Level 2: Hourly aggregation
CREATE TABLE hourly_stats (
    hour DateTime,
    product_id UInt32,
    sales_count UInt64,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (hour, product_id);

CREATE MATERIALIZED VIEW hourly_stats_mv TO hourly_stats AS
SELECT
    toStartOfHour(timestamp) as hour,
    product_id,
    COUNT() as sales_count,
    SUM(revenue) as total_revenue
FROM events
GROUP BY hour, product_id;

-- Level 3: Daily aggregation (from hourly, not raw)
CREATE TABLE daily_stats (
    date Date,
    product_id UInt32,
    sales_count UInt64,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, product_id);

CREATE MATERIALIZED VIEW daily_stats_mv TO daily_stats AS
SELECT
    toDate(hour) as date,
    product_id,
    SUM(sales_count) as sales_count,
    SUM(total_revenue) as total_revenue
FROM hourly_stats
GROUP BY date, product_id;

-- Level 4: Monthly aggregation (from daily)
CREATE TABLE monthly_stats (
    month Date,
    product_id UInt32,
    sales_count UInt64,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (month, product_id);

CREATE MATERIALIZED VIEW monthly_stats_mv TO monthly_stats AS
SELECT
    toStartOfMonth(date) as month,
    product_id,
    SUM(sales_count) as sales_count,
    SUM(total_revenue) as total_revenue
FROM daily_stats
GROUP BY month, product_id;

-- Benefits:
-- - Raw events processed once for hourly
-- - Hourly data processed for daily
-- - Daily data processed for monthly
-- - Each level optimized for query patterns
```

---

## 9. Filtering in Views

**Scenario**: Only aggregate specific event types

```sql
-- Aggregate only purchase events
CREATE TABLE purchase_metrics (
    date Date,
    product_id UInt32,
    purchase_count UInt64,
    total_amount Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, product_id);

CREATE MATERIALIZED VIEW purchase_metrics_mv TO purchase_metrics AS
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as purchase_count,
    SUM(amount) as total_amount
FROM events
WHERE event_type = 'purchase'  -- Filter in view
GROUP BY date, product_id;

-- Aggregate view events separately
CREATE TABLE view_metrics (
    date Date,
    product_id UInt32,
    view_count UInt64
) ENGINE = SummingMergeTree()
ORDER BY (date, product_id);

CREATE MATERIALIZED VIEW view_metrics_mv TO view_metrics AS
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as view_count
FROM events
WHERE event_type = 'view'
GROUP BY date, product_id;

-- Query: Calculate conversion rate
SELECT
    p.date,
    p.product_id,
    p.purchase_count,
    v.view_count,
    ROUND(100.0 * p.purchase_count / v.view_count, 2) as conversion_rate
FROM purchase_metrics p
LEFT JOIN view_metrics v USING (date, product_id)
WHERE p.date >= today() - INTERVAL 30 DAY
ORDER BY conversion_rate DESC;
```

---

## 10. Complex Aggregates with State/Merge

**Scenario**: Track multiple advanced aggregates (unique users, percentiles, top-K)

```sql
-- Comprehensive analytics
CREATE TABLE analytics (
    date Date,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2),
    avg_transaction_value Decimal(10, 2),
    p95_latency AggregateFunction(quantile(0.95), Float32),
    p99_latency AggregateFunction(quantile(0.99), Float32),
    top_products AggregateFunction(topK(5), String)
) ENGINE = AggregatingMergeTree()
ORDER BY date;

CREATE MATERIALIZED VIEW analytics_mv TO analytics AS
SELECT
    toDate(timestamp) as date,
    uniqState(user_id) as unique_users,
    SUM(revenue) as total_revenue,
    AVG(revenue) as avg_transaction_value,
    quantileState(0.95)(response_time) as p95_latency,
    quantileState(0.99)(response_time) as p99_latency,
    topKState(5)(product_name) as top_products
FROM events
GROUP BY date;

-- Query all metrics
SELECT
    date,
    uniqMerge(unique_users) as daily_active_users,
    total_revenue,
    avg_transaction_value,
    quantileMerge(0.95)(p95_latency) as p95,
    quantileMerge(0.99)(p99_latency) as p99,
    topKMerge(5)(top_products) as top_5_products
FROM analytics
WHERE date >= today() - INTERVAL 7 DAY
ORDER BY date DESC;
```

---

## 11. Multi-Destination Routing

**Scenario**: Route data to multiple aggregation tables based on value

```sql
-- High-value orders (> $1000)
CREATE TABLE high_value_orders (
    order_id UInt64,
    timestamp DateTime,
    customer_id UInt32,
    total_amount Decimal(18, 2)
) ENGINE = MergeTree()
ORDER BY (timestamp, customer_id);

CREATE MATERIALIZED VIEW high_value_orders_mv TO high_value_orders AS
SELECT *
FROM orders
WHERE total_amount > 1000;

-- Medium-value orders ($100-$1000)
CREATE TABLE medium_value_orders (
    order_id UInt64,
    timestamp DateTime,
    customer_id UInt32,
    total_amount Decimal(18, 2)
) ENGINE = MergeTree()
ORDER BY (timestamp, customer_id);

CREATE MATERIALIZED VIEW medium_value_orders_mv TO medium_value_orders AS
SELECT *
FROM orders
WHERE total_amount BETWEEN 100 AND 1000;

-- All orders (for complete record)
CREATE TABLE all_orders (
    order_id UInt64,
    timestamp DateTime,
    customer_id UInt32,
    total_amount Decimal(18, 2)
) ENGINE = MergeTree()
ORDER BY (timestamp, customer_id);

CREATE MATERIALIZED VIEW all_orders_mv TO all_orders AS
SELECT * FROM orders;
```

---

## Best Practices Summary

1. **Choose appropriate destination engine**: SummingMergeTree for simple aggregates, AggregatingMergeTree for complex ones

2. **Design ORDER BY for query patterns**: Group columns used in WHERE clauses together

3. **Keep views focused**: One view, one responsibility

4. **Chain views**: Don't re-process raw data for multiple aggregation levels

5. **Test with sample data**: Always verify view works before production use

6. **Monitor performance**: Use system.query_log to find slow views

7. **Use POPULATE carefully**: Can be expensive on large source tables

8. **Include necessary columns**: Store both aggregates and raw values when needed for flexibility
