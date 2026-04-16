# Pitfalls

Common mistakes and their fixes, organized by topic. Load this when starting implementation or when builds fail.

**Murphy's Law applies.** Every pitfall here is something that WILL happen in production. Don't assume happy paths. Don't assume entities exist. Don't assume tokens are valid. Don't assume networks are reliable. Code defensively.

## 1. Generated Code

**Editing generated files.**
Files under `frontend/src/lib/forge/` (SvelteKit) or `frontend/src/forge/` (Dioxus) are overwritten by `forge generate`. Fix the Rust source, not the output.

**Forgetting `forge generate` after backend changes.**
New queries, mutations, models, or enum changes require regeneration. The frontend compiles against stale types and fails at runtime with deserialization errors.

**Putting `#[derive(...)]` before `#[forge::model]`.**
The model macro must be the first attribute. Derives placed before it produce confusing compiler errors.
```rust
// wrong
#[derive(Debug, Clone)]
#[forge::model]
pub struct Item { ... }

// correct
#[forge::model]
#[derive(Debug, Clone)]
pub struct Item { ... }
```

## 2. Macros & Registration

**Naming functions with the macro type suffix.**
`heartbeat_daemon` generates `HeartbeatDaemonDaemon`. Name it `heartbeat` — the macro adds the suffix.

**Private handler functions.**
`#[forge::query] async fn get_items(...)` generates a private struct that `pub use` won't re-export. Always use `pub async fn`.

**Bare `log` flag.**
`#[forge::query(log)]` does not work. Use `#[forge::query(log = "info")]` with a quoted string.

**Dummy `Option<()>` parameters.**
If the handler has no business input, omit the parameter entirely. Dummy inputs trigger unnecessary validation.

**Using `public` by default.**
Auth is required by default for a reason. Only add `public` when the business requirement explicitly calls for unauthenticated access.

**Forgetting to register handlers.**
Macros generate structs but don't make them reachable. Each handler needs a register call in `main.rs` (`.register_query::<GetItemsQuery>()`, etc.) unless `auto_register()` is wired up.

## 3. Database & Transactions

**Using runtime SQL instead of compile-time checked queries.**
Never use `sqlx::query()` or `sqlx::query_as::<_, T>()`. Always use the bang-macro forms: `sqlx::query!()` and `sqlx::query_as!()`. Compile-time checking catches SQL typos, type mismatches, and schema drift before deployment. After modifying queries, run `forge migrate prepare` to update the `.sqlx/` cache.
```rust
// wrong - runtime checked, errors at runtime
sqlx::query_as::<_, User>("SELECT id, name FROM users WHERE id = $1")
    .bind(id)
    .fetch_one(&mut conn)
    .await

// correct - compile-time checked, errors at build time
sqlx::query_as!(User, "SELECT id, name FROM users WHERE id = $1", id)
    .fetch_one(&mut conn)
    .await
```

For enums, use explicit type casts in the SELECT: `status as "status: ScanStatus"`. SQLx infers nullability from the database schema. Use the `"column?"` suffix only when overriding inference (e.g., forcing a non-nullable column to be treated as nullable in complex queries).

**Calling `dispatch_job`/`start_workflow` without `transactional`.**
Without it, job inserts happen before the mutation commits. If the mutation rolls back, orphan jobs execute against non-existent data.

**Using `ctx.db()` in mutations instead of `ctx.conn()`.**
Mutations need `ctx.conn()` for transactional access. Bind to a mutable variable:
```rust
let mut conn = ctx.conn().await?;
sqlx::query_as!(User, "SELECT id, name FROM users WHERE id = $1", id)
    .fetch_one(&mut conn)
    .await
```

**Mocking the database in tests.**
Use `TestQueryContext`/`TestMutationContext` with real DB connections. Mocking hides migration bugs and constraint violations. Use `IsolatedTestDb` for clean per-test databases.

