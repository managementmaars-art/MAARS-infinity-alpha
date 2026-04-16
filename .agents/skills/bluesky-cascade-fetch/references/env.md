# Environment Variables

Use environment variables for all runtime behavior. Do not hardcode credentials or mutable limits in code.

- `BLUESKY_BASE_URL`
  - Default: `https://public.api.bsky.app`
  - Base URL for public `app.bsky.*` read endpoints.
- `BLUESKY_AUTH_SERVICE_URL`
  - Default: `https://bsky.social`
  - Host for `com.atproto.server.createSession` and authenticated proxied `app.bsky.*` requests.
- `BLUESKY_IDENTIFIER` (optional)
  - Account handle or DID for authenticated mode.
- `BLUESKY_APP_PASSWORD` (optional)
  - App password paired with `BLUESKY_IDENTIFIER`.
  - If either identifier/password is set, both must be set.
- `BLUESKY_TIMEOUT_SECONDS`
  - Default: `45`
  - HTTP timeout per request.
- `BLUESKY_MAX_RETRIES`
  - Default: `4`
  - Retry count for transient failures (`429/500/502/503/504` and network failures).
- `BLUESKY_RETRY_BACKOFF_SECONDS`
  - Default: `1.5`
  - Initial retry delay in seconds.
- `BLUESKY_RETRY_BACKOFF_MULTIPLIER`
  - Default: `2.0`
  - Exponential multiplier for retry backoff.
- `BLUESKY_MIN_REQUEST_INTERVAL_SECONDS`
  - Default: `0.4`
  - Minimum interval between requests.
- `BLUESKY_PAGE_SIZE`
  - Default: `25`
  - Default request `limit` value (range `1..100`).
- `BLUESKY_MAX_PAGES_PER_RUN`
  - Default: `20`
  - Hard safety cap for `--max-pages`.
- `BLUESKY_MAX_POSTS_PER_RUN`
  - Default: `300`
  - Hard safety cap for `--max-posts`.
- `BLUESKY_MAX_THREADS_PER_RUN`
  - Default: `80`
  - Hard safety cap for `--max-threads`.
- `BLUESKY_THREAD_DEPTH`
  - Default: `8`
  - Default `getPostThread` depth (range `0..1000`).
- `BLUESKY_THREAD_PARENT_HEIGHT`
  - Default: `5`
  - Default `getPostThread` parent height (range `0..1000`).
- `BLUESKY_MAX_RETRY_AFTER_SECONDS`
  - Default: `120`
  - Maximum accepted `Retry-After` for auto-wait.
- `BLUESKY_USER_AGENT`
  - Default: `bluesky-cascade-fetch/1.0`
  - User-Agent header for all requests.

Example:

```bash
export BLUESKY_BASE_URL="https://public.api.bsky.app"
export BLUESKY_AUTH_SERVICE_URL="https://bsky.social"
export BLUESKY_IDENTIFIER=""
export BLUESKY_APP_PASSWORD=""
export BLUESKY_TIMEOUT_SECONDS="45"
export BLUESKY_MAX_RETRIES="4"
export BLUESKY_RETRY_BACKOFF_SECONDS="1.5"
export BLUESKY_RETRY_BACKOFF_MULTIPLIER="2.0"
export BLUESKY_MIN_REQUEST_INTERVAL_SECONDS="0.4"
export BLUESKY_PAGE_SIZE="25"
export BLUESKY_MAX_PAGES_PER_RUN="20"
export BLUESKY_MAX_POSTS_PER_RUN="300"
export BLUESKY_MAX_THREADS_PER_RUN="80"
export BLUESKY_THREAD_DEPTH="8"
export BLUESKY_THREAD_PARENT_HEIGHT="5"
export BLUESKY_MAX_RETRY_AFTER_SECONDS="120"
export BLUESKY_USER_AGENT="bluesky-cascade-fetch/1.0"
```
