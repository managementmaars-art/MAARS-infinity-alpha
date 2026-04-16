# Scripts

These scripts are intended as **templates** you can copy into a project repo (e.g. `scripts/perf/`) to enable CI perf gates.

## report-export-sizes.mjs

Computes size metrics from an `expo export` output directory.

Example:

```bash
npx expo export --dump-assetmap --dump-sourcemap
node scripts/perf/report-export-sizes.mjs --export-dir dist --out .perf/sizes.json
```

## check-budgets.mjs

Compares measured sizes to a budgets JSON file.

Example:

```bash
node scripts/perf/check-budgets.mjs --budgets ./perf-budgets.json --sizes .perf/sizes.json
```

Add `--warn-only` to avoid failing CI.
