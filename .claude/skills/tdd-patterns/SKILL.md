---
name: tdd-patterns
description: "Test-Driven Development: red-green-refactor, unit/integration/e2e tests, mocking, test doubles, coverage"
---

# Test-Driven Development (TDD)

Comprehensive TDD practices: the red-green-refactor cycle, the test pyramid, test doubles, mocking strategies, property-based testing, and coverage analysis across Python, TypeScript, and Java.

## The Red-Green-Refactor Cycle

```
RED   → Write a failing test that describes the desired behavior
GREEN → Write the minimum code to make the test pass
REFACTOR → Clean up code without breaking tests

Rules:
- Never write production code without a failing test
- Write only enough test code to produce a failure
- Write only enough production code to make the test pass
```

## Python TDD Example (pytest)

```python
# Step 1 — RED: Write the failing test first
# tests/test_shopping_cart.py
import pytest
from decimal import Decimal
from app.shopping_cart import ShoppingCart, Item, CartError

class TestShoppingCart:
    def setup_method(self):
        self.cart = ShoppingCart(tax_rate=Decimal("0.08"))

    def test_new_cart_is_empty(self):
        assert self.cart.is_empty()
        assert self.cart.item_count == 0

    def test_add_item_increases_count(self):
        item = Item(id="prod-1", name="Widget", price=Decimal("9.99"), quantity=2)
        self.cart.add_item(item)
        assert self.cart.item_count == 2
        assert not self.cart.is_empty()

    def test_total_includes_tax(self):
        self.cart.add_item(Item(id="p1", name="Item A", price=Decimal("10.00"), quantity=1))
        self.cart.add_item(Item(id="p2", name="Item B", price=Decimal("20.00"), quantity=2))
        # subtotal = 10 + 40 = 50; tax = 4.00; total = 54.00
        assert self.cart.subtotal == Decimal("50.00")
        assert self.cart.tax == Decimal("4.00")
        assert self.cart.total == Decimal("54.00")

    def test_remove_nonexistent_item_raises_error(self):
        with pytest.raises(CartError, match="Item not found"):
            self.cart.remove_item("nonexistent-id")

    def test_apply_discount_reduces_total(self):
        self.cart.add_item(Item(id="p1", name="Widget", price=Decimal("100.00"), quantity=1))
        self.cart.apply_discount(percent=10)
        assert self.cart.subtotal == Decimal("90.00")

    @pytest.mark.parametrize("quantity,expected", [
        (0, "Quantity must be positive"),
        (-1, "Quantity must be positive"),
    ])
    def test_invalid_quantity_raises_error(self, quantity: int, expected: str):
        with pytest.raises(CartError, match=expected):
            self.cart.add_item(Item(id="p1", name="Widget", price=Decimal("9.99"), quantity=quantity))


# Step 2 — GREEN: Minimal implementation
# app/shopping_cart.py
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

@dataclass
class Item:
    id: str
    name: str
    price: Decimal
    quantity: int

class CartError(Exception):
    pass

class ShoppingCart:
    def __init__(self, tax_rate: Decimal = Decimal("0")):
        self._items: dict[str, Item] = {}
        self._tax_rate = tax_rate
        self._discount_pct: Decimal = Decimal("0")

    def add_item(self, item: Item) -> None:
        if item.quantity <= 0:
            raise CartError("Quantity must be positive")
        if item.id in self._items:
            existing = self._items[item.id]
            self._items[item.id] = Item(existing.id, existing.name, existing.price,
                                        existing.quantity + item.quantity)
        else:
            self._items[item.id] = item

    def remove_item(self, item_id: str) -> None:
        if item_id not in self._items:
            raise CartError(f"Item not found: {item_id}")
        del self._items[item_id]

    def apply_discount(self, percent: int) -> None:
        self._discount_pct = Decimal(str(percent))

    def is_empty(self) -> bool:
        return len(self._items) == 0

    @property
    def item_count(self) -> int:
        return sum(i.quantity for i in self._items.values())

    @property
    def subtotal(self) -> Decimal:
        raw = sum(i.price * i.quantity for i in self._items.values())
        if self._discount_pct:
            raw = raw * (1 - self._discount_pct / 100)
        return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def tax(self) -> Decimal:
        return (self.subtotal * self._tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.tax
```

## Mocking and Test Doubles

```python
from unittest.mock import AsyncMock, MagicMock, patch, call
import pytest

# Types of test doubles:
# Stub   — returns canned values
# Mock   — verifies interactions
# Fake   — lightweight working implementation
# Spy    — records calls, delegates to real implementation

class TestOrderService:
    @pytest.fixture
    def mock_payment_gateway(self):
        mock = MagicMock()
        mock.charge.return_value = {"status": "success", "transaction_id": "txn-123"}
        return mock

    @pytest.fixture
    def mock_inventory(self):
        mock = MagicMock()
        mock.reserve.return_value = True
        return mock

    @pytest.fixture
    def order_service(self, mock_payment_gateway, mock_inventory):
        from app.order_service import OrderService
        return OrderService(payment_gateway=mock_payment_gateway, inventory=mock_inventory)

    def test_place_order_charges_correct_amount(self, order_service, mock_payment_gateway):
        order = {"items": [{"id": "p1", "price": 29.99, "qty": 2}], "total": 59.98}
        order_service.place_order(order, card_token="tok_visa")
        mock_payment_gateway.charge.assert_called_once_with(amount=5998, token="tok_visa")

    def test_place_order_rolls_back_inventory_on_payment_failure(
        self, order_service, mock_payment_gateway, mock_inventory
    ):
        mock_payment_gateway.charge.side_effect = Exception("Card declined")
        order = {"items": [{"id": "p1", "price": 10.00, "qty": 1}], "total": 10.00}

        with pytest.raises(Exception, match="Card declined"):
            order_service.place_order(order, card_token="tok_bad")

        mock_inventory.release.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_notification_sent(self):
        mock_notifier = AsyncMock()
        mock_notifier.send_confirmation.return_value = None

        from app.notification_service import NotificationService
        service = NotificationService(notifier=mock_notifier)
        await service.notify_order_placed(order_id="ord-1", user_email="user@example.com")

        mock_notifier.send_confirmation.assert_awaited_once_with(
            to="user@example.com",
            order_id="ord-1"
        )

    @patch("app.order_service.datetime")
    def test_order_timestamp_is_utc(self, mock_datetime, order_service):
        from datetime import datetime, timezone
        fixed_time = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_time

        order = order_service.create_draft(user_id="u1")
        assert order["created_at"] == fixed_time
```