**Hand-writing PG triggers for reactivity.**
Call `SELECT forge_enable_reactivity('table_name');` in migrations. Hand-written triggers break change detection because the payload format won't match the Reactor.

**Using `SELECT *` in subscribed queries.**
Column-aware invalidation only works with explicit column lists. `SELECT *` falls back to table-level invalidation, triggering unnecessary re-fetches.

**Forgetting `forge_enable_reactivity` on joined tables.**
If a query joins `sites` and `scans`, both tables need reactivity enabled. The Reactor only fires on tables it watches. A missing `forge_enable_reactivity('scans')` means changes to scans won't push updates to the query, even though `sites` is reactive.

**Returning stale data from queries that join related tables.**
Queries like `list_sites` that use LATERAL JOIN to include latest scan data must use the actual joined columns in their return type, not the base model. Create a dedicated struct (e.g., `SiteSummary`) with the enriched fields. If you return the base `Site` struct, the joined data is silently dropped and the frontend shows stale or missing values.

## 4. Workflows

**Using `tokio::sleep` for long waits.**
Workflows survive restarts; `tokio::sleep` doesn't. Use `ctx.sleep()` which persists the wake time in the event store.

**Using `FnOnce` closures in sequential steps with retry.**
Sequential steps need `Fn` closures because they may execute multiple times on retry. Parallel steps use `FnOnce` (no retry).

**Step results are cached by name on resume.**
If you rename a step between deploys, the old cache entry won't match and the step re-executes. Keep step names stable across deploys.

**Changing the persisted contract under the same version.**
The runtime computes a signature from step keys, wait keys, event names, timeout, and type shapes, then persists it to `forge_workflow_definitions` on startup. If you rename a step, add a wait key, or change the input type without bumping the version, the signature won't match what's stored and the node will refuse to start. Bump the version any time the contract changes.

**Removing a deprecated workflow version while runs are still active.**
Deprecated handlers must stay deployed until all their in-flight runs finish. If you remove the handler while runs exist, those runs become `BlockedMissingHandler` and the `/_api/ready` endpoint returns 503, blocking deploys. Check `SELECT count(*) FROM forge_workflow_runs WHERE workflow_version = '...' AND status NOT IN ('completed', 'failed')` before removing old versions.

## 5. Frontend

**Calling `refetch()` on reactive queries.**
SSE pushes updates automatically. `refetch()` doubles traffic and causes flicker. Exception: after workflow step completion in tests where SSE timing is unreliable.

**Reusing ForgeClient across auth state changes.**
The SSE session binds to a principal on first connection. Toggling the token causes `SESSION_PRINCIPAL_MISMATCH`. Destroy and recreate the client when auth changes. Dioxus: keyed remount via `use_auth_key()`. SvelteKit with generated auth store: `setAuth`/`clearAuth` reconnect SSE automatically. SvelteKit with custom auth: wrap `ForgeProvider` in `{#key authGeneration}` so the provider remounts and opens a fresh SSE session with the new token.
```svelte
<!-- Custom auth: track a generation counter, increment on login/logout -->
{#key getAuthGeneration()}
<ForgeProvider url={apiUrl} {getToken} onMutationError={handleError}>
  {@render children()}
</ForgeProvider>
{/key}
```

**Using effects/watchers for data fetching.**
Reactive stores (`$`-suffixed in Svelte, `use_*_live` in Dioxus) handle subscriptions. Effects create race conditions, duplicate subscriptions, and memory leaks.

**Creating subscription stores inside `$derived` (SvelteKit).**
`$derived` re-runs on every dependency change. Placing `createSubscriptionStore()` or `listTodosStore$()` inside `$derived` creates a new SSE subscription each time without cleaning up the old one. Use `$effect` with explicit `unsubscribe()` cleanup instead:
```typescript
let store: ReactiveQuery<any> | null = $state(null);
let prevId = "";
$effect(() => {
  if (id === prevId) return;
  prevId = id;
  store?.unsubscribe();
  store = id ? toReactive(createSubscriptionStore("get_item", { id })) : null;
});
onDestroy(() => store?.unsubscribe());
```
This is the one case where `$effect` is correct for subscription lifecycle, because the subscription depends on a dynamic parameter.

