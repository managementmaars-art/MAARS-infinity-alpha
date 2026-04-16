# Kafka Streaming Pipeline with Materialized Views

Complete examples for integrating Kafka/Redpanda with ClickHouse materialized views for real-time stream processing.

## 1. Basic Kafka to ClickHouse Pipeline

**Scenario**: Stream orders from Kafka into ClickHouse with real-time aggregation

```sql
-- Step 1: Create Kafka table (source)
CREATE TABLE kafka_orders (
    order_id String,
    user_id String,
    product_id String,
    quantity String,
    price String,
    timestamp String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'orders',
    kafka_group_id = 'clickhouse-orders',
    kafka_format = 'JSONEachRow',
    kafka_max_block_size = 1000;

-- Step 2: Create target table (raw orders)
CREATE TABLE orders (
    order_id UInt64,
    user_id UInt32,
    product_id UInt32,
    quantity UInt32,
    price Decimal(10, 2),
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp);

-- Step 3: Create materialized view to consume Kafka
CREATE MATERIALIZED VIEW kafka_orders_to_clickhouse_mv TO orders AS
SELECT
    toUInt64(JSONExtractString(order_id, '')) as order_id,
    toUInt32(JSONExtractString(user_id, '')) as user_id,
    toUInt32(JSONExtractString(product_id, '')) as product_id,
    toUInt32(JSONExtractString(quantity, '')) as quantity,
    toDecimal(JSONExtractString(price, ''), 10, 2) as price,
    parseDateTimeBestEffort(JSONExtractString(timestamp, '')) as timestamp
FROM kafka_orders;

-- Step 4: Create aggregation on top
CREATE TABLE daily_sales (
    date Date,
    product_id UInt32,
    order_count UInt64,
    total_quantity UInt64,
    total_revenue Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, product_id);

CREATE MATERIALIZED VIEW daily_sales_mv TO daily_sales AS
SELECT
    toDate(timestamp) as date,
    product_id,
    COUNT() as order_count,
    SUM(quantity) as total_quantity,
    SUM(price * quantity) as total_revenue
FROM orders
GROUP BY date, product_id;

-- Test: Insert order into Kafka topic
-- Kafka message: {"order_id": 123, "user_id": 456, "product_id": 789, "quantity": 2, "price": 99.99, "timestamp": "2024-01-15 10:30:00"}
-- Wait a few seconds for consumption

-- Check results
SELECT * FROM orders WHERE order_id = 123;
SELECT * FROM daily_sales WHERE date = today();
```

---

## 2. Complex JSON Parsing from Kafka

**Scenario**: Extract nested data from complex JSON messages

```sql
-- Kafka table with raw message
CREATE TABLE kafka_events_raw (
    raw_message String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'events',
    kafka_group_id = 'clickhouse-events',
    kafka_format = 'RawBLOB';

-- Events table with parsed fields
CREATE TABLE events (
    timestamp DateTime,
    user_id UInt32,
    session_id String,
    event_type String,
    page_url String,
    properties Map(String, String),
    revenue Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp);

-- Parse and load from Kafka
CREATE MATERIALIZED VIEW kafka_events_mv TO events AS
SELECT
    parseDateTimeBestEffort(JSONExtractString(raw_message, 'timestamp')) as timestamp,
    toUInt32(JSONExtractInt(raw_message, 'user_id')) as user_id,
    JSONExtractString(raw_message, 'session_id') as session_id,
    JSONExtractString(raw_message, 'event_type') as event_type,
    JSONExtractString(raw_message, 'page_url') as page_url,
    parseJson(JSONExtractString(raw_message, 'properties')) as properties,
    toDecimal(JSONExtractString(raw_message, 'revenue'), 10, 2) as revenue
FROM kafka_events_raw
WHERE raw_message != '';  -- Skip empty messages
```

**Example Kafka message**:
```json
{
    "timestamp": "2024-01-15 10:30:45",
    "user_id": 12345,
    "session_id": "sess_abc123",
    "event_type": "purchase",
    "page_url": "https://example.com/checkout",
    "properties": {
        "cart_value": "299.99",
        "items_count": "3",
        "promo_code": "SAVE10"
    },
    "revenue": 269.99
}
```

---

## 3. Multi-Topic Kafka Pipeline

**Scenario**: Consume from multiple Kafka topics, aggregate together

