# Android Performance Observability Patterns

## Selection Notes
- Category: `quality-release`
- Best fit when the request matches the trigger language in `SKILL.md` and the implementation focus is `Measure startup, rendering, memory, jank, vitals, logs, and crash signals for Android apps with actionable traces.`
- Reach for neighboring skills only after this skill has framed the main problem.

## Measurement Ladder
- Startup time or scroll performance:
  Prefer: Macrobenchmark on a release-like build, then Baseline Profiles if startup or hot paths are repeatedly expensive.
- Deep frame or thread analysis:
  Prefer: Perfetto or System Tracing when you need to see main-thread, binder, render, or I/O timing in detail.
- In-app frame health:
  Prefer: JankStats or frame metrics when you need ongoing signals during manual or automated runs.
- Production drift:
  Prefer: Android Vitals or field crash/ANR signals before guessing from local reproduction alone.

## Default Review Sequence
1. Classify the symptom before choosing tooling.
2. Use release-like variants and stable device conditions whenever the question is quantitative.
3. Measure, change one variable, and measure again.
4. Keep traces, numbers, and field signals distinct in the write-up.
5. Hand off UI-tuning work only after the evidence is clear.

## Best-Practice Notes
- Baseline Profiles improve ART compilation behavior, but they are not a substitute for removing expensive startup work.
- Macrobenchmark results are most useful when the path is deterministic and external noise is controlled.
- Trace analysis should call out whether the diagnosis is measured or inferred.
- Crash, ANR, and battery issues belong in the same observability conversation even if they are not visible as frame drops.

## Handoff Shortlist
- `android-compose-performance`
- `android-ci-cd-release-playstore`
