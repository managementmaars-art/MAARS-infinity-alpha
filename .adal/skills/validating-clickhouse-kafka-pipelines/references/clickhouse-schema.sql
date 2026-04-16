-- ClickHouse Schema Templates for Validation Pattern
-- Complete schema setup with error handling, idempotency, and materialized views

-- ============================================================================
-- 1. KAFKA ENGINE TABLE - Entry point for streaming consumption
-- ============================================================================

CREATE TABLE IF NOT EXISTS shopify.kafka_orders (
    order_id String,
    created_at String,
    line_items Array(Tuple(
        line_item_id String,
        product_id String,
        product_title String,
        quantity Int32
    )),
    inserted_at String
)
ENGINE = Kafka()
SETTINGS
    -- Kafka connection
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'shopify-orders',
    kafka_group_name = 'clickhouse_storage',

    -- Message format
    kafka_format = 'JSONEachRow',

    -- Error handling (core setting for this pattern)
    kafka_handle_error_mode = 'stream',  -- Enable error virtual columns

    -- Schema flexibility for evolution
    input_format_skip_unknown_fields = 1,

    -- Performance tuning
    kafka_num_consumers = 2,              -- Match topic partition count
    kafka_max_block_size = 65536,         -- Balanced latency/throughput
    kafka_poll_timeout_ms = 5000,
    kafka_thread_per_consumer = 1;

-- Verify Kafka table is consuming
-- SELECT * FROM system.kafka_consumers
-- WHERE database = 'shopify' AND table = 'kafka_orders';

-- ============================================================================
-- 2. ERROR CAPTURE TABLE - Store all malformed messages
-- ============================================================================

