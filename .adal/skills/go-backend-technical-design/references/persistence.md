# Persistence Design Notes

Use when technical design includes storage changes.

## Topics to specify

- schema or table ownership
- primary access patterns
- transaction boundary
- locking strategy
- retention and audit needs
- migration rollout plan

## Decision pressure

- Strong consistency needed: favor narrow local transactions
- High fan-out side effects: consider outbox pattern
- Heavy reads with light writes: add read model only if justified
