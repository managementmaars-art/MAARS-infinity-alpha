"""
Consumer-Side Validation Patterns for ClickHouse + Kafka

This module demonstrates anti-corruption layer implementation
at the consumer boundary using msgspec deserialization and
defense-in-depth validation.
"""

from __future__ import annotations

import msgspec
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.core.monitoring.otel_logger import logger, traced

logger = logger(__name__)


# ============================================================================
# 1. CONTEXT-LOCAL MESSAGE SCHEMAS (Storage Context)
# ============================================================================

class LineItemMessage(msgspec.Struct, frozen=True):
    """Line item message schema (Storage Context).

    Note: Each bounded context owns its own schema definition.
    This prevents coupling between contexts.
    """
    line_item_id: str
    product_id: str
    product_title: str
    quantity: int


class OrderMessage(msgspec.Struct, frozen=True):
    """Order message schema (Storage Context).

    Important: This mirrors the producer schema but is
    independently maintained. Allows evolution without
    tight coupling.
    """
    order_id: str
    created_at: str  # ISO 8601 format
    line_items: list[LineItemMessage]
    inserted_at: str  # ISO 8601 format


# ============================================================================
# 2. DOMAIN EXCEPTIONS
# ============================================================================

class DataIntegrityException(Exception):
    """Raised when received data fails integrity validation."""
    pass


# ============================================================================
# 3. ANTI-CORRUPTION LAYER - Multi-Layer Validation
# ============================================================================

