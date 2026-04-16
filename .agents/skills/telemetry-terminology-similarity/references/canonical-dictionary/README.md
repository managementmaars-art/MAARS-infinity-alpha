# Canonical Telemetry Names Dictionary

Bundled reference of canonical attribute names from the four major FOSS observability standards. Used by `term_similarity.py --canonical` to anchor field names against established standards instead of just comparing them to each other.

## Sources

| Source        | License    | Attributes | Purpose                                |
| ------------- | ---------- | ---------- | -------------------------------------- |
| OpenTelemetry | Apache-2.0 | 536        | Logs/traces/metrics canonical attrs    |
| OCSF          | Apache-2.0 | 907        | Security event taxonomy                |
| CloudEvents   | Apache-2.0 | 10         | Event envelope (CloudNative Computing) |
| **Total**     | —          | **1,453**  | —                                      |

## Schema

Single JSON file `canonical-names.json` — array of objects:

```json
{
  "name": "http.request.method",
  "source": "otel",
  "namespace": "http",
  "brief": "HTTP request method.",
  "stability": "stable"
}
```

| Field       | Type   | Description                                                               |
| ----------- | ------ | ------------------------------------------------------------------------- |
| `name`      | string | Canonical attribute name as it appears in the upstream spec               |
| `source`    | string | One of `otel`, `ocsf`, `cloudevents`                                      |
| `namespace` | string | Logical grouping (e.g., `http`, `db`, `system`)                           |
| `brief`     | string | One-line description (max 200 chars)                                      |
| `stability` | string | `stable` / `experimental` / `deprecated` (OTel only) or `stable` (others) |

## Refresh

Run `build.sh` to refetch from upstream and regenerate. The script pins specific upstream versions for reproducibility — bump them when you want newer attributes.

## License Compatibility

All three sources are Apache-2.0, allowing redistribution as part of this skill (which inherits the cc-skills marketplace license). Attribution is preserved via the `source` field on every entry.

## Why bundle 318 KB?

Three reasons:

1. **Offline use** — the skill works without network access
2. **Reproducibility** — pinned versions mean the same input always produces the same output
3. **Speed** — avoids 67 GitHub API calls for OTel registry files on every run

The dictionary updates rarely (OTel ships ~quarterly), so the cost of staleness is low.
