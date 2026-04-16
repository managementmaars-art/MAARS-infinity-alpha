# State/Merge Functions Reference for AggregatingMergeTree

Complete reference for all State/Merge function pairs used with `AggregatingMergeTree`.

## Function Pair Pattern

Every aggregate function has three forms:

1. **Regular Form** (for normal queries):
   ```sql
   SELECT uniq(user_id), sum(revenue), quantile(0.95)(response_time) FROM ...
   ```

2. **State Form** (in materialized views):
   ```sql
   SELECT uniqState(user_id), sumState(revenue), quantileState(0.95)(response_time) FROM ...
   ```

3. **Merge Form** (in queries on aggregated data):
   ```sql
   SELECT uniqMerge(user_count), sumMerge(revenue), quantileMerge(0.95)(latency) FROM ...
   ```

---

## Complete Function Reference

### Basic Count and Sum Functions

#### COUNT()

**Table Definition**:
```sql
CREATE TABLE event_counts (
    date Date,
    event_count AggregateFunction(count)
) ENGINE = AggregatingMergeTree() ORDER BY date;
```

**View**:
```sql
CREATE MATERIALIZED VIEW event_counts_mv TO event_counts AS
SELECT
    toDate(timestamp) as date,
    countState() as event_count
FROM events
GROUP BY date;
```

**Query**:
```sql
SELECT
    date,
    countMerge(event_count) as total_events
FROM event_counts
GROUP BY date;
```

---

#### SUM(x)

**Table Definition**:
```sql
CREATE TABLE revenue_totals (
    date Date,
    total_revenue AggregateFunction(sum, Decimal(18, 2))
) ENGINE = AggregatingMergeTree() ORDER BY date;
```

**View**:
```sql
CREATE MATERIALIZED VIEW revenue_totals_mv TO revenue_totals AS
SELECT
    toDate(timestamp) as date,
    sumState(price * quantity) as total_revenue
FROM orders
GROUP BY date;
```

**Query**:
```sql
SELECT
    date,
    sumMerge(total_revenue) as revenue
FROM revenue_totals
GROUP BY date;
```

---

#### AVG(x)

**Table Definition**:
```sql
CREATE TABLE average_prices (
    category String,
    avg_price AggregateFunction(avg, Decimal(10, 2))
) ENGINE = AggregatingMergeTree() ORDER BY category;
```

**View**:
```sql
CREATE MATERIALIZED VIEW average_prices_mv TO average_prices AS
SELECT
    category,
    avgState(price) as avg_price
FROM products
GROUP BY category;
```

**Query**:
```sql
SELECT
    category,
    avgMerge(avg_price) as average_price
FROM average_prices
GROUP BY category;
```

---

#### MIN(x) and MAX(x)

**Table Definition**:
```sql
CREATE TABLE price_ranges (
    category String,
    min_price AggregateFunction(min, Decimal(10, 2)),
    max_price AggregateFunction(max, Decimal(10, 2))
) ENGINE = AggregatingMergeTree() ORDER BY category;
```

**View**:
```sql
CREATE MATERIALIZED VIEW price_ranges_mv TO price_ranges AS
SELECT
    category,
    minState(price) as min_price,
    maxState(price) as max_price
FROM products
GROUP BY category;
```

**Query**:
```sql
SELECT
    category,
    minMerge(min_price) as min_price,
    maxMerge(max_price) as max_price
FROM price_ranges
GROUP BY category;
```

---

### Unique Counting Functions

#### uniq(x) - HyperLogLog (Recommended)

Fast approximate unique count using HyperLogLog algorithm.

**Table Definition**:
```sql
CREATE TABLE daily_unique_users (
    date Date,
    unique_user_count AggregateFunction(uniq, UInt32)
) ENGINE = AggregatingMergeTree() ORDER BY date;
```

**View**:
```sql
CREATE MATERIALIZED VIEW daily_unique_users_mv TO daily_unique_users AS
SELECT
    toDate(timestamp) as date,
    uniqState(user_id) as unique_user_count
FROM events
GROUP BY date;
```

**Query**:
```sql
SELECT
    date,
    uniqMerge(unique_user_count) as unique_users
FROM daily_unique_users
GROUP BY date
ORDER BY date;
```

**Accuracy**:
- Typical error: 1-2%
- Fast, memory-efficient
- Best for large datasets

---

#### uniqExact(x) - Exact Unique Count

Exact unique count (slower, more memory).

**Table Definition**:
```sql
CREATE TABLE exact_unique_users (
    date Date,
    unique_user_count AggregateFunction(uniqExact, UInt32)
) ENGINE = AggregatingMergeTree() ORDER BY date;
```

**View**:
```sql
CREATE MATERIALIZED VIEW exact_unique_users_mv TO exact_unique_users AS
SELECT
    toDate(timestamp) as date,
    uniqExactState(user_id) as unique_user_count
FROM events
GROUP BY date;
```

