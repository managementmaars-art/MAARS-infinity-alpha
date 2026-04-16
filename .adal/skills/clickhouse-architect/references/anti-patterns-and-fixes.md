**Skill**: [ClickHouse Architect](../SKILL.md)

# Anti-Patterns and Fixes

<!-- ADR: 2025-12-09-clickhouse-architect-skill -->

The "13 Deadly Sins" of ClickHouse with v24.4+ status and modern fixes.

## Overview

Some traditional anti-patterns have been significantly improved in v24.4+:

| Pattern             | Traditional Status | v24.4+ Status      |
| ------------------- | ------------------ | ------------------ |
| Large JOINs         | Avoid              | **180x improved**  |
| Mutations           | Avoid              | **1700x improved** |
| Other anti-patterns | Avoid              | Still avoid        |

## Still Critical Anti-Patterns

### 1. Too Many Parts

**Problem**: More than 300 active parts per partition causes degraded performance.

**Detection**:

```sql
SELECT database, table, partition, count() AS parts
FROM system.parts
WHERE active = 1
GROUP BY database, table, partition
HAVING parts > 300;
```

**Fix**:

- Reduce PARTITION BY granularity (monthly instead of daily)
- Increase batch sizes for inserts
- Run `OPTIMIZE TABLE ... FINAL` during maintenance windows

### 2. Small Batch Inserts

**Problem**: Inserting fewer than 1,000 rows per batch creates too many parts.

**Symptoms**:

- Growing part count
- Slow inserts
- High CPU from merges

**Fix**:

```python
# Buffer rows before inserting
BATCH_SIZE = 50000
buffer = []

for row in source:
    buffer.append(row)
    if len(buffer) >= BATCH_SIZE:
        client.insert('table', buffer)
        buffer = []
```

**Target**: 10,000-100,000 rows per batch.

### 3. High-Cardinality First ORDER BY

**Problem**: Placing high-cardinality columns first in ORDER BY makes queries 10x slower.

**Bad Example**:

```sql
-- Wrong: trade_id is unique (highest cardinality)
ORDER BY (trade_id, timestamp, symbol, exchange)
```

**Fix**:

```sql
-- Correct: lowest cardinality first
ORDER BY (exchange, symbol, timestamp, trade_id)
```

### 4. No Memory Limits

**Problem**: 78% of deployments don't configure memory limits, risking OOM kills.

**Fix**:

```sql
-- Set per-query limit
SET max_memory_usage = 10000000000;  -- 10GB

-- In users.xml or config
<max_memory_usage>10000000000</max_memory_usage>
<max_memory_usage_for_all_queries>50000000000</max_memory_usage_for_all_queries>
```

### 5. Denormalization Overuse

**Problem**: Pre-joining data into wide tables increases storage 10-100x and slows queries.

**Bad Pattern**:

```sql
-- Wide denormalized table
CREATE TABLE orders_denormalized (
    order_id UInt64,
    -- Order fields
    customer_name String,
    customer_email String,
    customer_address String,
    -- Product fields (repeated per order item!)
    product_name String,
    product_category String,
    ...
);
```

**Fix**: Use dictionaries for dimension lookups:

```sql
-- Fact table (normalized)
CREATE TABLE orders (
    order_id UInt64,
    customer_id UInt64,
    product_id UInt64,
    quantity UInt32,
    price Float64
);

-- Dictionary for customer lookup
CREATE DICTIONARY customers_dict (...)
SOURCE(CLICKHOUSE(TABLE 'customers'))
LAYOUT(FLAT());

-- Query with dictionary (6.6x faster than JOIN)
SELECT
    order_id,
    dictGet('customers_dict', 'name', customer_id) AS customer_name
FROM orders;
```

### 6. Over-Partitioning (Nuanced)

**Problem**: Too many partitions degrades performance when parts haven't merged.

