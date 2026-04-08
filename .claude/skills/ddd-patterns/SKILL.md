---
name: ddd-patterns
version: 1.0.0
description: Domain-Driven Design patterns in Python and TypeScript - aggregates, entities, value objects, bounded contexts, domain events, repositories, CQRS
tags: [ddd, domain-driven-design, architecture, python, typescript, cqrs, events, patterns]
---

# Domain-Driven Design (DDD) Patterns

Tactical and strategic patterns for modeling complex business domains.

## Core Building Blocks

| Concept | Identity | Mutable | Lifecycle |
|---------|----------|---------|-----------|
| **Entity** | Has unique ID | Yes | Managed independently |
| **Value Object** | Defined by attributes | No (immutable) | Owned by entity |
| **Aggregate** | Root entity | Yes | Transactional boundary |
| **Domain Service** | N/A | N/A | Stateless, handles cross-entity logic |
| **Repository** | N/A | N/A | Persists/retrieves aggregates |
| **Domain Event** | N/A | No | Records something that happened |

---

## Entities and Value Objects

```python
# Python implementation using dataclasses and ABC

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from abc import ABC, abstractmethod

# Base Entity - has identity, equality by ID
class Entity(ABC):
    def __init__(self, id: UUID):
        self._id = id
        self._domain_events: list["DomainEvent"] = []

    @property
    def id(self) -> UUID:
        return self._id

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def add_domain_event(self, event: "DomainEvent"):
        self._domain_events.append(event)

    def pull_domain_events(self) -> list["DomainEvent"]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

# Value Objects - immutable, equality by attributes
@dataclass(frozen=True)
class Money:
    amount: int   # store in cents to avoid floating point
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: int) -> "Money":
        return Money(self.amount * factor, self.currency)

    def __str__(self) -> str:
        return f"{self.amount / 100:.2f} {self.currency}"

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        import re
        if not re.match(r"^[\w.-]+@[\w.-]+\.\w+$", self.value):
            raise ValueError(f"Invalid email: {self.value}")

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    country: str
    postal_code: str
```

---

## Aggregates

```python
# Aggregate Root - enforces invariants, controls access to child entities
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

@dataclass
class OrderLine:
    """Child entity within Order aggregate."""
    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Money

    @property
    def total(self) -> Money:
        return self.unit_price.multiply(self.quantity)

class Order(Entity):
    """Order aggregate root - enforces all order business rules."""

    def __init__(
        self,
        id: UUID,
        customer_id: UUID,
        status: OrderStatus = OrderStatus.PENDING,
    ):
        super().__init__(id)
        self._customer_id = customer_id
        self._status = status
        self._lines: list[OrderLine] = []
        self._created_at = datetime.utcnow()

    # Factory method - encapsulates creation logic
    @classmethod
    def create(cls, customer_id: UUID) -> "Order":
        order = cls(id=uuid4(), customer_id=customer_id)
        order.add_domain_event(OrderCreated(order_id=order.id, customer_id=customer_id))
        return order

    def add_line(self, product_id: UUID, product_name: str, quantity: int, unit_price: Money):
        """Business rule: can only add lines to pending orders."""
        if self._status != OrderStatus.PENDING:
            raise ValueError("Cannot add lines to a non-pending order")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Check if product already in order, increase quantity
        existing = next((l for l in self._lines if l.product_id == product_id), None)
        if existing:
            self._lines.remove(existing)
            self._lines.append(OrderLine(
                id=existing.id,
                product_id=product_id,
                product_name=product_name,
                quantity=existing.quantity + quantity,
                unit_price=unit_price,
            ))
        else:
            self._lines.append(OrderLine(
                id=uuid4(),
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
            ))

    def confirm(self):
        if self._status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be confirmed")
        if not self._lines:
            raise ValueError("Cannot confirm an empty order")
        self._status = OrderStatus.CONFIRMED
        self.add_domain_event(OrderConfirmed(order_id=self.id, total=self.total))

    def cancel(self, reason: str):
        if self._status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise ValueError("Cannot cancel shipped or delivered orders")
        self._status = OrderStatus.CANCELLED
        self.add_domain_event(OrderCancelled(order_id=self.id, reason=reason))

    @property
    def total(self) -> Money:
        if not self._lines:
            return Money(0, "USD")
        totals = [line.total for line in self._lines]
        return Money(sum(t.amount for t in totals), totals[0].currency)

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def lines(self) -> list[OrderLine]:
        return list(self._lines)  # return copy to protect encapsulation
```

