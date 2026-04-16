# ClickHouse Troubleshooting Guide

Extended troubleshooting guide with root cause analysis and resolution procedures.

## Query Performance Issues

### Issue: Query Timeout

**Diagnosis:**
```sql
SELECT query, query_duration_ms, read_rows, read_bytes / 1024 / 1024 as read_mb
FROM system.query_log
WHERE query_duration_ms > 30000  -- > 30 seconds
ORDER BY query_duration_ms DESC
LIMIT 10;
```

**Solutions:**
```sql
-- Option 1: Increase timeout for specific query
SET max_execution_time = 300;  -- 5 minutes
SELECT * FROM events WHERE timestamp > '2024-01-01';

-- Option 2: Add index for faster filtering
ALTER TABLE events ADD INDEX idx_timestamp timestamp TYPE minmax GRANULARITY 4;

-- Option 3: Use SAMPLE to estimate results faster
SELECT COUNT() FROM events SAMPLE 0.1;  -- Estimate from 10% of data

-- Option 4: Reduce scanned data with WHERE clauses
SELECT COUNT() FROM events WHERE timestamp >= today() - 7;  -- Last 7 days only
```

### Issue: Slow Queries

**Common Causes:**
1. No indexes on filtered columns
2. Scanning too many rows
3. Complex JOINs
4. Non-optimized GROUP BY
5. Large result sets

**Resolution Pattern:**
1. Check query execution plan with `EXPLAIN`
2. Add indexes on filter columns
3. Partition large tables
4. Use materialized views for aggregations
5. Optimize sort orders

## Memory Issues

### Issue: Out of Memory

**Diagnosis:**
```sql
SELECT
    query_id,
    user,
    memory_usage / 1024 / 1024 as memory_mb,
    query
FROM system.processes
ORDER BY memory_usage DESC;

-- Check recent OOM errors
SELECT exception FROM system.query_log
WHERE exception LIKE '%Memory%'
  AND event_date >= today() - 1;
```

**Solutions:**
```sql
-- Option 1: Increase memory limit per query
SET max_memory_usage = 30000000000;  -- 30 GB

-- Option 2: Use approximate aggregations
SELECT uniq(user_id) FROM events;  -- Faster approximate distinct count
SELECT topK(1000)(category) FROM events;  -- Top 1000 without full GROUP BY

-- Option 3: Process in smaller batches
SELECT * FROM events WHERE date = toDate(now()) LIMIT 1000000;

-- Option 4: Increase server memory limit
-- Edit config.xml: <max_server_memory_usage>128000000000</max_server_memory_usage>
```

## Insert Performance Issues

### Issue: Slow Inserts

**Diagnosis:**
```sql
SELECT
    table,
    COUNT() as insert_count,
    SUM(rows) as total_rows,
    SUM(rows) / SUM(CAST(query_duration_ms as Float64)) * 1000 as rows_per_second
FROM system.query_log
WHERE query LIKE 'INSERT%'
  AND type = 'QueryFinish'
  AND event_date >= today()
GROUP BY table;

-- Check parts count (high = slow inserts)
SELECT database, table, COUNT() as parts_count
FROM system.parts
WHERE active = 1
GROUP BY database, table
ORDER BY parts_count DESC;
```

**Solutions:**
```sql
-- Option 1: Increase batch size
INSERT INTO events
SELECT * FROM source_table
LIMIT 100000;  -- Larger batches = better throughput

-- Option 2: Enable async inserts
SET async_insert = 1;
SET wait_for_async_insert = 0;
INSERT INTO events VALUES (row1), (row2), ...;

-- Option 3: Reduce merge pressure
ALTER TABLE events MODIFY SETTING max_parts_in_total = 10000;
SYSTEM STOP MERGES events;  -- Temporarily during bulk load
-- ... run inserts ...
SYSTEM START MERGES events;

-- Option 4: Force merge after bulk load
OPTIMIZE TABLE events;
```

## Replication Issues

### Issue: High Replication Lag