```sql
-- Topic 1: Orders
CREATE TABLE kafka_orders (
    order_json String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'orders',
    kafka_group_id = 'clickhouse',
    kafka_format = 'RawBLOB';

-- Topic 2: Payments
CREATE TABLE kafka_payments (
    payment_json String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'payments',
    kafka_group_id = 'clickhouse',
    kafka_format = 'RawBLOB';

-- Orders table
CREATE TABLE orders (
    order_id UInt64,
    user_id UInt32,
    amount Decimal(18, 2),
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp);

-- Payments table
CREATE TABLE payments (
    payment_id UInt64,
    order_id UInt64,
    status String,
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY (order_id, timestamp);

-- Consume orders from Kafka
CREATE MATERIALIZED VIEW kafka_orders_mv TO orders AS
SELECT
    toUInt64(JSONExtractInt(order_json, 'order_id')) as order_id,
    toUInt32(JSONExtractInt(order_json, 'user_id')) as user_id,
    toDecimal(JSONExtractString(order_json, 'amount'), 18, 2) as amount,
    parseDateTimeBestEffort(JSONExtractString(order_json, 'timestamp')) as timestamp
FROM kafka_orders;

-- Consume payments from Kafka
CREATE MATERIALIZED VIEW kafka_payments_mv TO payments AS
SELECT
    toUInt64(JSONExtractInt(payment_json, 'payment_id')) as payment_id,
    toUInt64(JSONExtractInt(payment_json, 'order_id')) as order_id,
    JSONExtractString(payment_json, 'status') as status,
    parseDateTimeBestEffort(JSONExtractString(payment_json, 'timestamp')) as timestamp
FROM kafka_payments;

-- Aggregate: Orders with payment status
CREATE TABLE orders_with_payment_status (
    date Date,
    order_count UInt64,
    paid_count UInt64,
    pending_count UInt64,
    total_amount Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY date;

CREATE MATERIALIZED VIEW orders_with_payment_status_mv TO orders_with_payment_status AS
SELECT
    toDate(o.timestamp) as date,
    COUNT(*) as order_count,
    countIf(p.status = 'completed') as paid_count,
    countIf(p.status = 'pending') as pending_count,
    SUM(o.amount) as total_amount
FROM orders o
LEFT JOIN payments p ON o.order_id = p.order_id
GROUP BY date;

-- Query: Daily payment metrics
SELECT
    date,
    order_count,
    paid_count,
    pending_count,
    ROUND(100.0 * paid_count / order_count, 2) as success_rate,
    total_amount
FROM orders_with_payment_status
WHERE date >= today() - INTERVAL 30 DAY
ORDER BY date DESC;
```

---

## 4. Kafka with Deduplication (ReplacingMergeTree)

**Scenario**: Handle duplicate or update messages from Kafka with version tracking

```sql
-- Kafka table: User profile updates
CREATE TABLE kafka_user_updates (
    raw_message String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'user_updates',
    kafka_group_id = 'clickhouse-users',
    kafka_format = 'RawBLOB';

-- User profiles with version tracking
CREATE TABLE user_profiles (
    user_id UInt32,
    username String,
    email String,
    status String,
    update_time DateTime,
    _version UInt64
) ENGINE = ReplacingMergeTree(_version)
ORDER BY user_id;

-- Consume and deduplicate updates
CREATE MATERIALIZED VIEW kafka_user_updates_mv TO user_profiles AS
SELECT
    toUInt32(JSONExtractInt(raw_message, 'user_id')) as user_id,
    JSONExtractString(raw_message, 'username') as username,
    JSONExtractString(raw_message, 'email') as email,
    JSONExtractString(raw_message, 'status') as status,
    parseDateTimeBestEffort(JSONExtractString(raw_message, 'update_time')) as update_time,
    toUInt64(JSONExtractInt(raw_message, 'version')) as _version
FROM kafka_user_updates;

-- Query: Get latest profile for each user
SELECT
    user_id,
    username,
    email,
    status,
    update_time
FROM user_profiles FINAL
WHERE status != 'deleted'
ORDER BY username;

-- Or use GROUP BY with argMax for better performance:
SELECT
    user_id,
    argMax(username, _version) as username,
    argMax(email, _version) as email,
    argMax(status, _version) as status,
    argMax(update_time, _version) as update_time
FROM user_profiles
GROUP BY user_id
HAVING status != 'deleted'
ORDER BY username;
```

**Kafka message format**:
```json
{
    "user_id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "status": "active",
    "update_time": "2024-01-15 10:30:00",
    "version": 3
}
```

---

## 5. Error Handling and Dead Letter Queue

**Scenario**: Capture failed message parsing in a separate table