---

## Domain Events

```python
from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime

@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def event_type(self) -> str:
        return self.__class__.__name__

@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    order_id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default_factory=uuid4)

@dataclass(frozen=True)
class OrderConfirmed(DomainEvent):
    order_id: UUID = field(default_factory=uuid4)
    total: Money = field(default_factory=lambda: Money(0, "USD"))

@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: UUID = field(default_factory=uuid4)
    reason: str = ""

# Event dispatcher
from typing import Callable, Type, DefaultDict
from collections import defaultdict

EventHandler = Callable[[DomainEvent], None]

class DomainEventDispatcher:
    def __init__(self):
        self._handlers: DefaultDict[Type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler):
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: DomainEvent):
        for handler in self._handlers[type(event)]:
            await handler(event) if asyncio.iscoroutinefunction(handler) else handler(event)

    async def dispatch_all(self, events: list[DomainEvent]):
        for event in events:
            await self.dispatch(event)

# Handlers
dispatcher = DomainEventDispatcher()

async def on_order_confirmed(event: OrderConfirmed):
    await send_confirmation_email(event.order_id)
    await update_inventory(event.order_id)

dispatcher.subscribe(OrderConfirmed, on_order_confirmed)
```

---

## Repository Pattern

```python
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

# Repository interface (in domain layer)
class OrderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        ...

    @abstractmethod
    async def save(self, order: Order) -> None:
        ...

    @abstractmethod
    async def delete(self, order_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_by_customer(self, customer_id: UUID) -> list[Order]:
        ...

# SQLAlchemy implementation (in infrastructure layer)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class SQLOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession, dispatcher: DomainEventDispatcher):
        self._session = session
        self._dispatcher = dispatcher

    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        row = await self._session.get(OrderModel, order_id)
        return self._to_domain(row) if row else None

    async def save(self, order: Order) -> None:
        model = self._to_model(order)
        await self._session.merge(model)
        # Dispatch domain events after saving
        events = order.pull_domain_events()
        await self._dispatcher.dispatch_all(events)

    def _to_domain(self, model: "OrderModel") -> Order:
        order = Order.__new__(Order)
        order._id = model.id
        order._customer_id = model.customer_id
        order._status = OrderStatus(model.status)
        order._lines = [
            OrderLine(
                id=line.id,
                product_id=line.product_id,
                product_name=line.product_name,
                quantity=line.quantity,
                unit_price=Money(line.unit_price_cents, line.currency),
            )
            for line in model.lines
        ]
        order._created_at = model.created_at
        order._domain_events = []
        return order

    def _to_model(self, order: Order) -> "OrderModel":
        ...
```

---

## CQRS (Command Query Responsibility Segregation)

