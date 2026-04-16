# Logic Placement Guide

Where should a given piece of logic live — in the **entity** or in the **use case**?

## Decision Table

| Situation | Entity | Use Case |
|-----------|:------:|:--------:|
| Validates an invariant on the entity's own data | ✅ | |
| Represents a state transition owned by the entity (`publish()`, `delete()`) | ✅ | |
| Computes a value derivable purely from the entity's own fields | ✅ | |
| Behaviour shared by multiple use cases | ✅ | |
| Orchestrates multiple entities, repos, or services | | ✅ |
| Loads external data not owned by the entity | | ✅ |
| Crosses aggregate boundaries | | ✅ |
| Performs auth checks or transactional coordination | | ✅ |

## Examples

**Entity** — `entity.publish()` sets `published_at` and validates that all required fields are
filled. Pure domain logic: no IO, no dependencies, usable by any use case that needs to publish.

**Use case** — `PublishArticle` loads the entity by ID, verifies the actor's permission via the
auth service, calls `entity.publish()`, persists the result, and enqueues an email notification.
The orchestration and side-effects live here; the invariant lives in the entity.

## Rule of Thumb

> If the operation can be expressed purely in terms of the entity's own fields, push it to the
> entity. As soon as it needs to load or save something, it belongs in the use case.