```sql
-- Main Kafka topic
CREATE TABLE kafka_orders (
    raw_message String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'orders',
    kafka_group_id = 'clickhouse',
    kafka_format = 'RawBLOB';

-- Valid orders table
CREATE TABLE orders (
    order_id UInt64,
    user_id UInt32,
    amount Decimal(18, 2),
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp);

-- Dead letter queue for parse failures
CREATE TABLE orders_dlq (
    raw_message String,
    error_message String,
    captured_at DateTime
) ENGINE = MergeTree()
ORDER BY captured_at;

-- Consume with error handling
CREATE MATERIALIZED VIEW kafka_orders_mv TO orders AS
SELECT
    toUInt64(JSONExtractInt(raw_message, 'order_id')) as order_id,
    toUInt32(JSONExtractInt(raw_message, 'user_id')) as user_id,
    toDecimal(JSONExtractString(raw_message, 'amount'), 18, 2) as amount,
    parseDateTimeBestEffort(JSONExtractString(raw_message, 'timestamp')) as timestamp
FROM kafka_orders
WHERE
    JSONExtractInt(raw_message, 'order_id') > 0
    AND JSONExtractInt(raw_message, 'user_id') > 0
    AND JSONExtractString(raw_message, 'amount') != '';

-- Capture invalid messages
CREATE MATERIALIZED VIEW kafka_orders_errors_mv TO orders_dlq AS
SELECT
    raw_message,
    'Invalid order data' as error_message,
    now() as captured_at
FROM kafka_orders
WHERE
    JSONExtractInt(raw_message, 'order_id') <= 0
    OR JSONExtractInt(raw_message, 'user_id') <= 0
    OR JSONExtractString(raw_message, 'amount') = '';

-- Monitor DLQ
SELECT
    COUNT(*) as error_count,
    error_message
FROM orders_dlq
WHERE captured_at >= now() - INTERVAL 1 HOUR
GROUP BY error_message
ORDER BY error_count DESC;
```

---

## 6. Streaming Analytics: Real-Time Dashboard

**Scenario**: Create dashboard metrics from Kafka stream

```sql
-- Kafka events
CREATE TABLE kafka_events (
    raw_message String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'events',
    kafka_group_id = 'clickhouse-dashboard',
    kafka_format = 'RawBLOB';

-- Events table
CREATE TABLE events (
    timestamp DateTime,
    user_id UInt32,
    event_type String,
    revenue Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY (timestamp, user_id);

-- Parse Kafka messages
CREATE MATERIALIZED VIEW kafka_events_mv TO events AS
SELECT
    parseDateTimeBestEffort(JSONExtractString(raw_message, 'timestamp')) as timestamp,
    toUInt32(JSONExtractInt(raw_message, 'user_id')) as user_id,
    JSONExtractString(raw_message, 'event_type') as event_type,
    toDecimal(JSONExtractString(raw_message, 'revenue'), 10, 2) as revenue
FROM kafka_events;

-- Dashboard metrics (hourly)
CREATE TABLE dashboard_metrics (
    hour DateTime,
    total_events UInt64,
    unique_users AggregateFunction(uniq, UInt32),
    total_revenue Decimal(18, 2),
    purchases UInt64,
    purchase_revenue Decimal(18, 2)
) ENGINE = AggregatingMergeTree()
ORDER BY hour;

CREATE MATERIALIZED VIEW dashboard_metrics_mv TO dashboard_metrics AS
SELECT
    toStartOfHour(timestamp) as hour,
    COUNT() as total_events,
    uniqState(user_id) as unique_users,
    SUM(revenue) as total_revenue,
    countIf(event_type = 'purchase') as purchases,
    sumIf(revenue, event_type = 'purchase') as purchase_revenue
FROM events
GROUP BY hour;

-- Dashboard query (instant, pre-aggregated)
SELECT
    hour,
    total_events,
    uniqMerge(unique_users) as active_users,
    total_revenue,
    purchases,
    purchase_revenue,
    ROUND(100.0 * purchases / total_events, 2) as conversion_rate
FROM dashboard_metrics
WHERE hour >= now() - INTERVAL 24 HOUR
ORDER BY hour DESC;
```

---

## 7. Stream Enrichment: Join Kafka with Reference Data

**Scenario**: Enrich Kafka events with product information from reference tables

