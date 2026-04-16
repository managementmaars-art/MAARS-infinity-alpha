# API Reference

Macros, contexts, config, errors, and CLI. Token-efficient lookup for implementation.

## Macro Attributes

### `#[forge::query]`

Generated struct: `{PascalCase}Query`. Trait: `ForgeQuery`.

| Attribute | Type | Default | Notes |
|---|---|---|---|
| `public` | flag | false | Skip auth |
| `consistent` | flag | false | Force read from primary, bypass replicas |
| `require_role("x")` | string | — | Returns 403 if missing |
| `cache = "30s"` | duration | — | TTL-based, per-identity cache. Key = hash(fn + args + auth_scope) |
| `timeout = 30` | u64 | — | Seconds (bare integer, not quoted). For HTTP-capable handlers, an explicit timeout also becomes the default outbound HTTP timeout for `ctx.http()` |
| `rate_limit(requests=100, per="1m", key="user")` | group | — | Keys: `user`, `ip`, `tenant`, `user_action`, `global` |
| `log = "info"` | string | — | Must be quoted string, not bare flag |
| `unscoped` | flag | false | Skip compile-time user_id/owner_id scope enforcement |
| `tables = ["t1","t2"]` | array | auto | Override auto-extracted SQL table deps |

Signature: `async fn name(ctx: &QueryContext, ...) -> Result<T>`. SQL tables and columns auto-extracted at compile time for reactive invalidation. Private queries must filter by `user_id` or `owner_id` in SQL unless `unscoped`.

### `#[forge::mutation]`

Generated struct: `{PascalCase}Mutation`. Trait: `ForgeMutation`.

| Attribute | Type | Default |
|---|---|---|
| `public` | flag | false |
| `require_role("x")` | string | — |
| `transactional` | flag | false |
| `timeout = 30` | u64 | — |
| `max_size = "200mb"` | string | — |
| `rate_limit(...)` | group | — |
| `log = "info"` | string | — |
| `unscoped` | flag | false |

Signature: `async fn name(ctx: &MutationContext, ...) -> Result<T>`. Compile-time check: if body contains `dispatch_job` or `start_workflow` without `transactional`, hard error.

If `timeout` is omitted, outbound HTTP requests from `ctx.http()` remain unlimited by default.

### `#[forge::job]`

Generated struct: `{PascalCase}Job`. Trait: `ForgeJob`.

| Attribute | Type | Default |
|---|---|---|
| `name = "custom"` | string | fn_name |
| `timeout = "30m"` | duration | `"1h"` |
| `priority = "normal"` | enum | `"normal"` |
| `max_attempts = 3` | u32 | 3 |
| `backoff = "exponential"` | enum | `"exponential"` |
| `max_backoff = "5m"` | duration | `"5m"` |
| `retry(max_attempts=N, backoff="...", max_backoff="...")` | group | — |
| `worker_capability = "gpu"` | string | — |
| `idempotent` / `idempotent(key="input.id")` | flag | false |
| `ttl = "24h"` | duration | — |
| `compensate = "handler_fn"` | string | — |
| `public` / `require_role(...)` | — | — |

Priority values: `background`(0), `low`(25), `normal`(50), `high`(75), `critical`(100). Backoff: `fixed`, `linear`, `exponential`. Signature: `async fn name(ctx: &JobContext, args: T) -> Result<R>`.
When explicitly set, `timeout` also becomes the default outbound HTTP timeout for `ctx.http()`.

### `#[forge::cron("0 9 * * *")]`

Generated struct: `{PascalCase}Cron`. First quoted string = schedule.

| Attribute | Type | Default |
|---|---|---|
| `timezone = "UTC"` | string | `"UTC"` |
| `group = "default"` | string | `"default"` |
| `timeout = "1h"` | duration | `"1h"` |
| `catch_up` | flag | false |
| `catch_up_limit = 10` | u32 | 10 |

Signature: `async fn name(ctx: &CronContext) -> Result<()>`. No input args.
When explicitly set, `timeout` also becomes the default outbound HTTP timeout for `ctx.http()`.

### `#[forge::workflow]`

Generated struct: `{PascalCase}Workflow`.