**Forgetting `ForgeProvider`/`ForgeAuthProvider` at the root.**
Without it, `getForgeClient()` / `use_forge_client()` returns nothing and components silently fail.

**Silently dropping mutation errors.**
Most apps do `let _ = mutation.call(args).await` and never show errors to users. Use `.fire()` (Dioxus) or `fireMutation()` (Svelte) with a global `on_mutation_error` / `onMutationError` handler on the provider. This catches validation errors, network failures, and server errors in one place.

**Optimistic updates without expiry (Dioxus).**
If you overlay local state on top of `use_*_live()` data for optimistic UI (e.g., a `pending_moves` HashMap), entries must expire or be cleaned up once the server confirms them. Without expiry, stale entries permanently override incoming server state. This breaks cross-device sync: Device A focuses a task, its local override persists, and when Device B later changes focus, Device A's stale overlay fights the broadcast. Fix: use `use_optimistic()` which handles TTL automatically, or timestamp each entry and ignore entries older than a few seconds.

**Optimistic TTL too low.**
The default 3s TTL in `use_optimistic` / `createOptimisticMutation` accounts for server debounce (50ms) + client subscription debounce (120ms) + network latency. If your SSE latency is higher (slow network, large payloads), increase the TTL or you'll see the UI flicker back and forth.

**Dioxus: not cloning Mutation handles before async closures.**
Mutation handles must be cloned into the closure's scope before `spawn` or async blocks. Use `.fire()` to avoid this entirely.

**Dioxus: reading signals inside spawned async closures.**
`spawn(async move { sig.read() })` can panic if the component unmounted. Read signals before entering the async block and capture the values instead.

**Dioxus: wrong TLS feature for non-WASM targets.**
Use `reqwest` with `rustls-tls` for native targets. The default OpenSSL may not be available in all build environments.

**Dioxus: calling `logout` inside `with_auth_error_handler`.**
Logout triggers a keyed remount that destroys the refresh timer. Signal a refresh attempt instead; let the refresh logic decide whether to log out.

## 6. Auth

**Missing `access_token_ttl`/`refresh_token_ttl` in forge.toml.**
`issue_token_pair()` reads TTL values from the `[auth]` config. If they're missing, the call fails at runtime. Always add both when using self-issued auth:
```toml
[auth]
jwt_algorithm = "HS256"
jwt_secret = "${JWT_SECRET}"
access_token_ttl = "1h"
refresh_token_ttl = "30d"
```

**Holding `conn()` while calling `issue_token_pair()`.**
`issue_token_pair()` acquires its own connection from the pool. If the mutation is still holding a `conn()`, you're using two connections for one request, and under load this can exhaust the pool. Drop the connection before issuing tokens:
```rust
let mut conn = ctx.conn().await?;
let user_id = sqlx::query_scalar!("INSERT INTO users ... RETURNING id")
    .fetch_one(&mut conn).await?;
drop(conn);  // release before acquiring another
let pair = ctx.issue_token_pair(user_id, &["user"]).await?;
```

**Using authenticated client for refresh calls.**
The `ForgeClient` sends the expired token in the `Authorization` header. The runtime validates the token before checking if the endpoint is public. Use an anonymous `ForgeClient` for refresh:
```rust
let anon_client = ForgeClient::new(ForgeClientConfig::new(api_url.to_string()));
let input = RefreshInput::new(refresh_token);
refresh(&anon_client, input).await
```

**Using `#[query(unscoped)]` as the default escape hatch.**
Don't use `#[query(unscoped)]` as the default escape hatch. If your query touches user data, filter by `ctx.user_id()` in SQL. The compile error exists to prevent data leaks. Only use `unscoped` for genuinely shared data (public content, admin dashboards, aggregate stats).

