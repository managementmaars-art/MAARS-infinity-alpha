---
name: "android-rxjava-to-coroutines-migration"
description: "Migrate Android RxJava code to Kotlin coroutines and Flow with safe lifecycle-aware replacements."
metadata:
  version: "0.1.0"
  category: "legacy-rescue"
  tags: ["android", "rxjava", "coroutines", "flow", "migration"]
  triggers:
    include: ["rxjava to coroutines android", "observable to flow android", "replace composite disposable android", "single maybe completable migration android", "scheduler to dispatcher android"]
    exclude: ["room schema only", "play store release only", "xml constraintlayout only"]
  owners: ["@android-agent-skills/maintainers"]
  test_targets: ["examples/fixtures/rxjava-legacy-sample", "benchmarks/triggers.jsonl"]
---
# Android RxJava To Coroutines Migration

## When To Use
- Use this skill when the request is about: rxjava to coroutines android, observable to flow android, replace composite disposable android.
- Primary outcome: Migrate Android RxJava code to Kotlin coroutines and Flow with safe lifecycle-aware replacements.
- Reach for this skill when the codebase still exposes `Single`, `Observable`, schedulers, or disposables and the goal is to move to `suspend`, `Flow`, `StateFlow`, or `SharedFlow`.
- Read `references/patterns.md` for the type-mapping matrix and operator red-flag checklist.
- Read `references/scenarios.md` for staged migration and inventory-first workflows.
- Handoff skills when the scope expands:
- `android-modernization-upgrade`
- `android-coroutines-flow`

## Workflow
1. Scan the codebase for RxJava imports, base types, subjects, and scheduler usage before changing any API surface.
2. Classify each usage as one-shot work, stream work, hot state, hot events, callback bridging, or backpressure-sensitive work.
3. Replace repository and domain APIs first, then move UI-layer subscriptions to lifecycle-aware collection.
4. Rewrite scheduler and disposable management as dispatcher, scope, structured-concurrency ownership, and lifecycle-aware collection such as `repeatOnLifecycle`.
5. Leave a checklist for ambiguous operators or custom bridges instead of pretending every chain can be auto-converted safely.

## Guardrails
- Prefer `suspend` functions for one-shot work and `Flow` for streams; do not force everything into `Flow`.
- Preserve lifecycle ownership when replacing `CompositeDisposable` and manual subscription chains.
- Call out operator semantics that need human review, especially `flatMap`, `switchMap`, replay, and threading assumptions.
- Preserve hot-state and replay semantics explicitly with `StateFlow`, `SharedFlow`, `shareIn`, or `stateIn` instead of assuming cold `Flow` is equivalent.
- Treat migration as behavior-preserving refactor work, not a chance to redesign unrelated business logic.

## Anti-Patterns
- Converting every Rx type to `Flow` even when a `suspend` function is the better match.
- Dropping replay, buffering, or hot-stream semantics during subject migration.
- Leaving `observeOn` and `subscribeOn` assumptions undocumented after moving to dispatchers.
- Rewriting repository, ViewModel, and UI layers all at once with no staged verification.

## Review Focus
- Type mapping: `Single`, `Maybe`, `Completable`, `Observable`, `Flowable`, and Subjects.
- Hot vs cold semantics, replay behavior, and backpressure expectations.
- Dispatcher ownership, `viewModelScope`, and lifecycle collection.
- Testing fallout for coroutine timing, cancellation, and stream assertions.

## Examples
### Happy path
- Scenario: Scan a legacy RxJava sample and generate a migration checklist for repositories, ViewModels, and UI subscriptions.
- Command: `bash skills/android-rxjava-to-coroutines-migration/scripts/run_examples.sh`

### Edge case
- Scenario: Inventory subjects, disposables, and scheduler usage before converting state or one-off events.
- Command: `python3 skills/android-rxjava-to-coroutines-migration/scripts/scan_rxjava_usage.py examples/fixtures/rxjava-legacy-sample --json`

### Failure recovery
- Scenario: Produce a deterministic checklist when parts of the chain still need manual operator review.
- Command: `python3 skills/android-rxjava-to-coroutines-migration/scripts/generate_migration_checklist.py examples/fixtures/rxjava-legacy-sample`

## Done Checklist
- RxJava types and operators were inventoried before code changes were proposed.
- One-shot APIs, streams, hot state, and hot events are mapped to the right coroutine primitives.
- Lifecycle ownership and dispatcher assumptions are explicit.
- Ambiguous operators or bridging cases are recorded as manual follow-up work.

## Official References
- [https://developer.android.com/kotlin/coroutines](https://developer.android.com/kotlin/coroutines)
- [https://developer.android.com/kotlin/flow](https://developer.android.com/kotlin/flow)
- [https://developer.android.com/kotlin/coroutines/coroutines-best-practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)
- [https://developer.android.com/topic/libraries/architecture/coroutines](https://developer.android.com/topic/libraries/architecture/coroutines)
- [https://developer.android.com/kotlin/flow/stateflow-and-sharedflow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [https://kotlinlang.org/docs/flow.html](https://kotlinlang.org/docs/flow.html)
