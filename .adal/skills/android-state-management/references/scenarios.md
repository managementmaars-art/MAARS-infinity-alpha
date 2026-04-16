# Android State Management Runnable Scenarios

## Happy path
- Goal: Drive the Compose task board from a single immutable screen state.
- Command: `cd examples/orbittasks-compose && ./gradlew :app:testDebugUnitTest`

## Edge case
- Goal: Represent permission denied and sync failed states explicitly in the XML fixture.
- Command: `cd examples/orbittasks-xml && ./gradlew :app:testDebugUnitTest`

## Failure recovery
- Goal: Separate state requests from coroutines, navigation, and UI validation prompts.
- Command: `python3 scripts/eval_triggers.py --skill android-state-management`