**Relying on `#[serde(skip)]` to hide fields.**
`forge generate` reads the Rust AST, not serde attributes. Skipped fields still appear in generated types. Create a separate public struct (e.g., `PublicUser`) without sensitive fields and use it in return types.

### Social Login

**Validating OAuth tokens client-side.**
Frontend sends authorization code to mutation. Mutation exchanges it server-side. Never validate in browser.

**Storing provider access tokens.**
Provider tokens are for immediate userinfo fetch only. Issue Forge JWT via `issue_token_pair()` for ongoing auth.

**Putting provider IDs directly on users table.**
Single-provider columns (`google_sub`, `github_id` on users) break when adding more providers or handling email changes. Use separate `user_identities` table with `(provider, provider_id)` unique constraint. See patterns.md for schema.

**Using email as unique identifier.**
Emails change and overlap across providers. Use provider's stable ID (`sub` for Google/OIDC, `id` for GitHub).

**Not handling account linking.**
Same email from different provider: (1) auto-link by matching email to existing user and adding new identity, or (2) require explicit linking. Never silently create duplicate accounts.

**Leaking client secrets.**
`{PROVIDER}_CLIENT_SECRET` stays server-side via `ctx.env_require()`. Frontend only needs client ID for OAuth redirect.

## 7. Build & Runtime

**Killing processes on occupied ports.**
If `lsof` shows the port is taken, tell the user and stop. Don't kill processes or change ports — another Forge instance may be running intentionally.

**Skipping `forge check` after changes.**
Run `forge check` after every backend change, not just before finishing. It validates structure, formatting, clippy, SQLx cache, and frontend bindings. If it fails, fix the issue before moving on. If formatting fails, run `cargo fmt` and `bun run format` first.

**Skipping `forge generate` between backend and frontend work.**
Backend contract changes require regeneration before frontend code will compile correctly.

### Common Build Errors

**"cannot find type `GetItemQuery` in module `functions`"**
Handler function is not `pub`, or the module path in `main.rs` is wrong. Make the function `pub` and verify the registration path.

**SQLx compile errors (`SQLX_OFFLINE`)**
Run `forge migrate prepare` (or `cargo sqlx prepare`) after modifying queries to update the `.sqlx/` cache. This requires a running database with current migrations applied. Never fall back to runtime queries as a workaround.

**"type mismatch" in generated frontend code**
Re-run `forge generate`. The generated types are stale relative to the backend.

**SSE not updating after mutations**
Check that the table has `SELECT forge_enable_reactivity('table_name');` in its migration. Without it, the Reactor has no trigger to detect changes.

**Jobs not executing**
Check in order: (1) `[worker]` section in `forge.toml`, (2) handler registered in `main.rs`, (3) `worker_capability` matches node config, (4) queue status via `SELECT status, count(*) FROM forge_jobs GROUP BY status;`.

**`ForgeConn` doesn't implement `Executor`**
Bind `ctx.conn().await?` to a `let mut conn` variable and pass `&mut conn` to query methods.

**Pool exhaustion (`pool timed out`)**
Check `pg_stat_activity` for stuck connections. Isolate analytics/jobs into separate pools via `forge.toml`. Ensure mutations drop connections before long non-DB work.

## 8. Signals

**Signals events not appearing in Grafana**
Check: (1) `[signals] enabled = true` in forge.toml, (2) PostgreSQL datasource configured in Grafana, (3) materialized views have been refreshed (first refresh happens 5 min after startup), (4) events exist: `SELECT count(*) FROM forge_signals_events`.

**Don't log PII in signal properties**
Custom `track()` properties are stored as JSONB. Don't pass email addresses, passwords, or personal data. Use user IDs for identification via `identify()`.

