-- ============================================================================
-- MONITORING QUERIES FOR CLICKHOUSE + KAFKA VALIDATION PATTERN
-- ============================================================================

-- All queries assume the schema setup from clickhouse-schema.sql
-- Database: shopify
-- Tables: kafka_orders (Kafka engine), kafka_errors, orders (ReplacingMergeTree)

-- ============================================================================
-- 1. ERROR DETECTION & ALERTING
-- ============================================================================

-- Current error rate (5-minute window)
-- Use this to detect ongoing issues
SELECT
    count(*) as error_count,
    uniq(error_message) as unique_error_types,
    max(captured_at) as latest_error_time,
    round(count() / 5.0, 2) as errors_per_minute
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 5 MINUTE;

-- ERROR: Most common error types (last 24 hours)
-- Identifies root causes and patterns
SELECT
    error_message,
    count(*) as occurrences,
    round(100.0 * count() / (SELECT count(*) FROM shopify.kafka_errors WHERE captured_at > now() - INTERVAL 24 HOUR), 2) as percent,
    substring(raw_message, 1, 200) as sample_message,
    max(captured_at) as latest_occurrence
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 24 HOUR
GROUP BY error_message
ORDER BY occurrences DESC
LIMIT 20;

-- ERROR: Timeline of error rate (hourly breakdown)
-- Detects when errors started occurring
SELECT
    toStartOfHour(captured_at) as hour,
    count(*) as error_count,
    uniq(error_message) as unique_errors,
    round(count() / 3600.0, 2) as errors_per_second
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 7 DAY
GROUP BY hour
ORDER BY hour DESC;

-- ERROR: Rate by partition (detect hot partitions)
-- Helps identify imbalanced producers or specific broker issues
SELECT
    partition,
    count(*) as error_count,
    max(offset) as latest_offset
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR
GROUP BY partition
ORDER BY error_count DESC;

-- ERROR: Sample malformed messages for debugging
-- Examine actual message content to understand issues
SELECT
    error_message,
    raw_message,
    captured_at
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR
ORDER BY captured_at DESC
LIMIT 10;

-- ============================================================================
-- 2. CONSUMPTION & THROUGHPUT MONITORING
-- ============================================================================

-- Overall message consumption rate (messages/second)
-- Indicates whether consumer is keeping up with producer
SELECT
    count(*) as total_messages,
    round(count() / ((SELECT max(captured_at) FROM shopify.kafka_errors WHERE captured_at > now() - INTERVAL 1 HOUR) - (SELECT min(captured_at) FROM shopify.kafka_errors WHERE captured_at > now() - INTERVAL 1 HOUR)) * 1000000, 2) as throughput_msg_per_sec
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR;

-- Consumption lag (offset delta)
-- Shows how far behind consumer is from latest message
SELECT
    partition,
    max(offset) as latest_offset,
    now() - max(captured_at) as age_seconds
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR
GROUP BY partition
ORDER BY partition;

-- Valid vs invalid messages ratio (last hour)
-- Measures data quality from producer
SELECT
    count() as total_valid,
    (SELECT count() FROM shopify.kafka_errors WHERE captured_at > now() - INTERVAL 1 HOUR) as total_errors,
    round(100.0 * (SELECT count() FROM shopify.kafka_errors WHERE captured_at > now() - INTERVAL 1 HOUR) / (count() + (SELECT count() FROM shopify.kafka_errors WHERE captured_at > now() - INTERVAL 1 HOUR)), 2) as error_rate_percent
FROM shopify.orders
WHERE inserted_at > now() - INTERVAL 1 HOUR;

-- ============================================================================
-- 3. DEDUPLICATION & DATA QUALITY
-- ============================================================================

-- Deduplication effectiveness (check for duplicates)
-- Shows impact of at-least-once delivery semantics
SELECT
    count(*) as total_rows,
    count(DISTINCT order_id) as unique_orders,
    count(*) - count(DISTINCT order_id) as duplicate_count,
    round(100.0 * (count(*) - count(DISTINCT order_id)) / count(*), 2) as duplicate_percent
FROM shopify.orders
WHERE created_at > now() - INTERVAL 24 HOUR;

