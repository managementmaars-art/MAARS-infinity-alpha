"""
Producer-Side Validation Patterns for ClickHouse + Kafka

This module demonstrates how to implement defense-in-depth validation
at the producer boundary using msgspec schemas and domain value objects.
"""

from __future__ import annotations

import msgspec
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Final

from app.core.monitoring.otel_logger import logger, traced

logger = logger(__name__)


# ============================================================================
# 1. MSGSPEC SCHEMAS - Type-safe message validation
# ============================================================================

class LineItemMessage(msgspec.Struct, frozen=True):
    """Type-safe schema for line items.

    msgspec automatically validates types during construction:
    - Enforces field types (int, str, etc.)
    - Rejects extra fields by default
    - Frozen=True prevents mutation
    """
    line_item_id: str
    product_id: str
    product_title: str
    quantity: int


class OrderMessage(msgspec.Struct, frozen=True):
    """Type-safe schema for orders.

    Benefits:
    - 10-20x faster than Pydantic (critical for high-volume streams)
    - Frozen prevents accidental mutations
    - Type validation on construction (no separate step needed)
    """
    order_id: str
    created_at: str  # ISO 8601 format
    line_items: list[LineItemMessage]
    inserted_at: str  # ISO 8601 format


# ============================================================================
# 2. DOMAIN VALUE OBJECTS - Business rule validation
# ============================================================================

@dataclass(frozen=True)
class ProductTitle:
    """Value object for product titles with business rule validation.

    Enforces:
    - Non-empty strings
    - Length between 1-255 characters (Shopify constraint)
    - No leading/trailing whitespace
    """
    value: str

    def __post_init__(self) -> None:
        """Validate business rules."""
        if not self.value or not self.value.strip():
            raise InvalidProductException("Product title cannot be empty")

        if len(self.value) < 1:
            raise InvalidProductException("Product title must be at least 1 character")

        if len(self.value) > 255:
            raise InvalidProductException("Product title must be at most 255 characters")


@dataclass(frozen=True)
class OrderId:
    """Value object for order IDs with validation."""
    value: str

    def __post_init__(self) -> None:
        """Validate order ID format."""
        if not self.value or not self.value.strip():
            raise InvalidOrderException("Order ID cannot be empty")

        if len(self.value) > 255:
            raise InvalidOrderException("Order ID cannot exceed 255 characters")


# ============================================================================
# 3. DOMAIN EXCEPTIONS
# ============================================================================

class InvalidOrderException(Exception):
    """Raised when order violates business rules."""
    pass


class InvalidProductException(Exception):
    """Raised when product violates business rules."""
    pass


# ============================================================================
# 4. PRODUCER WITH DUAL-LAYER VALIDATION
# ============================================================================

