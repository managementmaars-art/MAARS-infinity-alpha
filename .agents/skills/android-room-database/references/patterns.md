# Android Room Database Patterns

## Selection Notes
- Category: `data-platform`
- Best fit when the request matches the trigger language in `SKILL.md` and the implementation focus is `Model Room entities, DAOs, transactions, migrations, schema exports, and test-safe local persistence.`
- Reach for neighboring skills only after this skill has framed the main problem.

## Review Sequence
- Schema design:
  entities, primary keys, foreign keys, indexes, and projections
- Access patterns:
  DAO shape, transactions, paging, and invalidation behavior
- Evolution:
  exported schemas, migration path, auto-migration eligibility, and destructive-fallback policy
- Verification:
  migration tests, query tests, and performance-sensitive projections

## Default Review Sequence
1. Define the persistence contract before touching annotations.
2. Separate entity shape from domain and UI models.
3. Make transactions and migration strategy explicit.
4. Validate with migration and query tests.
5. Hand off reactive API or sync concerns once the database boundary is stable.

## Best-Practice Notes
- Room works best when schema exports are versioned and reviewed.
- Query projections can be more stable and cheaper than broad entity reads.
- Auto migrations are useful, but only when the schema change fits their limits.
- Database migration and Rx/Flow migration are neighboring but different problems.

## Handoff Shortlist
- `android-local-persistence-datastore`
- `android-testing-unit`
