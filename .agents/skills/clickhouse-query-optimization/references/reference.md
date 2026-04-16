# ClickHouse Query Optimization - Advanced Reference

## Index Selection Matrix

Use this matrix to choose the right index type for your filtering column:

| Column Type | Filtering Pattern | Recommended Index | Selectivity | Example |
|-------------|------------------|-------------------|-------------|---------|
| Numeric (UInt, Int, Float) | Range: `>`, `<`, `>=`, `<=` | minmax | Medium-High | `session_duration > 300` |
| Date/DateTime | Range: `>=`, `<`, `BETWEEN` | minmax | Medium-High | `timestamp >= '2024-01-01'` |
| String (Low Cardinality) | Equality: `=`, `IN` | set(N) | Medium | `country = 'US'` |
| String (High Cardinality) | Equality: `=` | bloom_filter | Low-Medium | `url = 'https://...'` |
| String (Any) | Substring: `LIKE '%...'` | ngrambf_v1 | Low-Medium | `message LIKE '%error%'` |
| Enum | Equality: `=`, `IN` | set(N) | Medium-High | `event_type IN ('purchase', 'view')` |

**Selectivity definitions**:
- High: Filter eliminates 90%+ of data
- Medium: Filter eliminates 50-90% of data
- Low: Filter eliminates < 50% of data

**Rule**: Only add indexes for Medium or High selectivity columns.

## EXPLAIN Output Reference

### Understanding EXPLAIN Output

```sql
EXPLAIN SELECT user_id, COUNT()
FROM events
WHERE user_id = 12345
GROUP BY user_id;
```

**Key sections**:

1. **Expression**: The operation being performed (SELECT, WHERE, GROUP BY)
2. **Sorting Key**: The primary key of the table
3. **Filter Expression**: Conditions in WHERE/PREWHERE clause
4. **Partitions**: How many partitions are scanned

### Reading the Plan

Look for these indicators of good optimization:

```
✅ GOOD:
- Partitions: 1/12 (reads only 1 of 12 partitions - partition pruning works)
- Filter Expression: Uses primary key columns
- Index: Granules read (sparse index working)

❌ BAD:
- Partitions: 12/12 (reads all partitions - no partition pruning)
- Filter Expression: Column not in primary key
- Index: Reading granule minmax (full table scan)
```

### Common EXPLAIN Patterns

#### Pattern 1: Full Table Scan (Slow)
```
Expression: SELECT user_id, COUNT()
Filter Expression: (toUInt32(product_id) = 789)
Partitions: 12/12
Granules: 1500/1500

❌ Problem: Reading all partitions and granules
✅ Solution: Add data skipping index on product_id
```

#### Pattern 2: Partition Pruning Works (Good)
```
Expression: SELECT user_id, COUNT()
Filter Expression: (timestamp >= Date('2024-01-01'))
Partitions: 1/12
Granules: 45/1500

✅ Good: Partition pruning reduced partitions
✅ Sparse index reduced granules to read
```

#### Pattern 3: Primary Key Index Used (Excellent)
```
Expression: SELECT user_id, COUNT()
Filter Expression: (user_id = UInt32(12345))
Partitions: 12/12
Granules: 3/1500

✅ Excellent: Sparse index is very selective
Reading only 3 of 1500 granules (0.2% of data)
```

## Data Skipping Index Granularity Guide

The `GRANULARITY` parameter controls the block size for index storage:

```sql
ALTER TABLE events ADD INDEX idx_name column_name TYPE minmax GRANULARITY N;
```

### Granularity Impact

| Granularity | Block Rows (with default 8192 granule size) | Index Precision | Use Case |
|-------------|----------------------------------------------|-----------------|----------|
| 1 | 8,192 | Very high (most precise) | High-cardinality, low-selectivity filters |
| 2 | 16,384 | High | Medium-cardinality columns |
| 4 | 32,768 | Medium | Balanced (most common) |
| 8 | 65,536 | Low | Low-cardinality, high-selectivity filters |
| 16 | 131,072 | Very low | Large tables with predictable patterns |

