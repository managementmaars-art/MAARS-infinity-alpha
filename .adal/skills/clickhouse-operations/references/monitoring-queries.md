# ClickHouse Monitoring Queries

Complete library of diagnostic, monitoring, and operational queries organized by category.

## Monitoring & Diagnostics

### Current Cluster Health

```sql
-- Disk space
SELECT
    formatReadableSize(total_space) as total_disk,
    formatReadableSize(free_space) as free_disk,
    round(free_space / total_space * 100, 2) as free_percent
FROM system.disks;

-- Running queries
SELECT query_id, user, elapsed, memory_usage / 1024 / 1024 as memory_mb
FROM system.processes
LIMIT 5;

-- Recent errors
SELECT name, value as count, last_error_time
FROM system.errors
WHERE value > 0
ORDER BY last_error_time DESC
LIMIT 5;
```

### Query Performance

```sql
-- p95 latency
SELECT quantile(0.95)(query_duration_ms) as p95_latency_ms
FROM system.query_log
WHERE event_date >= today()
  AND type = 'QueryFinish'
  AND query NOT LIKE '%system.%';

-- Queries per second
SELECT COUNT() / max(CAST(elapsed as Float64)) as qps
FROM system.processes
WHERE query NOT LIKE '%system.%';

-- Slowest queries (last 24 hours)
SELECT
    event_time,
    query_duration_ms,
    read_rows,
    formatReadableSize(read_bytes) as bytes_read,
    formatReadableSize(memory_usage) as peak_memory,
    query
FROM system.query_log
WHERE type = 'QueryFinish'
  AND event_date >= today() - 1
  AND query NOT LIKE '%system.%'
ORDER BY query_duration_ms DESC
LIMIT 20;

-- Most resource-intensive queries
SELECT
    query,
    COUNT() as exec_count,
    AVG(query_duration_ms) as avg_duration_ms,
    MAX(memory_usage) / 1024 / 1024 as peak_memory_mb,
    SUM(read_bytes) / 1024 / 1024 / 1024 as total_gb_read
FROM system.query_log
WHERE event_date >= today() - 7
  AND type = 'QueryFinish'
GROUP BY query
ORDER BY total_gb_read DESC
LIMIT 20;
```

### Insert Performance

```sql
-- Insert throughput
SELECT
    table,
    SUM(rows) / SUM(CAST(query_duration_ms as Float64)) * 1000 as rows_per_second
FROM system.query_log
WHERE query LIKE 'INSERT%'
  AND type = 'QueryFinish'
  AND event_date >= today()
GROUP BY table;

-- Merge pressure
SELECT database, table, COUNT() as parts_count
FROM system.parts
WHERE active = 1
GROUP BY database, table
HAVING parts_count > 1000
ORDER BY parts_count DESC;
```

### Memory Usage

```sql
-- Current memory tracking
SELECT
    formatReadableSize(value) as current_memory,
    formatReadableSize(80000000000) as target_limit
FROM system.metrics
WHERE metric = 'MemoryTracking';

-- Queries using excessive memory
SELECT
    query_id,
    user,
    memory_usage / 1024 / 1024 / 1024 as memory_gb,
    query
FROM system.processes
WHERE memory_usage > 10000000000  -- > 10 GB
ORDER BY memory_usage DESC;
```

### Failed Queries

```sql
-- Error breakdown
SELECT
    exception,
    COUNT() as count,
    MAX(event_time) as last_error
FROM system.query_log
WHERE type = 'ExceptionWhileProcessing'
  AND event_date >= today() - 1
GROUP BY exception
ORDER BY count DESC;
```

### Table Growth

```sql
-- Largest tables
SELECT
    database,
    name as table,
    SUM(rows) as total_rows,
    formatReadableSize(SUM(bytes_on_disk)) as disk_size,
    formatReadableSize(SUM(data_compressed_bytes)) as compressed,
    round(SUM(data_uncompressed_bytes) / SUM(data_compressed_bytes), 1) as compression_ratio
FROM system.parts
WHERE active = 1
  AND database NOT IN ('system', 'information_schema')
GROUP BY database, name
ORDER BY bytes_on_disk DESC;
```