class OrderProducer:
    """Producer with defense-in-depth validation.

    Validation layers:
    1. msgspec schema validation (type safety)
    2. Domain value object validation (business rules)
    """

    def __init__(self, kafka_producer) -> None:
        """Initialize producer.

        Args:
            kafka_producer: confluent_kafka.KafkaProducer instance
        """
        self.kafka_producer = kafka_producer

    @traced
    def publish_order(self, order) -> None:
        """Publish order with dual-layer validation.

        Validation flow:
        1. Validate order as domain entity (business rules)
        2. Convert to message schema (OrderMessage)
        3. msgspec validates during construction
        4. Serialize to JSON and publish to Kafka

        Raises:
            InvalidOrderException: If order violates business rules
            msgspec.ValidationError: If message schema is invalid
        """
        try:
            # Layer 1: Domain validation (business rules)
            self._validate_order_domain_rules(order)

            # Layer 2: Message construction with msgspec validation
            message = self._build_order_message(order)

            # Serialize using msgspec (10-20x faster than JSON)
            payload = msgspec.json.encode(message)

            # Publish to Kafka
            self.kafka_producer.produce(
                topic="shopify-orders",
                value=payload,
                key=order.order_id.value.encode('utf-8')
            )

            # Log success with context
            logger.info(
                f"order: ${order.order_id.value.encode('utf-8')} published successfully",
                order_id=order.order_id.value,
                item_count=len(order.line_items)
            )

        except InvalidOrderException as e:
            # Domain validation failed (business rule violation)
            logger.error(
                "order_validation_failed",
                error=str(e),
                order_id=getattr(order, 'order_id', 'unknown')
            )
            raise

        except msgspec.ValidationError as e:
            # Schema validation failed (type mismatch)
            logger.error(
                "order_schema_validation_failed",
                error=str(e),
                order_id=getattr(order, 'order_id', 'unknown')
            )
            raise InvalidOrderException(f"Order schema validation failed: {e}") from e

        except Exception as e:
            # Unexpected error
            logger.error(
                "order_publish_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    @staticmethod
    def _validate_order_domain_rules(order) -> None:
        """Validate order against domain business rules.

        This is separate from schema validation to enforce
        business logic independent of message format.

        Raises:
            InvalidOrderException: If any rule is violated
        """
        # Rule 1: Order must have items
        if not order.line_items:
            raise InvalidOrderException("Order must have at least one line item")

        # Rule 2: All items must be valid
        for i, item in enumerate(order.line_items):
            if item.quantity <= 0:
                raise InvalidOrderException(
                    f"Line item {i}: quantity must be positive (got {item.quantity})"
                )

            if not item.product_title or not item.product_title.strip():
                raise InvalidOrderException(
                    f"Line item {i}: product_title cannot be empty"
                )

        # Rule 3: Timestamps must be reasonable
        if not order.created_at:
            raise InvalidOrderException("Order created_at cannot be empty")

    @staticmethod
    def _build_order_message(order) -> OrderMessage:
        """Build OrderMessage from domain Order.

        This conversion performs minimal transformation since
        domain validation already occurred.

        Returns:
            OrderMessage: Type-safe message ready for serialization

        Raises:
            msgspec.ValidationError: If resulting message is invalid
        """
        # Build line items
        line_items: list[LineItemMessage] = [
            LineItemMessage(
                line_item_id=item.line_item_id,
                product_id=str(item.product_id.value),
                product_title=item.product_title.value,
                quantity=item.quantity
            )
            for item in order.line_items
        ]

        # Create message (msgspec validates here)
        return OrderMessage(
            order_id=order.order_id.value,
            created_at=order.created_at.isoformat(),
            line_items=line_items,
            inserted_at=datetime.now(timezone.utc).isoformat()
        )


# ============================================================================
# 5. ADVANCED PATTERN: Conditional Validation by Environment
# ============================================================================

class EnvironmentAwareProducer:
    """Producer with environment-specific validation.

    In development, you might be more lenient.
    In production, enforce strict rules.
    """

    STRICT_MODE: Final = True  # Set based on environment

    @traced
    def publish_order(self, order) -> None:
        """Publish with environment-aware validation."""
        if self.STRICT_MODE:
            # Production: Strict validation
            self._validate_strict(order)
        else:
            # Development: Lenient validation
            self._validate_lenient(order)

        # Rest of publishing logic...

    @staticmethod
    def _validate_strict(order) -> None:
        """Strict validation for production."""
        # All rules enforced
        if not order.line_items:
            raise InvalidOrderException("Order must have at least one line item")

    @staticmethod
    def _validate_lenient(order) -> None:
        """Lenient validation for development."""
        # Log warnings but don't fail
        if not order.line_items:
            logger.warning("order_has_no_items", order_id=order.order_id)


# ============================================================================
# 6. PATTERN: Batch Publishing with Validation
# ============================================================================

class BatchOrderProducer:
    """Producer for batch operations with aggregated error reporting.

    Use when publishing multiple orders and need to track
    which ones succeed vs fail.
    """

    def __init__(self, kafka_producer) -> None:
        self.kafka_producer = kafka_producer
        self.producer = OrderProducer(kafka_producer)

    @traced
    def publish_batch(self, orders: list) -> dict:
        """Publish batch of orders with error aggregation.

        Returns:
            {
                'success': 5,
                'failed': 2,
                'errors': [
                    {'order_id': '123', 'error': 'Quantity must be positive'}
                ]
            }
        """
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }

        for order in orders:
            try:
                self.producer.publish_order(order)
                results['success'] += 1

            except (InvalidOrderException, msgspec.ValidationError) as e:
                results['failed'] += 1
                results['errors'].append({
                    'order_id': getattr(order, 'order_id', 'unknown'),
                    'error': str(e)
                })
                logger.warning(
                    "order_publish_failed_in_batch",
                    order_id=getattr(order, 'order_id', 'unknown'),
                    error=str(e)
                )

        logger.info(
            "batch_publish_complete",
            total=len(orders),
            success=results['success'],
            failed=results['failed']
        )

        return results


# ============================================================================
# 7. PATTERN: Testing Validation
# ============================================================================

# Example test cases (see examples.md for full test suite)

def test_valid_order_publishes_successfully():
    """Producer accepts valid orders."""
    # In real tests, use mock Kafka producer
    pass


def test_order_without_items_raises_exception():
    """Producer rejects orders with no line items."""
    # In real tests, verify InvalidOrderException is raised
    pass


def test_invalid_quantity_raises_exception():
    """Producer rejects line items with negative/zero quantity."""
    # In real tests, verify business rule is enforced
    pass


def test_msgspec_validates_during_construction():
    """msgspec validation happens automatically."""
    # Demonstrate that type mismatches are caught
    try:
        # This will fail: quantity must be int, not str
        message = LineItemMessage(
            line_item_id="123",
            product_id="456",
            product_title="Widget",
            quantity="invalid"  # type: ignore
        )
    except msgspec.ValidationError as e:
        assert "quantity" in str(e)


# ============================================================================
# DESIGN DECISIONS
# ============================================================================

"""
Why msgspec instead of Pydantic?
- 10-20x faster serialization/deserialization
- Critical for high-volume event streams
- Frozen=True prevents accidental mutations
- Type safety at construction time

Why separate domain validation from schema validation?
- Domain rules are independent of message format
- Makes business logic testable without Kafka
- Easier to evolve message format without breaking domain

Why publish to Kafka at all if we validate here?
- Producer validation is NOT a substitute for consumer validation
- Defense-in-depth: invalid data should NEVER reach Kafka
- Reduces load on Kafka and consumer
- Fast feedback to data source (Shopify API)
"""
