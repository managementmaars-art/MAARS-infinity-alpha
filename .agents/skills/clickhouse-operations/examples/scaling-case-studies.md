# ClickHouse Scaling Decision Trees & Case Studies

Practical guidance for scaling decisions based on real-world scenarios and bottlenecks.

## Case Study 1: Scaling for Growing Data Volume

**Scenario:**
- Current: Single node, 2 TB data, 100 GB/day growth
- Problem: Disk filling up, approaching 500 GB free (< 20%)
- Timeline: 5 days until critical space

**Assessment Queries:**

```sql
-- Current capacity
SELECT
    database,
    name as table,
    formatReadableSize(total_bytes) as size,
    total_rows
FROM system.tables
WHERE database NOT IN ('system', 'information_schema')
ORDER BY total_bytes DESC;

-- Growth rate (daily average)
SELECT
    toDate(event_date) as day,
    SUM(rows) as daily_rows,
    formatReadableSize(SUM(bytes_on_disk)) as daily_size
FROM system.part_log
WHERE event_date >= today() - 30
  AND event_type = 'NewPart'
GROUP BY day
ORDER BY day DESC
LIMIT 30;

-- Projection: Days until disk full
SELECT
    100 as gb_free,
    10 as gb_per_day_growth,
    100 / 10 as days_until_critical;
```

**Decision Tree:**

```
Is growth predictable and stable?
├─ YES
│  ├─ Is adding disk cheaper than cluster?
│  │  ├─ YES → Add 10 TB NVMe SSD
│  │  └─ NO → Scale horizontally (add shards)
│  └─ When? Within 1 week (before 10 days remaining)
│
└─ NO (bursty/unpredictable)
   ├─ Implement TTL policies immediately
   │  ALTER TABLE events MODIFY TTL timestamp + INTERVAL 60 DAY;
   │
   ├─ Add disk (short-term safety)
   │
   └─ Implement incremental backups to reduce local storage
```

**Implementation Plan (Vertical Scaling - Quick Win):**

```bash
#!/bin/bash
# 1. Add storage to existing server (if VM/cloud)

# For cloud VM:
# - AWS: Add EBS volume, mount to /var/lib/clickhouse-new
# - Azure: Add managed disk
# - GCP: Add persistent disk

# 2. Stop ClickHouse
sudo systemctl stop clickhouse-server

# 3. Migrate data (if needed)
# - If same disk: no action
# - If different disk:
rsync -av /var/lib/clickhouse/ /new-larger-disk/clickhouse/
sudo chown -R clickhouse:clickhouse /new-larger-disk/clickhouse

# 4. Update config.xml to point to new location
# <path>/new-larger-disk/clickhouse/</path>

# 5. Restart
sudo systemctl start clickhouse-server

# 6. Verify
clickhouse-client --query "SELECT COUNT() FROM events;"
```

**Implementation Plan (Horizontal Scaling - Permanent Solution):**

```yaml
# Decision: Add 2 additional nodes (3-node cluster)
# Cost: 3x server cost, but scales infinitely

# Step 1: Configure cluster
# /etc/clickhouse-server/config.xml on all 3 nodes

<remote_servers>
    <production_cluster>
        <shard>
            <replica>
                <host>node1.example.com</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>node2.example.com</host>
                <port>9000</port>
            </replica>
        </shard>
        <shard>
            <replica>
                <host>node3.example.com</host>
                <port>9000</port>
            </replica>
        </shard>
    </production_cluster>
</remote_servers>

# Step 2: Create distributed tables on all nodes
# CREATE TABLE events_local (...)
# ENGINE = ReplicatedMergeTree(...)
#
# CREATE TABLE events (...)
# ENGINE = Distributed('production_cluster', default, events_local, rand())

# Step 3: Migrate existing data
# INSERT INTO events_distributed SELECT * FROM events_local;
# DROP TABLE events_local;

# Step 4: Verify distribution
# SELECT hostname(), COUNT() FROM clusterAllReplicas(...);
```

**Cost Comparison:**
- Single node + extra disk: $2k upfront, no ongoing scaling
- 3-node cluster: $6k upfront, infinite scale capacity
- Recommendation: If growth continues beyond 5 TB, choose cluster

---

## Case Study 2: Scaling for Query Performance

**Scenario:**
- Current: Single node, 1 TB data
- Problem: Query latency p95 = 15 seconds (SLA = 5s)
- Symptom: `SELECT COUNT(*) FROM events` takes 12 seconds
- Cause: Scanning 1 TB of uncompressed data, only 1 thread

