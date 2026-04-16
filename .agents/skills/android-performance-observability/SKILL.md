---
name: "android-performance-observability"
description: "Measure startup, rendering, memory, jank, vitals, logs, and crash signals for Android apps with actionable traces."
metadata:
  version: "0.1.0"
  category: "quality-release"
  tags: ["android", "performance", "observability", "profiling"]
  triggers:
    include: ["android performance profiling", "baseline profile or macrobenchmark", "app startup issue android", "observability for android app", "trace jank crash android"]
    exclude: ["permission request only", "retrofit dto change only", "fragment transaction only"]
  owners: ["@android-agent-skills/maintainers"]
  test_targets: ["examples/orbittasks-compose", "examples/orbittasks-xml", "benchmarks/triggers.jsonl"]
---
# Android Performance Observability

## When To Use
- Use this skill when the request is about: android performance profiling, baseline profile or macrobenchmark, app startup issue android.
- Primary outcome: Measure startup, rendering, memory, jank, vitals, logs, and crash signals for Android apps with actionable traces.
- Read `references/patterns.md` when you need the measurement ladder for startup, jank, traces, and production signals.
- Read `references/scenarios.md` for repeatable profiling and trace-oriented entry points.
- Handoff skills when the scope expands:
- `android-compose-performance`
- `android-ci-cd-release-playstore`

## Workflow
1. Classify the symptom before choosing tools: cold start, warm start, frame/jank, scrolling, memory, ANR, crash, battery, or production vitals drift.
2. Measure on release-like builds and physical devices whenever possible; avoid debugging from debug-only traces or profile-unfriendly builds.
3. Pick the smallest tool that answers the question: Macrobenchmark for startup/scroll numbers, Baseline Profiles for ahead-of-time optimization, Perfetto/System Tracing for deep traces, JankStats or FrameMetrics for frame quality, and Play Vitals for field evidence.
4. Change one thing at a time, then compare before and after traces or benchmark outputs instead of stacking multiple optimizations blindly.
5. Hand off UI-specific rendering changes or release rollouts only after the measurement surface is stable and the bottleneck is evidenced.

## Guardrails
- Treat benchmarks, traces, and vitals as different evidence sources with different noise profiles; do not mix them casually.
- Prefer reproducible release-build measurements over debug-build intuition.
- Tie optimizations back to user-facing metrics such as startup time, frame pacing, ANRs, or battery impact.
- Keep the profiling setup stable enough that regressions are attributable to code changes instead of device or environment churn.

## Anti-Patterns
- Chasing micro-optimizations before identifying whether the problem is startup, rendering, I/O, or field reliability.
- Reading one noisy trace and presenting the result as settled fact.
- Measuring debug builds and assuming the same behavior in production.
- Adding Baseline Profiles or macrobenchmarks without checking whether the target path is stable enough to compare.

## Review Focus
- Startup: cold and warm launch, expensive initialization, and Baseline Profile coverage.
- Rendering: jank, skipped frames, Compose or View invalidation churn, and long main-thread work.
- Memory and reliability: allocations, leaks, ANRs, crashes, and Play Vitals trends.
- Evidence quality: repeatable commands, release-like variants, and documented before/after comparisons.

## Examples
### Happy path
- Scenario: Audit the repo for profiling surfaces and benchmark-related hooks before proposing a measurement plan.
- Command: `rg -n "baseline|macrobenchmark|profileable|JankStats|Trace|Perfetto" .`

### Edge case
- Scenario: Keep startup and rendering investigations grounded in repeatable release-like builds.
- Command: `cd examples/orbittasks-compose && ./gradlew :app:assembleDebug`

### Failure recovery
- Scenario: Keep observability requests distinct from Compose-only tuning or release automation.
- Command: `python3 scripts/eval_triggers.py --skill android-performance-observability`

## Done Checklist
- The bottleneck is classified and tied to an evidence source that can be re-run.
- The chosen tools match the symptom instead of duplicating noisy measurements.
- Before/after comparisons are explicit for any recommended optimization.
- UI-only or release-only work is separated from measurement and tracing.

## Official References
- [https://developer.android.com/studio/profile/overview](https://developer.android.com/studio/profile/overview)
- [https://developer.android.com/topic/performance/vitals](https://developer.android.com/topic/performance/vitals)
- [https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview)
- [https://developer.android.com/topic/performance/benchmarking/macrobenchmark-metrics](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-metrics)
- [https://developer.android.com/topic/performance/baselineprofiles/overview](https://developer.android.com/topic/performance/baselineprofiles/overview)
- [https://developer.android.com/topic/performance/tracing](https://developer.android.com/topic/performance/tracing)
- [https://developer.android.com/topic/performance/rendering/jankstats](https://developer.android.com/topic/performance/rendering/jankstats)
