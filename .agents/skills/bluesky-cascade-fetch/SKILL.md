---
name: bluesky-cascade-fetch
description: Fetch Bluesky seed posts and expand reply-thread cascades in configurable UTC time windows with retries, throttling, transport checks, and structure validation. Use when tasks need social-opinion diffusion signals from Bluesky (query/feed/list/author sources) as JSON/JSONL artifacts for downstream sentiment or viral-cascade analysis.
---

# Bluesky Cascade Fetch

## Core Goal
- Fetch seed posts from Bluesky using one of:
  - `searchPosts`
  - `getAuthorFeed`
  - `getFeed`
  - `getListFeed`
- Expand each seed into a reply cascade with `getPostThread`.
- Enforce UTC time-window filters (`start` inclusive, `end` exclusive).
- Return machine-readable JSON and optional artifact files.
- Keep execution observable with structured logs.

## Required Environment
- Configure runtime via environment variables (see `references/env.md`).
- Start from `assets/config.example.env`.
- Load env values before running commands:

```bash
set -a
source assets/config.example.env
set +a
```

## Workflow
1. Validate effective configuration.

```bash
python3 scripts/bluesky_cascade_fetch.py check-config --pretty
```

2. Dry-run the fetch plan first.

```bash
python3 scripts/bluesky_cascade_fetch.py fetch \
  --source-mode search \
  --query "environment policy" \
  --start-datetime 2026-03-10T00:00:00Z \
  --end-datetime 2026-03-11T00:00:00Z \
  --max-pages 2 \
  --max-posts 50 \
  --max-threads 20 \
  --dry-run \
  --pretty
```

3. Run fetch with cascade expansion and output artifacts.

```bash
python3 scripts/bluesky_cascade_fetch.py fetch \
  --source-mode search \
  --query "environment policy" \
  --search-sort latest \
  --start-datetime 2026-03-10T00:00:00Z \
  --end-datetime 2026-03-11T00:00:00Z \
  --max-pages 5 \
  --max-posts 120 \
  --max-threads 40 \
  --thread-depth 8 \
  --thread-parent-height 5 \
  --output-dir ./data/bluesky-cascade \
  --log-level INFO \
  --log-file ./logs/bluesky-cascade-fetch.log \
  --pretty
```

## Built-in Robustness
- Retry transient failures (`429/500/502/503/504`) with exponential backoff.
- Respect `Retry-After` and fail fast when it exceeds configured cap.
- Throttle request rate with minimum request interval.
- Enforce run safety caps:
  - max pages
  - max posts
  - max threads
- Validate transport:
  - JSON content-type
  - UTF-8 decode
  - JSON object parse
- Validate structure:
  - seed URI/timestamp checks
  - duplicate/orphan thread-node checks
  - cascade topology stats (`max_depth`, `max_branching_factor`)

## Scope Decision
- Keep the skill atomic and request-driven:
  - one invocation = one configured windowed fetch task
- No built-in scheduler/poller loops.
- If periodic polling is needed, orchestrate repeated invocations externally.
- If `public.api.bsky.app` returns route-level `403`, the script automatically retries with `--base-url https://api.bsky.app`. Manual override is still allowed.

## References
- `references/env.md`
- `references/bluesky-api-notes.md`
- `references/bluesky-limitations.md`
- `references/openclaw-chaining-templates.md`

## Script
- `scripts/bluesky_cascade_fetch.py`

## OpenClaw Invocation Compatibility
- Keep trigger metadata in `name`, `description`, and `agents/openai.yaml`.
- Invoke with `$bluesky-cascade-fetch`.
- Keep calls atomic and parameterized by time window and source mode.
- Use OpenClaw orchestration (not this script) for recurring jobs.

## OpenClaw Prompt Templates

Use these templates directly in OpenClaw and only replace bracketed placeholders.

1. Recon (plan check)

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

2. Fetch (windowed cascade data)

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
Check validation_summary.total_issue_count and thread_fetch.success_count.
Return JSON plus one-line pass/fail verdict.
```
