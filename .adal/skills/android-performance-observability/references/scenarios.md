# Android Performance Observability Runnable Scenarios

## Happy path
- Goal: Find the current profiling and benchmark hooks before recommending a measurement plan.
- Command: `rg -n "baseline|macrobenchmark|profileable|JankStats|Trace|Perfetto" .`

## Edge case
- Goal: Verify the Compose fixture still builds in a release-like path before discussing startup or rendering numbers.
- Command: `cd examples/orbittasks-compose && ./gradlew :app:assembleDebug`

## Failure recovery
- Goal: Keep observability requests distinct from Compose-only tuning or release automation.
- Command: `python3 scripts/eval_triggers.py --skill android-performance-observability`