class KafkaMessageTranslator:
    """Anti-corruption layer with defense-in-depth validation.

    This layer sits at the boundary between the event stream
    (Kafka) and the storage context domain. It:

    1. Deserializes msgspec messages (type validation)
    2. Validates timestamp formats (data integrity)
    3. Validates business rules (domain constraints)
    4. Translates to domain entities (domain models)

    Benefits:
    - Defense-in-depth: Catches corruption after producer
    - Context isolation: Validation specific to storage domain
    - Clear boundaries: Translation explicitly documented
    - OTEL logging: Full tracing of validation steps
    """

    @staticmethod
    @traced
    def translate_order(raw_message: bytes) -> Order:
        """Translate Kafka message to domain Order.

        This is the main entry point for consuming order messages.
        It handles the full validation pipeline.

        Args:
            raw_message: Raw bytes from Kafka

        Returns:
            Order: Domain entity ready for storage

        Raises:
            DataIntegrityException: If message is invalid at any step

        Validation layers:
            1. Deserialization: msgspec validates JSON + types
            2. Timestamp format: ISO 8601 parsing
            3. Business rules: Non-empty fields, valid quantities
            4. Translation: Convert to domain entities
        """
        # Layer 1: Deserialize with msgspec (type validation)
        try:
            message = msgspec.json.decode(raw_message, type=OrderMessage)
            logger.debug("order_message_deserialized", order_id=message.order_id)

        except msgspec.DecodeError as e:
            logger.error(
                "order_deserialization_failed",
                error=str(e),
                sample=raw_message[:200]
            )
            raise DataIntegrityException(
                f"Failed to deserialize order message: {e}"
            ) from e

        # Layer 2: Validate timestamps
        try:
            created_at = _parse_iso_timestamp(message.created_at)
            inserted_at = _parse_iso_timestamp(message.inserted_at)
            logger.debug("order_timestamps_validated")

        except ValueError as e:
            logger.error("order_timestamp_validation_failed", error=str(e))
            raise DataIntegrityException(f"Invalid timestamp: {e}") from e

        # Layer 3: Validate business rules
        try:
            _validate_order_integrity(message)
            logger.debug("order_business_rules_validated")

        except ValueError as e:
            logger.error("order_business_rule_violation", error=str(e))
            raise DataIntegrityException(f"Business rule violation: {e}") from e

        # Layer 4: Translate to domain entities
        try:
            line_items = [
                _translate_line_item(item)
                for item in message.line_items
            ]

            order = Order(
                order_id=message.order_id,
                created_at=created_at,
                line_items=line_items,
                inserted_at=inserted_at
            )

            logger.info(
                "order_translated",
                order_id=message.order_id,
                item_count=len(line_items)
            )

            return order

        except Exception as e:
            logger.error(
                "order_translation_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise DataIntegrityException(f"Order translation failed: {e}") from e


# ============================================================================
# 4. VALIDATION HELPERS
# ============================================================================

def _parse_iso_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO 8601 timestamp string.

    Handles:
    - ISO 8601 format with timezone (2024-11-09T10:30:00Z)
    - ISO 8601 format with offset (2024-11-09T10:30:00+00:00)
    - ISO 8601 format without timezone (2024-11-09T10:30:00)

    Raises:
        ValueError: If timestamp is not valid ISO 8601
    """
    if not timestamp_str:
        raise ValueError("Timestamp cannot be empty")

    try:
        # Replace 'Z' with '+00:00' for parsing
        normalized = timestamp_str.replace('Z', '+00:00')
        return datetime.fromisoformat(normalized)

    except ValueError as e:
        raise ValueError(
            f"Invalid ISO 8601 timestamp: {timestamp_str}"
        ) from e


def _validate_order_integrity(message: OrderMessage) -> None:
    """Validate order-level business rules.

    Checks:
    - Non-empty order ID
    - At least one line item
    - Timestamps are present

    Raises:
        ValueError: If any rule is violated
    """
    # Rule 1: Order ID must be non-empty
    if not message.order_id or not message.order_id.strip():
        raise ValueError("Order ID cannot be empty")

    # Rule 2: Order must have at least one line item
    if not message.line_items:
        raise ValueError("Order must have at least one line item")

    # Rule 3: Timestamps must be non-empty
    if not message.created_at or not message.inserted_at:
        raise ValueError("Order must have both created_at and inserted_at timestamps")

    # Rule 4: Order ID length constraint
    if len(message.order_id) > 255:
        raise ValueError(f"Order ID too long: {len(message.order_id)} > 255")


def _validate_line_item_integrity(item: LineItemMessage) -> None:
    """Validate line item-level business rules.

    Checks:
    - Non-empty product ID
    - Non-empty product title
    - Positive quantity
    - Title length constraint

    Raises:
        ValueError: If any rule is violated
    """
    # Rule 1: Product ID must be non-empty
    if not item.product_id or not item.product_id.strip():
        raise ValueError("Product ID cannot be empty")

    # Rule 2: Product title must be non-empty and non-whitespace
    if not item.product_title or not item.product_title.strip():
        raise ValueError("Product title cannot be empty")

    # Rule 3: Quantity must be positive
    if item.quantity <= 0:
        raise ValueError(f"Quantity must be positive (got {item.quantity})")

    # Rule 4: Product title length constraint (Shopify limit)
    if len(item.product_title) > 255:
        raise ValueError(
            f"Product title too long: {len(item.product_title)} > 255"
        )

    # Rule 5: Product ID length constraint
    if len(item.product_id) > 255:
        raise ValueError(
            f"Product ID too long: {len(item.product_id)} > 255"
        )


def _translate_line_item(item: LineItemMessage) -> OrderItem:
    """Translate message line item to domain OrderItem.

    Performs additional validation and creates domain entity.

    Args:
        item: Message line item

    Returns:
        OrderItem: Domain line item entity

    Raises:
        ValueError: If item is invalid
    """
    # Validate before translation
    _validate_line_item_integrity(item)

    # Create domain entity
    return OrderItem(
        line_item_id=item.line_item_id,
        product_id=item.product_id,
        product_title=item.product_title,
        quantity=item.quantity
    )


# ============================================================================
# 5. DOMAIN ENTITIES
# ============================================================================

@dataclass
class OrderItem:
    """Domain line item entity."""
    line_item_id: str
    product_id: str
    product_title: str
    quantity: int


@dataclass
class Order:
    """Domain order entity."""
    order_id: str
    created_at: datetime
    line_items: list[OrderItem]
    inserted_at: datetime


# ============================================================================
# 6. ADVANCED PATTERN: Versioned Message Translation
# ============================================================================

class VersionedMessageTranslator:
    """Translator supporting multiple message schema versions.

    Use when you need to handle schema evolution and can have
    multiple versions of messages in the stream simultaneously.
    """

    SUPPORTED_VERSIONS = [1, 2]  # What versions we can handle

    @staticmethod
    @traced
    def translate_order_with_version(raw_message: bytes) -> Order:
        """Translate order message with version detection.

        Supports graceful schema evolution by handling multiple
        message versions.
        """
        try:
            # Deserialize without strict schema to extract version
            base_message = msgspec.json.decode(raw_message, type=dict)

            version = base_message.get('version', 1)

            if version == 1:
                return VersionedMessageTranslator._translate_v1(raw_message)
            elif version == 2:
                return VersionedMessageTranslator._translate_v2(raw_message)
            else:
                logger.warning(
                    "order_version_unsupported",
                    version=version,
                    supported=VersionedMessageTranslator.SUPPORTED_VERSIONS
                )
                raise DataIntegrityException(
                    f"Unsupported message version: {version}"
                )

        except Exception as e:
            logger.error("order_version_detection_failed", error=str(e))
            raise DataIntegrityException(f"Failed to detect message version: {e}") from e

    @staticmethod
    def _translate_v1(raw_message: bytes) -> Order:
        """Translate v1 message (original schema)."""
        # Use standard translator
        return KafkaMessageTranslator.translate_order(raw_message)

    @staticmethod
    def _translate_v2(raw_message: bytes) -> Order:
        """Translate v2 message (with customer email)."""
        # Parse v2-specific schema with additional fields
        # Return same Order domain entity
        pass


# ============================================================================
# 7. PATTERN: Batch Message Translation
# ============================================================================

class BatchMessageTranslator:
    """Translator for batch operations with aggregated error reporting."""

    @staticmethod
    @traced
    def translate_batch(raw_messages: list[bytes]) -> dict:
        """Translate batch of messages with error aggregation.

        Returns:
            {
                'success': [Order, Order, ...],
                'failed': [
                    {
                        'message': raw_bytes,
                        'error': 'Invalid timestamp',
                        'sample': 'first 100 chars'
                    }
                ]
            }
        """
        results = {
            'success': [],
            'failed': []
        }

        for raw_message in raw_messages:
            try:
                order = KafkaMessageTranslator.translate_order(raw_message)
                results['success'].append(order)

            except DataIntegrityException as e:
                results['failed'].append({
                    'error': str(e),
                    'sample': raw_message[:100]
                })
                logger.warning(
                    "batch_message_translation_failed",
                    error=str(e)
                )

        logger.info(
            "batch_translation_complete",
            total=len(raw_messages),
            success=len(results['success']),
            failed=len(results['failed'])
        )

        return results


# ============================================================================
# 8. PATTERN: Validation with Context
# ============================================================================

class ContextAwareTranslator:
    """Translator with context-specific validation rules.

    Some validation rules may depend on runtime context
    (e.g., customer tier, feature flags, time windows).
    """

    def __init__(self, context: dict) -> None:
        """Initialize with context.

        Args:
            context: Runtime context with flags, config, etc.
                {
                    'strict_mode': True,
                    'customer_tier': 'premium',
                    'min_order_value': 10.0
                }
        """
        self.context = context

    @traced
    def translate_order(self, raw_message: bytes) -> Order:
        """Translate with context-aware validation."""
        # Standard translation
        order = KafkaMessageTranslator.translate_order(raw_message)

        # Additional context-specific validation
        if self.context.get('strict_mode'):
            self._validate_strict(order)

        return order

    def _validate_strict(self, order: Order) -> None:
        """Enforce stricter validation in strict mode."""
        if len(order.line_items) > 100:
            raise DataIntegrityException("Order too large for strict mode")


# ============================================================================
# DESIGN DECISIONS
# ============================================================================

"""
Why separate consumer validation from producer validation?
- Defense-in-depth: Don't trust even valid producers
- Protection against data corruption in transit
- Context-specific validation (storage domain rules)
- Isolates failure domains

Why msgspec deserialization as first step?
- Type validation happens automatically
- Fails fast on schema mismatches
- Better performance than Pydantic

Why explicit validation functions?
- Business rules documented separately
- Easy to test without domain entities
- Reusable across different message types
- Clear error messages in logs

Why translate to domain entities separately?
- Domain entities are clean (no Kafka concepts)
- Easier to test business logic
- Allows evolution of domain without touching adapters

Why OTEL logging at each step?
- Full visibility into translation pipeline
- Easy to identify where failures occur
- Performance metrics for each validation layer
- Debugging support for data issues
"""
