# ClickHouse Operations Query Reference

Complete library of diagnostic, monitoring, and operational queries for ClickHouse production management.

## Table of Contents

1. [Monitoring & Diagnostics](#monitoring--diagnostics)
2. [Performance Analysis](#performance-analysis)
3. [Resource Management](#resource-management)
4. [Cluster Operations](#cluster-operations)
5. [Data Lifecycle](#data-lifecycle)
6. [System Introspection](#system-introspection)

---

## Monitoring & Diagnostics

### Real-Time Cluster Status

```sql
-- All servers in cluster with uptime
SELECT
    hostname() as server,
    version() as version,
    formatReadableSize(uptime() * 1000000 * 1000) as uptime,
    uptime() > 3600 as healthy
FROM clusterAllReplicas('production_cluster', system.one)
ORDER BY server;

-- Quick health check (run from any node)
SELECT
    formatReadableSize(total_space) as disk_total,
    formatReadableSize(free_space) as disk_free,
    round(free_space / total_space * 100, 1) as disk_free_pct,
    formatReadableSize(value) as memory_usage
FROM system.disks, system.metrics
WHERE metric = 'MemoryTracking';
```

### Query Performance Monitoring

```sql
-- Top 20 slowest queries in past 24 hours
SELECT
    event_time,
    query_duration_ms,
    formatReadableSize(read_bytes) as bytes_read,
    formatReadableSize(memory_usage) as peak_memory,
    read_rows,
    exception,
    substring(query, 1, 100) as query_snippet
FROM system.query_log
WHERE event_date >= today() - 1
  AND type = 'QueryFinish'
  AND query NOT LIKE '%system.%'
ORDER BY query_duration_ms DESC
LIMIT 20;

-- Query latency percentiles (for SLA tracking)
SELECT
    quantile(0.50)(query_duration_ms) as p50_ms,
    quantile(0.90)(query_duration_ms) as p90_ms,
    quantile(0.95)(query_duration_ms) as p95_ms,
    quantile(0.99)(query_duration_ms) as p99_ms,
    quantile(1.0)(query_duration_ms) as max_ms
FROM system.query_log
WHERE event_date >= today()
  AND type = 'QueryFinish'
  AND query NOT LIKE '%system.%';

-- Query volume and user breakdown
SELECT
    user,
    COUNT() as query_count,
    COUNT(DISTINCT query_id) as unique_queries,
    SUM(query_duration_ms) as total_duration_ms,
    AVG(query_duration_ms) as avg_duration_ms,
    MAX(query_duration_ms) as max_duration_ms,
    SUM(read_rows) as total_rows_read,
    formatReadableSize(SUM(read_bytes)) as total_bytes_read
FROM system.query_log
WHERE event_date >= today()
  AND type = 'QueryFinish'
GROUP BY user
ORDER BY query_count DESC;

-- Query patterns causing most reads
SELECT
    substring(query, 1, 200) as query_pattern,
    COUNT() as exec_count,
    AVG(query_duration_ms) as avg_ms,
    formatReadableSize(SUM(read_bytes)) as total_bytes,
    formatReadableSize(AVG(read_bytes)) as avg_bytes
FROM system.query_log
WHERE event_date >= today() - 7
  AND type = 'QueryFinish'
GROUP BY query_pattern
ORDER BY total_bytes DESC
LIMIT 20;
```

### Error Tracking

```sql
-- Error rate by user (last 24 hours)
SELECT
    user,
    COUNT(*) as total_queries,
    SUM(if(exception != '', 1, 0)) as failed_queries,
    round(SUM(if(exception != '', 1, 0)) * 100 / COUNT(*), 2) as error_rate_pct,
    MAX(event_time) as last_error_time
FROM system.query_log
WHERE event_date >= today() - 1
GROUP BY user
HAVING error_rate_pct > 0
ORDER BY error_rate_pct DESC;

-- Most common error types
SELECT
    exception,
    COUNT() as count,
    MAX(event_time) as last_occurrence,
    GROUP_CONCAT(DISTINCT user) as affected_users
FROM system.query_log
WHERE event_date >= today() - 7
  AND exception != ''
GROUP BY exception
ORDER BY count DESC;

-- Errors by table (INSERT failures, etc.)
SELECT
    extractString(query, '^(\\w+)') as query_type,
    extractString(query, 'FROM\\s+(\\S+)') as table,
    COUNT() as error_count,
    exception,
    MAX(event_time) as last_error
FROM system.query_log
WHERE exception != ''
  AND event_date >= today() - 1
GROUP BY query_type, table, exception
ORDER BY error_count DESC;
```

---

## Performance Analysis

### Insert Performance

```sql
-- Insert throughput by table (rows/sec)
SELECT
    table,
    COUNT() as insert_count,
    SUM(rows) as total_rows_inserted,
    SUM(CAST(query_duration_ms as Float64)) as total_duration_ms,
    SUM(rows) / (SUM(CAST(query_duration_ms as Float64)) / 1000) as rows_per_second,
    formatReadableSize(SUM(bytes_written_uncompressed)) as total_data
FROM system.query_log
WHERE query LIKE 'INSERT%'
  AND type = 'QueryFinish'
  AND event_date >= today()
GROUP BY table
ORDER BY rows_per_second DESC;

-- Batch insert analysis (optimal batch size discovery)
SELECT
    table,
    quantile(0.25)(rows) as q25_rows,
    quantile(0.50)(rows) as q50_rows,
    quantile(0.75)(rows) as q75_rows,
    quantile(0.95)(rows) as q95_rows,
    quantile(0.99)(rows) as q99_rows,
    AVG(query_duration_ms) as avg_duration_ms,
    quantile(0.50)(rows) / AVG(query_duration_ms) * 1000 as median_rows_per_sec
FROM system.query_log
WHERE query LIKE 'INSERT%'
  AND type = 'QueryFinish'
  AND event_date >= today() - 7
GROUP BY table
ORDER BY table;

-- Kafka table consumption rate
SELECT
    table,
    consumer_number,
    messages_read,
    last_poll_time,
    formatReadableSize(bytes_read) as data_read
FROM system.kafka_consumers
ORDER BY last_poll_time DESC;
```

### Merge & Background Operation Monitoring

```sql
-- Active merges with progress
SELECT
    database,
    table,
    elapsed,
    progress,
    num_parts,
    formatReadableSize(total_size_bytes_compressed) as merge_size,
    formatReadableSize(bytes_read_uncompressed / 1024 / 1024) as read_size,
    rows_read
FROM system.merges
ORDER BY elapsed DESC;

-- Merge performance history (last 7 days)
SELECT
    event_date,
    table,
    COUNT() as merge_count,
    SUM(rows_read) as rows_merged,
    formatReadableSize(SUM(bytes_read_uncompressed)) as data_merged,
    AVG(duration_ms) as avg_merge_ms,
    MAX(duration_ms) as max_merge_ms,
    MIN(duration_ms) as min_merge_ms
FROM system.part_log
WHERE event_type = 'MergeParts'
  AND event_date >= today() - 7
GROUP BY event_date, table
ORDER BY event_date DESC, merge_count DESC;

-- Pending merges (queue depth)
SELECT
    database,
    table,
    COUNT() as parts_count,
    SUM(rows) as total_rows,
    formatReadableSize(SUM(bytes_on_disk)) as total_size,
    COUNT() / max(bytes_on_disk) * 1000000 as fragmentation_ratio
FROM system.parts
WHERE active = 1
GROUP BY database, table
HAVING parts_count > 100
ORDER BY parts_count DESC;
```

### Memory Usage Analysis

```sql
-- Memory usage by query
SELECT
    query_id,
    user,
    formatReadableSize(memory_usage) as current_memory,
    formatReadableSize(peak_memory_usage) as peak_memory,
    elapsed,
    read_rows,
    substring(query, 1, 100) as query_snippet
FROM system.processes
ORDER BY memory_usage DESC;

-- Historical memory peaks (by query type)
SELECT
    extractString(query, '^(\\w+)') as query_type,
    COUNT() as query_count,
    formatReadableSize(MAX(memory_usage)) as peak_memory,
    formatReadableSize(AVG(memory_usage)) as avg_memory,
    formatReadableSize(quantile(0.95)(memory_usage)) as p95_memory
FROM system.query_log
WHERE event_date >= today() - 7
  AND type = 'QueryFinish'
GROUP BY query_type
ORDER BY peak_memory DESC;

-- Memory vs data processed (efficiency)
SELECT
    extractString(query, '^(\\w+)') as query_type,
    AVG(memory_usage / read_bytes * 100) as memory_per_gb_read,
    COUNT() as query_count,
    formatReadableSize(AVG(read_bytes)) as avg_data_read
FROM system.query_log
WHERE event_date >= today() - 7
  AND type = 'QueryFinish'
  AND read_bytes > 0
GROUP BY query_type
ORDER BY memory_per_gb_read DESC;
```

### Index & Partition Effectiveness

```sql
-- Granule-level statistics (table read efficiency)
SELECT
    table,
    COUNT() as total_parts,
    SUM(marks) as total_granules,
    SUM(rows) as total_rows,
    SUM(rows) / SUM(marks) as rows_per_granule,
    formatReadableSize(SUM(bytes_on_disk)) as total_size
FROM system.parts
WHERE active = 1
  AND database NOT IN ('system', 'information_schema')
GROUP BY table
ORDER BY total_parts DESC;

-- Column compression effectiveness
SELECT
    table,
    name as column,
    type,
    formatReadableSize(data_uncompressed_bytes) as uncompressed,
    formatReadableSize(data_compressed_bytes) as compressed,
    round(data_uncompressed_bytes / data_compressed_bytes, 2) as compression_ratio
FROM system.columns
WHERE database = 'default'
  AND table NOT LIKE 'system.%'
ORDER BY compression_ratio DESC
LIMIT 30;

-- Partition distribution (for hot/cold analysis)
SELECT
    partition,
    COUNT() as parts_count,
    SUM(rows) as total_rows,
    formatReadableSize(SUM(bytes_on_disk)) as size,
    MAX(modification_time) as last_modified
FROM system.parts
WHERE active = 1
  AND database = 'default'
  AND table = 'events'
GROUP BY partition
ORDER BY partition DESC;
```

---

## Resource Management

### Disk Space Management

```sql
-- Disk usage by table (detailed breakdown)
SELECT
    database,
    name as table,
    COUNT() as parts_count,
    SUM(rows) as total_rows,
    formatReadableSize(SUM(bytes_on_disk)) as disk_size,
    formatReadableSize(SUM(data_uncompressed_bytes)) as uncompressed,
    formatReadableSize(SUM(data_compressed_bytes)) as compressed,
    round(SUM(data_uncompressed_bytes) / SUM(data_compressed_bytes), 2) as compression_ratio,
    round(SUM(bytes_on_disk) / (SELECT total_space FROM system.disks LIMIT 1) * 100, 2) as pct_of_disk
FROM system.parts
WHERE active = 1
  AND database NOT IN ('system', 'information_schema')
GROUP BY database, name
ORDER BY bytes_on_disk DESC;

-- Largest tables with row/byte density
SELECT
    database,
    table,
    SUM(rows) as total_rows,
    formatReadableSize(SUM(bytes_on_disk)) as size,
    round(SUM(bytes_on_disk) / SUM(rows), 2) as bytes_per_row,
    COUNT() as parts_count,
    round(SUM(bytes_on_disk) / COUNT(), 2) as avg_part_size
FROM system.parts
WHERE active = 1
GROUP BY database, table
ORDER BY bytes_on_disk DESC
LIMIT 30;

-- TTL and data expiration readiness
SELECT
    table,
    row_policy_name,
    formatReadableSize(SUM(bytes_on_disk)) as old_data_size,
    COUNT() as partitions_to_drop
FROM system.parts
WHERE active = 1
  AND partition < toYYYYMM(today() - INTERVAL 90 DAY)
GROUP BY table
ORDER BY bytes_on_disk DESC;
```

### Connection Management

```sql
-- Current connections summary
SELECT
    COUNT() as total_connections,
    COUNT(DISTINCT user) as unique_users,
    COUNT(DISTINCT client_hostname) as unique_clients,
    SUM(if(query NOT LIKE '', 1, 0)) as active_queries
FROM system.processes;

-- Active queries by user
SELECT
    user,
    COUNT() as query_count,
    SUM(if(elapsed > 60, 1, 0)) as long_running,
    MAX(elapsed) as max_elapsed_sec,
    MAX(memory_usage) as max_memory,
    GROUP_CONCAT(DISTINCT client_hostname) as clients
FROM system.processes
WHERE query NOT LIKE '%system.%'
GROUP BY user
ORDER BY query_count DESC;

-- Connection leak detection
SELECT
    client_hostname,
    user,
    COUNT() as connection_count,
    SUM(if(query = '', 1, 0)) as idle_connections,
    MAX(elapsed) as idle_time_sec
FROM system.processes
WHERE query = ''
GROUP BY client_hostname, user
HAVING idle_connections > 5
ORDER BY idle_connections DESC;

-- Query queue depth (active vs waiting)
SELECT
    COUNT() as total_queries,
    SUM(if(elapsed < 1, 1, 0)) as starting,
    SUM(if(elapsed >= 1 and elapsed < 5, 1, 0)) as normal,
    SUM(if(elapsed >= 5 and elapsed < 60, 1, 0)) as slow,
    SUM(if(elapsed >= 60, 1, 0)) as very_slow
FROM system.processes
WHERE query NOT LIKE '%system.%';
```

---

## Cluster Operations

### Replication Health

```sql
-- Replica lag across cluster
SELECT
    database,
    table,
    total_replicas,
    active_replicas,
    absolute_delay,
    relative_delay,
    last_queue_update,
    if(absolute_delay > 60, 'WARNING', 'OK') as status
FROM system.replicas
ORDER BY absolute_delay DESC;

-- Replication queue depth per replica
SELECT
    database,
    table,
    COUNT() as queue_length,
    MAX(create_time) as oldest_entry_age
FROM system.replication_queue
GROUP BY database, table
HAVING queue_length > 0
ORDER BY queue_length DESC;

-- Replication status including failed replicas
SELECT
    replica_name,
    database,
    table,
    is_leader,
    absolute_delay,
    total_replicas,
    active_replicas,
    if(is_leader = 0 and absolute_delay > 300, 'CRITICAL', if(absolute_delay > 60, 'WARNING', 'OK')) as health
FROM system.replicas
ORDER BY absolute_delay DESC;

-- Data consistency check (partition counts across replicas)
SELECT
    table,
    partition,
    COUNT(DISTINCT replica_name) as replica_count,
    COUNT() as partition_copies
FROM clusterAllReplicas('production_cluster', default.system.parts)
WHERE active = 1
GROUP BY table, partition
HAVING replica_count < (SELECT COUNT(DISTINCT host) FROM system.clusters WHERE cluster = 'production_cluster')
LIMIT 20;
```

### Cluster-Wide Metrics

```sql
-- CPU usage across cluster
SELECT
    hostname() as server,
    metric,
    round(value, 2) as cpu_percent
FROM clusterAllReplicas('production_cluster', system.asynchronous_metrics)
WHERE metric LIKE '%CPU%'
ORDER BY server, metric;

-- Memory distribution across cluster
SELECT
    hostname() as server,
    formatReadableSize(value) as memory_usage
FROM clusterAllReplicas('production_cluster', system.metrics)
WHERE metric = 'MemoryTracking'
ORDER BY server;

-- Query execution across cluster nodes
SELECT
    hostname() as server,
    COUNT() as query_count,
    COUNT(DISTINCT user) as unique_users,
    SUM(if(elapsed > 60, 1, 0)) as long_running_queries
FROM clusterAllReplicas('production_cluster', system.processes)
GROUP BY server
ORDER BY query_count DESC;

-- Table distribution verification (sharding check)
SELECT
    database,
    table,
    COUNT() as partition_count,
    SUM(rows) as total_rows,
    COUNT(DISTINCT hostname()) as replica_count
FROM clusterAllReplicas('production_cluster', default.system.parts)
WHERE active = 1
GROUP BY database, table
ORDER BY total_rows DESC;
```

---

## Data Lifecycle

### TTL and Retention Management

```sql
-- Tables with TTL policies
SELECT
    database,
    table,
    engine,
    formatReadableSize(SUM(bytes_on_disk)) as total_size,
    MAX(modification_time) as last_modified
FROM system.tables
WHERE database NOT IN ('system', 'information_schema')
  AND engine LIKE '%MergeTree%'
GROUP BY database, table, engine
ORDER BY total_size DESC;

-- Expired data awaiting cleanup
SELECT
    database,
    table,
    COUNT() as expired_partitions,
    formatReadableSize(SUM(bytes_on_disk)) as expired_size,
    MIN(partition) as oldest_partition,
    MAX(modification_time) as last_modified
FROM system.parts
WHERE active = 1
  AND modification_time < now() - INTERVAL 30 DAY
GROUP BY database, table
ORDER BY expired_size DESC;

-- Data age distribution
SELECT
    table,
    toDate(modification_time) as data_date,
    COUNT() as parts_count,
    SUM(rows) as row_count,
    formatReadableSize(SUM(bytes_on_disk)) as size
FROM system.parts
WHERE active = 1
  AND database = 'default'
  AND table = 'events'
GROUP BY table, data_date
ORDER BY data_date DESC
LIMIT 90;  -- Last 90 days
```

### Partition Management

```sql
-- Partition size analysis
SELECT
    partition,
    COUNT() as parts_count,
    SUM(rows) as total_rows,
    formatReadableSize(SUM(bytes_on_disk)) as partition_size,
    AVG(bytes_on_disk) as avg_part_size,
    MAX(modification_time) as last_modified
FROM system.parts
WHERE active = 1
  AND database = 'default'
  AND table = 'events'
GROUP BY partition
ORDER BY partition DESC;

-- Identify tables needing optimization
SELECT
    database,
    table,
    COUNT() as parts_count,
    SUM(rows) as total_rows,
    formatReadableSize(SUM(bytes_on_disk)) as total_size,
    if(COUNT() > 100, 'OPTIMIZE_NEEDED', 'OK') as status
FROM system.parts
WHERE active = 1
GROUP BY database, table
HAVING parts_count > 100
ORDER BY parts_count DESC;
```

---

## System Introspection

### Configuration & Settings

```sql
-- Current server settings
SELECT
    name,
    value,
    changed,
    description
FROM system.settings
WHERE name IN (
    'max_threads',
    'max_memory_usage',
    'max_server_memory_usage',
    'max_connections',
    'max_execution_time'
)
ORDER BY name;

-- Database and table engine information
SELECT
    database,
    name as table,
    engine,
    total_rows,
    formatReadableSize(total_bytes) as size,
    data_compression_codec
FROM system.tables
WHERE database NOT IN ('system', 'information_schema')
ORDER BY total_bytes DESC;

-- Column types and codecs
SELECT
    table,
    name as column,
    type,
    compression_codec,
    formatReadableSize(data_uncompressed_bytes) as uncompressed,
    formatReadableSize(data_compressed_bytes) as compressed
FROM system.columns
WHERE database = 'default'
ORDER BY data_compressed_bytes DESC;
```

### System Events & Metrics

```sql
-- Overall event counters
SELECT
    event,
    value,
    description
FROM system.events
WHERE event IN (
    'Query',
    'InsertedRows',
    'InsertedBytes',
    'SelectQuery',
    'FailedQuery'
)
ORDER BY value DESC;

-- Real-time throughput metrics
SELECT
    metric,
    value,
    description
FROM system.asynchronous_metrics
WHERE metric IN (
    'jemalloc_allocated_bytes',
    'MemoryTracking',
    'OSMemoryAvailable'
)
ORDER BY metric;
```