**The real metric is PARTS COUNT, not partition count.** A table with 100K partitions but 1 merged part each is fine. A table with 10 partitions but 50K unmerged parts is broken. Always check `system.parts WHERE active = 1` — that is the number that determines mutation speed, query latency, and merge pressure.

#### Partition Key Design for Time-Series with Compound Keys

For tables with ORDER BY like `(symbol, threshold, first_agg_trade_id)` where the last column is time-correlated (monotonic trade IDs, timestamps), **time should NOT be in the partition key**. The ORDER BY index already provides efficient time-range pruning within partitions — adding time to the partition key is redundant and harmful.

**Best partition key**: The dimensions you use for **data lifecycle** (DELETE/DROP scope) — typically the non-time columns that define your mutation boundaries.

```sql
-- CORRECT: Partition by dimensions used for DELETE/DROP scope.
-- ORDER BY index handles time-range pruning automatically.
PARTITION BY (symbol, threshold_decimal_bps)
ORDER BY (symbol, threshold_decimal_bps, ouroboros_mode, first_agg_trade_id)

-- WRONG: Time in partition key when ORDER BY already has a time-correlated column.
-- Creates N × days partitions, each with unmerged parts from streaming inserts.
PARTITION BY (symbol, threshold_decimal_bps, toYYYYMMDD(open_time_ms / 1000))
```

**Why this matters — validated benchmark**:

- Dimension-only partitions: **1,037 days/min** (heavy symbols), **3,800 days/min** (light symbols)
- Daily time partitions: **200 days/min** — 5x slower on heavy, 18x slower on light
- Root cause: daily partitions create O(symbols × thresholds × days) partitions, each accumulating unmerged parts from streaming inserts. Mutations must scan all active parts.

#### When Time in Partition Key IS Correct

Time belongs in the partition key **only** when:

1. You need `DROP PARTITION` for bulk time-range cleanup (e.g., TTL replacement, purging old months)
2. The table is append-only with no DELETE operations targeting specific rows
3. ORDER BY does NOT already contain a time-correlated column

```sql
-- Append-only logs where you DROP entire months for retention
PARTITION BY toYYYYMM(timestamp)
ORDER BY (service, timestamp)
```

#### Critical: Post-Migration OPTIMIZE

After any partition key change (requires table recreation + data copy), the new table has 1 part per INSERT batch — potentially 50K+ unmerged parts. **You MUST run `OPTIMIZE TABLE ... FINAL` and wait for completion before starting any services that run mutations.** Mutations scan all active parts — 50K unmerged parts means 300s+ timeouts on every DELETE.

```sql
-- After migration: force merge BEFORE restarting services
OPTIMIZE TABLE db.table FINAL;  -- may take 10-30 min for large tables

-- Verify parts are merged
SELECT count() FROM system.parts WHERE database = 'db' AND table = 'table' AND active;
-- Target: ~1 part per partition (or low single digits)
```

#### Detection

```sql
-- Check active parts count per table (THE metric that matters)
SELECT
    database,
    table,
    count() AS active_parts,
    countDistinct(partition) AS partitions,
    round(count() / countDistinct(partition), 1) AS avg_parts_per_partition
FROM system.parts
WHERE active = 1
GROUP BY database, table
HAVING active_parts > 1000
ORDER BY active_parts DESC;

-- Drill down: which partitions have the most unmerged parts?
SELECT
    database,
    table,
    partition,
    count() AS parts_in_partition,
    formatReadableSize(sum(bytes_on_disk)) AS size
FROM system.parts
WHERE active = 1 AND database = 'your_db' AND table = 'your_table'
GROUP BY database, table, partition
HAVING parts_in_partition > 10
ORDER BY parts_in_partition DESC
LIMIT 20;
```

### 7. Missing Codecs

**Problem**: Not using specialized codecs wastes 5-10x storage.

**Fix**: Apply appropriate codecs:

```sql
timestamp DateTime64(3) CODEC(DoubleDelta, ZSTD)
price Float64 CODEC(Gorilla, ZSTD)
count UInt64 CODEC(T64, ZSTD)
```

