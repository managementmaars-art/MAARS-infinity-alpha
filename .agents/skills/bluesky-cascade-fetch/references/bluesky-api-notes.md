# Bluesky API Notes (for this skill)

This skill uses HTTP XRPC endpoints defined in official AT Protocol lexicons and Bluesky docs.

## Host and Auth Model

- Public read endpoints for many `app.bsky.*` APIs can be called against:
  - `https://public.api.bsky.app` (cached AppView host).
- Authenticated requests can be done by:
  1. Calling `com.atproto.server.createSession` on `https://bsky.social`.
  2. Using `Authorization: Bearer <accessJwt>` for subsequent requests.
- The skill supports both modes:
  - Public mode (no credentials).
  - Session mode (`BLUESKY_IDENTIFIER` + `BLUESKY_APP_PASSWORD`).

References:
- API Hosts and Auth:
  - `https://raw.githubusercontent.com/bluesky-social/bsky-docs/main/docs/advanced-guides/api-directory.mdx`
- Session endpoint lexicon:
  - `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/com/atproto/server/createSession.json`

## Seed Post Endpoints

The script fetches seed posts from one of these endpoints:

1. `app.bsky.feed.searchPosts`
- Required: `q`
- Optional: `sort`, `since`, `until`, `author`, `mentions`, `lang`, `domain`, `url`, `tag`, `limit`, `cursor`
- Notes:
  - Endpoint may require auth for some providers/implementations.
  - Cursor may not allow full result scrolling.

2. `app.bsky.feed.getAuthorFeed`
- Required: `actor`
- Optional: `limit`, `cursor`, `filter`, `includePins`
- Filter known values:
  - `posts_with_replies`
  - `posts_no_replies`
  - `posts_with_media`
  - `posts_and_author_threads`
  - `posts_with_video`

3. `app.bsky.feed.getFeed`
- Required: `feed` (AT-URI)
- Optional: `limit`, `cursor`

4. `app.bsky.feed.getListFeed`
- Required: `list` (AT-URI)
- Optional: `limit`, `cursor`

References:
- `searchPosts`:
  - `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/searchPosts.json`
- `getAuthorFeed`:
  - `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/getAuthorFeed.json`
- `getFeed`:
  - `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/getFeed.json`
- `getListFeed`:
  - `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/getListFeed.json`

## Thread Expansion Endpoint

- `app.bsky.feed.getPostThread`
  - Required: `uri`
  - Optional: `depth` (`0..1000`), `parentHeight` (`0..1000`)
- Returned union for `thread`:
  - `threadViewPost`
  - `notFoundPost`
  - `blockedPost`

Reference:
- `getPostThread`:
  - `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/getPostThread.json`
- Thread-related shapes (`postView`, `threadViewPost`, etc.):
  - `https://raw.githubusercontent.com/bluesky-social/atproto/main/lexicons/app/bsky/feed/defs.json`

## Time Window Semantics in this Skill

- The script supports `--start-datetime` (inclusive) and `--end-datetime` (exclusive).
- Filtering is applied client-side on normalized UTC timestamps:
  - Primary source: `record.createdAt`
  - Fallback: `indexedAt`
- For `searchPosts`, optional server-side `since/until` can also be sent unless `--disable-server-time-filter` is used.
- The script still enforces client-side time filtering for deterministic behavior.