**Default (4) is optimal for most cases** - balances precision and index size.

## Index Selection Decision Tree

```
Question 1: Is the column in my primary key?
  ├─ YES → Don't add index (primary index is sufficient)
  └─ NO → Continue to Question 2

Question 2: What type of filter do I apply?
  ├─ Range (>, <, >=, <=, BETWEEN)
  │   └─ Column type: Numeric/Date?
  │       ├─ YES → Use minmax
  │       └─ NO → Go to Q3
  │
  ├─ Equality (=, IN, NOT IN)
  │   └─ Cardinality: Low/Medium (< 1000 unique)?
  │       ├─ YES → Use set(N) where N = max unique
  │       └─ NO → Continue to Q3
  │
  └─ Substring (LIKE, hasToken)
      └─ Use ngrambf_v1

Question 3: High-cardinality string column?
  └─ Use bloom_filter(false_positive_rate)
     └─ Rate: 0.01 (1%) for most cases, 0.001 (0.1%) for critical
```

## Primary Key Design Patterns

### Pattern 1: Time-Series by User (Most Common)

```sql
-- Use case: User behavior analytics
ORDER BY (user_id, timestamp)

-- Fast queries:
-- - WHERE user_id = X
-- - WHERE user_id = X AND timestamp > Y
-- - WHERE user_id IN (1, 2, 3) AND timestamp BETWEEN X AND Y

-- Slow queries:
-- - WHERE timestamp > Y (full scan)
-- - WHERE event_type = 'purchase' (full scan)
```

**Add indexes**:
```sql
ALTER TABLE user_events ADD INDEX idx_event_type event_type TYPE set(50) GRANULARITY 4;
ALTER TABLE user_events ADD INDEX idx_timestamp timestamp TYPE minmax GRANULARITY 4;
```

### Pattern 2: Product Analytics (Low → High Cardinality)

```sql
-- Use case: E-commerce product reporting
ORDER BY (category, product_id, timestamp)

-- Fast queries:
-- - WHERE category = 'Electronics'
-- - WHERE category = 'Electronics' AND product_id = 789
-- - WHERE category = 'Electronics' AND timestamp > '2024-01-01'

-- Slow queries:
-- - WHERE product_id = 789 (missing category prefix)
-- - WHERE timestamp > '2024-01-01' (missing category prefix)
```

### Pattern 3: Multi-Dimensional Analytics (Explicit PRIMARY KEY)

```sql
-- Full sort order optimizes for cache
ORDER BY (country, date, user_id, event_id)

-- Smaller index optimizes for memory
PRIMARY KEY (country, date)

-- Fast queries:
-- - WHERE country = 'US' AND date = '2024-01-15'
-- - Uses compact (country, date) index
-- - Reads sorted by user_id, event_id (good cache locality)
```

## Query Optimization Checklist

### Before Optimization

- [ ] Run `EXPLAIN` to see current plan
- [ ] Check `system.query_log` for baseline metrics (duration, rows read)
- [ ] Identify bottleneck (partition pruning? sparse index? aggregation?)

### Design Phase

- [ ] Primary key: Low cardinality → High cardinality?
- [ ] Primary key: Filters by prefix in typical queries?
- [ ] Data skipping indexes: Added for commonly filtered non-primary columns?
- [ ] Partitions: Time-based with manageable count (< 1,000)?

### Query Optimization

- [ ] `PREWHERE`: Filters small columns before large columns?
- [ ] Column selection: `SELECT` only needed columns?
- [ ] Approximate functions: Using `uniq()` instead of `COUNT(DISTINCT)`?
- [ ] GROUP BY order: Low cardinality columns first?
- [ ] JOINs: Small table first (builds hash table)?

### Projection Strategy

- [ ] Different query patterns need projections? (e.g., both user_id and product_id filters)
- [ ] Repeated aggregations can be pre-computed?

### Verification

- [ ] `EXPLAIN` shows reduced partition/granule count?
- [ ] `system.query_log` shows improved metrics (lower read_rows, faster duration)?
- [ ] No unexpected memory growth from indexes?

## Common EXPLAIN Warnings

### Warning 1: "Reading the whole partition"

```
Filter Expression: (status = 'cancelled')
Partitions: 12/12
Granules: 1500/1500
```

**Problem**: No partition or index pruning
**Solution**: Add data skipping index on `status` column

```sql
ALTER TABLE orders ADD INDEX idx_status status TYPE set(10) GRANULARITY 4;
```

### Warning 2: "Primary key prefix not used"

```
Filter Expression: (product_id = 789)
-- But primary key is ORDER BY (user_id, timestamp, product_id)
```

**Problem**: Filter doesn't use primary key prefix (missing user_id)
**Solution**: Add data skipping index or add projection

```sql
ALTER TABLE orders ADD INDEX idx_product product_id TYPE minmax GRANULARITY 4;
-- Or add projection for product-first queries
ALTER TABLE orders ADD PROJECTION proj_by_product (
    SELECT * ORDER BY (product_id, timestamp)
);
```

### Warning 3: "SELECT * reading unnecessary columns"

```
Expression: SELECT *
-- Query only needs user_id and timestamp
```

**Problem**: Reading all columns from disk
**Solution**: Select only needed columns

```sql
-- Bad
SELECT * FROM orders WHERE user_id = 12345;

-- Good
SELECT user_id, timestamp, status FROM orders WHERE user_id = 12345;
```

## Performance Metrics to Monitor

Track these metrics in `system.query_log`:

| Metric | Good Range | Warning | Critical |
|--------|-----------|---------|----------|
| `read_rows` | < 100K | 100K-10M | > 10M |
| `read_bytes` | < 100MB | 100MB-1GB | > 1GB |
| `query_duration_ms` | < 100ms | 100ms-1s | > 1s |
| `memory_usage` | < 100MB | 100MB-500MB | > 500MB |
| `partitions_scanned` | 1-5 | 5-20 | > 20 |
| `granules_scanned` | < 100 | 100-1000 | > 1000 |

**Ratio Analysis**:
- `read_rows / total_rows`: Should be < 1% for well-optimized queries
- `read_bytes / query_duration_ms`: Throughput (MB/s) - higher is better

## Materialized Columns and Computed Indexes

Pre-compute expensive transformations to avoid repeated calculation:

```sql
-- Add materialized column
ALTER TABLE events ADD COLUMN event_date Date MATERIALIZED toDate(timestamp);

-- Add index on materialized column
ALTER TABLE events ADD INDEX idx_event_date event_date TYPE minmax GRANULARITY 4;

-- Query uses materialized column (no computation needed)
SELECT COUNT() FROM events WHERE event_date = '2024-01-15';
-- Faster than: WHERE toDate(timestamp) = '2024-01-15'
```

**Trade-off**: Slower inserts, faster queries.

## Bloom Filter Parameters

```sql
ALTER TABLE logs ADD INDEX idx_url url TYPE bloom_filter(false_positive_rate) GRANULARITY N;
```

**False positive rate selection**:
- `0.01` (1%): Standard choice - 99% accuracy, reasonable index size
- `0.001` (0.1%): Higher precision, larger index, more CPU
- `0.1` (10%): Lower precision, smaller index, faster processing

**Example**:
```sql
-- Standard: 1% false positive
ALTER TABLE events ADD INDEX idx_url url TYPE bloom_filter(0.01) GRANULARITY 4;

-- Critical equality: 0.1% false positive
ALTER TABLE transactions ADD INDEX idx_txn_id txn_id TYPE bloom_filter(0.001) GRANULARITY 4;

-- Exploratory: 10% false positive
ALTER TABLE logs ADD INDEX idx_request_id request_id TYPE bloom_filter(0.1) GRANULARITY 8;
```

## ngrambf_v1 Parameters

```sql
ALTER TABLE logs ADD INDEX idx_message message TYPE ngrambf_v1(n_gram_size, bloom_filter_size, num_hashes, seed) GRANULARITY N;
```

