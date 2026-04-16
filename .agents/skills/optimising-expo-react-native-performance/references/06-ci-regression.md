# Regression control: budgets, CI gates, and monitoring

Performance is not a one-off exercise. Treat it like security:
- You don’t “fix it once”; you **prevent regressions**.

This file focuses on controls that are cheap to adopt and high leverage.

## The minimum viable controls (do these)

### 1) Commit a perf budgets file

- Store budgets for:
  - JS bundle size (bytes)
  - Total update assets size (bytes)
  - A handful of app KPIs (startup, nav p95)

Use `assets/templates/perf-budgets.example.json` as a starting point.

### 2) Add a CI gate for bundle/update size

Why bundle size gates matter:
- Bigger JS = slower parse/execute = slower startup.
- Bigger OTA payloads = slower update adoption.

A practical approach:
1) In CI, run an export:
   - `npx expo export --dump-sourcemap --dump-assetmap`
2) Compute sizes from the output.
3) Compare against budgets and fail if exceeded.

This is intentionally “dumb but reliable”. It catches accidental dependency bloat and asset explosions.

Scripts included in this skill (copy into your repo, e.g. `scripts/perf/`):
- `scripts/report-export-sizes.mjs`
- `scripts/check-budgets.mjs`

### 3) Add production monitoring

At minimum:
- Crash reporting.
- Transaction/performance traces for key flows.
- Proper symbolication/mapping for release builds.

Choose a provider that fits your constraints (Sentry, Firebase Perf, Datadog, etc.).

## Nice-to-have controls (next step)

### 4) Automated “scenario timing” tests

If you have E2E tests (Detox, Maestro, etc.), add a small number of perf assertions:
- “Open feed screen p95 < X ms”
- “Scroll feed for 5 seconds with no sustained jank” (harder)

This is more brittle than bundle size gates; do it only once your test harness is stable.

### 5) Release build cadence

Make it cheap to produce production-like builds frequently.
- Use build caching features where available.
- Run performance checks on nightly builds or before release branches.

## Example GitHub Actions gate (generic)

This is a template you can adapt:

```yaml
name: perf-gates
on:
  pull_request:

jobs:
  bundle-size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npx expo export --dump-assetmap --dump-sourcemap
      - run: node ./scripts/perf/report-export-sizes.mjs --export-dir dist --out .perf/sizes.json
      - run: node ./scripts/perf/check-budgets.mjs --budgets ./perf-budgets.json --sizes .perf/sizes.json
```

Notes:
- Adjust the export directory (`dist`) to match your setup.
- Some CI environments need extra config for iOS/Android native builds; this gate avoids native builds by using export output.

## Links

See `references/resources.md` for:
- EAS Workflows / EAS Build
- EAS Build caching docs
- Monitoring provider docs
