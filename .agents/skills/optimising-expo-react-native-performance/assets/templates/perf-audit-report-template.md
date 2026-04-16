# Performance audit report (template)

## Context

- App name:
- Repo / branch / commit:
- Expo SDK / RN / React:
- New Architecture:
- JS engine (Hermes/JSC/V8):
- Build type measured (Release/Profile/debugOptimized):
- Devices tested:
  - Device A (model, OS)
  - Device B (model, OS)

## Problem statement

What users report:

Reproduction steps:
1)
2)
3)

## KPIs and budgets

| KPI | Budget | Baseline | After | Notes |
|---|---:|---:|---:|---|
| Cold start → first render | | | | |
| TTI | | | | |
| Scroll smoothness (scenario) | | | | |
| Navigation p95 (flow) | | | | |
| Memory steady-state | | | | |
| Network p95 (endpoint) | | | | |

## Baseline evidence

Attach:
- DevTools traces:
- Android System Trace / Perfetto:
- Instruments traces:
- Screenshots of key profiler views:

Observations:
- JS thread:
- UI thread:
- Memory:
- Network:

## Root cause hypothesis

Hypothesis:

Evidence that supports it:
- 

Evidence against it / risks:
- 

## Fix plan (ordered by ROI)

### Fix 1
- Goal:
- Change:
- Risk:
- Rollback:
- How we measure success:

### Fix 2
...

## Results

- Before/after KPI table updated.
- Notes about variability (cold vs warm, device variance).

## Regression control

- Budgets file updated/created:
- CI gates added:
- Monitoring configured:
- Remaining known risks:

## Follow-ups

- Deferred optimisations:
- Suggested refactors:
- Long-term improvements:
