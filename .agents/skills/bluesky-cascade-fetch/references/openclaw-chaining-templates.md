# OpenClaw Chaining Templates

Use these templates directly in OpenClaw and only replace bracketed placeholders.

1. Recon (query plan check)

```text
Use $bluesky-cascade-fetch.
Run:
python3 scripts/bluesky_cascade_fetch.py fetch \
  --source-mode search \
  --query "[QUERY]" \
  --start-datetime [YYYY-MM-DDTHH:MM:SSZ] \
  --end-datetime [YYYY-MM-DDTHH:MM:SSZ] \
  --max-pages [N] \
  --max-posts [M] \
  --dry-run \
  --pretty
Return only the JSON result.
```

2. Fetch (seed posts + thread cascades)

```text
Use $bluesky-cascade-fetch.
Run:
python3 scripts/bluesky_cascade_fetch.py fetch \
  --source-mode search \
  --query "[QUERY]" \
  --search-sort latest \
  --start-datetime [YYYY-MM-DDTHH:MM:SSZ] \
  --end-datetime [YYYY-MM-DDTHH:MM:SSZ] \
  --max-pages [N] \
  --max-posts [M] \
  --max-threads [K] \
  --thread-depth [D] \
  --thread-parent-height [P] \
  --output-dir [OUTPUT_DIR] \
  --pretty
Return only the JSON result.
```

3. Validate (quality gate)

```text
Use $bluesky-cascade-fetch.
Run:
python3 scripts/bluesky_cascade_fetch.py fetch \
  --source-mode author-feed \
  --actor [HANDLE_OR_DID] \
  --start-datetime [YYYY-MM-DDTHH:MM:SSZ] \
  --end-datetime [YYYY-MM-DDTHH:MM:SSZ] \
  --max-pages 1 \
  --max-posts 30 \
  --max-threads 10 \
  --pretty
Check:
- validation_summary.total_issue_count
- seed_fetch.seed_count
- thread_fetch.success_count
Return JSON plus one-line pass/fail verdict.
```