| Attribute | Type | Default | Notes |
|---|---|---|---|
| `name = "x"` | string | fn_name | Logical workflow identity. Two versions share the same name. |
| `version = "2026-05"` | string | — | Freeform string. Paired with `name` to form the unique definition key. |
| `active` | flag | true | This version handles new runs. At most one active version per name. |
| `deprecated` | flag | false | Keeps executing in-flight runs but rejects new ones. Cannot combine with `active`. |
| `timeout = "24h"` | duration | `"24h"` | |
| `public` / `require_role(...)` | — | — | |

Default is `active` when neither `active` nor `deprecated` is specified. Specifying both is a compile error.

A workflow **signature** is derived automatically from step keys, wait keys, event names, timeout, and type shapes. The runtime persists definitions to `forge_workflow_definitions` on startup and stamps each run with `workflow_version` and `workflow_signature`. If a handler's signature differs from what was persisted under the same name+version, the node refuses to start.

Versioned example:
```rust
#[forge::workflow(name = "user_onboarding", version = "2026-05", active)]
pub async fn user_onboarding_v2(ctx: &WorkflowContext, input: OnboardingInput) -> Result<()> {
    // current version — all new runs land here
    ctx.step("verify_email", || async { verify(input.email).await }).run().await?;
    ctx.step("provision", || async { provision(input.user_id).await }).run().await?;
    Ok(())
}

#[forge::workflow(name = "user_onboarding", version = "2026-03", deprecated)]
pub async fn user_onboarding_v1(ctx: &WorkflowContext, input: OnboardingInputV1) -> Result<()> {
    // old version — only finishes in-flight runs, no new dispatches
    ctx.step("send_welcome", || async { welcome(input.user_id).await }).run().await?;
    Ok(())
}
```

Compile-time: detects `tokio::sleep` > 100s and errors (must use `ctx.sleep()`). Signature: `async fn name(ctx: &WorkflowContext, input: T) -> Result<R>`.
When explicitly set, `timeout` also becomes the default outbound HTTP timeout for `ctx.http()`.

### `#[forge::daemon]`

Generated struct: `{PascalCase}Daemon`.

| Attribute | Type | Default |
|---|---|---|
| `leader_elected = true` | bool | `true` |
| `restart_on_panic = true` | bool | `true` |
| `timeout = "30s"` | duration | — |
| `restart_delay = "5s"` | duration | `"5s"` |
| `startup_delay = "0s"` | duration | `"0s"` |
| `max_restarts = 10` | u32 | unlimited |

Signature: `async fn name(ctx: &DaemonContext) -> Result<()>`.
`timeout` on daemons sets the default outbound HTTP timeout for `ctx.http()`.

### `#[forge::webhook(path = "/hooks/stripe")]`

Generated struct: `{PascalCase}Webhook`. `path` is required.

| Attribute | Type | Default |
|---|---|---|
| `path = "/hooks/x"` | string | REQUIRED |
| `signature = WebhookSignature::hmac_sha256("Header", "ENV")` | — | — |
| `allow_unsigned` | flag | false |
| `idempotency = "header:X-Id"` or `"body:$.id"` | string | — |
| `timeout = "30s"` | duration | `"30s"` |

Algorithms: `hmac_sha256`, `hmac_sha1`, `hmac_sha512`. Webhooks mount under `/_api/webhooks`.
When explicitly set, `timeout` also becomes the default outbound HTTP timeout for `ctx.http()`.

### `#[forge::model]`

Place BEFORE `#[derive(...)]` — the macro strips derive attrs and re-emits the struct. Table name: pluralized snake_case of struct name. Primary key always `"id"`. Override with `#[table(name = "custom_name")]` when auto-pluralization is wrong.

### `#[forge::forge_enum]`

Derives: `Debug`, `Clone`, `Copy`, `PartialEq`, `Eq`, `Hash`, `Serialize`, `Deserialize` with `#[serde(rename_all = "snake_case")]`. Generates: `Display`, `FromStr`, `sqlx::Type`/`Encode`/`Decode`. Variants stored as snake_case strings in PG; PG type name = snake_case of the enum name.

```rust
#[forge::forge_enum]
pub enum TaskStatus {
    Pending,
    InProgress,
    Done,
}
// PG type: task_status, values: 'pending', 'in_progress', 'done'
```

### `#[forge::mcp_tool]`