**Diagnosis:**

```sql
-- Identify slow query
SELECT
    query_duration_ms,
    read_bytes / 1024 / 1024 / 1024 as gb_read,
    read_rows,
    memory_usage / 1024 / 1024 / 1024 as memory_gb,
    query
FROM system.query_log
WHERE query LIKE 'SELECT COUNT%'
ORDER BY query_duration_ms DESC
LIMIT 5;

-- Check table compression
SELECT
    table,
    formatReadableSize(SUM(data_uncompressed_bytes)) as uncompressed,
    formatReadableSize(SUM(data_compressed_bytes)) as compressed,
    round(SUM(data_uncompressed_bytes) / SUM(data_compressed_bytes), 1) as ratio
FROM system.columns
WHERE database = 'default'
  AND table = 'events'
GROUP BY table;

-- Check CPU thread allocation
SELECT value FROM system.settings WHERE name = 'max_threads';
```

**Decision Tree:**

```
What's the bottleneck?
├─ High compression ratio (data_uncompressed / data_compressed > 5)
│  └─ Opportunity: Better compression codec can speed up by 2-3x
│     → Try ZSTD instead of LZ4
│     → Use column-specific codecs (DoubleDelta for timestamps)
│     → Downtime: Minutes (OPTIMIZE TABLE FINAL)
│
├─ Many parts / fragmented table
│  └─ Solution: Force merge to consolidate parts
│     → OPTIMIZE TABLE events FINAL;
│     → Instant reads become fast (fewer parts to scan)
│
├─ Low thread count (max_threads < 8)
│  └─ Solution: Increase parallelism
│     → SET max_threads = 16;  -- Use all cores
│     → Downtime: None, immediate effect
│
├─ Full table scan inefficient (no index)
│  └─ Solution: Add primary key / index
│     → ALTER TABLE events ADD INDEX idx_timestamp timestamp TYPE minmax;
│     → Helps filtering, not COUNT(*)
│
└─ Truly large dataset (> 2 TB per node)
   └─ Must scale horizontally
      → Shard across nodes
      → Each node handles smaller dataset
      → Queries parallelize across shards
```

**Quick Win (< 5 minutes downtime):**

```sql
-- 1. Check current compression
SELECT value FROM system.settings WHERE name = 'compression';

-- 2. Optimize table with better compression
-- Create new table with better codec
CREATE TABLE events_new (
    id UInt32,
    timestamp DateTime CODEC(DoubleDelta, LZ4),  -- Better for timestamps
    event_type LowCardinality(String),  -- Dictionary for enum-like columns
    user_id UInt32,
    value Float32 CODEC(Gorilla)  -- Optimized for floats
)
ENGINE = MergeTree()
ORDER BY timestamp;

-- 3. Copy data (can be done in background)
INSERT INTO events_new SELECT * FROM events;

-- 4. Switch
-- RENAME TABLE events TO events_old;
-- RENAME TABLE events_new TO events;

-- 5. After verifying: DROP TABLE events_old;
```

**Medium Solution (Increase threads, 15 mins):**

```sql
-- 1. Check current threads
SELECT value FROM system.settings WHERE name = 'max_threads';

-- 2. Increase for current session
SET max_threads = 32;  -- If 32-core system

-- 3. Make permanent
-- Edit /etc/clickhouse-server/config.xml
-- <max_threads>32</max_threads>
-- systemctl restart clickhouse-server

-- 4. Verify improvement
SELECT query_duration_ms FROM system.query_log
WHERE query LIKE 'SELECT COUNT%'
ORDER BY event_time DESC LIMIT 5;
```

**Long-term Solution (Shard cluster, 1-2 days):**

```sql
-- If single node still bottleneck after optimization:
-- Add 2 more nodes, shard data across them

-- Benefits:
-- - Each node processes 1/3 of data
-- - 3x faster query (3 parallel executions)
-- - Scales to any data size

-- See Case Study 1 for cluster setup procedure
```

**Expected Results:**
- Quick win alone: 2-4x speedup (better compression)
- + More threads: Another 2-4x (parallelism)
- + Sharding: Another 3x (distributed processing)
- Combined: 12-48x faster queries possible

---

## Case Study 3: Scaling for Insert Throughput

