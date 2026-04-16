# ClickHouse + Kafka Validation - Comprehensive Examples

## Test Patterns

### Unit Test: Domain Value Objects

Test business rule validation at the value object level:

```python
# tests/unit/extraction/domain/test_value_objects.py
import pytest
from app.extraction.domain.value_objects import ProductTitle
from app.extraction.domain.exceptions import InvalidProductException


class TestProductTitle:
    """Test ProductTitle value object validation."""

    def test_valid_title_is_accepted(self) -> None:
        """Valid title is created without error."""
        title = ProductTitle("Laptop")
        assert title.value == "Laptop"

    def test_empty_title_raises_error(self) -> None:
        """Empty title raises InvalidProductException."""
        with pytest.raises(InvalidProductException) as exc_info:
            ProductTitle("")
        assert "cannot be empty" in str(exc_info.value)

    def test_whitespace_only_title_raises_error(self) -> None:
        """Whitespace-only title is treated as empty."""
        with pytest.raises(InvalidProductException):
            ProductTitle("   ")

    def test_title_too_long_raises_error(self) -> None:
        """Title exceeding 255 chars raises error."""
        long_title = "x" * 256
        with pytest.raises(InvalidProductException) as exc_info:
            ProductTitle(long_title)
        assert "255" in str(exc_info.value)

    def test_title_at_max_length_is_accepted(self) -> None:
        """Title exactly 255 chars is accepted."""
        max_title = "x" * 255
        title = ProductTitle(max_title)
        assert len(title.value) == 255
```

### Unit Test: msgspec Schema Validation

Test that msgspec validates types automatically:

```python
# tests/unit/extraction/adapters/kafka/test_schemas.py
import pytest
import msgspec
from app.extraction.adapters.kafka.schemas import (
    OrderMessage, LineItemMessage
)


class TestLineItemMessageSchema:
    """Test msgspec schema validation for line items."""

    def test_valid_line_item_schema(self) -> None:
        """Valid line item passes msgspec validation."""
        item = LineItemMessage(
            line_item_id="123",
            product_id="456",
            product_title="Widget",
            quantity=5
        )
        assert item.quantity == 5

    def test_invalid_quantity_type_raises_error(self) -> None:
        """String quantity instead of int raises msgspec.ValidationError."""
        with pytest.raises(msgspec.ValidationError) as exc_info:
            LineItemMessage(
                line_item_id="123",
                product_id="456",
                product_title="Widget",
                quantity="invalid"  # type: ignore
            )
        assert "quantity" in str(exc_info.value)

    def test_missing_required_field_raises_error(self) -> None:
        """Missing required field raises msgspec.ValidationError."""
        with pytest.raises(msgspec.ValidationError):
            LineItemMessage(
                line_item_id="123",
                product_id="456"
                # Missing product_title and quantity
            )  # type: ignore

    def test_schema_is_frozen(self) -> None:
        """Schema is frozen and cannot be mutated."""
        item = LineItemMessage(
            line_item_id="123",
            product_id="456",
            product_title="Widget",
            quantity=5
        )
        with pytest.raises(AttributeError):
            item.quantity = 10  # type: ignore


class TestOrderMessageSchema:
    """Test msgspec schema validation for orders."""

    def test_valid_order_message(self) -> None:
        """Valid order message passes validation."""
        message = OrderMessage(
            order_id="O123",
            created_at="2024-11-09T10:30:00Z",
            line_items=[
                LineItemMessage("L1", "P1", "Widget", 5)
            ],
            inserted_at="2024-11-09T10:35:00Z"
        )
        assert message.order_id == "O123"
        assert len(message.line_items) == 1

    def test_empty_line_items_still_validates_schema(self) -> None:
        """Empty line items list passes schema validation.

        Note: Business rule validation (not empty) happens separately.
        """
        message = OrderMessage(
            order_id="O123",
            created_at="2024-11-09T10:30:00Z",
            line_items=[],  # Empty - allowed by schema
            inserted_at="2024-11-09T10:35:00Z"
        )
        assert len(message.line_items) == 0
```

### Unit Test: Anti-Corruption Layer

Test consumer validation logic:

```python
# tests/unit/storage/adapters/test_anti_corruption.py
import pytest
from datetime import datetime
from app.storage.adapters.anti_corruption import (
    KafkaMessageTranslator,
    _parse_iso_timestamp,
    _validate_order_integrity
)
from app.storage.adapters.kafka.schemas import (
    OrderMessage, LineItemMessage
)
from app.storage.domain.exceptions import DataIntegrityException


class TestTimestampParsing:
    """Test ISO 8601 timestamp parsing."""

    def test_parses_iso_with_z_suffix(self) -> None:
        """ISO format with Z suffix is parsed correctly."""
        ts = _parse_iso_timestamp("2024-11-09T10:30:00Z")
        assert ts.year == 2024
        assert ts.month == 11

    def test_parses_iso_with_timezone_offset(self) -> None:
        """ISO format with +00:00 is parsed correctly."""
        ts = _parse_iso_timestamp("2024-11-09T10:30:00+00:00")
        assert ts.year == 2024

    def test_parses_iso_without_timezone(self) -> None:
        """ISO format without timezone is parsed."""
        ts = _parse_iso_timestamp("2024-11-09T10:30:00")
        assert ts.year == 2024

    def test_invalid_timestamp_raises_error(self) -> None:
        """Invalid timestamp format raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            _parse_iso_timestamp("not-a-timestamp")
        assert "Invalid ISO 8601" in str(exc_info.value)

    def test_empty_timestamp_raises_error(self) -> None:
        """Empty timestamp raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            _parse_iso_timestamp("")
        assert "cannot be empty" in str(exc_info.value)


class TestOrderIntegrityValidation:
    """Test business rule validation."""

    def test_valid_order_passes_validation(self) -> None:
        """Valid order passes all integrity checks."""
        message = OrderMessage(
            order_id="O123",
            created_at="2024-11-09T10:30:00Z",
            line_items=[
                LineItemMessage("L1", "P1", "Widget", 5)
            ],
            inserted_at="2024-11-09T10:35:00Z"
        )
        # Should not raise
        _validate_order_integrity(message)

    def test_empty_order_id_raises_error(self) -> None:
        """Empty order ID raises ValueError."""
        message = OrderMessage(
            order_id="",
            created_at="2024-11-09T10:30:00Z",
            line_items=[LineItemMessage("L1", "P1", "Widget", 5)],
            inserted_at="2024-11-09T10:35:00Z"
        )
        with pytest.raises(ValueError) as exc_info:
            _validate_order_integrity(message)
        assert "Order ID" in str(exc_info.value)

    def test_order_without_line_items_raises_error(self) -> None:
        """Order with no line items raises ValueError."""
        message = OrderMessage(
            order_id="O123",
            created_at="2024-11-09T10:30:00Z",
            line_items=[],
            inserted_at="2024-11-09T10:35:00Z"
        )
        with pytest.raises(ValueError) as exc_info:
            _validate_order_integrity(message)
        assert "at least one" in str(exc_info.value)


class TestMessageTranslation:
    """Test full message translation with validation."""

    def test_valid_message_translates_successfully(self) -> None:
        """Valid message is translated to domain Order."""
        raw_message = b'{"order_id":"O123","created_at":"2024-11-09T10:30:00Z","line_items":[{"line_item_id":"L1","product_id":"P1","product_title":"Widget","quantity":5}],"inserted_at":"2024-11-09T10:35:00Z"}'

        order = KafkaMessageTranslator.translate_order(raw_message)

        assert order.order_id == "O123"
        assert len(order.line_items) == 1
        assert order.line_items[0].quantity == 5

    def test_invalid_json_raises_error(self) -> None:
        """Malformed JSON raises DataIntegrityException."""
        raw_message = b'{"invalid": json}'  # Missing quotes

        with pytest.raises(DataIntegrityException) as exc_info:
            KafkaMessageTranslator.translate_order(raw_message)
        assert "deserialize" in str(exc_info.value).lower()

    def test_invalid_timestamp_raises_error(self) -> None:
        """Invalid timestamp in message raises DataIntegrityException."""
        raw_message = b'{"order_id":"O123","created_at":"invalid-date","line_items":[{"line_item_id":"L1","product_id":"P1","product_title":"Widget","quantity":5}],"inserted_at":"2024-11-09T10:35:00Z"}'

        with pytest.raises(DataIntegrityException) as exc_info:
            KafkaMessageTranslator.translate_order(raw_message)
        assert "timestamp" in str(exc_info.value).lower()

    def test_missing_line_items_raises_error(self) -> None:
        """Order without line items raises DataIntegrityException."""
        raw_message = b'{"order_id":"O123","created_at":"2024-11-09T10:30:00Z","line_items":[],"inserted_at":"2024-11-09T10:35:00Z"}'

        with pytest.raises(DataIntegrityException) as exc_info:
            KafkaMessageTranslator.translate_order(raw_message)
        assert "at least one" in str(exc_info.value).lower()

    def test_negative_quantity_raises_error(self) -> None:
        """Negative quantity raises DataIntegrityException."""
        raw_message = b'{"order_id":"O123","created_at":"2024-11-09T10:30:00Z","line_items":[{"line_item_id":"L1","product_id":"P1","product_title":"Widget","quantity":-5}],"inserted_at":"2024-11-09T10:35:00Z"}'

        with pytest.raises(DataIntegrityException) as exc_info:
            KafkaMessageTranslator.translate_order(raw_message)
        assert "must be positive" in str(exc_info.value).lower()
```

