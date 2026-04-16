# Android RxJava To Coroutines Migration Runnable Scenarios

## Happy path
- Goal: Scan the legacy RxJava sample and emit a coroutine migration checklist.
- Command: `bash skills/android-rxjava-to-coroutines-migration/scripts/run_examples.sh`

## Edge case
- Goal: Classify `Single`, `Observable`, schedulers, `CompositeDisposable`, and hot-stream semantics before touching the UI layer.
- Command: `python3 skills/android-rxjava-to-coroutines-migration/scripts/scan_rxjava_usage.py examples/fixtures/rxjava-legacy-sample --json`

## Failure recovery
- Goal: Generate a handoff checklist for operators and subjects that need human review.
- Command: `python3 skills/android-rxjava-to-coroutines-migration/scripts/generate_migration_checklist.py examples/fixtures/rxjava-legacy-sample --json`
