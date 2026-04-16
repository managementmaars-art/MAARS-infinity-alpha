---
name: "android-room-database"
description: "Model Room entities, DAOs, transactions, migrations, schema exports, and test-safe local persistence."
metadata:
  version: "0.1.0"
  category: "data-platform"
  tags: ["android", "room", "database", "migrations"]
  triggers:
    include: ["room database android", "dao query migration android", "room schema export", "transaction issue room", "android local database cleanup", "android-room-database skill", "room dao query migration", "room migration test android", "room auto migration android"]
    exclude: ["deeplink back stack", "compose semantics", "play rollout", "rxjava migration", "coroutines migration android"]
  owners: ["@android-agent-skills/maintainers"]
  test_targets: ["examples/orbittasks-compose", "examples/orbittasks-xml", "benchmarks/triggers.jsonl"]
---
# Android Room Database

## When To Use
- Use this skill when the request is about: room database android, dao query migration android, room schema export.
- Primary outcome: Model Room entities, DAOs, transactions, migrations, schema exports, and test-safe local persistence.
- Reach for this skill when the hard part is schema design, DAO queries, transactions, migrations, or Room testing. Hand off to `android-rxjava-to-coroutines-migration` only if the main work is reactive API migration rather than the database contract itself.
- Handoff skills when the scope expands:
- `android-local-persistence-datastore`
- `android-testing-unit`

## Workflow
1. Start with the persistence contract: entities, keys, indexes, relations, and whether the data is source-of-truth, cache, or offline-first state.
2. Model DAO access patterns explicitly, including transaction boundaries, query shape, paging, and invalidation behavior.
3. Plan schema evolution before changing entities: exported schemas, migration steps, auto-migration eligibility, and destructive-fallback policy.
4. Validate migration and query behavior with deterministic tests rather than assuming Room annotations are enough.
5. Hand off DataStore, sync, or reactive API questions only after the Room boundary is correct.

## Guardrails
- Export schemas and treat them as part of the contract, not optional tooling noise.
- Keep entities persistence-focused; map to domain/UI models instead of leaking table shape upward.
- Use explicit transactions for multi-step writes that must remain consistent.
- Test migrations against real old schemas before trusting them in release builds.

## Anti-Patterns
- Treating Room entities as the app's domain model everywhere.
- Editing schemas without exporting or validating migration paths.
- Writing broad `SELECT *` queries when the screen only needs a narrow projection.
- Collapsing database, sync, and reactive-stream migration problems into one undifferentiated task.

## Review Focus
- Entity keys, indexes, relations, and schema ownership.
- DAO query shape, transactions, and invalidation behavior.
- Migration safety, schema exports, and test coverage.
- Clear boundaries between Room models and higher-level app models.

## Examples
### Happy path
- Scenario: Persist task items and reminder flags with schema-aware entities.
- Command: `cd examples/orbittasks-compose && ./gradlew :app:testDebugUnitTest`

### Edge case
- Scenario: Recover from a failed schema change with an explicit migration path.
- Command: `python3 scripts/eval_triggers.py --skill android-room-database`

### Failure recovery
- Scenario: Keep Room requests separate from DataStore, networking, and modernization prompts.
- Command: `cd examples/orbittasks-xml && ./gradlew :app:testDebugUnitTest`

## Done Checklist
- Entities, DAOs, and transactions match the real persistence contract.
- Schema export and migration strategy are explicit.
- Query and migration tests cover the risky paths.
- Non-Room concerns are handed off instead of mixed into the database task.

## Official References
- [https://developer.android.com/training/data-storage/room](https://developer.android.com/training/data-storage/room)
- [https://developer.android.com/training/data-storage/room/migrating-db-versions](https://developer.android.com/training/data-storage/room/migrating-db-versions)
- [https://developer.android.com/training/data-storage/room/accessing-data](https://developer.android.com/training/data-storage/room/accessing-data)
- [https://developer.android.com/training/data-storage/room/prepopulate](https://developer.android.com/training/data-storage/room/prepopulate)
- [https://developer.android.com/topic/performance/sqlite-performance-best-practices](https://developer.android.com/topic/performance/sqlite-performance-best-practices)