**Scenario:**
- Current: 50 MB/s insert rate, goal = 500 MB/s (10x)
- Problem: Kafka topic has 10x data, ClickHouse can't keep up
- Lag: 100 hours behind and growing
- Root cause: Single consumer group, table fragmentation

**Diagnosis:**

```sql
-- Check Kafka lag
SELECT
    consumer_number,
    messages_read,
    last_poll_time
FROM system.kafka_consumers;

-- Measure insert rate
SELECT
    toStartOfMinute(event_time) as minute,
    SUM(rows) as rows_inserted,
    SUM(CAST(query_duration_ms as Float64)) / 1000 as seconds_spent,
    SUM(rows) / (SUM(CAST(query_duration_ms as Float64)) / 1000) as rows_per_second,
    formatReadableSize(SUM(bytes_written_uncompressed)) as bytes_written
FROM system.query_log
WHERE query LIKE 'INSERT%'
  AND type = 'QueryFinish'
  AND event_date >= today()
GROUP BY minute
ORDER BY minute DESC;

-- Check parts count (high = merge overhead)
SELECT
    database,
    table,
    COUNT() as parts,
    SUM(rows) as total_rows,
    AVG(rows) as avg_rows_per_part
FROM system.parts
WHERE active = 1
GROUP BY database, table
ORDER BY parts DESC;
```

**Decision Tree:**

```
What's limiting insert throughput?

├─ Merges causing write stalls
│  └─ Parts count > 1000
│     ├─ Symptom: Inserts pause during merges
│     ├─ Solution 1: Pause merges, complete bulk load, resume
│     │  SYSTEM STOP MERGES events;
│     │  INSERT INTO events SELECT * FROM kafka_events LIMIT 10000000;
│     │  SYSTEM START MERGES events;
│     │
│     └─ Solution 2: Larger batch sizes
│        INSERT INTO events (...) LIMIT 100000;  # Instead of 1000
│
├─ Single Kafka consumer too slow
│  └─ Create multiple consumer groups in parallel
│     table_events_1: Partition 0,1,2
│     table_events_2: Partition 3,4,5
│     table_events_3: Partition 6,7,8
│     Then: INSERT INTO distributed_table SELECT * FROM table_events_N;
│
├─ Single insert thread saturated
│  └─ Use async inserts
│     SET async_insert = 1;
│     SET wait_for_async_insert = 0;
│     Inserts buffered and batched automatically
│
├─ Network bottleneck (unlikely but check)
│  └─ Profile insert query
│     SET send_logs_level = 'trace';
│     INSERT INTO events ...;
│     Check clickhouse-server.log for time breakdown
│
└─ Hardware CPU/disk I/O maxed
   └─ Only solution: Add nodes (horizontal scaling)
```

**Quick Wins (Same Day, No Downtime):**

```sql
-- 1. Enable async inserts
SET async_insert = 1;
SET wait_for_async_insert = 0;
-- Rows buffered (2 seconds or 100k rows), then batch inserted

-- 2. Pause merges during peak
SYSTEM STOP MERGES events;
-- Let merge operations complete first
-- Run in morning when traffic low
-- SYSTEM START MERGES events;

-- 3. Increase batch size (if pulling from queue)
-- Instead of: INSERT INTO events VALUES (row), (row), (row);
-- Do: INSERT INTO events SELECT * FROM source_queue LIMIT 100000;

-- 4. Check if replication is bottleneck
-- If replicas are slow, async might block
-- Verify: SYSTEM SHOW REPLICATION QUEUES;
```

**Medium Solutions (24 Hours, Minor Downtime):**

```sql
-- 1. Increase background pool size for merges
-- /etc/clickhouse-server/config.xml
-- <background_pool_size>64</background_pool_size>  <!-- Was 16 -->
-- systemctl restart clickhouse-server

-- 2. Optimize table settings
ALTER TABLE events MODIFY SETTING
    min_bytes_for_wide_part = 1048576,  -- 1 MB (lower = more frequent wide parts)
    min_rows_for_wide_part = 10000;     -- 10k rows

-- 3. Add multiple Kafka consumer tables (each reads subset of partitions)
CREATE TABLE kafka_events_1 (...) ENGINE = Kafka() SETTINGS
    kafka_topic_list = 'events',
    kafka_group_id = 'clickhouse_consumer_1',
    kafka_num_consumers = 1;  -- Only read partitions assigned to this group

CREATE TABLE kafka_events_2 (...) ENGINE = Kafka() SETTINGS
    kafka_topic_list = 'events',
    kafka_group_id = 'clickhouse_consumer_2',
    kafka_num_consumers = 1;  # Different group = different partitions

-- Then insert from both:
-- INSERT INTO events SELECT * FROM kafka_events_1;
-- INSERT INTO events SELECT * FROM kafka_events_2;
```