**Session timeout too short**
Default 30 minutes. If users have long idle periods (reading docs, filling forms), increase `session_timeout_mins`. Too short = inflated session counts and bounce rates.

**Batch exceeds 50 events**
Signal endpoints reject batches larger than 50. Client SDKs default to `maxBatchSize: 20`, so this only happens with custom integrations. Split into multiple requests.

**Missing correlation between frontend and backend**
If `correlation_id` is null on signal events, the frontend isn't attaching `x-correlation-id` headers. Check that `ForgeProvider` wraps your app. Direct `fetch()` calls bypass this; use generated RPC functions instead.

**Bot traffic skewing metrics**
Bot detection tags events with `is_bot = true` but doesn't filter them. Dashboard queries should use `WHERE NOT is_bot` for user-facing metrics.

**Events dropped silently**
Collector uses a bounded channel (capacity 10,000). Under extreme load, events drop with a warning log (`signals collector channel full`). Increase `batch_size` or decrease `flush_interval_ms` to drain faster.

## 9. Resilience Anti-Patterns

**Assuming entities exist because you have an ID.**
User got the ID from somewhere, so the entity must exist, right? Wrong. It was deleted, soft-deleted, or never existed. Always use `fetch_optional` + `ok_or_else(NotFound)`.
```rust
// Wrong: panics or returns confusing error
let item = sqlx::query_as!(Item, "SELECT * FROM items WHERE id = $1", id)
    .fetch_one(ctx.db()).await?;

// Correct: explicit not-found handling
let item = sqlx::query_as!(Item, "SELECT * FROM items WHERE id = $1", id)
    .fetch_optional(ctx.db()).await?
    .ok_or_else(|| ForgeError::NotFound(format!("Item {id} not found")))?;
```

**Assuming auth state persists across the request.**
JWT was valid when request started, so the user is still valid, right? Wrong. Their row was deleted. Their role was revoked. Always verify critical permissions against current DB state for sensitive operations.

**Trusting frontend state for authorization.**
User's local state shows they have access, so they must still have access, right? Wrong. Permissions changed. Always enforce authorization server-side.

**Assuming prior mutations succeeded.**
This request follows another one, so the prior data exists, right? Wrong. Prior request failed. Data was deleted between requests. Concurrent user modified it. Check existence and validity at every step.

**Ignoring concurrent modification.**
Nobody else will edit this while the user has the form open, right? Wrong. Add version/etag checking for any mutable entity. Return `Conflict` when versions don't match.

**Happy-path-only error messages.**
"An error occurred" when something fails. Users can't report issues. Include entity IDs, action attempted, and what went wrong in error messages.

**Fire-and-forget mutations without feedback.**
Mutation fires, no loading state, no success confirmation, no error handling. User doesn't know if it worked. Always show loading state, confirm success, and handle errors visibly.

**Assuming network reliability.**
Request will complete because it started, right? Wrong. Network drops. Timeouts occur. Show offline indicators. Retry or fail gracefully. Don't leave UI in broken state.

**Assuming SSE stays connected.**
Data will update because SSE is connected, right? Wrong. Connection dropped silently. Tab was backgrounded. Handle stale states. Show reconnection indicators.

**Assuming job targets still exist.**
Job was dispatched to process entity X, so entity X exists, right? Wrong. Deleted before job ran. Always check existence at job start and exit gracefully.

**Assuming form state matches DB state.**
User has the latest version in their form, right? Wrong. Another user edited it. Another tab edited it. DB migration changed the schema. Include version checks on submit.

**Assuming token refresh will succeed.**
Refresh token is valid, so refresh will work, right? Wrong. Token was revoked on another device. User was deactivated. Always handle refresh failure with logout and explanation.

**Only testing the happy path.**
Tests pass, so the code works, right? Wrong. Tests only cover success. Add tests for: missing auth, wrong role, missing entity, invalid input, duplicate entry, concurrent modification. If you only write one test, write the failure test.