## Improved in v24.4+ (Use with Caution)

### 8. Large JOINs (180x Improved)

**v24.4+ Improvement**: Predicate pushdown makes JOINs 180x faster in many cases.

**Still Avoid For**: Ultra-low-latency (<10ms) requirements.

**CTE Range Joins**: The v24.4+ improvement does NOT apply to range joins on CTEs (e.g., `FROM cte_a JOIN cte_b ON b.rn BETWEEN a.rn + 1 AND a.rn + 101`). ClickHouse cannot index into CTEs — these remain O(N×M) nested loop scans. For forward-looking array collection patterns, use window functions (`groupArray() OVER (ROWS BETWEEN ...)`) instead of self-joins. See rangebar-patterns AP-14 for benchmarks showing 11x speedup.

**Signal Timing**: When using `lagInFrame()` for pattern detection in CTE-based signal pipelines, verify that lag offsets match the intended bar. Off-by-one errors cause SQL signals to fire 1 bar late relative to event-driven backtesting engines. See rangebar-patterns AP-15 (Signal Timing Off-by-One) for the `lagInFrame` offset correction rules.

**Better Alternative**: Dictionaries for dimension lookups.

```sql
-- Now acceptable for most use cases
SELECT o.*, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.timestamp > now() - INTERVAL 1 DAY;

-- Still better: Dictionary lookup
SELECT o.*, dictGet('customers', 'name', customer_id)
FROM orders o
WHERE timestamp > now() - INTERVAL 1 DAY;
```

### 9. Mutations (1700x Improved)

**v24.4+ Improvement**: Lightweight updates are 1700x faster.

**Traditional Mutations**: Still slow, avoid for frequent operations.

**Lightweight Updates**:

```sql
-- Fast in v24.4+ (lightweight)
ALTER TABLE trades UPDATE status = 'processed' WHERE trade_id = 123;

-- Still slow (traditional mutation) — use a Python-computed literal instead of now()
-- e.g. cutoff = datetime.utcnow() - timedelta(days=90), then pass as a parameter
ALTER TABLE trades DELETE WHERE timestamp < %(cutoff)s
SETTINGS mutations_sync = 1;
```

> **WARNING**: Lightweight `DELETE FROM` sets a `_row_exists=0` mask that persists after
> completion and re-applies to new parts during background merges. If you INSERT after
> a lightweight DELETE, the mask will delete your new rows. Always use `ALTER TABLE ... DELETE`
> (traditional mutation) when INSERTs will follow. Use `SETTINGS mutations_sync = 1` to
> ensure the DELETE completes before proceeding.

**Better Pattern**: Use TTL for deletions:

```sql
TTL timestamp + INTERVAL 90 DAY DELETE
```

## Detection Query

Run to identify anti-patterns (parts count is the primary health metric):

```sql
-- Anti-pattern detection: parts count, avg parts per partition, total size
SELECT
    p.database,
    p.table,
    count() AS active_parts,
    countDistinct(p.partition) AS partitions,
    round(count() / countDistinct(p.partition), 1) AS avg_parts_per_partition,
    formatReadableSize(sum(p.bytes_on_disk)) AS total_size,
    -- Red flags
    multiIf(
        count() > 10000, 'CRITICAL: merge backlog or over-partitioned',
        count() / countDistinct(p.partition) > 50, 'WARNING: high parts/partition ratio',
        'OK'
    ) AS status
FROM system.parts p
WHERE p.active = 1
  AND p.database NOT IN ('system', 'INFORMATION_SCHEMA')
GROUP BY p.database, p.table
ORDER BY active_parts DESC;
```

## Related References

- [Schema Design Workflow](./schema-design-workflow.md)
- [Audit and Diagnostics](./audit-and-diagnostics.md)
- [Idiomatic Architecture](./idiomatic-architecture.md)