**Long-term Solution (Scale Horizontally):**

```yaml
# Add 2 more nodes (3 total)
# Each pulls from 1/3 of Kafka partitions

node1: Reads partitions [0,1,2]
node2: Reads partitions [3,4,5]
node3: Reads partitions [6,7,8]

# Local inserts on each node, then:
INSERT INTO distributed_events SELECT * FROM events_local;

# Result:
# - 3x parallelism
# - 3x throughput (150 MB/s per node)
# - Data spread across 3 nodes
# - Query parallelizes across all 3
```

**Expected Improvements:**

| Change | Throughput Increase | Implementation Time |
|--------|--------------------|--------------------|
| Async inserts | 1.5-2x | Minutes |
| Pause merges | 1.2-1.5x | Minutes |
| Bigger batches | 1.5-3x | Minutes |
| More Kafka consumers | 2-3x | 1 hour |
| Higher merge pool | 1.2-1.5x | 30 mins restart |
| Horizontal scale (3 nodes) | 3x | 24 hours |
| **All combined** | **10-30x** | **24 hours** |

---

## Scaling Decision Matrix

Use this matrix to choose between vertical and horizontal scaling:

| Metric | Current | Vertical Scaling | Horizontal Scaling |
|--------|---------|------------------|--------------------|
| **Data Size** | < 1 TB | Recommended | Optional |
| | 1-10 TB | Possible | Recommended |
| | > 10 TB | Limited | Required |
| **Query Latency** | < 1s | N/A | Consider later |
| | 1-5s | Add RAM/CPU | Consider sharding |
| | > 5s | Add CPU/disk I/O | Add nodes |
| **Concurrent Queries** | < 10 | Single node fine | N/A |
| | 10-100 | Increase CPU | Consider sharding |
| | > 100 | CPU maxed | Add nodes |
| **Insert Rate** | < 100 MB/s | Single node fine | N/A |
| | 100-500 MB/s | Increase CPU/disk | Consider sharding |
| | > 500 MB/s | Disk I/O limit | Add nodes |
| **Availability** | Non-critical | Single node OK | N/A |
| | 99.9% SLA | Add replicas | Add nodes |
| **Cost Tolerance** | Low | Vertical only | N/A |
| | Medium | Vertical first | Then horizontal |
| | High | Horizontal | Replicated cluster |

---

## Scaling Roadmap Template

```markdown
# Scaling Plan for [Your Deployment]

## Current State
- Nodes: 1
- Storage: 1 TB
- CPU: 16 cores
- Memory: 64 GB
- Throughput: 50 MB/s
- Query p95: 8 seconds

## Problem
- Disk filling (15% free)
- Query latency SLA breached (> 5s)
- Insert throughput insufficient

## 6-Month Roadmap

### Phase 1 (Week 1) - Quick Wins
- [ ] Enable better compression (ZSTD)
- [ ] Set max_threads = 16 (was 8)
- [ ] Enable async inserts
- Estimated gain: 2-3x faster

### Phase 2 (Month 1) - Vertical Scaling
- [ ] Add 2 TB storage (total 3 TB)
- [ ] Upgrade to 256 GB memory
- [ ] Upgrade to 32-core CPU
- Cost: $5k, Timeline: 1 day
- Expected: 5-10x improvement

### Phase 3 (Month 3) - Initial Horizontal
- [ ] Add node 2 and 3 (create 3-node cluster)
- [ ] Configure replication
- [ ] Migrate to distributed tables
- Cost: $15k, Timeline: 2 days
- Expected: 3x capacity, 3x throughput

### Phase 4 (Month 6) - Advanced Cluster
- [ ] Add node 4 and 5 (5-node cluster)
- [ ] Implement sharding across 3 shards
- [ ] Set up dedicated ZooKeeper cluster
- [ ] Implement backup automation
- Cost: $25k, Timeline: 3 days

## Success Criteria
- Query p95 < 1 second
- Insert throughput 500+ MB/s
- Disk usage < 70%
- Replication lag < 5 seconds
- 99.99% uptime (>= 99% active replicas)
```