Generated struct: `{PascalCase}McpTool` (strips `_mcp_tool` / `_tool` suffix from fn name first).

| Attribute | Type | Default |
|---|---|---|
| `name`, `title`, `description` | string | — |
| `public` / `require_role(...)` | — | — |
| `timeout = 30` | u64 | — |
| `rate_limit(...)` | group | — |
| `read_only`, `destructive`, `idempotent`, `open_world` | flag | — |

No HTTP client available on McpToolContext. Parameters with `#[schemars(...)]` and `#[serde(...)]` attributes are preserved on the generated Args struct for JSON Schema generation. Use `#[schemars(description = "...")]` for parameter descriptions visible to MCP clients. MCP tools are authenticated by default; only add `public` when unauthenticated access is intentional, and use `require_role("...")` for role-gated tools.

## Duration Formats

All duration strings: `500ms`, `30s`, `5m`, `2h`, `7d`, or bare number (= seconds). Note: `query`/`mutation`/`mcp_tool` timeout uses bare integer u64 seconds, not quoted duration.

## Context Capability Matrix

| Feature | Query | Mutation | Job | Cron | Workflow | Daemon | Webhook | MCP |
|---|---|---|---|---|---|---|---|---|
| `db()` ForgeDb | yes | — | yes | yes | yes | yes | yes | yes |
| `conn()` ForgeConn | — | yes | yes | yes | yes | yes | yes | yes |
| `http()` | — | yes | yes | yes | yes | yes | yes | — |
| `raw_http()` | — | yes | yes | yes | yes | yes | yes | — |
| `auth` field | yes | yes | yes | yes | yes | — | — | yes |
| `request` metadata | yes | yes | — | — | — | — | — | yes |
| `dispatch_job` | — | yes | — | — | — | yes | yes | yes |
| `start_workflow` | — | yes | — | — | — | yes | — | yes |
| `cancel_job` | — | yes | — | — | — | — | yes | — |
| `issue_token` | — | yes | — | — | — | — | — | — |
| `issue_token_pair` | — | yes | — | — | — | — | — | — |
| `rotate_refresh_token` | — | yes | — | — | — | — | — | — |
| `revoke_refresh_token` | — | yes | — | — | — | — | — | — |
| `revoke_all_refresh_tokens` | — | yes | — | — | — | — | — | — |
| `step()`/`parallel()` | — | — | — | — | yes | — | — | — |
| `sleep()`/`wait_for_event()` | — | — | — | — | yes | — | — | — |
| `heartbeat()` | — | — | yes | — | — | yes | — | — |
| `progress()` | — | — | yes | — | — | — | — | — |
| `save()`/`saved()` | — | — | yes | — | — | — | — | — |
| `shutdown_signal()` | — | — | — | — | — | yes | — | — |
| `header()` | — | — | — | — | — | — | yes | — |
| `EnvAccess` | yes | yes | yes | yes | yes | yes | yes | yes |

### Key Context Notes

- `MutationContext` uses `conn()` for transactional access, not `db()`. `ctx.conn().await?` returns `ForgeConn<'_>`. Must bind to `let mut conn` before passing to sqlx: `sqlx::query_as!(T, "...", args).fetch_one(&mut conn)`. Passing `ctx.conn().await?` directly fails because sqlx needs `&mut ForgeConn`, not owned `ForgeConn`. Always use compile-time checked macros (`query!`, `query_as!`), never runtime forms.
- `QueryContext.db()` returns `ForgeDb` for pool-level access (works with query methods directly, no `&mut` needed).
- Production `ctx.http()` is circuit-breaker-backed by default. Use `raw_http()` only when you intentionally need bare `reqwest`.
- An explicit handler `timeout` also becomes the default outbound HTTP timeout for `ctx.http()`. If omitted, outbound requests stay unlimited unless the request sets its own timeout.
- Job async methods: `heartbeat()`, `save()`, `saved()`, `set_saved()`, `is_cancel_requested()`, `check_cancelled()` are all async.
- `WorkflowContext.elapsed()` returns `chrono::Duration`, not `std::time::Duration`.
- `StepRunner.run()` returns `Result<Option<T>>`. `Some(T)` on success, `None` if step was optional and failed.
- `StepRunner.retry(count, delay)`: count = retries, so total attempts = count + 1.
- `issue_token_pair(user_id, roles)` works for any auth flow (password, social OAuth, magic link). Exchange provider code server-side, upsert user, then issue Forge JWT. See patterns.md "Social Login".