**Diagnosis:**
```sql
SELECT
    database,
    table,
    total_replicas,
    active_replicas,
    absolute_delay
FROM system.replicas
ORDER BY absolute_delay DESC;

-- Check replication queue
SELECT * FROM system.replication_queue;
```

**Solutions:**
```bash
# Check network between replicas
ping replica-host
mtr replica-host

# Check ZooKeeper health
echo stat | nc zookeeper-host 2181
echo mntr | nc zookeeper-host 2181

# Force sync replica
clickhouse-client --query "SYSTEM SYNC REPLICA database.table;"

# Restart replica if stuck
sudo systemctl restart clickhouse-server

# If far behind, resync from scratch
# clickhouse-client --query "SYSTEM DROP REPLICA 'replica2' FROM ZOOKEEPER;"
```

## Kafka Integration Issues

### Issue: Kafka Table Not Consuming

**Diagnosis:**
```sql
-- Check Kafka consumer status
SELECT * FROM system.kafka_consumers;

-- Check for Kafka-related errors
SELECT exception, COUNT() as count
FROM system.query_log
WHERE query LIKE '%Kafka%'
  AND exception != ''
  AND event_date >= today() - 1
GROUP BY exception;
```

**Solutions:**
```bash
# Check connectivity to Kafka broker
telnet kafka-broker 9092

# Verify consumer group exists
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
    --group clickhouse_consumer --describe

# Reset offsets to consume from beginning
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
    --group clickhouse_consumer --reset-offsets --to-earliest \
    --topic events --execute

# Recreate Kafka table if needed
# clickhouse-client --query "DROP TABLE kafka_events;"
# clickhouse-client -d default < create_kafka_table.sql
```

## Disk Space Issues

### Issue: Disk Running Out

**Emergency Response:**
```sql
-- 1. Check disk space
SELECT
    formatReadableSize(free_space) as free,
    formatReadableSize(total_space) as total,
    round(free_space / total_space * 100, 2) as free_percent
FROM system.disks;

-- 2. Identify largest tables
SELECT
    database,
    name as table,
    formatReadableSize(SUM(bytes_on_disk)) as size,
    COUNT() as parts_count
FROM system.parts
WHERE active = 1
  AND database NOT IN ('system', 'information_schema')
GROUP BY database, name
ORDER BY bytes_on_disk DESC
LIMIT 10;

-- 3. Drop old partitions (instant)
ALTER TABLE events DROP PARTITION '202301';
ALTER TABLE events DROP PARTITION '202302';

-- 4. Trigger optimization
OPTIMIZE TABLE events FINAL;

-- 5. Add TTL for automatic cleanup
ALTER TABLE events MODIFY TTL timestamp + INTERVAL 90 DAY;
```

## Configuration Issues

### Issue: Connections Exhausted

**Check:**
```sql
SELECT COUNT() as active_connections
FROM system.processes;

-- Check per-user connections
SELECT user, COUNT() as connections
FROM system.processes
GROUP BY user;
```

**Fix:**
```xml
<!-- config.xml -->
<max_connections>4096</max_connections>
<max_concurrent_queries>200</max_concurrent_queries>
```

### Issue: Slow Merges

**Check:**
```sql
SELECT
    database,
    table,
    elapsed,
    progress,
    num_parts
FROM system.merges
ORDER BY elapsed DESC;
```

**Fix:**
```xml
<!-- config.xml -->
<merge_tree>
    <max_bytes_to_merge_at_max_space_in_pool>161061273600</max_bytes_to_merge_at_max_space_in_pool>
    <max_replicated_merges_in_queue>16</max_replicated_merges_in_queue>
</merge_tree>

<background_pool_size>32</background_pool_size>
<background_schedule_pool_size>16</background_schedule_pool_size>
```

## Cluster Issues

### Issue: Node Unresponsive

**Check:**
```bash
# Check if process running
ps aux | grep clickhouse-server

# Check logs
tail -f /var/log/clickhouse-server/clickhouse-server.log
tail -f /var/log/clickhouse-server/clickhouse-server.err.log

# Check connections
netstat -an | grep 9000
netstat -an | grep 8123
```

