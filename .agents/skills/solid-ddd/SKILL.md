---
name: solid-ddd
description: >
  Language-agnostic SOLID principles and DDD tactical patterns.
  Trigger: Always loaded for non-documentation code changes via sdd-apply.
format: reference
---

# solid-ddd

> Language-agnostic catalog of SOLID design principles and Domain-Driven Design tactical patterns with concrete do/don't examples.

**Triggers**: Always loaded for non-documentation code changes. Load when writing or reviewing any class, module, domain object, service, or repository. Applicable across all languages and frameworks.

---

## Patterns

### SOLID Principles

---

#### SRP — Single Responsibility Principle

A class, module, or function has exactly one reason to change. One unit = one concern.

**DON'T** — one class handles both order persistence and email notification:

```typescript
// [Illustrative — TypeScript]
class OrderService {
  save(order: Order): void { /* writes to DB */ }
  sendConfirmationEmail(order: Order): void { /* sends email */ }
  calculateDiscount(order: Order): number { /* discount logic */ }
}
```

**DO** — each class owns one responsibility:

```typescript
// [Illustrative — TypeScript]
class OrderRepository { save(order: Order): void { /* DB only */ } }
class OrderNotifier { sendConfirmation(order: Order): void { /* email only */ } }
class DiscountCalculator { calculate(order: Order): number { /* pricing only */ } }
```

**Signal — SRP violated**: the class has multiple unrelated reasons to change (schema change AND email template change affect the same file).

---

#### OCP — Open/Closed Principle

A unit is open for extension, closed for modification. Add behavior by adding code, not by editing existing code.

**DON'T** — every new payment method requires editing the same function:

```typescript
// [Illustrative — TypeScript]
function processPayment(type: string, amount: number) {
  if (type === 'credit') { /* ... */ }
  else if (type === 'paypal') { /* ... */ }
  // Adding 'crypto' forces editing this function
}
```

**DO** — new behavior is added by adding a new implementation:

```typescript
// [Illustrative — TypeScript]
interface PaymentProcessor { process(amount: number): void; }
class CreditProcessor implements PaymentProcessor { process(amount) { /* ... */ } }
class PaypalProcessor implements PaymentProcessor { process(amount) { /* ... */ } }
// Adding crypto: create CryptoProcessor — no existing code touched
```

**Signal — OCP violated**: adding a new variant requires touching a central switch/if chain that already exists.

---

#### LSP — Liskov Substitution Principle

Subtypes must be substitutable for their base types without altering correctness. A subclass must honor the contract of its parent.

**DON'T** — subclass breaks the parent contract by throwing where parent succeeds:

```typescript
// [Illustrative — TypeScript]
class Rectangle { setWidth(w: number) { this.width = w; } }
class Square extends Rectangle {
  setWidth(w: number) { this.width = w; this.height = w; } // Breaks area contract
}
```

**DO** — prefer composition or a shared interface with separate implementations:

```typescript
// [Illustrative — TypeScript]
interface Shape { area(): number; }
class Rectangle implements Shape { area() { return this.width * this.height; } }
class Square implements Shape { area() { return this.side * this.side; } }
```

**Signal — LSP violated**: calling code needs to check the concrete type before using the abstraction (`if (shape instanceof Square)`).

---

#### ISP — Interface Segregation Principle

Clients must not be forced to depend on methods they do not use. Prefer narrow, focused interfaces over fat ones.

**DON'T** — one fat interface forces every implementor to stub unused methods:

```typescript
// [Illustrative — TypeScript]
interface Worker {
  work(): void;
  eat(): void;   // Robots don't eat
  sleep(): void; // Robots don't sleep
}
class RobotWorker implements Worker {
  work() { /* real logic */ }
  eat() { throw new Error('Not supported'); }   // forced no-op
  sleep() { throw new Error('Not supported'); } // forced no-op
}
```

**DO** — split into narrow interfaces; each class implements only what it needs:

```typescript
// [Illustrative — TypeScript]
interface Workable { work(): void; }
interface Feedable { eat(): void; sleep(): void; }
class HumanWorker implements Workable, Feedable { /* all methods real */ }
class RobotWorker implements Workable { work() { /* only real method */ } }
```

**Signal — ISP violated**: an implementor has one or more methods that throw `NotImplementedException`, return empty, or are no-ops.

---

#### DIP — Dependency Inversion Principle

High-level modules must not depend on low-level modules. Both depend on abstractions. Abstractions must not depend on details.

**DON'T** — high-level service directly instantiates a concrete repository:

```typescript
// [Illustrative — TypeScript]
class OrderService {
  private repo = new PostgresOrderRepository(); // concrete dependency
  placeOrder(order: Order) { this.repo.save(order); }
}
```

**DO** — high-level service depends on an abstraction; the concrete class is injected:

```typescript
// [Illustrative — TypeScript]
interface OrderRepository { save(order: Order): void; }
class OrderService {
  constructor(private repo: OrderRepository) {} // depends on abstraction
  placeOrder(order: Order) { this.repo.save(order); }
}
// Caller injects: new OrderService(new PostgresOrderRepository())
```

**Signal — DIP violated**: `new ConcreteClass()` inside a service constructor or method body with no injection seam.

---

### DDD Tactical Patterns

---

#### Entity

An object defined by its identity, not its attributes. Two entities with the same ID are the same entity even if their data differs.

- **Has**: a stable, unique identifier (ID) that persists across state changes.
- **Behavior**: encapsulates domain logic relevant to its lifecycle.
- **Distinguishing signal vs. Value Object**: ask "does it matter which one it is?" — if yes, it is an Entity.

```
// [Pseudocode]
Entity Order { id: OrderId; status: OrderStatus; items: Item[] }
// Two Orders with id=42 are the same order even if status changed
```

---

#### Value Object

An object defined entirely by its attributes. No identity. Immutable. Equality is structural.

- **Has**: no ID field. Equality is based on all attribute values.
- **Immutable**: replace, never mutate. Operations return new instances.
- **Distinguishing signal vs. Entity**: ask "does it matter which one it is?" — if no, it is a Value Object.

```
// [Pseudocode]
ValueObject Money { amount: Decimal; currency: Currency }
// Money(10, USD) == Money(10, USD) — two instances are equal by value
```

---

#### Aggregate

A cluster of domain objects (one Entity as root + optional child objects) treated as a single unit for data changes. All access to internal objects goes through the Aggregate Root.

- **Aggregate Root** is the only public entry point. External code holds a reference only to the root.
- **Invariants** that span multiple child objects are enforced by the root.
- **Transactions** should not span multiple Aggregates — each Aggregate is a consistency boundary.

```
// [Pseudocode]
Aggregate Order (root) {
  addItem(product, qty) // enforces max-items invariant
  removeItem(itemId)
  confirm()             // guards: status must be DRAFT
}
// External code: order.addItem(…) — never order.items.push(…) directly
```

---

#### Repository

An abstraction that provides collection-like access to Aggregates. Hides the persistence mechanism from the domain layer.

- **Interface** lives in the domain layer. **Implementation** lives in the infrastructure layer (DIP applied).
- Methods are domain-language methods (`findById`, `findByCustomer`, `save`) — not SQL or ORM calls.
- One Repository per Aggregate Root — not per entity or table.

```
// [Pseudocode]
interface OrderRepository {
  findById(id: OrderId): Order | null
  findByCustomer(customerId: CustomerId): Order[]
  save(order: Order): void
}
```

---

#### Domain Service

A stateless operation that belongs to the domain but does not naturally fit inside a single Entity or Value Object.

- **Stateless**: no mutable fields; takes input, returns output or raises domain events.
- **Belongs in the domain layer**: contains business rules, not application orchestration.
- **Use when**: the operation involves multiple Aggregates or the logic does not belong to any single object.

```
// [Pseudocode]
DomainService TransferService {
  transfer(from: Account, to: Account, amount: Money): void {
    from.debit(amount)
    to.credit(amount)
    // Invariant: total money in system unchanged
  }
}
```