### DbConn Abstraction

Write shared helpers using `DbConn<'_>` to work across all context types:
```rust
pub async fn get_item(db: DbConn<'_>, id: Uuid) -> Result<Item> { ... }
```
- All contexts provide `db_conn()` → `DbConn` for shared helpers
- `MutationContext.db()` also returns `DbConn` (transaction-aware)
- `db()` on other contexts returns `ForgeDb` (pool wrapper with tracing, implements `sqlx::Executor`)
- See `references/patterns.md` for the full pattern

### EnvAccess (all contexts)

```
env(key) -> Option<String>
env_or(key, default) -> String
env_require(key) -> Result<String>
env_parse::<T>(key) -> Result<T>
env_parse_or::<T>(key, default) -> Result<T>  // errors if set but unparseable
env_contains(key) -> bool
```

## ForgeError Variants

| Variant | HTTP | Code |
|---|---|---|
| `NotFound(String)` | 404 | `NOT_FOUND` |
| `Unauthorized(String)` | 401 | `UNAUTHORIZED` |
| `Forbidden(String)` | 403 | `FORBIDDEN` |
| `Validation(String)` | 400 | `VALIDATION_ERROR` |
| `InvalidArgument(String)` | 400 | `INVALID_ARGUMENT` |
| `Timeout(String)` | 504 | `TIMEOUT` |
| `RateLimitExceeded { retry_after, limit, remaining }` | 429 | `RATE_LIMITED` |
| `Database(String)` | 500 | `INTERNAL_ERROR` |
| `Internal(String)` | 500 | `INTERNAL_ERROR` |
| `Sql(sqlx::Error)` | 500 | `INTERNAL_ERROR` |
| `JobCancelled(String)` | 409 | `JOB_CANCELLED` |

## forge.toml Quick Reference

```toml
[project]
name = "my-app"            # telemetry service name

[database]
url = "${DATABASE_URL}"    # required, non-empty
pool_size = 50
min_pool_size = 5
pool_timeout_secs = 30
statement_timeout_secs = 30
test_before_acquire = true
replica_urls = []
read_from_replica = false

[database.pools.jobs]      # optional isolated pools: default, jobs, analytics, observability
size = 10

[gateway]
port = 9081
sse_max_sessions = 10000
request_timeout_secs = 30
cors_origins = ["http://localhost:9080", "http://127.0.0.1:9080"]
quiet_routes = ["/_api/health", "/_api/ready"]
max_body_size = "20mb"    # global upload size limit, per-mutation max_size overrides

[function]
timeout_secs = 30

[auth]
jwt_algorithm = "HS256"    # HS256/384/512, RS256/384/512
jwt_secret = "${JWT_SECRET}"
# OR for JWKS: jwks_url = "https://...", jwt_issuer = "...", jwt_audience = "..."
access_token_ttl = "1h"
refresh_token_ttl = "30d"

[worker]
max_concurrent_jobs = 50
poll_interval_ms = 100

[cluster]
discovery = "postgres"     # postgres, dns, kubernetes, static
heartbeat_interval_secs = 5
dead_threshold_secs = 15

[node]
roles = ["gateway", "function", "worker", "scheduler"]
worker_capabilities = ["general"]

[mcp]
enabled = false
path = "/mcp"

[observability]
enabled = false
otlp_endpoint = "http://localhost:4318"

[signals]
enabled = true              # default: true
auto_capture = true         # auto-track RPC calls
diagnostics = true          # capture frontend errors
session_timeout_mins = 30
retention_days = 90
anonymize_ip = false        # when true, store hashed visitor ID instead of raw IP
batch_size = 100            # events per DB flush
flush_interval_ms = 5000    # max ms between flushes
excluded_functions = []     # function names to skip (exact match)
bot_detection = true        # tag bot traffic via UA patterns
```

Env var substitution: `${VAR}`, `${VAR-default}`, `${VAR:-default}`. Names: `[A-Z_][A-Z0-9_]*`.