### Integration Test: ClickHouse Error Capture

Test that malformed messages are captured:

```python
# tests/integration/storage/test_kafka_error_capture.py
import pytest
import time
import msgspec
from testcontainers.kafka import KafkaContainer
from testcontainers.clickhouse import ClickHouseContainer
from confluent_kafka import Producer
from clickhouse_driver import Client


@pytest.fixture
def kafka_producer(kafka_container):
    """Kafka producer fixture."""
    producer = Producer({
        'bootstrap.servers': kafka_container.get_bootstrap_server()
    })
    yield producer
    producer.flush()


@pytest.fixture
def clickhouse_client(clickhouse_container):
    """ClickHouse client fixture."""
    client = Client(
        host=clickhouse_container.get_container_host_ip(),
        port=clickhouse_container.get_exposed_port(9000)
    )
    yield client


@pytest.mark.asyncio
class TestErrorCapture:
    """Test error capture mechanism."""

    async def test_malformed_json_captured_in_error_table(
        self, kafka_producer, clickhouse_client
    ) -> None:
        """Malformed JSON is captured in kafka_errors table."""
        # Publish invalid JSON (broken syntax)
        invalid_payload = b'{"order_id": broken_json}'
        kafka_producer.produce(topic="shopify-orders", value=invalid_payload)
        kafka_producer.flush()

        # Wait for ClickHouse to consume
        time.sleep(5)

        # Check error table
        errors = clickhouse_client.execute("""
            SELECT topic, error_message FROM shopify.kafka_errors
            WHERE captured_at > now() - INTERVAL 1 MINUTE
        """)

        assert len(errors) > 0
        assert errors[0][0] == "shopify-orders"
        assert "JSON" in errors[0][1] or "parse" in errors[0][1]

    async def test_valid_json_reaches_orders_table(
        self, kafka_producer, clickhouse_client
    ) -> None:
        """Valid JSON is processed and reaches orders table."""
        # Publish valid message
        message = {
            "order_id": "O123",
            "created_at": "2024-11-09T10:30:00Z",
            "line_items": [
                {
                    "line_item_id": "L1",
                    "product_id": "P1",
                    "product_title": "Widget",
                    "quantity": 5
                }
            ],
            "inserted_at": "2024-11-09T10:35:00Z"
        }
        payload = msgspec.json.encode(message)
        kafka_producer.produce(topic="shopify-orders", value=payload)
        kafka_producer.flush()

        # Wait for processing
        time.sleep(5)

        # Check orders table
        orders = clickhouse_client.execute("""
            SELECT order_id FROM shopify.orders
            WHERE order_id = 'O123'
        """)

        assert len(orders) > 0
        assert orders[0][0] == "O123"

    async def test_error_table_has_raw_message(
        self, kafka_producer, clickhouse_client
    ) -> None:
        """Error table preserves raw message for debugging."""
        invalid_payload = b'{"invalid": "json syntax"'  # Missing closing brace
        kafka_producer.produce(topic="shopify-orders", value=invalid_payload)
        kafka_producer.flush()

        time.sleep(5)

        errors = clickhouse_client.execute("""
            SELECT raw_message FROM shopify.kafka_errors
            WHERE captured_at > now() - INTERVAL 1 MINUTE
            LIMIT 1
        """)

        assert len(errors) > 0
        assert b"invalid" in errors[0][0]
```