-- Deduplication status (with FINAL for exact count)
-- Shows true unique count after background merges
SELECT
    'without_final' as query_type,
    count(*) as row_count,
    count(DISTINCT order_id) as unique_count
FROM shopify.orders
WHERE created_at > now() - INTERVAL 24 HOUR
UNION ALL
SELECT
    'with_final' as query_type,
    count(*) as row_count,
    count(DISTINCT order_id) as unique_count
FROM shopify.orders FINAL
WHERE created_at > now() - INTERVAL 24 HOUR;

-- Most duplicated orders (ordering issues)
-- Identifies orders that appear multiple times
SELECT
    order_id,
    count(*) as occurrence_count,
    min(inserted_at) as first_seen,
    max(inserted_at) as last_seen,
    dateDiff('second', first_seen, last_seen) as duration_seconds
FROM shopify.orders
WHERE created_at > now() - INTERVAL 24 HOUR
GROUP BY order_id
HAVING count(*) > 1
ORDER BY occurrence_count DESC
LIMIT 20;

-- ============================================================================
-- 4. PERFORMANCE & RESOURCE USAGE
-- ============================================================================

-- Table size and row count
-- Monitor storage growth and compression ratio
SELECT
    table,
    formatReadableSize(sum(bytes_on_disk)) as disk_size,
    count() as row_count,
    uniq(partition) as partition_count,
    round(sum(bytes_on_disk) / row_count, 2) as bytes_per_row
FROM system.parts
WHERE database = 'shopify' AND table IN ('kafka_errors', 'orders')
GROUP BY table
ORDER BY sum(bytes_on_disk) DESC;

-- Partition breakdown (size and row count by date)
-- Helps with time-range query planning
SELECT
    table,
    partition,
    formatReadableSize(sum(bytes_on_disk)) as partition_size,
    count() as row_count
FROM system.parts
WHERE database = 'shopify' AND table = 'shopify.orders'
GROUP BY table, partition
ORDER BY partition DESC
LIMIT 30;

-- Merge activity (background deduplication)
-- Shows whether ReplacingMergeTree merges are running
SELECT
    table,
    count() as active_merges,
    max(num_parts) as max_parts_in_merge,
    max(memory_usage) as max_memory
FROM system.merges
WHERE database = 'shopify'
GROUP BY table;

-- Query latency sampling (last 100 queries)
-- Identifies slow queries that need optimization
SELECT
    query_kind,
    count() as query_count,
    round(avg(query_duration_ms), 2) as avg_duration_ms,
    max(query_duration_ms) as max_duration_ms,
    min(query_start_time) as earliest_query
FROM system.query_log
WHERE database = 'shopify' AND query_start_time > now() - INTERVAL 1 HOUR
GROUP BY query_kind
ORDER BY avg_duration_ms DESC
LIMIT 20;

-- ============================================================================
-- 5. VALIDATION SUCCESS METRICS
-- ============================================================================

-- Validation success rate (orders that passed all checks)
-- Combines error rate and valid message count
SELECT
    toStartOfHour(max(captured_at)) as hour,
    (SELECT count() FROM shopify.orders WHERE inserted_at > (now() - INTERVAL 1 HOUR)) as valid_orders,
    count() as failed_validations,
    round(100.0 * count() / (count() + (SELECT count() FROM shopify.orders WHERE inserted_at > (now() - INTERVAL 1 HOUR))), 2) as failure_rate_percent
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR
GROUP BY hour;

-- Validation errors by type (categorized)
-- Helps prioritize fixes
SELECT
    CASE
        WHEN error_message LIKE '%JSON%' THEN 'JSON Parse Error'
        WHEN error_message LIKE '%schema%' THEN 'Schema Mismatch'
        WHEN error_message LIKE '%number%' THEN 'Type Mismatch'
        WHEN error_message LIKE '%required%' THEN 'Missing Field'
        ELSE 'Other'
    END as error_category,
    count(*) as count,
    round(100.0 * count() / (SELECT count(*) FROM shopify.kafka_errors WHERE captured_at > now() - INTERVAL 24 HOUR), 2) as percent
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 24 HOUR
GROUP BY error_category
ORDER BY count DESC;