CREATE TABLE IF NOT EXISTS shopify.kafka_errors (
    topic String,
    partition Int64,
    offset Int64,
    raw_message String,
    error_message String,
    captured_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (topic, partition, offset)
PARTITION BY toYYYYMM(captured_at)
TTL captured_at + INTERVAL 30 DAY  -- Auto-cleanup after 30 days;

-- ============================================================================
-- 3. ERROR CAPTURE MATERIALIZED VIEW - Automatic error extraction
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS shopify.kafka_errors_mv
TO shopify.kafka_errors AS
SELECT
    _topic AS topic,
    _partition AS partition,
    _offset AS offset,
    _raw_message AS raw_message,
    _error AS error_message
FROM shopify.kafka_orders
WHERE length(_error) > 0;  -- Only capture actual errors

-- ============================================================================
-- 4. TARGET TABLE - Idempotent storage with automatic deduplication
-- ============================================================================

CREATE TABLE IF NOT EXISTS shopify.orders (
    order_id String,
    created_at DateTime,
    line_items Array(Tuple(
        line_item_id String,
        product_id String,
        product_title String,
        quantity Int32
    )),
    inserted_at DateTime
)
ENGINE = ReplacingMergeTree()
ORDER BY (order_id, created_at)
PARTITION BY toYYYYMM(created_at);

-- Key design decisions:
-- - ReplacingMergeTree handles at-least-once delivery (automatic deduplication)
-- - ORDER BY (order_id, created_at) deduplicates by business key
-- - PARTITION BY toYYYYMM(created_at) for efficient time-range queries
-- - Deduplication happens during background merges (eventual consistency)

-- ============================================================================
-- 5. DATA TRANSFORMATION MATERIALIZED VIEW - Valid message processing
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS shopify.orders_mv
TO shopify.orders AS
SELECT
    order_id,
    parseDateTime64BestEffort(created_at) AS created_at,
    line_items,
    parseDateTime64BestEffort(inserted_at) AS inserted_at
FROM shopify.kafka_orders
WHERE length(_error) = 0;  -- Only process valid messages

-- Key design decisions:
-- - WHERE length(_error) = 0 filters out malformed messages
-- - parseDateTime64BestEffort handles flexible timestamp parsing
-- - Materialized view automatically extracts from Kafka table
-- - Data flows: Kafka table → MV → orders table (with automatic dedup)

-- ============================================================================
-- MONITORING & TROUBLESHOOTING QUERIES
-- ============================================================================

-- 1. Check current error rate (last 5 minutes)
-- SELECT
--     count(*) as error_count,
--     uniq(error_message) as unique_errors,
--     max(captured_at) as latest_error_time
-- FROM shopify.kafka_errors
-- WHERE captured_at > now() - INTERVAL 5 MINUTE;

-- 2. Most common error types (last 24 hours)
-- SELECT
--     error_message,
--     count(*) as occurrences,
--     substring(raw_message, 1, 200) as sample_message
-- FROM shopify.kafka_errors
-- WHERE captured_at > now() - INTERVAL 24 HOUR
-- GROUP BY error_message
-- ORDER BY occurrences DESC
-- LIMIT 10;

-- 3. Error rate by partition (last hour)
-- SELECT
--     partition,
--     count(*) as error_count
-- FROM shopify.kafka_errors
-- WHERE captured_at > now() - INTERVAL 1 HOUR
-- GROUP BY partition
-- ORDER BY error_count DESC;

-- 4. Deduplication effectiveness (check for duplicates)
-- SELECT
--     count(*) as total_rows,
--     count(DISTINCT order_id) as unique_orders,
--     count(*) - count(DISTINCT order_id) as duplicate_count,
--     round(100.0 * (count(*) - count(DISTINCT order_id)) / count(*), 2) as duplicate_percent
-- FROM shopify.orders
-- WHERE created_at > now() - INTERVAL 24 HOUR;

-- 5. Query data with FINAL modifier (immediate deduplication)
-- SELECT * FROM shopify.orders FINAL
-- WHERE order_id = 'YOUR_ORDER_ID';

-- 6. Force merge for immediate deduplication
-- OPTIMIZE TABLE shopify.orders FINAL;

-- ============================================================================
-- ALTERNATIVE: LOW LATENCY CONFIGURATION
-- ============================================================================

-- For applications requiring very low latency (sub-second):
--
-- ALTER TABLE shopify.kafka_orders
-- MODIFY SETTING
--     kafka_num_consumers = 1,
--     kafka_max_block_size = 1024,
--     kafka_poll_timeout_ms = 500,
--     kafka_flush_interval_ms = 500;

-- Trade-off: Lower throughput (100s of msgs/sec vs 1000s)

-- ============================================================================
-- ALTERNATIVE: HIGH THROUGHPUT CONFIGURATION
-- ============================================================================

-- For batch processing and maximum throughput:
--
-- ALTER TABLE shopify.kafka_orders
-- MODIFY SETTING
--     kafka_num_consumers = 4,
--     kafka_max_block_size = 524288,
--     kafka_poll_timeout_ms = 10000,
--     kafka_flush_interval_ms = 10000;

-- Trade-off: Higher latency (few seconds)

-- ============================================================================
-- SCHEMA EVOLUTION EXAMPLE: Adding Optional Field
-- ============================================================================

-- Step 1: Add field to Kafka table
-- ALTER TABLE shopify.kafka_orders
-- ADD COLUMN customer_email String DEFAULT '';

-- Step 2: Update transformation view to include new field
-- DROP VIEW IF EXISTS shopify.orders_mv;
--
-- CREATE MATERIALIZED VIEW shopify.orders_mv
-- TO shopify.orders AS
-- SELECT
--     order_id,
--     parseDateTime64BestEffort(created_at) AS created_at,
--     line_items,
--     parseDateTime64BestEffort(inserted_at) AS inserted_at,
--     customer_email
-- FROM shopify.kafka_orders
-- WHERE length(_error) = 0;

-- Step 3: Update target table if needed
-- ALTER TABLE shopify.orders
-- ADD COLUMN customer_email String DEFAULT '';

-- Notes:
-- - OLD messages will have customer_email = '' (default value)
-- - NEW messages will have customer_email populated
-- - No errors occur because field has default
-- - This is forward-compatible schema evolution

-- ============================================================================
-- IMPORTANT: Query Best Practices
-- ============================================================================

-- ✅ DO: Query destination tables (orders, kafka_errors)
-- SELECT * FROM shopify.orders WHERE order_id = '123';
-- SELECT * FROM shopify.kafka_errors LIMIT 10;

-- ❌ DON'T: Query Kafka engine table directly
-- SELECT * FROM shopify.kafka_orders;  -- Empty! Kafka engine is streaming only

-- ✅ DO: Use FINAL for immediate deduplication
-- SELECT count(DISTINCT order_id) FROM shopify.orders FINAL;

-- ❌ DON'T: Assume immediate deduplication without FINAL
-- SELECT count(*) FROM shopify.orders;  -- May include duplicates before merge

-- ============================================================================
-- CLEANUP & MAINTENANCE
-- ============================================================================

-- Force immediate merge (executes deduplication for FINAL queries)
-- OPTIMIZE TABLE shopify.orders FINAL;

-- Check table size and row count
-- SELECT
--     table,
--     formatReadableSize(sum(bytes_on_disk)) as disk_size,
--     count() as row_count
-- FROM system.parts
-- WHERE database = 'shopify'
-- GROUP BY table;

-- View table mutations and merges
-- SELECT
--     table,
--     mutation_id,
--     command,
--     create_time,
--     latest_failed_part
-- FROM system.mutations
-- WHERE database = 'shopify';
