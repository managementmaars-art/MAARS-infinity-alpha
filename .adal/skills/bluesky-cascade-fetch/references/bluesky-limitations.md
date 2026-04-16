# Bluesky Fetch Constraints and Safety Notes

## Officially Documented Constraints

- Endpoint-level parameter bounds:
  - Feed/search/list endpoints: `limit` max is `100`.
  - `getPostThread.depth`: `0..1000`.
  - `getPostThread.parentHeight`: `0..1000`.
- `searchPosts` specifically states:
  - It may require authentication depending on provider/implementation.
  - Cursor pagination may not allow scrolling through the entire result set.

References:
- `searchPosts`: `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/searchPosts.json`
- `getAuthorFeed`: `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/getAuthorFeed.json`
- `getFeed`: `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/getFeed.json`
- `getListFeed`: `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/getListFeed.json`
- `getPostThread`: `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/getPostThread.json`

## Rate Limits

From official Bluesky docs:

- Rate-limit headers are commonly returned.
- Exceeding limits usually yields `HTTP 429 Too Many Requests`.
- For hosted-account (PDS/entryway) API requests:
  - Overall API requests: `3000 / 5 minutes` (IP scoped).
- `com.atproto.server.createSession`: `30 / 5 minutes` and `300 / day` (account scoped).

Reference:
- `https://raw.githubusercontent.com/bluesky-social/bsky-docs/main/docs/advanced-guides/rate-limits.md`

## Endpoint Availability Nuance

- `public.api.bsky.app` is recommended for public/cached reads, but some environments may see endpoint-specific blocking or provider-side filtering (for example HTTP 403 on selected routes).
- This skill supports host override:
  - env: `BLUESKY_BASE_URL=https://api.bsky.app`
  - CLI: `--base-url https://api.bsky.app`

## Built-in Protections in This Skill

- Retry transient errors (`429/500/502/503/504`) with exponential backoff.
- Respect `Retry-After` when present and fail fast if it exceeds configured cap.
- Request throttling with minimum interval (`BLUESKY_MIN_REQUEST_INTERVAL_SECONDS`).
- Hard safety caps per invocation:
  - max pages
  - max posts
  - max threads
- Transport checks:
  - content-type must be JSON
  - UTF-8 decode
  - JSON object parse
- Structure checks:
  - seed post URI/timestamp validation
  - duplicate/orphan thread node detection
  - cascade stats (`max_depth`, `max_branching_factor`)

## Scope Boundaries

- This skill is a pull-based fetcher for:
  - seed posts
  - thread cascades for those seeds
- It does not provide internal scheduling/polling.
- Long-running periodic collection should be orchestrated externally (for example by OpenClaw scheduler loops).