```sql
-- Reference data (product catalog)
CREATE TABLE products (
    product_id UInt32,
    product_name String,
    category String,
    base_price Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY product_id;

-- Insert reference data
INSERT INTO products VALUES
    (1, 'Laptop', 'Electronics', 999.99),
    (2, 'Mouse', 'Electronics', 29.99),
    (3, 'Keyboard', 'Electronics', 79.99);

-- Kafka orders
CREATE TABLE kafka_orders (
    raw_message String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'orders',
    kafka_group_id = 'clickhouse',
    kafka_format = 'RawBLOB';

-- Raw orders table
CREATE TABLE orders_raw (
    order_id UInt64,
    timestamp DateTime,
    product_id UInt32,
    quantity UInt32,
    paid_price Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY (timestamp, product_id);

-- Parse from Kafka
CREATE MATERIALIZED VIEW kafka_orders_mv TO orders_raw AS
SELECT
    toUInt64(JSONExtractInt(raw_message, 'order_id')) as order_id,
    parseDateTimeBestEffort(JSONExtractString(raw_message, 'timestamp')) as timestamp,
    toUInt32(JSONExtractInt(raw_message, 'product_id')) as product_id,
    toUInt32(JSONExtractInt(raw_message, 'quantity')) as quantity,
    toDecimal(JSONExtractString(raw_message, 'paid_price'), 10, 2) as paid_price
FROM kafka_orders;

-- Enriched orders (join with products)
CREATE TABLE orders_enriched (
    date Date,
    product_name String,
    category String,
    order_count UInt64,
    total_quantity UInt64,
    total_paid Decimal(18, 2),
    total_value Decimal(18, 2),
    discount Decimal(18, 2)
) ENGINE = SummingMergeTree()
ORDER BY (date, category, product_name);

-- Join and enrich
CREATE MATERIALIZED VIEW orders_enriched_mv TO orders_enriched AS
SELECT
    toDate(o.timestamp) as date,
    p.product_name,
    p.category,
    COUNT(*) as order_count,
    SUM(o.quantity) as total_quantity,
    SUM(o.paid_price * o.quantity) as total_paid,
    SUM(p.base_price * o.quantity) as total_value,
    SUM((p.base_price - o.paid_price) * o.quantity) as discount
FROM orders_raw o
LEFT JOIN products p ON o.product_id = p.product_id
GROUP BY date, p.product_name, p.category;

-- Query: Sales by category
SELECT
    date,
    category,
    SUM(order_count) as orders,
    SUM(total_quantity) as items,
    SUM(total_paid) as revenue,
    SUM(discount) as discount_given,
    ROUND(100.0 * SUM(discount) / SUM(total_value), 2) as discount_rate
FROM orders_enriched
WHERE date >= today() - INTERVAL 7 DAY
GROUP BY date, category
ORDER BY date DESC, revenue DESC;
```

---

## Configuration Best Practices

```sql
-- Optimal Kafka table settings for ClickHouse
CREATE TABLE kafka_events (
    raw_message String
) ENGINE = Kafka()
SETTINGS
    -- Connection
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'events',
    kafka_group_id = 'clickhouse-consumer',

    -- Format and parsing
    kafka_format = 'RawBLOB',  -- or 'JSONEachRow'

    -- Performance tuning
    kafka_max_block_size = 65536,  -- Messages per block (default good for most cases)
    kafka_num_consumers = 1,  -- Number of consumer threads

    -- Offset handling
    kafka_skip_broken_messages = 1,  -- Skip messages that can't be parsed
    kafka_max_rows_per_message = 1,  -- Rows per Kafka message

    -- Timeout settings
    kafka_poll_timeout_ms = 0,
    kafka_flush_interval_ms = 10000,

    -- Offset management
    kafka_commit_every_batch = 1,  -- Commit after each batch
    kafka_auto_offset_reset = 'smallest';  -- Or 'largest' for new topics
```

---

## Monitoring Kafka Pipeline Health

```sql
-- Check how many messages are being consumed
SELECT
    table,
    SUM(rows) as total_rows,
    MAX(modification_time) as last_modified
FROM system.parts
WHERE database = 'default'
  AND table IN ('orders', 'events', 'payments')
GROUP BY table;

-- Check for slow Kafka consumption
SELECT
    view_name,
    COUNT(*) as executions,
    AVG(elapsed) as avg_duration_ms,
    MAX(elapsed) as max_duration_ms,
    SUM(read_rows) as total_rows_read
FROM system.query_log
WHERE query_kind = 'MaterializedView'
  AND event_date >= today()
  AND query LIKE '%kafka%'
GROUP BY view_name
ORDER BY max_duration_ms DESC;
```