### Integration Test: Deduplication

Test ReplacingMergeTree deduplication:

```python
# tests/integration/storage/test_deduplication.py
import pytest
import time
import msgspec
from confluent_kafka import Producer
from clickhouse_driver import Client


@pytest.mark.asyncio
class TestDeduplication:
    """Test ReplacingMergeTree deduplication."""

    async def test_duplicate_messages_deduplicated(
        self, kafka_producer, clickhouse_client
    ) -> None:
        """Duplicate messages are deduplicated by ReplacingMergeTree."""
        # Publish same message twice (simulating retransmission)
        message = {
            "order_id": "O123",
            "created_at": "2024-11-09T10:30:00Z",
            "line_items": [{
                "line_item_id": "L1",
                "product_id": "P1",
                "product_title": "Widget",
                "quantity": 5
            }],
            "inserted_at": "2024-11-09T10:35:00Z"
        }
        payload = msgspec.json.encode(message)

        # Publish twice
        for _ in range(2):
            kafka_producer.produce(topic="shopify-orders", value=payload)
        kafka_producer.flush()

        # Wait for consumption and merge
        time.sleep(10)

        # Force merge for immediate deduplication
        clickhouse_client.execute("OPTIMIZE TABLE shopify.orders FINAL")

        # Check deduplication
        result = clickhouse_client.execute("""
            SELECT count(*) as total, count(DISTINCT order_id) as unique
            FROM shopify.orders FINAL
            WHERE order_id = 'O123'
        """)

        assert result[0][0] == result[0][1]  # No duplicates

    async def test_deduplication_respects_order_by_key(
        self, kafka_producer, clickhouse_client
    ) -> None:
        """Deduplication uses ORDER BY (order_id, created_at)."""
        # Same order_id but different created_at
        message1 = {
            "order_id": "O123",
            "created_at": "2024-11-09T10:30:00Z",
            "line_items": [{"line_item_id": "L1", "product_id": "P1", "product_title": "Widget", "quantity": 5}],
            "inserted_at": "2024-11-09T10:35:00Z"
        }
        message2 = {
            "order_id": "O123",
            "created_at": "2024-11-09T11:00:00Z",  # Different time
            "line_items": [{"line_item_id": "L2", "product_id": "P1", "product_title": "Widget", "quantity": 3}],
            "inserted_at": "2024-11-09T11:05:00Z"
        }

        for msg in [message1, message2]:
            kafka_producer.produce(topic="shopify-orders", value=msgspec.json.encode(msg))
        kafka_producer.flush()

        time.sleep(10)

        # Both should exist (different created_at)
        result = clickhouse_client.execute("""
            SELECT count(*) FROM shopify.orders FINAL
            WHERE order_id = 'O123'
        """)

        assert result[0][0] == 2  # Two distinct orders
```

### Integration Test: Schema Evolution

Test adding optional fields without breaking consumption:

```python
# tests/integration/storage/test_schema_evolution.py
import pytest
import time
import msgspec


@pytest.mark.asyncio
class TestSchemaEvolution:
    """Test forward-compatible schema evolution."""

    async def test_new_optional_field_with_default(
        self, kafka_producer, clickhouse_client
    ) -> None:
        """New optional field with default doesn't break consumption."""
        # Old message format (without customer_email)
        old_message = {
            "order_id": "O123",
            "created_at": "2024-11-09T10:30:00Z",
            "line_items": [{
                "line_item_id": "L1",
                "product_id": "P1",
                "product_title": "Widget",
                "quantity": 5
            }],
            "inserted_at": "2024-11-09T10:35:00Z"
            # No customer_email field
        }

        kafka_producer.produce(
            topic="shopify-orders",
            value=msgspec.json.encode(old_message)
        )
        kafka_producer.flush()

        time.sleep(5)

        # Should process successfully
        orders = clickhouse_client.execute("""
            SELECT count(*) FROM shopify.orders
            WHERE order_id = 'O123'
        """)

        assert orders[0][0] == 1  # Processed without error

    async def test_extra_unknown_field_skipped(
        self, kafka_producer, clickhouse_client
    ) -> None:
        """Extra unknown fields are skipped without error.

        Requires: input_format_skip_unknown_fields = 1
        """
        # Message with extra field
        message = {
            "order_id": "O456",
            "created_at": "2024-11-09T10:30:00Z",
            "line_items": [{
                "line_item_id": "L1",
                "product_id": "P1",
                "product_title": "Widget",
                "quantity": 5
            }],
            "inserted_at": "2024-11-09T10:35:00Z",
            "future_field": "this will be ignored"  # Unknown field
        }

        kafka_producer.produce(
            topic="shopify-orders",
            value=msgspec.json.encode(message)
        )
        kafka_producer.flush()

        time.sleep(5)

        # Should process successfully despite extra field
        orders = clickhouse_client.execute("""
            SELECT count(*) FROM shopify.orders
            WHERE order_id = 'O456'
        """)

        assert orders[0][0] == 1
```