**Query**:
```sql
SELECT
    date,
    uniqExactMerge(unique_user_count) as unique_users
FROM exact_unique_users
GROUP BY date;
```

**When to Use**:
- Small datasets (< 100K unique values)
- Require exact accuracy
- Memory is not constrained

---

#### uniqCombined(x) - Hybrid Approach

Combines exact counting for small sets with HyperLogLog for large sets.

**View**:
```sql
CREATE MATERIALIZED VIEW combined_unique_users_mv AS
SELECT
    toDate(timestamp) as date,
    uniqCombinedState(user_id) as unique_user_count
FROM events
GROUP BY date;
```

**Query**:
```sql
SELECT
    date,
    uniqCombinedMerge(unique_user_count) as unique_users
FROM combined_unique_users;
```

---

### Percentile and Quantile Functions

#### quantile(x) - Single Quantile

Calculate a specific percentile (e.g., p95).

**Table Definition**:
```sql
CREATE TABLE response_time_percentiles (
    hour DateTime,
    p95_latency AggregateFunction(quantile(0.95), Float32),
    p99_latency AggregateFunction(quantile(0.99), Float32)
) ENGINE = AggregatingMergeTree() ORDER BY hour;
```

**View**:
```sql
CREATE MATERIALIZED VIEW response_time_percentiles_mv TO response_time_percentiles AS
SELECT
    toStartOfHour(timestamp) as hour,
    quantileState(0.95)(response_time) as p95_latency,
    quantileState(0.99)(response_time) as p99_latency
FROM requests
GROUP BY hour;
```

**Query**:
```sql
SELECT
    hour,
    quantileMerge(0.95)(p95_latency) as p95,
    quantileMerge(0.99)(p99_latency) as p99
FROM response_time_percentiles
WHERE hour >= now() - INTERVAL 24 HOUR
ORDER BY hour;
```

**Common Percentiles**:
- 0.50: Median (p50)
- 0.95: 95th percentile (p95)
- 0.99: 99th percentile (p99)
- 0.999: 99.9th percentile (p999)

---

#### quantiles(x) - Multiple Quantiles

Calculate multiple percentiles in one call.

**Table Definition**:
```sql
CREATE TABLE percentile_ranges (
    metric_name String,
    percentiles AggregateFunction(quantiles(0.50, 0.95, 0.99), Float32)
) ENGINE = AggregatingMergeTree() ORDER BY metric_name;
```

**View**:
```sql
CREATE MATERIALIZED VIEW percentile_ranges_mv TO percentile_ranges AS
SELECT
    'request_latency' as metric_name,
    quantilesState(0.50, 0.95, 0.99)(response_time) as percentiles
FROM requests
GROUP BY metric_name;
```

**Query**:
```sql
SELECT
    metric_name,
    quantilesMerge(0.50, 0.95, 0.99)(percentiles) as [p50, p95, p99]
FROM percentile_ranges
GROUP BY metric_name;
```

---

#### quantileDeterministic(level)(x) - Deterministic Quantile

Quantile with deterministic results for testing/reproducibility.

**View**:
```sql
CREATE MATERIALIZED VIEW deterministic_percentiles_mv AS
SELECT
    toStartOfHour(timestamp) as hour,
    quantileDeterministicState(0.95)(response_time) as p95_latency
FROM requests
GROUP BY hour;
```

---

### Top-K Functions

#### topK(k)(x) - Top-K Elements

Track the top K most frequent values.

**Table Definition**:
```sql
CREATE TABLE top_products_daily (
    date Date,
    top_10_products AggregateFunction(topK(10), String)
) ENGINE = AggregatingMergeTree() ORDER BY date;
```

**View**:
```sql
CREATE MATERIALIZED VIEW top_products_daily_mv TO top_products_daily AS
SELECT
    toDate(timestamp) as date,
    topKState(10)(product_name) as top_10_products
FROM orders
GROUP BY date;
```

**Query**:
```sql
SELECT
    date,
    topKMerge(10)(top_10_products) as top_products
FROM top_products_daily
ORDER BY date;
```

**Result Format**:
Returns array of top K elements with their frequencies:
```
['Product A', 'Product B', 'Product C']
```

---

#### topKWeighted(k)(x, weight) - Top-K with Weights

Top-K considering weights/scores.

**View**:
```sql
CREATE MATERIALIZED VIEW top_products_by_revenue_mv AS
SELECT
    toDate(timestamp) as date,
    topKWeightedState(10)(product_name, revenue) as top_products_by_revenue
FROM orders
GROUP BY date;
```

**Query**:
```sql
SELECT
    date,
    topKWeightedMerge(10)(top_products_by_revenue) as top_products
FROM top_products_by_revenue
ORDER BY date;
```

---

### Array Aggregation Functions

#### groupArray(x) - Collect All Values

Collects all values into an array.

