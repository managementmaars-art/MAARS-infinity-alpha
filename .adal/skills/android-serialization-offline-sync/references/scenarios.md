# Android Serialization Offline Sync Runnable Scenarios

## Happy path
- Goal: Sync local task edits to a remote model with explicit mapping.
- Command: `cd examples/orbittasks-compose && ./gradlew :app:testDebugUnitTest`

## Edge case
- Goal: Recover when remote and local timestamps disagree after offline edits.
- Command: `cd examples/orbittasks-xml && ./gradlew :app:testDebugUnitTest`

## Failure recovery
- Goal: Keep sync/serialization work separate from pure networking or Room-only requests.
- Command: `python3 scripts/eval_triggers.py --skill android-serialization-offline-sync`