## Cluster Operations

### Replication Status

```sql
-- Check replication health
SELECT
    database,
    table,
    total_replicas,
    active_replicas,
    absolute_delay
FROM system.replicas
ORDER BY absolute_delay DESC;

-- Verify all nodes responding
SELECT hostname(), version(), uptime() as uptime_seconds
FROM clusterAllReplicas('production_cluster', system.one);

-- Replication queue
SELECT * FROM system.replication_queue;
```

### Distributed Table Health

```sql
-- Check distributed table mapping
SELECT shard_num, replica_num, host_name, port
FROM system.clusters
WHERE cluster = 'production_cluster';

-- Data distribution across shards
SELECT
    _shard_num as shard,
    COUNT() as rows,
    formatReadableSize(SUM(bytes_on_disk)) as size
FROM distributed_table
GROUP BY _shard_num;
```

## Resource Management

### Disk Management

```sql
-- Disk utilization by table
SELECT
    database,
    table,
    formatReadableSize(SUM(bytes_on_disk)) as size_on_disk,
    SUM(rows) as total_rows,
    COUNT() as parts_count
FROM system.parts
WHERE active = 1
GROUP BY database, table
ORDER BY bytes_on_disk DESC;

-- Partition sizes
SELECT
    partition,
    formatReadableSize(SUM(bytes_on_disk)) as size,
    SUM(rows) as rows
FROM system.parts
WHERE table = 'events' AND active = 1
GROUP BY partition
ORDER BY partition DESC;
```

### Connection Management

```sql
-- Active connections
SELECT
    query_id,
    user,
    client_hostname,
    elapsed as elapsed_seconds,
    query
FROM system.processes
ORDER BY elapsed DESC;

-- Connection count by user
SELECT
    user,
    COUNT() as connection_count
FROM system.processes
GROUP BY user;
```

### Background Operations

```sql
-- Merge queue
SELECT
    database,
    table,
    elapsed,
    progress,
    num_parts,
    formatReadableSize(total_size_bytes_compressed) as size
FROM system.merges
ORDER BY elapsed DESC;

-- Mutation status
SELECT
    database,
    table,
    mutation_id,
    command,
    is_done,
    parts_to_do,
    latest_fail_reason
FROM system.mutations
WHERE NOT is_done;
```

## Alert Thresholds

Recommended alert conditions:

- **Query latency p95 > 5 seconds** - Queries taking too long
- **Insert rate drops > 20%** - Ingestion issues
- **Free disk < 20%** - Disk space critical
- **Active parts > 1000 per table** - Merge pressure
- **Memory usage > 80% of limit** - Memory pressure
- **Replication lag > 60 seconds** - Replication falling behind
- **Failed query rate > 1%** - High error rate

## Performance Optimization Queries

### Index Effectiveness

```sql
-- Check if indexes are used
SELECT
    table,
    name as index_name,
    type,
    expr
FROM system.data_skipping_indices
WHERE database = 'default';

-- Index hit rate
SELECT
    table,
    sum(read_rows) as rows_read,
    sum(read_bytes) / 1024 / 1024 / 1024 as gb_read
FROM system.query_log
WHERE type = 'QueryFinish'
  AND event_date >= today()
  AND query LIKE '%WHERE%'
GROUP BY table;
```

### Compression Analysis

```sql
-- Compression ratio by table
SELECT
    database,
    table,
    round(SUM(data_uncompressed_bytes) / SUM(data_compressed_bytes), 2) as compression_ratio,
    formatReadableSize(SUM(data_compressed_bytes)) as compressed_size,
    formatReadableSize(SUM(data_uncompressed_bytes)) as uncompressed_size
FROM system.parts
WHERE active = 1
GROUP BY database, table
ORDER BY compression_ratio DESC;
```

### Query Cache Effectiveness

```sql
-- Query cache hit rate
SELECT
    sum(ProfileEvents['QueryCacheHits']) as cache_hits,
    sum(ProfileEvents['QueryCacheMisses']) as cache_misses,
    round(cache_hits / (cache_hits + cache_misses) * 100, 2) as hit_rate_percent
FROM system.query_log
WHERE event_date >= today();
```