## Integration Tests

```python
# tests/integration/test_user_repository.py
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from app.database import Base
from app.repositories.user_repository import UserRepository

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg

@pytest.fixture(scope="session")
def engine(postgres_container):
    url = postgres_container.get_connection_url()
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def repo(engine):
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        yield UserRepository(session)
        session.rollback()  # isolation between tests

class TestUserRepository:
    def test_create_and_fetch_user(self, repo):
        user = repo.create(email="alice@example.com", name="Alice")
        assert user.id is not None

        fetched = repo.find_by_id(user.id)
        assert fetched.email == "alice@example.com"

    def test_find_by_email_case_insensitive(self, repo):
        repo.create(email="bob@example.com", name="Bob")
        assert repo.find_by_email("BOB@EXAMPLE.COM") is not None

    def test_delete_removes_user(self, repo):
        user = repo.create(email="charlie@example.com", name="Charlie")
        repo.delete(user.id)
        assert repo.find_by_id(user.id) is None
```

## TypeScript TDD (Vitest)

```typescript
// src/__tests__/password-validator.test.ts
import { describe, it, expect } from 'vitest'
import { validatePassword, PasswordStrength } from '../password-validator'

describe('validatePassword', () => {
  it('returns WEAK for short passwords', () => {
    expect(validatePassword('abc123')).toBe(PasswordStrength.WEAK)
  })

  it('returns MEDIUM for 8+ chars with letters and numbers', () => {
    expect(validatePassword('Pass1234')).toBe(PasswordStrength.MEDIUM)
  })

  it('returns STRONG for 12+ chars with upper, lower, digits, symbols', () => {
    expect(validatePassword('P@ssw0rd!2024')).toBe(PasswordStrength.STRONG)
  })

  it.each([
    ['', PasswordStrength.WEAK],
    ['1234567', PasswordStrength.WEAK],
    ['password', PasswordStrength.MEDIUM],
    ['P@ssw0rd!2024Xyz', PasswordStrength.STRONG],
  ])('validatePassword(%s) === %s', (input, expected) => {
    expect(validatePassword(input)).toBe(expected)
  })
})

// Property-based testing with fast-check
import fc from 'fast-check'

describe('validatePassword properties', () => {
  it('always returns a valid PasswordStrength enum value', () => {
    fc.assert(
      fc.property(fc.string(), (pwd) => {
        const result = validatePassword(pwd)
        return Object.values(PasswordStrength).includes(result)
      })
    )
  })

  it('strong passwords always have length >= 12', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 12 }).filter(s =>
          /[A-Z]/.test(s) && /[a-z]/.test(s) && /\d/.test(s) && /[^A-Za-z0-9]/.test(s)
        ),
        (pwd) => validatePassword(pwd) === PasswordStrength.STRONG
      )
    )
  })
})
```

## Coverage and Test Pyramid

```bash
# Python coverage (pytest-cov)
pytest --cov=src --cov-report=html --cov-report=term-missing \
       --cov-fail-under=80 tests/

# Coverage exclusions (.coveragerc)
[coverage:run]
source = src
omit = src/migrations/*, src/conftest.py, */tests/*

[coverage:report]
exclude_lines =
    pragma: no cover
    if TYPE_CHECKING:
    @abstractmethod
    raise NotImplementedError

# TypeScript (Vitest)
vitest run --coverage --coverage.provider=v8 \
  --coverage.thresholds.statements=80 \
  --coverage.thresholds.branches=75

# Test pyramid targets (adjust per team):
# Unit tests:       70% of test suite — fast, isolated, run on every save
# Integration tests: 20% — test DB/API contracts, run on every commit
# E2E/System tests:  10% — test user journeys, run on every PR/deploy
```

## Best Practices

- Write the test name as a sentence: `test_should_throw_when_email_already_exists` — failing tests are self-documenting
- One assert per test concept — not necessarily one `assert` statement
- Follow the AAA pattern in every test: Arrange, Act, Assert
- Use `pytest.fixture(scope="session")` for expensive setup (DB containers); `scope="function"` for isolation
- Never test private methods directly — test behavior through the public API
- Use `freezegun` (Python) or `vi.useFakeTimers()` (Vitest) to control time in tests
- Avoid `sleep()` in tests — use event-based synchronization or polling with timeout
- Run tests in parallel: `pytest -n auto` (pytest-xdist) for unit tests; sequential for DB tests
- Mutation testing reveals untested paths: `mutmut run` (Python) or `stryker` (TypeScript)
- Aim for deterministic tests — no random data without a seed, no order dependency

## Models to Use

- **Default**: `claude-sonnet-4-5` — writing tests, mocking patterns, TDD guidance
- **Complex system design**: `claude-opus-4-5` — test architecture, property-based testing, mutation testing strategy
- **Boilerplate**: `claude-haiku-3-5` — generating test stubs, fixture factories, parametrize cases
