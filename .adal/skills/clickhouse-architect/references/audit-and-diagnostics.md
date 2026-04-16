**Skill**: [ClickHouse Architect](../SKILL.md)

# Audit and Diagnostics

<!-- ADR: 2025-12-09-clickhouse-architect-skill -->

Comprehensive guide to ClickHouse system tables and diagnostic queries.

## System Tables Overview

| Table                       | Purpose                            |
| --------------------------- | ---------------------------------- |
| `system.parts`              | Part count, size, compression      |
| `system.columns`            | Column types, codecs, statistics   |
| `system.tables`             | Engine settings, TTL, partitioning |
| `system.query_log`          | Query execution history            |
| `system.processes`          | Active queries                     |
| `system.replicas`           | Replication status                 |
| `system.distribution_queue` | Distributed table health           |
| `system.disks`              | Storage capacity                   |
| `system.metrics`            | Real-time metrics                  |
| `system.merges`             | Ongoing merge operations           |

## Schema Health Queries

### Part Count Analysis

Critical threshold: >300 parts per partition indicates problems.

```sql
SELECT
    database,
    table,
    partition,
    count() AS parts,
    sum(rows) AS total_rows,
    formatReadableSize(sum(bytes_on_disk)) AS disk_size,
    CASE
        WHEN count() > 300 THEN 'CRITICAL'
        WHEN count() > 100 THEN 'WARNING'
        ELSE 'OK'
    END AS status
FROM system.parts
WHERE active = 1
GROUP BY database, table, partition
HAVING parts > 10
ORDER BY parts DESC;
```

### Compression Effectiveness

```sql
SELECT
    database,
    table,
    column,
    type,
    compression_codec,
    formatReadableSize(data_compressed_bytes) AS compressed,
    formatReadableSize(data_uncompressed_bytes) AS uncompressed,
    round(data_uncompressed_bytes / data_compressed_bytes, 2) AS ratio
FROM system.columns
WHERE database NOT IN ('system', 'INFORMATION_SCHEMA')
    AND data_compressed_bytes > 0
ORDER BY data_uncompressed_bytes DESC
LIMIT 50;
```

### Table Overview

```sql
SELECT
    database,
    name AS table,
    engine,
    partition_key,
    sorting_key,
    formatReadableSize(total_bytes) AS total_size,
    total_rows
FROM system.tables
WHERE database NOT IN ('system', 'INFORMATION_SCHEMA')
ORDER BY total_bytes DESC;
```

## Query Performance Queries

### Slow Queries (Last 24 Hours)

```sql
SELECT
    type,
    query_kind,
    round(query_duration_ms / 1000, 2) AS duration_sec,
    formatReadableSize(memory_usage) AS memory,
    formatReadableSize(read_bytes) AS read_bytes,
    read_rows,
    substring(query, 1, 100) AS query_preview
FROM system.query_log
WHERE event_time > now() - INTERVAL 24 HOUR
    AND type = 'QueryFinish'
    AND query_duration_ms > 1000
ORDER BY query_duration_ms DESC
LIMIT 20;
```

### Active Queries

```sql
SELECT
    query_id,
    user,
    round(elapsed, 2) AS elapsed_sec,
    formatReadableSize(memory_usage) AS memory,
    formatReadableSize(read_bytes) AS read_bytes,
    substring(query, 1, 100) AS query_preview
FROM system.processes
ORDER BY elapsed DESC;
```

### Query Patterns Analysis

```sql
SELECT
    normalized_query_hash,
    count() AS query_count,
    avg(query_duration_ms) AS avg_ms,
    max(query_duration_ms) AS max_ms,
    sum(read_rows) AS total_rows_read,
    any(substring(query, 1, 100)) AS sample_query
FROM system.query_log
WHERE event_time > now() - INTERVAL 7 DAY
    AND type = 'QueryFinish'
GROUP BY normalized_query_hash
ORDER BY query_count DESC
LIMIT 20;
```

## Index Effectiveness

Use EXPLAIN to analyze index usage:

```sql
EXPLAIN indexes = 1
SELECT * FROM your_table
WHERE your_conditions;
```

**Key metrics**:

| Metric         | Meaning               | Good Value         |
| -------------- | --------------------- | ------------------ |
| SelectedParts  | Parts scanned         | As low as possible |
| SelectedRanges | Index ranges selected | < TotalRanges      |
| SelectedMarks  | Granules to read      | < TotalMarks       |
| PrimaryKeyUsed | Primary key utilized  | 1 (true)           |