**Resolution:**
```bash
# Restart service
sudo systemctl restart clickhouse-server

# Check status
sudo systemctl status clickhouse-server

# If corruption suspected, check data directory
sudo -u clickhouse clickhouse-local --query "SELECT * FROM file('/var/lib/clickhouse/data/default/events/*.bin', Native)" LIMIT 1
```

### Issue: Split Brain (Cluster)

**Detection:**
```sql
-- Check cluster view from each node
SELECT * FROM system.clusters WHERE cluster = 'production_cluster';

-- Check ZooKeeper connectivity
SELECT * FROM system.zookeeper WHERE path = '/';
```

**Resolution:**
```bash
# Verify ZooKeeper ensemble
echo mntr | nc zookeeper1 2181
echo mntr | nc zookeeper2 2181
echo mntr | nc zookeeper3 2181

# Check ZooKeeper quorum
# Should have leader + followers, not multiple leaders

# If necessary, restart ZooKeeper ensemble
# (Follow ZooKeeper maintenance procedures)
```

## Backup/Restore Issues

### Issue: Backup Failed

**Check:**
```bash
# Check backup command output
clickhouse-client --query "BACKUP DATABASE default TO Disk('backups', 'test.zip');"

# Check disk space on backup destination
df -h /backups

# Check permissions
ls -la /var/lib/clickhouse/disks/backups/
```

**Resolution:**
```bash
# Ensure backup disk configured in config.xml
# <clickhouse>
#   <storage_configuration>
#     <disks>
#       <backups>
#         <type>local</type>
#         <path>/backups/clickhouse/</path>
#       </backups>
#     </disks>
#   </storage_configuration>
# </clickhouse>

# Test backup to local directory
clickhouse-client --query "BACKUP TABLE events TO File('/tmp/events_backup.zip');"
```

### Issue: Restore Failed

**Troubleshooting:**
```bash
# Verify backup integrity
unzip -t /backups/clickhouse/db_20240115.zip

# Check ClickHouse version compatibility
clickhouse-client --version

# Try restoring single table first
clickhouse-client --query "RESTORE TABLE events FROM Disk('backups', 'events_20240115.zip');"

# Check error logs
tail -100 /var/log/clickhouse-server/clickhouse-server.err.log
```

## Performance Degradation Checklist

When experiencing slow queries or high latency:

1. **Check resource utilization** (CPU, memory, disk I/O)
2. **Review recent configuration changes**
3. **Check for long-running queries** (KILL if necessary)
4. **Verify replication is healthy**
5. **Check merge queue length**
6. **Review query patterns** (new expensive queries?)
7. **Check disk space** (< 20% triggers slowdowns)
8. **Verify network latency** (for distributed queries)
9. **Check ZooKeeper performance** (if using replication)
10. **Review recent schema changes** (new indexes, codecs)

## Emergency Runbook

### Critical: Service Down

1. Check if process running: `ps aux | grep clickhouse`
2. Check logs: `tail -100 /var/log/clickhouse-server/clickhouse-server.err.log`
3. Try restart: `sudo systemctl restart clickhouse-server`
4. If fails, check disk space: `df -h`
5. If disk full, emergency cleanup (see Disk Space section)
6. Check for corrupted data: review error logs
7. Last resort: restore from backup

### Critical: Data Corruption

1. Identify affected tables from error logs
2. Check data integrity: `CHECK TABLE table_name;`
3. Try to recover: `OPTIMIZE TABLE table_name FINAL;`
4. If unrecoverable, restore from backup
5. Document incident for post-mortem

### Critical: Replication Broken

1. Check replication status on all replicas
2. Identify lagging replicas
3. Check ZooKeeper connectivity
4. Force sync: `SYSTEM SYNC REPLICA database.table;`
5. If stuck, consider re-syncing replica from scratch
6. Document root cause after resolution