## ClickHouse Query Examples

### Error Monitoring

Check error rate over the last hour:

```sql
SELECT
    toStartOfMinute(captured_at) as minute,
    count(*) as error_count
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR
GROUP BY minute
ORDER BY minute DESC;
```

Sample error messages:

```sql
SELECT
    error_message,
    count(*) as cnt,
    max(raw_message) as example
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR
GROUP BY error_message
ORDER BY cnt DESC;
```

### Data Quality

Check deduplication effectiveness:

```sql
SELECT
    'before_merge' as status,
    count(*) as rows,
    count(DISTINCT order_id) as unique_orders
FROM shopify.orders
WHERE created_at > now() - INTERVAL 1 HOUR
UNION ALL
SELECT
    'after_merge' as status,
    count(*) as rows,
    count(DISTINCT order_id) as unique_orders
FROM shopify.orders FINAL
WHERE created_at > now() - INTERVAL 1 HOUR;
```

### Performance

Check consumption throughput:

```sql
SELECT
    count() as total_messages,
    min(captured_at) as start_time,
    max(captured_at) as end_time,
    dateDiff('second', start_time, end_time) as duration_seconds,
    round(count() / duration_seconds, 2) as msg_per_second
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR;
```

## Common Issues & Solutions

### Issue: No errors captured despite invalid messages

**Diagnosis:**
```sql
-- Check if error table exists
SELECT * FROM system.tables
WHERE database = 'shopify' AND name = 'kafka_errors';

-- Check if Kafka engine has error streaming enabled
SELECT * FROM system.settings
WHERE name LIKE '%error%';
```

**Solution:**
1. Verify `kafka_handle_error_mode = 'stream'` is set
2. Restart the Kafka table consumption
3. Check ClickHouse logs for errors

### Issue: Messages arrive but not in orders table

**Diagnosis:**
```sql
-- Check if materialized view exists
SELECT * FROM system.tables
WHERE database = 'shopify' AND name = 'orders_mv';

-- Check error table for processing errors
SELECT * FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 5 MINUTE;
```

**Solution:**
1. Check `kafka_errors` for deserialization or parsing errors
2. Verify materialized view filter: `WHERE length(_error) = 0`
3. Check consumer lag: How far behind is consumption?

### Issue: Duplicate orders in results

**Diagnosis:**
```sql
-- Check for duplicates without FINAL
SELECT order_id, count(*) as cnt
FROM shopify.orders
WHERE created_at > now() - INTERVAL 1 HOUR
GROUP BY order_id
HAVING cnt > 1
LIMIT 10;
```

**Solution:**
1. Use FINAL modifier in queries: `SELECT * FROM shopify.orders FINAL`
2. Force merge: `OPTIMIZE TABLE shopify.orders FINAL`
3. Wait for background merges (5-10 minutes)

### Issue: High error rate

**Diagnosis:**
```sql
-- Identify error types
SELECT error_message, count(*) as cnt
FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR
GROUP BY error_message
ORDER BY cnt DESC;

-- Check sample messages
SELECT raw_message FROM shopify.kafka_errors
WHERE captured_at > now() - INTERVAL 1 HOUR
LIMIT 5;
```

**Solution:**
- JSON parsing errors: Check producer is sending valid JSON
- Schema mismatches: Verify field names and types match
- Type errors: Check quantity, order_id are correct types
- Missing fields: Verify all required fields are present
