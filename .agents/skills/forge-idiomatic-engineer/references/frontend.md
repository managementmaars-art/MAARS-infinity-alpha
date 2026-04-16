# Frontend Playbook

Shared principles for building Forge frontends. Framework-specific details live in `frontend/svelte.md` and `frontend/dioxus.md`.

## Core Rule

Backend is the source of truth. Frontend is a projection of the backend contract.

1. Finish backend handlers + tests
2. Run `forge generate`
3. Wire frontend against generated bindings
4. Never hand-edit generated files

## Generated Files

SvelteKit: `frontend/src/lib/forge/` (types.ts, api.ts, stores.ts, reactive.svelte.ts, auth.svelte.ts, index.ts)

Dioxus: `frontend/src/forge/` (types.rs, api.rs, mod.rs)

These are overwritten on every `forge generate`. Treat as read-only.

## Reactivity Model

Forge uses query-based subscriptions, not table-based. The backend query is the unit of reactivity. When underlying tables change (via LISTEN/NOTIFY), the server re-executes the query, hashes the result, and only pushes over SSE if data actually differs.

What this means for frontends:
- No manual refetch loops. Subscribe and the data stays current.
- No WebSocket management. SSE is handled by the generated client.
- No cache invalidation logic. The server decides when to push.

## State Shape

All subscription stores expose:

```
loading: bool       // true until first data arrives
data: T | null      // the result
error: Error | null // last error
stale: bool         // reserved for reconnection status
```

Jobs add: `jobId`, `status`, `progress`, `message`, `output`, `error`.
Workflows add: `workflowId`, `status`, `step`, `steps[]`, `output`, `error`.

Workflow `status` values: `pending`, `running`, `suspended`, `completed`, `failed`, `cancelled_by_operator`, `blocked_missing_version`, `blocked_signature_mismatch`, `blocked_missing_handler`, `retired_unresumable`. The `blocked_*` statuses indicate the backend has no matching handler for the run's version or signature. `retired_unresumable` means the workflow version was removed after the run was already past the point of safe resumption. Treat all blocked/retired statuses as terminal from the UI perspective and show an operational error state.

## Auth Pattern

1. Backend: `[auth]` config in `forge.toml` (must include `access_token_ttl` and `refresh_token_ttl`) + public `register`/`login`/`refresh` mutations using `ctx.issue_token_pair()`
2. Frontend: auth layer persists tokens + user/viewer to localStorage, provides token to the client, runs periodic refresh
3. On auth change: client reconnects SSE (how depends on framework, see below)

Both SvelteKit (`auth.setAuth(token, refreshToken, user)`) and Dioxus (`auth.login_with_viewer(token, refreshToken, &viewer)`) store the authenticated user alongside tokens. This avoids apps needing their own user persistence layer.

**SSE reconnect on auth change:**
- Generated auth store (SvelteKit `auth.setAuth`/`clearAuth`, Dioxus `use_auth_key()`): automatic. The store signals the client to tear down and reconnect.
- Custom auth store: manual. SvelteKit: wrap `ForgeProvider` in `{#key authGeneration}` so it remounts on auth changes. Dioxus: use a keyed component wrapper. Without this, the SSE session stays bound to the old principal and either shows stale data or returns `SESSION_PRINCIPAL_MISMATCH`.

**Backend auth mutations must drop `conn()` before calling `issue_token_pair()`.** The token pair call acquires its own connection. Holding both under load exhausts the pool.

Protected endpoints require `Authorization: Bearer <token>`. Public endpoints (`#[forge::query(public)]`) skip auth.

## Error Handling

Backend errors serialize to `{ code, message, details? }`. Frontend gets typed `ForgeError` / `ForgeClientError`.

Pattern: check `error.code` for control flow (`NOT_FOUND`, `VALIDATION_ERROR`, `UNAUTHORIZED`, `RATE_LIMITED`), show `error.message` for user display.

Rate limit errors include `details.retry_after_secs`. Implement a countdown or disable the action until the cooldown expires:
```typescript
if (error.code === 'RATE_LIMITED') {
  const retryAfter = error.details?.retry_after_secs ?? 60;
  // disable button for retryAfter seconds
}
```

For network errors during data fetching, the generated client retries SSE connections with exponential backoff (1s base, max 10 attempts) automatically. SvelteKit: 30s cap. Dioxus: 16s cap (`1s * 2^min(attempts, 4)`). Don't add your own retry logic on top.

## File Uploads

Mutations with `Upload`-typed parameters automatically use multipart/form-data. The generated client detects `File`/`Blob` args and routes to `/_api/rpc/{fn}/upload`.

SvelteKit: pass `File` from `<input>` directly. Dioxus: use `ForgeUpload` type.

Backend types: `Upload` (single file), `Vec<Upload>` (batch uploads), `Option<Upload>` (optional file). Upload serializes as base64 for JSON compatibility but the generated client handles multipart/form-data automatically when it detects `File`/`Blob` values.

Limits: total payload defaults to 20 MB, configurable globally via `gateway.max_body_size` in `forge.toml` or per-mutation via `#[forge::mutation(max_size = "200mb")]`. Other fixed limits: 20 fields max, 1 MB max JSON field, 255 char max field name. For uploads exceeding the configured limit, use presigned URLs (mutation returns upload URL, client uploads directly to storage, then calls confirm mutation).

## Performance

- Use `cache = "30s"` on queries that tolerate stale reads
- Paginate with `LIMIT`/`OFFSET` or cursor-based pagination
- Avoid `SELECT *` in queries that don't need all columns (defeats column-aware invalidation)
- Jobs for anything > 100ms that doesn't need a synchronous response

## Accessibility

- Semantic HTML: `<main>`, `<nav>`, `<header>`, headings in order
- Form labels on every input
- Loading/error states visible and announced (`aria-live="polite"`)
- Keyboard navigation works
- `prefers-reduced-motion` respected
- WCAG AA contrast minimum

## Signals (Analytics & Diagnostics)

Both frontend runtimes include `ForgeSignals` for product analytics and error diagnostics. It is initialized automatically by `ForgeProvider` (enabled by default, disable with `signals={false}` in Svelte or equivalent in Dioxus).

**Auto-captured**: Page views (SPA navigation via history.pushState/replaceState), frontend errors (window.onerror, unhandled rejections), RPC correlation IDs.

**Manual API**: `track(event, properties)`, `identify(userId, traits)`, `captureError(error, context)`, `breadcrumb(message, data)`, `page()`.

**GDPR**: No cookies, no localStorage for tracking. Session IDs are in-memory only, server-managed. Visitor identity is a daily-rotating `SHA256(ip + ua + salt)` hash. Raw IPs stored by default; set `anonymize_ip = true` in `[signals]` to store only the hashed ID.

**Correlation**: Every RPC call gets a unique `x-correlation-id` header. Errors include the last correlation ID and breadcrumbs for reproduction.

**Client config**: `enabled` (default true), `autoPageViews` (true), `autoCaptureErrors` (true), `flushInterval` (5000ms), `maxBatchSize` (20). Pass `signals={false}` to ForgeProvider to disable. Both SDKs send `x-forge-platform` header for device classification.

**Beacon flush**: On page visibility change (tab close/navigation), pending events flush via Beacon API (Svelte/WASM) or synchronous request (desktop/mobile Dioxus).

## Never Do

- Edit files in `frontend/src/lib/forge/` or `frontend/src/forge/`
- Manual refetch loops (use Forge reactivity)
- Client-side auth enforcement without backend validation
- `SELECT *` subscriptions that could be column-specific
- Skip `forge generate` after backend contract changes