**Table Definition**:
```sql
CREATE TABLE order_items (
    order_id UInt32,
    product_ids AggregateFunction(groupArray, UInt32)
) ENGINE = AggregatingMergeTree() ORDER BY order_id;
```

**View**:
```sql
CREATE MATERIALIZED VIEW order_items_mv TO order_items AS
SELECT
    order_id,
    groupArrayState(product_id) as product_ids
FROM order_details
GROUP BY order_id;
```

**Query**:
```sql
SELECT
    order_id,
    groupArrayMerge(product_ids) as all_products
FROM order_items
GROUP BY order_id;
```

---

#### groupArraySorted(limit)(x) - Limited Sorted Array

Collect top-N values (memory-bounded).

**View**:
```sql
CREATE MATERIALIZED VIEW top_prices_mv AS
SELECT
    category,
    groupArraySortedState(10)(price) as top_10_prices
FROM products
GROUP BY category;
```

---

### Statistical Functions

#### stddevPop(x) - Population Standard Deviation

**View**:
```sql
CREATE MATERIALIZED VIEW price_variability_mv AS
SELECT
    category,
    stddevPopState(price) as price_stddev
FROM products
GROUP BY category;
```

**Query**:
```sql
SELECT
    category,
    stddevPopMerge(price_stddev) as stddev
FROM price_variability
GROUP BY category;
```

---

#### varPop(x) - Population Variance

**View**:
```sql
CREATE MATERIALIZED VIEW variance_mv AS
SELECT
    category,
    varPopState(price) as price_variance
FROM products
GROUP BY category;
```

---

### Tuple Functions for Multiple Aggregates

#### sumMap(keys, values) - Aggregated Map

Aggregate maps by summing values for matching keys.

**View**:
```sql
CREATE MATERIALIZED VIEW category_sales_mv AS
SELECT
    date,
    sumMapState(array(category), array(sales)) as category_sales_map
FROM sales
GROUP BY date;
```

---

## Combining Multiple Aggregates in Single View

**Example: Comprehensive Analytics View**

```sql
CREATE TABLE comprehensive_analytics (
    date Date,
    event_count AggregateFunction(count),
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue AggregateFunction(sum, Decimal(18, 2)),
    avg_order_value AggregateFunction(avg, Decimal(10, 2)),
    p95_latency AggregateFunction(quantile(0.95), Float32),
    top_products AggregateFunction(topK(5), String)
) ENGINE = AggregatingMergeTree() ORDER BY date;

CREATE MATERIALIZED VIEW comprehensive_analytics_mv TO comprehensive_analytics AS
SELECT
    toDate(timestamp) as date,
    countState() as event_count,
    uniqState(user_id) as unique_users,
    sumState(revenue) as total_revenue,
    avgState(order_value) as avg_order_value,
    quantileState(0.95)(response_time) as p95_latency,
    topKState(5)(product_name) as top_products
FROM events
GROUP BY date;

-- Query with multiple Merge functions
SELECT
    date,
    countMerge(event_count) as total_events,
    uniqMerge(unique_users) as daily_users,
    sumMerge(total_revenue) as revenue,
    avgMerge(avg_order_value) as avg_value,
    quantileMerge(0.95)(p95_latency) as latency_p95,
    topKMerge(5)(top_products) as top_5_products
FROM comprehensive_analytics
WHERE date >= today() - INTERVAL 7 DAY
ORDER BY date DESC;
```

---

## State Function Quick Reference Table

| Aggregate | Regular | State | Merge |
|-----------|---------|-------|-------|
| COUNT() | count() | countState() | countMerge() |
| SUM(x) | sum(x) | sumState(x) | sumMerge() |
| AVG(x) | avg(x) | avgState(x) | avgMerge() |
| MIN(x) | min(x) | minState(x) | minMerge() |
| MAX(x) | max(x) | maxState(x) | maxMerge() |
| uniq(x) | uniq(x) | uniqState(x) | uniqMerge() |
| uniqExact(x) | uniqExact(x) | uniqExactState(x) | uniqExactMerge() |
| uniqCombined(x) | uniqCombined(x) | uniqCombinedState(x) | uniqCombinedMerge() |
| quantile(p)(x) | quantile(p)(x) | quantileState(p)(x) | quantileMerge(p)() |
| quantiles(ps)(x) | quantiles(ps)(x) | quantilesState(ps)(x) | quantilesMerge(ps)() |
| topK(k)(x) | topK(k)(x) | topKState(k)(x) | topKMerge(k)() |
| topKWeighted(k)(x, w) | topKWeighted(k)(x, w) | topKWeightedState(k)(x, w) | topKWeightedMerge(k)() |
| groupArray(x) | groupArray(x) | groupArrayState(x) | groupArrayMerge() |
| stddevPop(x) | stddevPop(x) | stddevPopState(x) | stddevPopMerge() |
| varPop(x) | varPop(x) | varPopState(x) | varPopMerge() |