---

#### Application Service

Orchestrates domain objects and services to fulfill a single use case. Lives in the application layer, not the domain layer.

- **Thin**: no business logic — only coordination (load, call domain, save, emit events).
- **Transaction boundary**: one use case = one transaction (typically).
- **Calls domain services and repositories** — never bypasses the domain to manipulate entities directly.

```
// [Pseudocode]
ApplicationService PlaceOrderUseCase {
  execute(cmd: PlaceOrderCommand): OrderId {
    customer = customerRepo.findById(cmd.customerId)
    order = Order.create(customer, cmd.items)   // domain logic in Order
    orderRepo.save(order)
    eventBus.publish(order.domainEvents())
    return order.id
  }
}
```

---

#### Domain Event

A record that something meaningful happened in the domain. Published by Aggregates; consumed by other parts of the system.

- **Immutable**: represents a past fact — never modified after creation.
- **Named in past tense**: `OrderPlaced`, `PaymentReceived`, `InventoryDepleted`.
- **Carries only what happened**: not a command, not a query — a fact with a timestamp and relevant data.

```
// [Pseudocode]
DomainEvent OrderPlaced {
  orderId: OrderId
  customerId: CustomerId
  occurredAt: Timestamp
}
```

---

## Anti-Patterns

---

### God Class

**What it is**: one class that accumulates responsibilities across multiple unrelated concerns — persistence, business rules, HTTP handling, formatting, notification, etc.

**Detection signals**:
- Class has > 10 public methods spanning unrelated concerns.
- Multiple unrelated reasons to change (DB schema change AND email template change both affect this class).
- Class name ends in `Manager`, `Handler`, `Processor`, or `Helper` and does everything.

**Why it is a problem**: violates SRP. Any change risks breaking unrelated functionality. Testing requires setting up the entire class even for a small feature.

**Corrective direction**: identify distinct responsibilities, extract each into a focused class. Apply the "one reason to change" test to each extract.

---

### Anemic Domain Model

**What it is**: domain objects (entities, aggregates) are pure data containers — they have fields and getters/setters but no behavior. All business logic lives in service classes.

**Detection signals**:
- Entity classes contain only fields, constructors, and getters/setters.
- Service classes contain all conditionals, calculations, and state transitions that relate to entity data.
- To understand business rules you must read the service, not the entity.

**Why it is a problem**: violates DDD. Domain logic leaks into the application layer, becomes scattered across services, and is hard to find, test, or enforce as invariants.

**Corrective direction**: move business behavior (state transitions, invariant enforcement, calculations) into the entity or value object that owns the data.

---

### Service as God Object

**What it is**: a single application service (or domain service) that directly orchestrates all domain logic with no delegation — it reads entities, applies all business rules inline, and writes results.

**Detection signals**:
- Service method is > 50 lines of business logic with no calls to domain object methods.
- Service knows the internal structure of multiple unrelated aggregates.
- Removing one service method would break unrelated features.

**Why it is a problem**: combines the God Class problem with the Anemic Domain Model — SRP is violated at the service level, and domain objects remain empty data bags.

**Corrective direction**: delegate business logic to domain objects and domain services. The application service should orchestrate (load → call domain → persist → publish) without containing rules itself.

---

## Rules

- Apply SRP before adding a second responsibility to any class, module, or function — extract first, then implement.
- Apply DIP at every layer boundary: domain → infrastructure, application → domain. Never instantiate a concrete dependency inside a high-level class.
- Value Objects MUST be immutable. Mutation returns a new instance; it never modifies `this`.
- Aggregate Roots are the sole entry points for state changes on their cluster. No direct mutation of child objects from outside the Aggregate.
- Repositories are defined as interfaces in the domain layer. Concrete implementations belong in the infrastructure layer.
- Application Services MUST be thin orchestrators. Business logic inside an Application Service is a violation — move it to the domain object or Domain Service.
- Domain Events MUST be named in past tense and treated as immutable facts.
- Code examples in this skill are illustrative only (labeled with language). They are not production templates.