-- ============================================================================
-- 6. ALERTING QUERIES (Threshold-Based)
-- ============================================================================

-- ALERT: High error rate (> 20 errors per second)
SELECT
    'HIGH_ERROR_RATE' as alert_type,
    round(count() / 300.0, 2) as errors_per_second,
    'CRITICAL' as severity
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 5 MINUTE
HAVING round(count() / 300.0, 2) > 20;

-- ALERT: Consumption stalled (0 messages in 10 minutes)
SELECT
    'CONSUMPTION_STALLED' as alert_type,
    max(captured_at) as last_message_time,
    'CRITICAL' as severity
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 10 MINUTE
HAVING count() = 0;

-- ALERT: High duplicate rate (> 10% duplicates)
SELECT
    'HIGH_DUPLICATE_RATE' as alert_type,
    round(100.0 * (count(*) - count(DISTINCT order_id)) / count(*), 2) as duplicate_percent,
    'WARNING' as severity
FROM shopify.orders
WHERE created_at > now() - INTERVAL 1 HOUR
HAVING duplicate_percent > 10;

-- ALERT: Kafka errors growing exponentially
SELECT
    'EXPONENTIAL_ERROR_GROWTH' as alert_type,
    (SELECT count() FROM shopify.kafka_errors WHERE captured_at > now() - INTERVAL 5 MINUTE) as recent_errors,
    (SELECT count() FROM shopify.kafka_errors WHERE captured_at BETWEEN now() - INTERVAL 10 MINUTE AND now() - INTERVAL 5 MINUTE) as previous_errors,
    'WARNING' as severity
WHERE recent_errors > (previous_errors * 2);

-- ============================================================================
-- 7. DIAGNOSTIC QUERIES
-- ============================================================================

-- Kafka consumer status in ClickHouse
-- Verify consumer is actively consuming
SELECT
    database,
    table,
    consumer_group,
    num_active_consumers,
    num_queued_messages,
    total_messages_read
FROM system.kafka_consumers
WHERE database = 'shopify' AND table = 'kafka_orders';

-- Recent DDL changes
-- Track schema modifications
SELECT
    event_date,
    event_time,
    query_kind,
    query
FROM system.query_log
WHERE database = 'shopify' AND query_kind IN ('Create', 'Alter', 'Drop')
ORDER BY event_time DESC
LIMIT 20;

-- Active materialized view status
-- Verify views are pushing data correctly
SELECT
    table,
    create_table_query
FROM system.tables
WHERE database = 'shopify' AND engine = 'MaterializedView'
ORDER BY table;

-- ============================================================================
-- 8. CUSTOM DASHBOARD QUERIES (Aggregated for display)
-- ============================================================================

-- Dashboard: System health overview
SELECT
    'error_rate_5m' as metric,
    toString(count(*) / 5.0) as value
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 5 MINUTE
UNION ALL
SELECT
    'valid_messages_1h' as metric,
    toString(count(*)) as value
FROM shopify.orders
WHERE inserted_at > now() - INTERVAL 1 HOUR
UNION ALL
SELECT
    'duplicate_percent_24h' as metric,
    toString(round(100.0 * (count(*) - count(DISTINCT order_id)) / count(*), 2)) as value
FROM shopify.orders
WHERE created_at > now() - INTERVAL 24 HOUR;

-- Dashboard: Error distribution (top 10)
SELECT
    arrayConcat(
        [error_message],
        [toString(count(*))]
    ) as error_info
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 24 HOUR
GROUP BY error_message
ORDER BY count() DESC
LIMIT 10;

-- ============================================================================
-- USEFUL CLICKHOUSE SYSTEM QUERIES
-- ============================================================================

-- Force immediate deduplication (wait for merge to complete)
-- OPTIMIZE TABLE shopify.orders FINAL;

-- Clear Kafka offsets (restart consumption from beginning)
-- DELETE FROM system.kafka_consumers WHERE database = 'shopify';

-- Check for stuck mutations
-- SELECT * FROM system.mutations WHERE database = 'shopify' AND is_done = 0;

-- View recent errors in system log
-- SELECT * FROM system.system_events WHERE event = 'QueryExecutionPipeline' ORDER BY event_time DESC LIMIT 20;
