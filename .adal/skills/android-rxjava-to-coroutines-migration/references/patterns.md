# Android RxJava To Coroutines Migration Patterns

## Selection Notes
- Category: `legacy-rescue`
- Best fit when a codebase still exposes RxJava types, subjects, schedulers, or disposables and needs a staged migration.
- Hand off to `android-coroutines-flow` once the request stops being migration work and becomes coroutine architecture work.

## Type Mapping Matrix
- `Single<T>`:
  Usually `suspend fun ...: T`
- `Maybe<T>`:
  Usually `suspend fun ...: T?` or a sealed result when absence is semantically important
- `Completable`:
  Usually `suspend fun ...: Unit`
- `Observable<T>`:
  Usually `Flow<T>` when it is a stream, but check whether it is really hot or cold
- `Flowable<T>`:
  Usually `Flow<T>` plus explicit buffering/backpressure review
- `BehaviorSubject<T>`:
  Usually `MutableStateFlow<T>`
- `PublishSubject<T>`:
  Usually `MutableSharedFlow<T>` with replay and buffer rules chosen explicitly

## Default Review Sequence
1. Inventory imports, base types, subjects, schedulers, and disposables.
2. Classify hot vs cold and one-shot vs streaming behavior before mapping.
3. Replace subscription ownership with lifecycle-aware coroutine scopes.
4. Flag ambiguous operators for manual review.
5. Verify behavior on a focused sample before broader rollout.

## Operator Red Flags
- `flatMap`, `switchMap`, `concatMap`, and custom transformers can change cancellation or ordering semantics during migration.
- Time-based operators need an explicit coroutine testing plan.
- `share`, `replay`, `publish`, and ref-count behavior often need `shareIn` or `stateIn`, not plain `Flow`.
- Callback bridges are often best expressed with `callbackFlow` instead of ad-hoc channels.

## Handoff Shortlist
- `android-modernization-upgrade`
- `android-coroutines-flow`
