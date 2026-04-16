# ClickHouse Troubleshooting Deep Dive

Extended troubleshooting guide for production issues with root cause analysis and resolution procedures.

## Issue Categories

1. [Query Performance Issues](#query-performance-issues)
2. [Resource Issues (Memory, CPU, Disk)](#resource-issues)
3. [Replication & Clustering](#replication--clustering)
4. [Data Ingestion Issues](#data-ingestion-issues)
5. [Operational Issues](#operational-issues)

---

## Query Performance Issues

### Issue: Query Timeout (Slow Queries)

**Symptoms:**
- Queries killed with "Max execution time exceeded"
- Client connection timeouts
- p95 latency > 5 seconds
- Users reporting "queries hang"

**Root Causes:**
1. Insufficient indexing / too much data scanned
2. Expensive GROUP BY cardinality
3. Memory pressure causing disk spilling
4. Table fragmentation (too many parts)
5. Replication lag blocking queries

**Diagnosis Queries:**

```sql
-- Find the slow queries
SELECT
    event_time,
    query_duration_ms,
    read_rows,
    read_bytes / 1024 / 1024 / 1024 as read_gb,
    memory_usage / 1024 / 1024 / 1024 as memory_gb,
    exception,
    query
FROM system.query_log
WHERE event_date >= today() - 1
  AND type = 'QueryFinish'
  AND query_duration_ms > 5000  -- > 5 seconds
  AND query NOT LIKE '%system.%'
ORDER BY query_duration_ms DESC
LIMIT 30;

-- Estimate how much data each table read
SELECT
    table,
    AVG(read_bytes) / 1024 / 1024 / 1024 as avg_gb_per_query,
    MAX(read_bytes) / 1024 / 1024 / 1024 as max_gb_per_query,
    AVG(query_duration_ms) as avg_duration_ms
FROM system.query_log
WHERE event_date >= today() - 7
  AND type = 'QueryFinish'
  AND query NOT LIKE '%INSERT%'
GROUP BY table
ORDER BY avg_gb_per_query DESC;

-- Identify GROUP BY cardinality problems
SELECT
    substring(query, 1, 300) as query_pattern,
    COUNT() as exec_count,
    AVG(memory_usage) / 1024 / 1024 / 1024 as avg_memory_gb,
    MAX(memory_usage) / 1024 / 1024 / 1024 as max_memory_gb,
    AVG(query_duration_ms) as avg_duration_ms
FROM system.query_log
WHERE event_date >= today() - 7
  AND query LIKE '%GROUP BY%'
  AND type = 'QueryFinish'
GROUP BY query_pattern
ORDER BY max_memory_gb DESC
LIMIT 20;
```

**Solutions:**

1. **Add missing indexes:**
   ```sql
   -- Identify columns frequently filtered
   -- From query logs, find WHERE clause columns

   -- Add index to accelerate filtering
   ALTER TABLE events ADD INDEX idx_user_id user_id TYPE minmax GRANULARITY 4;
   ALTER TABLE events ADD INDEX idx_timestamp timestamp TYPE minmax GRANULARITY 4;

   -- For text search
   ALTER TABLE events ADD INDEX idx_event_type event_type TYPE set(1) GRANULARITY 4;
   ```

2. **Optimize expensive GROUP BY:**
   ```sql
   -- Instead of exact count of unique users (memory intensive):
   SELECT COUNT(DISTINCT user_id) FROM events;

   -- Use approximate (memory efficient):
   SELECT uniq(user_id) FROM events;  -- Approximate count
   SELECT topK(1000)(user_id) FROM events;  -- Top N without full GROUP BY

   -- For cardinality reduction:
   SELECT
       user_id,
       count() as event_count
   FROM events
   WHERE timestamp >= today() - 7  -- Reduce date range
   GROUP BY user_id
   LIMIT 1000000;  -- Limit result set
   ```

3. **Reduce scanned data:**
   ```sql
   -- Always filter by partition key
   SELECT COUNT() FROM events WHERE timestamp >= today() - 7;

   -- Use sampling for estimates
   SELECT COUNT() * 10 as estimated_total FROM events SAMPLE 0.1;

   -- Enable early termination for LIMIT
   SET max_rows_to_read = 1000000;
   SELECT * FROM events LIMIT 1000;
   ```

4. **Increase memory limit for specific query:**
   ```sql
   SET max_memory_usage = 30000000000;  -- 30 GB
   SELECT ... GROUP BY ...;
   ```

5. **Increase global execution timeout:**
   ```sql
   SET max_execution_time = 300;  -- 5 minutes (from default 30s)
   SELECT ... FROM long_running_analysis;
   ```

---

### Issue: Query Returns Wrong Results

**Symptoms:**
- Results differ between runs
- Partial data returned
- COUNT() mismatch between replicas

**Root Causes:**
1. Dirty reads during merges (reading inconsistent snapshots)
2. TTL removal between queries
3. Replication lag causing different data on replicas
4. Integer overflow in SUM operations

**Diagnosis:**

```sql
-- Check for ongoing merges affecting data
SELECT * FROM system.merges;

-- Compare data between replicas
SELECT
    COUNT() as count_replica1
FROM clusterAllReplicas('production_cluster', default.events)
WHERE timestamp >= today();

-- Detect recent TTL deletions
SELECT
    event_date,
    COUNT() as partition_drop_count
FROM system.part_log
WHERE event_type = 'RemovePartFolder'
  AND event_date >= today() - 1
GROUP BY event_date;

-- Check for integer overflow (SUM of large numbers)
SELECT
    toTypeName(SUM(price)) as sum_type,
    SUM(CAST(price as Decimal128(2))) as exact_sum
FROM events;
```

**Solutions:**

1. **Force consistency by using FINAL (slow but accurate):**
   ```sql
   SELECT COUNT() FROM events FINAL;  -- Waits for merges
   ```

2. **Use materialized views for consistent snapshots:**
   ```sql
   CREATE MATERIALIZED VIEW events_snapshot (...)
   ENGINE = SummingMergeTree()
   AS SELECT timestamp, event_type, COUNT() FROM events
   GROUP BY timestamp, event_type;

   SELECT * FROM events_snapshot;  -- Consistent results
   ```

3. **Handle integer overflow:**
   ```sql
   -- Instead of SUM(price) which may overflow
   SELECT CAST(SUM(CAST(price as Decimal128(2))) as Decimal(18, 2))
   FROM events;
   ```

4. **Wait for replication to catch up:**
   ```sql
   SYSTEM SYNC REPLICA events;  -- On replica node
   ```

---

## Resource Issues

### Issue: Out of Memory (OOM) Killer

**Symptoms:**
- `Memory limit exceeded` error in logs
- ClickHouse process killed unexpectedly
- `dmesg` shows OOM killer messages
- Query failures with "Cannot allocate memory"

**Root Causes:**
1. Single query with huge GROUP BY cardinality
2. Multiple concurrent queries hitting memory limits
3. Memory leak in background operations (rare)
4. Insufficient server memory for workload
5. Memory limits set too low

**Diagnosis:**

```sql
-- Find memory peak by query type
SELECT
    extractString(query, '^(\\w+)') as query_type,
    COUNT() as exec_count,
    MAX(memory_usage) / 1024 / 1024 / 1024 as peak_memory_gb,
    AVG(memory_usage) / 1024 / 1024 / 1024 as avg_memory_gb
FROM system.query_log
WHERE event_date >= today() - 7
GROUP BY query_type
ORDER BY peak_memory_gb DESC;

-- Check current memory usage breakdown
SELECT
    query_id,
    user,
    memory_usage / 1024 / 1024 / 1024 as memory_gb,
    peak_memory_usage / 1024 / 1024 / 1024 as peak_memory_gb,
    elapsed,
    query
FROM system.processes
ORDER BY memory_usage DESC;

-- Monitor memory trend (daily peak)
SELECT
    event_date,
    MAX(memory_usage) / 1024 / 1024 / 1024 as daily_peak_gb,
    AVG(memory_usage) / 1024 / 1024 / 1024 as daily_avg_gb
FROM system.query_log
WHERE event_date >= today() - 30
  AND type = 'QueryFinish'
GROUP BY event_date
ORDER BY event_date DESC;

-- Check server-level memory limit
SELECT
    value as max_server_memory_bytes,
    value / 1024 / 1024 / 1024 as max_server_memory_gb
FROM system.settings
WHERE name = 'max_server_memory_usage';
```

**Solutions:**

1. **Increase server memory limit (if hardware allows):**
   ```xml
   <!-- /etc/clickhouse-server/config.xml -->
   <max_server_memory_usage>128000000000</max_server_memory_usage>  <!-- 128 GB -->
   ```

2. **Kill memory-intensive query:**
   ```sql
   KILL QUERY WHERE query_id = 'abc123def456';

   -- Or kill all queries from user running memory tests
   KILL QUERY WHERE user = 'batch_user';
   ```

3. **Reduce GROUP BY cardinality:**
   ```sql
   -- Problematic: full distinct count
   SELECT COUNT(DISTINCT user_id) FROM events;

   -- Better: approximate
   SELECT uniq(user_id) FROM events;

   -- Or: top-N instead of all
   SELECT topK(1000)(user_id) FROM events;
   ```

4. **Use approximate aggregations:**
   ```sql
   -- Instead of exact GROUP BY with massive cardinality
   SELECT user_id, COUNT() FROM events GROUP BY user_id;

   -- Use sampling or limit
   SELECT user_id, COUNT() FROM events SAMPLE 0.1 GROUP BY user_id;
   SELECT user_id, COUNT() FROM events GROUP BY user_id LIMIT 1000000;
   ```

5. **Process in batches:**
   ```sql
   -- Instead of processing all data at once
   FOR date IN (SELECT DISTINCT toDate(timestamp) FROM events)
   LOOP
       INSERT INTO results SELECT ... FROM events WHERE toDate(timestamp) = date;
   END LOOP;
   ```

6. **Monitor and alert on memory:**
   ```sql
   -- Add to monitoring/alerting
   SELECT
       formatReadableSize(value) as memory_usage,
       formatReadableSize(80000000000) as memory_limit,
       round(value / 80000000000 * 100, 1) as percent_of_limit
   FROM system.metrics
   WHERE metric = 'MemoryTracking';
   -- Alert if > 80% of limit
   ```

---

### Issue: High CPU Usage

**Symptoms:**
- CPU at 100% on all cores
- Load average > core count
- Query latency degradation
- System becomes unresponsive

**Root Causes:**
1. Queries with max_threads set too high
2. Merge operations running during query peak
3. Too many concurrent queries
4. Inefficient query plans

**Diagnosis:**

```sql
-- Check thread allocation
SELECT
    value,
    description
FROM system.settings
WHERE name IN ('max_threads', 'background_pool_size');

-- Identify CPU-heavy queries
SELECT
    event_date,
    COUNT() as query_count,
    AVG(query_duration_ms) as avg_duration_ms,
    SUM(query_duration_ms) as total_cpu_ms
FROM system.query_log
WHERE event_date >= today() - 1
GROUP BY event_date
ORDER BY total_cpu_ms DESC;

-- Monitor concurrent query count
SELECT
    COUNT() as active_queries,
    COUNT(DISTINCT user) as unique_users,
    MAX(elapsed) as longest_query_sec
FROM system.processes;
```

**Solutions:**

1. **Reduce max_threads:**
   ```sql
   -- Instead of max_threads = CPU cores
   SET max_threads = 8;  -- Even on 16-core system

   -- Permanently in config.xml
   <max_threads>8</max_threads>
   ```

2. **Throttle background operations during peak:**
   ```sql
   SYSTEM STOP MERGES events;  -- Pause merges
   -- ... run peak queries ...
   SYSTEM START MERGES events;

   -- Or reduce merge concurrency
   <background_pool_size>4</background_pool_size>  <!-- Default 16 -->
   ```

3. **Limit concurrent queries:**
   ```xml
   <max_concurrent_queries>50</max_concurrent_queries>  <!-- Queue beyond this -->
   ```

4. **Kill runaway queries:**
   ```sql
   -- Find long-running queries
   SELECT query_id, user, elapsed FROM system.processes ORDER BY elapsed DESC;

   -- Kill specific query
   KILL QUERY WHERE query_id = 'abc123';

   -- Kill all from user
   KILL QUERY WHERE user = 'problematic_app';
   ```

---

### Issue: Disk Space Running Out

**Symptoms:**
- INSERT queries fail with "No space left on device"
- ClickHouse stops responding
- Backups fail
- Merge operations halt

**Root Causes:**
1. Rapid data growth exceeding capacity
2. Old data not cleaned up (missing TTL)
3. Backup files consuming space
4. Log files growing unchecked
5. Failed merges leaving orphaned files

**Diagnosis:**

```sql
-- Check disk space immediately
SELECT
    formatReadableSize(total_space) as total,
    formatReadableSize(free_space) as free,
    round(free_space / total_space * 100, 1) as free_pct,
    if(free_space / total_space < 0.2, 'CRITICAL', if(free_space / total_space < 0.3, 'WARNING', 'OK')) as status
FROM system.disks;

-- Find largest tables
SELECT
    database,
    name as table,
    formatReadableSize(total_bytes) as size
FROM system.tables
WHERE database NOT IN ('system', 'information_schema')
ORDER BY total_bytes DESC
LIMIT 20;

-- Check backup directory size
SELECT
    COUNT() as backup_count,
    SUM(size) / 1024 / 1024 / 1024 as total_backup_gb
FROM file('/backups/clickhouse/*');  -- If accessible
```

**Solutions - Immediate (Crisis Mode):**

```bash
# 1. Check disk space and identify culprits
df -h /var/lib/clickhouse
du -sh /var/lib/clickhouse/*

# 2. Delete old backups
rm -rf /backups/clickhouse/*_20231*  # Delete backups older than certain date

# 3. Clear log files
rm -f /var/log/clickhouse-server/*.log.10
rm -f /var/log/clickhouse-server/*.err.log.10

# 4. If still critical, drop oldest partitions
clickhouse-client << 'EOF'
ALTER TABLE events DROP PARTITION '202301';
ALTER TABLE events DROP PARTITION '202302';
EOF
```

**Solutions - Long-term (Proper Fix):**

```sql
-- 1. Enable TTL for automatic cleanup
ALTER TABLE events MODIFY TTL timestamp + INTERVAL 90 DAY;

-- 2. Force optimization to clean up old data
OPTIMIZE TABLE events FINAL;

-- 3. Drop partitions in batches (non-blocking)
ALTER TABLE events DROP PARTITION '202301';
ALTER TABLE events DROP PARTITION '202302';
ALTER TABLE events DROP PARTITION '202303';

-- 4. Schedule regular cleanup
-- Add to cron:
-- 0 3 * * * clickhouse-client -q "ALTER TABLE events DELETE WHERE timestamp < now() - INTERVAL 90 DAY;"

-- 5. Verify new disk space
SELECT
    formatReadableSize(total_space) as total,
    formatReadableSize(free_space) as free,
    round(free_space / total_space * 100, 2) as free_pct
FROM system.disks;
```

**Capacity Planning:**

```bash
# Calculate growth rate
# Days to fill = free_space / (daily_growth_rate * 3)
# Example: 500 GB free, 50 GB/day growth = 500 / 50 / 3 = 3.3 days

# Monitor growth trend
clickhouse-client << 'EOF'
SELECT
    event_date,
    (SELECT formatReadableSize(SUM(bytes_on_disk)) FROM system.parts WHERE active = 1 AND event_date = DATE) as daily_size
FROM system.part_log
WHERE event_date >= today() - 30
GROUP BY event_date
ORDER BY event_date DESC;
EOF
```

---

## Replication & Clustering

### Issue: High Replication Lag

**Symptoms:**
- `absolute_delay > 60` seconds
- Queries return stale data on replicas
- Read-heavy applications see inconsistent results
- "Unable to fetch from ZooKeeper" errors

**Root Causes:**
1. Network latency or packet loss between replicas
2. ZooKeeper unavailable or slow
3. Replica disk I/O bottleneck
4. Large mutations causing slow replay
5. Replica resource constraints (memory/CPU)

**Diagnosis:**

```sql
-- Check lag per table
SELECT
    database,
    table,
    total_replicas,
    active_replicas,
    absolute_delay,
    relative_delay,
    last_queue_update
FROM system.replicas
WHERE absolute_delay > 0
ORDER BY absolute_delay DESC;

-- Check replication queue depth
SELECT
    database,
    table,
    COUNT() as queue_length,
    MIN(create_time) as oldest_entry_age
FROM system.replication_queue
WHERE active = 1
GROUP BY database, table
ORDER BY queue_length DESC;

-- Check ZooKeeper connectivity
SELECT * FROM system.zookeeper PATH '/clickhouse/tables';

-- Monitor replica resource usage
SELECT
    hostname() as server,
    COUNT(DISTINCT query_id) as active_queries,
    SUM(memory_usage) / 1024 / 1024 / 1024 as memory_gb,
    MAX(elapsed) as longest_query_sec
FROM clusterAllReplicas('production_cluster', system.processes)
GROUP BY server;
```

**Solutions:**

1. **Force sync if slightly lagged:**
   ```sql
   -- On the replica
   SYSTEM SYNC REPLICA database.table;
   ```

2. **Check network connectivity:**
   ```bash
   # From replica to leader
   ping -c 5 leader-host

   # Test TCP connection
   nc -zv leader-host 9000

   # Check network path (show hops)
   mtr leader-host --report --report-cycles=10
   ```

3. **Verify ZooKeeper health:**
   ```bash
   # Check ZK cluster status
   echo stat | nc zookeeper-host 2181

   # Check leader
   echo mntr | nc zookeeper-host 2181 | grep zk_server_state

   # List ZK nodes
   echo ls /clickhouse/tables | nc zookeeper-host 2181
   ```

4. **Restart replica if stuck:**
   ```bash
   sudo systemctl restart clickhouse-server

   # Monitor during restart
   tail -f /var/log/clickhouse-server/clickhouse-server.log
   ```

5. **Process replication queue manually (if severely stuck):**
   ```sql
   -- Drain queue by processing entries
   SELECT * FROM system.replication_queue LIMIT 100;

   -- If needed, drop replica and resync
   -- SYSTEM DROP REPLICA 'replica2' FROM ZOOKEEPER;
   ```

---

### Issue: Cluster Coordination Failures

**Symptoms:**
- "Cannot connect to ZooKeeper" errors
- Random replica drops from cluster
- INSERT failures: "Not leader"
- Distributed queries return partial results

**Root Causes:**
1. ZooKeeper quorum lost (< 3 nodes healthy)
2. ZooKeeper GC pauses causing timeout
3. Network partition between replicas
4. ZooKeeper disk full

**Diagnosis:**

```bash
# Check ZooKeeper quorum (need > 3 nodes for 5-node cluster)
for host in zk1 zk2 zk3 zk4 zk5; do
    echo "=== $host ==="
    echo stat | nc $host 2181 | grep Mode
done

# Check ZooKeeper disk space
ssh zk1 "df -h /var/lib/zookeeper"

# Monitor ZooKeeper logs for issues
ssh zk1 "tail -50 /var/log/zookeeper/zookeeper.log | grep -i error"

# Check ClickHouse ZK connection logs
grep -i zookeeper /var/log/clickhouse-server/clickhouse-server.log | tail -50
```

**Solutions:**

1. **Restore ZooKeeper quorum:**
   ```bash
   # If one ZK node down, wait for restart
   sudo systemctl status zookeeper

   # If two+ down, need manual intervention
   # Contact ZK team / consult ZK documentation
   ```

2. **Force full replication resync (last resort):**
   ```bash
   # On each replica
   clickhouse-client << 'EOF'
   SYSTEM DROP REPLICA 'replica2' FROM ZOOKEEPER;
   EOF

   # Will re-fetch all data from leader
   # Takes time proportional to data size
   ```

---

## Data Ingestion Issues

### Issue: Slow Inserts

**Symptoms:**
- INSERT throughput < expected rows/second
- Batch inserts take longer than anticipated
- Rows/second degrades over time
- `Cannot set data_max_wait_time_when_write_to_one_replica_timeout` errors

**Root Causes:**
1. Too many small parts (table fragmentation)
2. Merge operations competing for resources
3. Replication bottleneck (waiting for replicas)
4. Row/batch too small (overhead dominates)
5. Kafka consumer lag accumulating

**Diagnosis:**

```sql
-- Check insert throughput
SELECT
    table,
    COUNT() as insert_count,
    SUM(rows) as total_rows,
    round(SUM(rows) / SUM(CAST(query_duration_ms as Float64)) * 1000, 0) as rows_per_second,
    AVG(query_duration_ms) as avg_insert_ms
FROM system.query_log
WHERE query LIKE 'INSERT%'
  AND type = 'QueryFinish'
  AND event_date >= today()
GROUP BY table
ORDER BY rows_per_second DESC;

-- Check parts count (fragmentation)
SELECT
    database,
    table,
    COUNT() as parts_count,
    SUM(rows) as total_rows,
    if(COUNT() > 1000, 'VERY_FRAGMENTED', if(COUNT() > 100, 'FRAGMENTED', 'OK')) as health
FROM system.parts
WHERE active = 1
GROUP BY database, table
ORDER BY parts_count DESC;

-- Check merge queue depth
SELECT
    database,
    table,
    COUNT() as pending_merges,
    SUM(total_size_bytes_compressed) / 1024 / 1024 / 1024 as pending_merge_gb
FROM system.merges
GROUP BY database, table
ORDER BY pending_merge_gb DESC;

-- Analyze Kafka consumption lag
SELECT
    table,
    consumer_number,
    messages_read,
    last_poll_time
FROM system.kafka_consumers;
```

**Solutions:**

1. **Increase batch size:**
   ```sql
   -- Instead of: INSERT INTO events VALUES (1), (2), (3);
   -- Insert larger batch:
   INSERT INTO events
   SELECT *
   FROM external_events_source
   LIMIT 100000;  -- Batch of 100k rows instead of individual rows
   ```

2. **Pause merges during bulk load:**
   ```sql
   SYSTEM STOP MERGES events;

   -- Run inserts
   INSERT INTO events ...;
   INSERT INTO events ...;
   INSERT INTO events ...;

   SYSTEM START MERGES events;
   OPTIMIZE TABLE events FINAL;  -- Consolidate parts after load
   ```

3. **Use async inserts for non-critical data:**
   ```sql
   SET async_insert = 1;
   SET wait_for_async_insert = 0;

   -- Rows buffered and inserted in batches automatically
   INSERT INTO events VALUES (123, 'event', now());
   INSERT INTO events VALUES (124, 'event', now());
   ```

4. **Optimize table settings:**
   ```sql
   ALTER TABLE events MODIFY SETTING
       max_parts_in_total = 10000,  -- Allow more parts before forced merge
       parts_to_throw_insert = 20000;  -- Fail at this threshold
   ```

5. **Add resources:**
   ```xml
   <!-- Increase merge parallelism in config.xml -->
   <background_pool_size>32</background_pool_size>  <!-- Up from 16 -->
   <background_schedule_pool_size>16</background_schedule_pool_size>
   ```

---

### Issue: Kafka Consumer Not Consuming

**Symptoms:**
- Kafka table shows no consumption
- Consumer lag grows indefinitely
- No errors in ClickHouse logs
- Data never appears in ClickHouse table

**Root Causes:**
1. Kafka broker unreachable
2. Topic doesn't exist or wrong name
3. Consumer group offset reset needed
4. Schema mismatch
5. ClickHouse Kafka table stopped/crashed

**Diagnosis:**

```sql
-- Check Kafka consumer status
SELECT * FROM system.kafka_consumers;

-- Check for Kafka connection errors
SELECT
    exception,
    COUNT() as count,
    MAX(event_time) as last_error
FROM system.query_log
WHERE query LIKE '%kafka%'
  AND exception != ''
GROUP BY exception;

-- Monitor table row count (should increase)
SELECT COUNT() FROM kafka_events;

-- Wait 30 seconds and check again
SELECT COUNT() FROM kafka_events;
```

**Solutions:**

1. **Verify broker connectivity:**
   ```bash
   # From ClickHouse server
   nc -zv kafka-broker.example.com 9092

   # Check topic exists
   kafka-topics.sh --list --bootstrap-server kafka:9092 | grep events_topic
   ```

2. **Check consumer group status:**
   ```bash
   # List consumer groups
   kafka-consumer-groups.sh --list --bootstrap-server kafka:9092

   # Check lag
   kafka-consumer-groups.sh \
       --bootstrap-server kafka:9092 \
       --group clickhouse_consumer \
       --describe
   ```

3. **Reset consumer offsets (restart from beginning):**
   ```bash
   kafka-consumer-groups.sh \
       --bootstrap-server kafka:9092 \
       --group clickhouse_consumer \
       --reset-offsets \
       --to-earliest \
       --topic events_topic \
       --execute
   ```

4. **Recreate Kafka table:**
   ```sql
   -- Drop existing
   DROP TABLE kafka_events;

   -- Recreate with correct settings
   CREATE TABLE kafka_events (
       user_id UInt32,
       event_type String,
       timestamp DateTime
   )
   ENGINE = Kafka()
   SETTINGS
       kafka_broker_list = 'kafka1:9092,kafka2:9092',
       kafka_topic_list = 'events_topic',
       kafka_group_id = 'clickhouse_consumer',
       kafka_format = 'JSONEachRow',
       kafka_skip_broken_messages = 1;  -- Skip malformed messages
   ```

5. **Monitor consumption rate:**
   ```sql
   -- Check consumption speed
   SELECT
       table,
       messages_read,
       last_poll_time,
       now() - last_poll_time as seconds_since_poll
   FROM system.kafka_consumers;
   ```

---

## Operational Issues

### Issue: Unresponsive ClickHouse Server

**Symptoms:**
- Queries hang indefinitely
- Cannot connect via clickhouse-client
- Process shows 100% CPU or high I/O wait
- Server locks up for seconds at a time

**Root Causes:**
1. Long-running query blocking other queries
2. Deadlock in table operations
3. Memory pressure causing I/O thrashing
4. Merge operation on large table
5. Kernel-level I/O issue

**Diagnosis & Recovery:**

```bash
# Check if process is running
ps aux | grep clickhouse-server

# Monitor system resources
top -b -n 1 | head -20
iostat -x 1 5

# Check network connections to ClickHouse
netstat -an | grep :9000 | wc -l

# Check logs for recent errors
tail -100 /var/log/clickhouse-server/clickhouse-server.log | grep -i error

# If severely stuck, check strace (identify blocking syscall)
sudo strace -p $(pgrep clickhouse-server) -e trace=open,read,write 2>&1 | head -50
```

**Solutions:**

1. **Identify and kill long-running query:**
   ```sql
   -- If can still connect
   SELECT query_id, user, elapsed, query
   FROM system.processes
   ORDER BY elapsed DESC
   LIMIT 5;

   KILL QUERY WHERE query_id = 'long_query_id';
   ```

2. **Graceful restart (preferred):**
   ```bash
   # Stop gracefully (waits for queries to finish)
   sudo systemctl stop clickhouse-server

   # Monitor shutdown
   tail -f /var/log/clickhouse-server/clickhouse-server.log

   # Start
   sudo systemctl start clickhouse-server
   ```

3. **Force kill (only if graceful fails):**
   ```bash
   # Kill server process
   sudo pkill -SIGTERM clickhouse-server

   # Wait 30 seconds, then force
   sudo pkill -9 clickhouse-server

   # Restart
   sudo systemctl start clickhouse-server
   ```

4. **Check for data corruption:**
   ```bash
   # After restart, verify table integrity
   clickhouse-client << 'EOF'
   CHECK TABLE events;
   CHECK TABLE other_table;
   EOF
   ```

---

### Issue: Failed Backup/Restore

**Symptoms:**
- BACKUP command hangs or fails
- RESTORE fails with "File not found"
- Backup file corrupted or incomplete
- Restore leaves database in bad state

**Solutions:**

```bash
# 1. Verify backup destination has space
df -h /backups

# 2. Check backup file integrity
ls -lah /backups/clickhouse_backup.zip
file /backups/clickhouse_backup.zip

# 3. Restore to test server first
# Don't restore to production without testing

# 4. If restore fails mid-way, cleanup
# DROP DATABASE test_restore;

# 5. Use alternative backup method if native BACKUP fails
# rsync -av /var/lib/clickhouse/ /backup/location/
```