```python
# Commands - intent to change state
@dataclass
class CreateOrderCommand:
    customer_id: UUID
    lines: list[dict]  # [{product_id, quantity, unit_price}]

@dataclass
class ConfirmOrderCommand:
    order_id: UUID
    confirmed_by: UUID

# Command handlers
class OrderCommandHandler:
    def __init__(self, repo: OrderRepository):
        self._repo = repo

    async def handle_create_order(self, cmd: CreateOrderCommand) -> UUID:
        order = Order.create(customer_id=cmd.customer_id)
        for line in cmd.lines:
            order.add_line(
                product_id=line["product_id"],
                product_name=line["product_name"],
                quantity=line["quantity"],
                unit_price=Money(line["unit_price_cents"], line["currency"]),
            )
        await self._repo.save(order)
        return order.id

    async def handle_confirm_order(self, cmd: ConfirmOrderCommand) -> None:
        order = await self._repo.get_by_id(cmd.order_id)
        if not order:
            raise ValueError(f"Order {cmd.order_id} not found")
        order.confirm()
        await self._repo.save(order)

# Queries - optimized read models, bypass domain layer
class OrderReadModel(TypedDict):
    id: str
    customer_id: str
    status: str
    total_cents: int
    currency: str
    line_count: int
    created_at: str

class OrderQueryService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_order_summary(self, order_id: UUID) -> Optional[OrderReadModel]:
        # Direct SQL for read performance - no ORM overhead
        result = await self._session.execute(
            text("""
                SELECT o.id, o.customer_id, o.status, o.created_at,
                       COUNT(l.id) as line_count,
                       SUM(l.quantity * l.unit_price_cents) as total_cents,
                       MAX(l.currency) as currency
                FROM orders o
                LEFT JOIN order_lines l ON l.order_id = o.id
                WHERE o.id = :order_id
                GROUP BY o.id
            """),
            {"order_id": str(order_id)},
        )
        row = result.fetchone()
        return dict(row) if row else None

    async def list_customer_orders(
        self,
        customer_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[OrderReadModel]:
        ...
```

---

## Bounded Contexts in TypeScript

```typescript
// Each bounded context owns its own models and language

// ORDER context
namespace OrderContext {
  export interface Order {
    id: string;
    customerId: string;
    status: "pending" | "confirmed" | "shipped" | "delivered" | "cancelled";
    lines: OrderLine[];
    totalCents: number;
  }

  export interface OrderLine {
    productId: string;
    quantity: number;
    unitPriceCents: number;
  }

  export class OrderService {
    constructor(private repo: OrderRepository) {}

    async createOrder(customerId: string, lines: OrderLine[]): Promise<Order> {
      // Order context logic
    }
  }
}

// SHIPPING context - has its own view of an "order" (shipment)
namespace ShippingContext {
  export interface Shipment {
    id: string;
    orderId: string;       // reference by ID only, not full object
    destinationAddress: Address;
    status: "preparing" | "in_transit" | "delivered";
    trackingNumber?: string;
  }

  // Anti-Corruption Layer: translates from Order context events
  export class OrderEventTranslator {
    translate(event: OrderContext.OrderConfirmedEvent): CreateShipmentCommand {
      return {
        orderId: event.orderId,
        destinationAddress: event.shippingAddress,
        items: event.lines.map(l => ({
          sku: l.productId,
          qty: l.quantity,
        })),
      };
    }
  }
}

// Context Map: how contexts communicate
// - Published Language: shared events (OrderConfirmed, OrderCancelled)
// - Anti-Corruption Layer: ShippingContext translates from OrderContext
// - Open Host Service: OrderContext exposes read API for other contexts
```

---

## Best Practices

- **Keep aggregates small**: each aggregate is a transactional boundary; large aggregates = lock contention
- **Reference other aggregates by ID only**: never hold a direct object reference across aggregate roots
- **Enforce invariants in the domain, not the service layer**: business rules belong on the entity/aggregate
- **Value objects are your friends**: replace primitive obsession with rich types (`Money`, `Email`, `PhoneNumber`)
- **Domain events decouple bounded contexts**: use async events between contexts, not direct calls
- **Repository interface in domain, implementation in infrastructure**: domain layer has zero infrastructure dependencies
- **CQRS is not required but fits well**: separate write model (aggregates) from read model (optimized SQL/views)
- **Ubiquitous language matters**: code should use the same terms as domain experts use in conversation
- **Bounded contexts over one giant model**: resist the urge to share entities across contexts

## Models to Use

- **claude-opus-4-5**: Strategic DDD design sessions, defining bounded contexts, designing aggregate boundaries, complex domain modeling
- **claude-sonnet-4-5**: Implementing entities, value objects, repositories, domain event handlers
- **claude-haiku-3-5**: Generating boilerplate value objects, simple CRUD repositories