**Parameters**:
- `n_gram_size`: Break strings into substrings of length N (default: 4)
- `bloom_filter_size`: Size of Bloom filter in bytes (default: 512)
- `num_hashes`: Number of hash functions (default: 3)
- `seed`: Random seed for hash functions (default: 0)

**Examples**:
```sql
-- Standard substring search
ALTER TABLE logs ADD INDEX idx_message message TYPE ngrambf_v1(4, 512, 3, 0) GRANULARITY 1;

-- Very sensitive substring search (large strings)
ALTER TABLE logs ADD INDEX idx_body body TYPE ngrambf_v1(3, 1024, 4, 0) GRANULARITY 1;

-- Token-based search
ALTER TABLE logs ADD INDEX idx_tag tag TYPE ngrambf_v1(5, 256, 2, 0) GRANULARITY 2;
```

## Partition TTL Configuration

Automatically delete old data based on partition age:

```sql
-- Delete partitions older than 90 days
ALTER TABLE events MODIFY TTL timestamp + INTERVAL 90 DAY;

-- Delete partitions older than 1 year
ALTER TABLE events MODIFY TTL created_at + INTERVAL 1 YEAR;

-- Check TTL status
SELECT
    partition_key,
    partition,
    min_date,
    max_date,
    partition_value
FROM system.parts
WHERE table = 'events'
ORDER BY partition DESC;
```

**Rules**:
- TTL is checked during merges (not immediately)
- Set to table maintenance window if possible
- Monitor storage with `system.parts` table

## Query Rewrite Patterns

### Pattern 1: GROUP BY Optimization

```sql
-- Bad: High-cardinality GROUP BY
SELECT url, COUNT() FROM events GROUP BY url;
-- Memory usage proportional to unique URLs (millions?)

-- Good: LIMIT or approximate
SELECT topK(1000)(url) FROM events;
-- Constant memory for top 1000 values

-- Or:
SELECT url, COUNT() FROM events GROUP BY url LIMIT 1000;
-- Returns top 1000 most frequent URLs
```

### Pattern 2: JOIN Optimization

```sql
-- Bad: Large table first
SELECT *
FROM large_orders l (1 billion rows)
JOIN small_customers s (1 million rows) ON l.customer_id = s.id;

-- Good: Small table first (builds hash table first)
SELECT *
FROM small_customers s (1 million rows)
JOIN large_orders l (1 billion rows) ON s.id = l.customer_id;
-- Hash table built on 1M rows, then probed 1B times
```

### Pattern 3: Filtering Optimization

```sql
-- Bad: Multiple filters in WHERE
SELECT user_id, COUNT()
FROM events
WHERE timestamp >= '2024-01-01' AND
      country = 'US' AND
      properties LIKE '%premium%' AND
      session_duration > 300
GROUP BY user_id;

-- Good: Early filtering in PREWHERE
SELECT user_id, COUNT()
FROM events
PREWHERE timestamp >= '2024-01-01' AND country = 'US' AND session_duration > 300
WHERE properties LIKE '%premium%'
GROUP BY user_id;
-- Reads small columns first, then large columns only for matches
```

## Storage and Index Size Monitoring

```sql
-- Check table size and part count
SELECT
    table,
    partition,
    bytes as total_bytes,
    rows,
    uncompressed_bytes,
    count() as part_count
FROM system.parts
WHERE table = 'events' AND database = 'default'
GROUP BY table, partition
ORDER BY bytes DESC;

-- Check index effectiveness
SELECT
    name as index_name,
    type as index_type,
    bytes as index_bytes
FROM system.data_skipping_indexes
WHERE table = 'events';

-- Estimate index overhead
SELECT
    sum(bytes) as total_data_bytes,
    (SELECT sum(bytes) FROM system.data_skipping_indexes WHERE table = 'events') as total_index_bytes,
    (SELECT sum(bytes) FROM system.data_skipping_indexes WHERE table = 'events') / sum(bytes) * 100 as index_overhead_percent
FROM system.parts
WHERE table = 'events';
```