Substitution happens before TOML parsing, so the result must be valid TOML syntax:
```toml
# booleans: no quotes (substitution produces bare true/false)
enabled = ${FORGE_OTEL_ENABLED-false}

# strings: use quotes
otlp_endpoint = "${OTEL_EXPORTER_OTLP_ENDPOINT-http://localhost:4318}"

# WRONG: quoting a boolean produces a string, not a boolean
enabled = "${FORGE_OTEL_ENABLED-false}"
```

### Pool Routing

- `default`: queries, mutations, reactor, rate limiter, cluster coordination
- `jobs`: job workers, cron runners, daemon processes, workflow executors
- `analytics`: available via `db.analytics_pool()` for user code
- `observability`: internal metrics collection (pool utilization, slow query tracking)

Unconfigured pools fall back to primary.

## CLI Commands

| Command | Purpose |
|---|---|
| `forge new <name> --template <id>` | Scaffold project |
| `docker compose up --build` / `docker compose down -v` | Docker Compose dev environment |
| `forge generate` | Generate frontend bindings from backend |
| `forge test` | Build binary, start PG container, run backend + Playwright tests. Set `FORGE_TEST_URL` to skip build/start and test against a running server. |
| `forge check` | Validate config, structure, linting, bindings |
| `forge migrate up` / `down [N]` / `status` / `prepare` | Database migrations |

Templates: `with-svelte/minimal`, `with-svelte/demo`, `with-svelte/realtime-todo-list`, `with-dioxus/minimal`, `with-dioxus/demo`, `with-dioxus/realtime-todo-list`.

## Project Structure

### Safe Edit Zones

- `src/functions/*`, `src/schema/*`, `src/utils/*`
- `frontend/src/routes/*`
- `frontend/src/lib/*` excluding generated Forge paths

### Generated (never edit)

- `frontend/src/lib/forge/*` (SvelteKit)
- `frontend/src/forge/*` (Dioxus)

### Migration Cleanup

When creating real migrations, check `migrations/` for scaffolded files from `forge new`:
- `with-*/minimal` templates create `0001_initial.sql.example` (commented placeholder). Delete it.
- `with-*/demo` templates create `0001_initial.sql` (real migration with tables). Delete it and drop those tables if already run.

Do not use `CREATE TABLE IF NOT EXISTS` in migrations. It silently skips creation if a conflicting table from the scaffold already exists.

### Common `forge check` Issues

- **`#[forge::model]` info warning**: Informational, not an error. Standard derives work fine without the macro.
- **Clippy flakiness on first run**: Stale incremental cache. Run `cargo clean` and retry if persistent.

## Migration Format

Files: `migrations/NNNN_description.sql`. Markers: `-- @up` (required), `-- @down` (optional). System migrations run first, then user migrations alphabetically. Advisory lock `0x464F524745` prevents concurrent runs. Dollar-quoting (`$$`) works for PL/pgSQL.

## Endpoints

| Path | Purpose |
|---|---|
| `/_api/rpc/batch` | Batch multiple RPC calls in one request (POST) |
| `/_api/rpc/{function}` | RPC (POST) |
| `/_api/rpc/{function}/upload` | Multipart upload (POST) |
| `/_api/events?token=...` | SSE connection (GET) |
| `/_api/subscribe` | Register subscription (POST) |
| `/_api/unsubscribe` | Remove subscription (POST) |
| `/_api/subscribe-job` | Track job (POST) |
| `/_api/subscribe-workflow` | Track workflow (POST) |
| `/_api/health` | Liveness (GET, 200) |
| `/_api/ready` | Readiness (GET, 200/503) |
| `/_api/webhooks/{path}` | Webhook handlers |
| `/_api/mcp` | MCP endpoint (if enabled) |
| `/_api/signal/event` | Signal: batch custom events (POST, max 50) |
| `/_api/signal/view` | Signal: page view with UTM (POST) |
| `/_api/signal/user` | Signal: identify user (POST) |
| `/_api/signal/report` | Signal: diagnostic error reports (POST, max 50) |

Signal endpoints return `{ "ok": true, "session_id": "UUID" }`. Headers: `x-session-id` (session continuity), `x-forge-platform` (device: `web`, `desktop-macos`, `ios`, `android`, etc.), `x-correlation-id` (links to RPC). Endpoint batch limit (50) is separate from server-side `batch_size` (100) which controls DB flush size.