## Replication Diagnostics

### Replication Status

```sql
SELECT
    database,
    table,
    is_readonly,
    is_session_expired,
    future_parts,
    parts_to_check,
    queue_size,
    inserts_in_queue,
    merges_in_queue,
    log_pointer,
    CASE
        WHEN is_readonly = 1 THEN 'CRITICAL: READONLY'
        WHEN queue_size > 100 THEN 'WARNING: LARGE QUEUE'
        ELSE 'OK'
    END AS status
FROM system.replicas
ORDER BY queue_size DESC;
```

### Cross-Replica Check

```sql
SELECT
    hostName() AS host,
    database,
    table,
    total_rows,
    formatReadableSize(total_bytes) AS size
FROM clusterAllReplicas('your_cluster', system.tables)
WHERE database NOT IN ('system')
ORDER BY database, table, host;
```

## Resource Monitoring

### Disk Usage

```sql
SELECT
    name,
    path,
    formatReadableSize(free_space) AS free_space,
    formatReadableSize(total_space) AS total_space,
    round(100 * (1 - free_space / total_space), 2) AS used_percent
FROM system.disks;
```

### Memory Metrics

```sql
SELECT
    metric,
    formatReadableSize(value) AS value
FROM system.metrics
WHERE metric LIKE '%Memory%'
ORDER BY value DESC;
```

### Ongoing Merges

```sql
SELECT
    database,
    table,
    elapsed,
    progress,
    num_parts,
    formatReadableSize(total_size_bytes_compressed) AS size
FROM system.merges
ORDER BY elapsed DESC;
```

## ProfileEvents for Deep Analysis

Key ProfileEvents to monitor:

| Event                 | Meaning           | Action if High               |
| --------------------- | ----------------- | ---------------------------- |
| OSIOWaitMicroseconds  | Disk I/O waits    | Check disk performance       |
| OSCPUWaitMicroseconds | CPU contention    | Scale up or optimize queries |
| SelectedParts         | Parts scanned     | Improve ORDER BY             |
| SelectedRanges        | Index ranges      | Add skip indexes             |
| SelectedMarks         | Granules read     | Tune granularity             |
| RowsReadByMainReader  | Main data reading | Column pruning               |

```sql
SELECT
    event,
    value
FROM system.events
WHERE event IN (
    'OSIOWaitMicroseconds',
    'OSCPUWaitMicroseconds',
    'SelectedParts',
    'SelectedRanges',
    'SelectedMarks'
)
ORDER BY value DESC;
```

## Production Health Checks

Production-validated diagnostic queries for operational monitoring.

### Parts Health Check

More important than per-partition count: total active parts per table. Target: below 10K.

```sql
-- Check active parts per table (target: <10K)
SELECT database, table, count() AS active_parts,
       countDistinct(partition) AS partitions
FROM system.parts WHERE active
GROUP BY database, table
HAVING active_parts > 3000
ORDER BY active_parts DESC;
```

### Mutation Queue Check

Stuck mutations cause timeout cascades. Should be 0 in steady state.

```sql
-- Pending mutations (should be 0 in steady state)
SELECT count() AS pending,
       min(create_time) AS oldest
FROM system.mutations
WHERE NOT is_done AND database NOT IN ('system');
```

### Background Merge Health

```sql
-- Are merges keeping up?
SELECT count() AS active_merges FROM system.merges;
-- If consistently >0 during writes, increase background_pool_size
```

### Insert Throughput Check

Useful for comparing Arrow vs other insert formats and spotting latency regressions.

```sql
-- Last 20 inserts: check format and latency
SELECT query_kind, formatReadableSize(written_bytes),
       query_duration_ms, result_rows
FROM system.query_log
WHERE type = 'QueryFinish' AND query_kind = 'Insert'
ORDER BY event_time DESC LIMIT 20;
```

### Post-Migration Checklist

After any `PARTITION BY` change, follow this sequence strictly:

1. `OPTIMIZE TABLE ... FINAL` (wait for completion)
2. Verify parts count < 10K using the parts health check above
3. Only then restart services that run mutations

Skipping step 2 risks mutation timeouts if the merge backlog has not cleared.

## Automated Audit Script

Run the comprehensive audit:

```bash
clickhouse-client --multiquery < scripts/schema-audit.sql
```

## Related References

- [Schema Design Workflow](./schema-design-workflow.md)
- [Anti-Patterns and Fixes](./anti-patterns-and-fixes.md)
- [Idiomatic Architecture](./idiomatic-architecture.md)
