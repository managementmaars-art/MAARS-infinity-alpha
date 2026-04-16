---
name: arch-domain-driven
cluster: se-architecture
description: "DDD: bounded contexts, aggregates, entities, value objects, domain events, ubiquitous language"
tags: ["ddd","domain","bounded-context","architecture"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "domain driven design bounded context aggregate entity value object"
---

## Purpose

This skill implements Domain-Driven Design (DDD) principles to structure code effectively. It helps generate and manage bounded contexts, aggregates, entities, value objects, and domain events, while promoting ubiquitous language for better team alignment.

## When to Use

Use this skill for complex applications with rich domain logic, such as e-commerce platforms or financial systems, where clear boundaries reduce coupling. Apply it during architecture design phases to avoid monolithic codebases, especially when dealing with multiple subdomains or legacy integrations.

## Key Capabilities

- Generate bounded contexts with isolated modules for specific domains.
- Define aggregates as clusters of entities with a single root for transaction consistency.
- Create entities with identity and value objects for immutable data.
- Handle domain events to trigger reactions, like publishing to event buses.
- Enforce ubiquitous language by embedding domain terms into code and configurations.

## Usage Patterns

Always begin by mapping the domain to identify bounded contexts. Use the skill to scaffold structures, then refine aggregates within contexts. For example, integrate with CI/CD by running generation commands in build scripts. Test incrementally: generate an entity, add it to an aggregate, and verify invariants. Avoid over-modeling by limiting contexts to high-cohesion areas, and use events for cross-context communication.

## Common Commands/API

Interact via OpenClaw's CLI or REST API. Authentication requires setting `$OPENCLAW_API_KEY` in your environment.

CLI Commands:
- Generate a bounded context: `openclaw ddd generate-context --name MyContext --description "User management" --language python`
  This creates a directory like `./my_context/` with subfolders for aggregates and entities.
- Define an aggregate: `openclaw ddd generate-aggregate --context MyContext --name AccountAggregate --root EntityName --invariants "balance > 0"`
  Adds files like `account_aggregate.py` with the root entity and invariant checks.
- Create an entity: `openclaw ddd generate-entity --context MyContext --name UserEntity --properties "id:UUID, name:String"`
- Handle domain events: `openclaw ddd generate-event --context MyContext --name UserCreatedEvent --payload "user_id:UUID"`

API Endpoints:
- POST /api/v1/ddd/contexts with JSON body: `{"name": "MyContext", "description": "User management", "language": "python"}`
  Requires header: `Authorization: Bearer $OPENCLAW_API_KEY`
- POST /api/v1/ddd/aggregates with body: `{"context": "MyContext", "name": "AccountAggregate", "root": "Account", "invariants": ["balance > 0"]}`

Config Formats:
Use YAML for configurations, e.g., in a `.openclaw/config.yml` file:
```
ddd:
  default_language: python
  contexts:
    - name: MyContext
      description: User management
```

Code Snippets:
1. Generate and use a context in Python:
```python
import openclaw.ddd as oc
oc.generate_context(name="MyContext", description="User management")
context = oc.load_context("MyContext")
```
2. Define an aggregate in code:
```python
from openclaw.ddd import Aggregate
class AccountAggregate(Aggregate):
    def __init__(self, account_id):
        self.root = Entity(account_id)  # Assuming Entity is generated
```

## Integration Notes

Integrate by exporting `$OPENCLAW_API_KEY=your_api_key` before CLI/API calls. Add OpenClaw as a dependency in your project (e.g., `pip install openclaw` for Python). For IDEs, use plugins like VS Code extensions to trigger commands via keyboard shortcuts, such as binding `openclaw ddd generate-context` to a key. Chain with other tools: pipe CLI output to Git for auto-commits, or use webhooks to call API endpoints from services like Jenkins. Ensure compatibility by specifying language flags (e.g., `--language java`) to match your stack.

## Error Handling

Always check CLI exit codes; non-zero indicates failure (e.g., `if [ $? -ne 0 ]; then echo "Error: Invalid input"; fi`). For API calls, handle HTTP errors like 400 for validation failures or 401 for auth issues by checking response status. In code, wrap operations in try-except blocks:
```python
try:
    oc.generate_aggregate(context="MyContext", name="InvalidAggregate", invariants=["invalid"])
except oc.DDDValidationError as e:  # Specific error for invariant checks
    print(f"Error: {e.message} - Fix invariants and retry")
except oc.AuthError as e:  # For $OPENCLAW_API_KEY issues
    print("Error: Authentication failed - Set $OPENCLAW_API_KEY")
```
Validate inputs upfront, e.g., ensure context names are alphanumeric via CLI flags like `--validate`.

## Concrete Usage Examples

1. Building a bounded context for an e-commerce order system:
   First, identify the domain: orders involve aggregates like Order and LineItems. Run: `openclaw ddd generate-context --name OrderContext --description "Manages orders" --modules orders,items`
   This outputs: `./order_context/orders.py` and `./order_context/items.py`. Next, add an aggregate: `openclaw ddd generate-aggregate --context OrderContext --name OrderAggregate --root Order --invariants "total > 0"`
   In code, import and use: `from order_context.aggregates import OrderAggregate; order = OrderAggregate(order_id=1)`

2. Handling domain events in a user registration flow:
   Start by generating the event: `openclaw ddd generate-event --context UserContext --name UserRegisteredEvent --payload "user_id:UUID, email:String"`
   This creates `./user_context/events/user_registered_event.py`. Then, trigger it via API: `curl -H "Authorization: Bearer $OPENCLAW_API_KEY" -X POST /api/v1/ddd/events -d '{"context": "UserContext", "event": "UserRegisteredEvent", "payload": {"user_id": "123"}}'`
   In your application code: `oc.publish_event(context="UserContext", event="UserRegisteredEvent", payload={"user_id": "123"})` to notify other services.

## Graph Relationships

- Related to cluster: se-architecture (e.g., shares dependencies with other architecture skills).
- Connected via tags: ddd (links to domain modeling tools), domain (connects to entity management skills), bounded-context (relates to microservices patterns), architecture (ties into se-architecture cluster for broader design tools).
