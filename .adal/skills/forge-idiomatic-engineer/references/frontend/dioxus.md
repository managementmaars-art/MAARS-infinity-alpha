# Dioxus Reference

Load when the repo has `frontend/Cargo.toml` with `dioxus` dep, `Dioxus.toml`, and generated bindings in `frontend/src/forge/`.

## Generated Naming Patterns

For a backend function `get_user(ctx, id: Uuid)`:

| Export | Returns | Usage |
|---|---|---|
| `get_user(client, args)` | `Result<User, ForgeClientError>` | Async fn for manual calls |
| `use_get_user(args)` | `QueryState<User>` | One-shot query hook |
| `use_get_user_live(args)` | `SubscriptionState<User>` | Live subscription hook |
| `use_get_user_signal(args)` | `Signal<QueryState<User>>` | Signal variant for passing to child components |

Mutations: `use_create_user()` → `Mutation<CreateUserParams, User>`. Call via `mutation.call(params).await`.

Jobs: `use_send_email(args)` → `JobExecutionState<()>`.

Workflows: `use_onboard_user(args)` → `WorkflowExecutionState<User>`.

## State Types

```rust
pub struct QueryState<T> {
    pub loading: bool,
    pub data: Option<T>,
    pub error: Option<ForgeError>,
}

pub struct SubscriptionState<T> {
    pub loading: bool,
    pub data: Option<T>,
    pub error: Option<ForgeError>,
    pub stale: bool,
    pub connection_state: ConnectionState,
}

// ConnectionState: Disconnected | Connecting | Connected
```

`WorkflowStepState.status` is `String` in Dioxus (not a typed enum). Pattern match carefully.

## Params Generation

Multiple args → `{PascalCase}Params` struct with builder:
```rust
let params = GetUserParams::new("user-id");
let params = UpdateUserParams::new("id").email("new@example.com");
```

Single custom Args/Input struct → passes through directly, no Params generated.

## App Setup

```rust
use crate::forge::*;

fn main() {
    dioxus::launch(app);
}

// Without auth:
fn app() -> Element {
    rsx! {
        ForgeProvider {
            url: "http://localhost:9081",
            Router::<Route> {}
        }
    }
}

// With built-in auth (token storage, refresh, 401 recovery):
fn app() -> Element {
    rsx! {
        ForgeAuthProvider {
            url: "http://localhost:9081",
            app_name: "my-app",
            refresh_interval_secs: 2400,  // ~2/3 of access_token_ttl
            Router::<Route> {}
        }
    }
}
```

`ForgeProvider` accepts `url: String` and `children: Element`. No auth built in.
`ForgeAuthProvider` adds token storage (localStorage on web, filesystem on native), automatic 401 handling with refresh, and periodic token refresh. Use `use_forge_auth()` in components to access the auth handle.

## Component Pattern

```rust
#[component]
fn TodoList() -> Element {
    let todos = use_list_todos_live();

    rsx! {
        if todos.loading {
            p { "Loading..." }
        } else if let Some(error) = &todos.error {
            p { "Error: {error.message}" }
        } else if let Some(data) = &todos.data {
            for todo in data {
                p { "{todo.title}" }
            }
        }
    }
}
```

## Mutation Pattern

`Mutation` must be cloned before moving into async closures. The `onclick` handler is `move`, so the mutation handle needs a clone inside the closure body before `spawn`:

```rust
#[component]
fn CreateTodo() -> Element {
    let mut title = use_signal(|| String::new());
    let create = use_create_todo();

    rsx! {
        input {
            value: "{title}",
            oninput: move |e| title.set(e.value())
        }
        button {
            onclick: move |_| {
                let create = create.clone();
                let t = title.read().clone();
                spawn(async move {
                    create.call(CreateTodoParams::new(t)).await;
                });
            },
            "Add"
        }
    }
}
```

Without the `let create = create.clone()` line inside the closure, you get `cannot move out of captured variable` errors.

## Type Mappings

| Rust backend | Dioxus frontend |
|---|---|
| `String`, `Uuid` | `String` |
| `DateTime<Utc>` | `String` (ISO 8601) |
| `i32`, `i64`, `f32`, `f64` | same |
| `bool` | `bool` |
| `Option<T>` | `Option<T>` |
| `Vec<T>` | `Vec<T>` |
| `Upload` | `ForgeUpload` |
| `serde_json::Value` | `JsonValue` |
| `Bytes` | `Vec<u8>` |

## Re-exports

Generated `mod.rs` re-exports everything from `forge_dioxus`:
```rust
pub use forge_dioxus::{
    ConnectionState, ForgeAuth, ForgeAuthProvider, ForgeClient, ForgeClientConfig,
    ForgeClientError, ForgeError, ForgeProvider, ForgeUpload, JobExecutionState, Mutation,
    QueryState, SubscriptionHandle, SubscriptionState, WorkflowExecutionState,
    use_auth_key, use_connection_state, use_forge_auth, use_forge_client, use_forge_job,
    use_forge_mutation, use_forge_query, use_forge_subscription, use_forge_workflow,
    use_require_auth, use_viewer,
};
```

Import via `use crate::forge::*;` in components.

## Subscription Internals

- SSE-based, same as SvelteKit
- Reconnection: exponential backoff 1s * 2^min(attempts, 4), max 10 attempts
- Data updates debounced at 120ms to coalesce rapid pushes
- `reconnect_nonce` signal triggers re-render on reconnect

## Cross-Platform Setup

Dioxus compiles the same Rust code to web (WASM), desktop (native window), and mobile (iOS/Android) by switching feature flags. The `frontend/Cargo.toml` must separate these as features, not hardcode one:

```toml
[features]
default = ["web"]
web = ["dioxus/web"]
desktop = ["dioxus/desktop"]
mobile = ["dioxus/mobile"]

[dependencies]
dioxus = { version = "=0.7.3" }  # no features here

[target.'cfg(not(target_arch = "wasm32"))'.dependencies]
reqwest = { version = "0.12", default-features = false, features = ["json", "rustls-tls"] }
```

The `reqwest` with `rustls-tls` dependency is required for non-WASM targets. Without it, the native SSE client has no TLS backend and fails with `SSE_CONNECTION_FAILED: Invalid header value` errors.

`Dioxus.toml` needs a `[bundle]` section for mobile:
```toml
[bundle]
identifier = "com.yourapp.id"
publisher = "YourName"
```

Build commands per platform:
- Web: `dx serve` (default)
- Desktop: `dx serve --features desktop --no-default-features`
- Mobile: `dx serve --features mobile --no-default-features`

## SSE Platform Differences

The forge_dioxus SSE client has two code paths:

- **WASM (web)**: Uses browser `EventSource` API. Token passed as URL query parameter (`/_api/events?token=...`) because EventSource doesn't support custom headers.
- **Native (desktop/mobile)**: Uses `reqwest-eventsource`. Token passed as `Authorization: Bearer` header.

Both paths handle missing tokens correctly when no auth is configured. If SSE fails on native targets, the most common cause is a missing `rustls-tls` feature on `reqwest`.

## Auth with ForgeAuthProvider (Recommended)

`ForgeAuthProvider` handles token + viewer storage, 401 recovery, periodic refresh, and ForgeClient wiring automatically:

```rust
fn App() -> Element {
    rsx! {
        ForgeAuthProvider {
            url: API_URL,
            app_name: "my-app",
            refresh_interval_secs: 2400, // ~2/3 of access_token_ttl
            AppShell {}
        }
    }
}

fn AppShell() -> Element {
    let auth_key = use_auth_key();
    rsx! { main { key: "{auth_key}", Router::<Route> {} } }
}
```

### Login with Viewer

Store the user profile alongside tokens so it persists across sessions:

```rust
let mut auth = use_forge_auth();

// After login/register:
auth.login_with_viewer(
    response.access_token,
    response.refresh_token,
    &response.viewer,
);

// Without viewer (tokens only):
auth.login(response.access_token, response.refresh_token);
```

### Reading the Viewer

`use_viewer<V>()` deserializes the stored viewer into your app's type:

```rust
// Returns None when unauthenticated or viewer not set
let viewer: Option<Viewer> = use_viewer::<Viewer>();

// Common pattern: extract viewer_id
let viewer_id = use_viewer::<Viewer>().map(|v| v.id).unwrap_or_default();
```

### Updating the Viewer

After profile edits, update the stored viewer without touching tokens:

```rust
let mut auth = use_forge_auth();
auth.update_viewer(&updated_viewer);
```

### Keyed Remount on Auth Change

The SSE session is bound to the principal at connection time. `use_auth_key()` returns a key that changes on login/logout, forcing a full remount that recreates the SSE connection:

```rust
fn AppShell() -> Element {
    let auth_key = use_auth_key();
    rsx! { main { key: "{auth_key}", Router::<Route> {} } }
}
```

### Route Guard

`use_require_auth` redirects unauthenticated users and returns whether the user is authenticated:

```rust
#[component]
fn ProtectedLayout() -> Element {
    if !use_require_auth("/login") {
        return rsx! { div { class: "loading" } };
    }
    let Some(viewer) = use_viewer::<Viewer>() else {
        return rsx! {};
    };
    rsx! { /* render with viewer */ }
}
```

### Logout

```rust
let mut auth = use_forge_auth();
auth.logout();  // clears tokens + viewer, increments auth key
```

### Manual Auth (Advanced)

For full control, construct `ForgeClientConfig` manually with `.with_token_provider()` and `.with_auth_error_handler()`:

```rust
ForgeClientConfig::new(url)
    .with_token_provider(|| -> Option<String>)
    .with_auth_error_handler(|ForgeError| { ... })
```

The error handler takes `Fn` (not `FnMut`). Copy signals into locals: `let mut flag = needs_refresh; flag.set(true);`

Do NOT call `logout` inside `with_auth_error_handler` directly: it triggers a keyed remount that kills the refresh timer. Signal a refresh attempt instead.

## Dioxus vs SvelteKit Auth Comparison

| Feature | Dioxus (`ForgeAuth`) | SvelteKit (`AuthStore`) |
|---|---|---|
| Login with user | `auth.login_with_viewer(t, rt, &v)` | `auth.setAuth(t, rt, user)` |
| Read user | `use_viewer::<V>()` | `auth.user` |
| Update user | `auth.update_viewer(&v)` | `auth.updateUser(user)` |
| Update tokens | `auth.update_tokens(t, rt)` | `auth.updateTokens(t, rt)` |
| Logout | `auth.logout()` | `auth.clearAuth()` |
| SSE reconnect | `use_auth_key()` keyed remount | `reconnect()` called automatically |
| Route guard | `use_require_auth("/login")` | SvelteKit layout `+page.server.ts` |
| 401 recovery | Built into `ForgeAuthProvider` | `auth.handleAuthError()` |

## Reusable Components

Extract repeated UI patterns into reusable components. Don't inline everything into page-level components.

```rust
// ✅ Reusable loading/error wrapper
#[component]
fn QueryView<T: Clone + PartialEq + 'static>(
    state: SubscriptionState<T>,
    children: Element,
) -> Element {
    if state.loading {
        rsx! { LoadingSpinner {} }
    } else if let Some(error) = &state.error {
        rsx! { ErrorMessage { message: "{error:?}" } }
    } else {
        children
    }
}

// ✅ Small, focused UI atoms
#[component]
fn LoadingSpinner() -> Element {
    rsx! { div { class: "loading-spinner" } }
}

#[component]
fn ErrorMessage(message: String) -> Element {
    rsx! { div { class: "error-message", "{message}" } }
}

// ❌ Duplicating loading/error handling in every page component
```

Compose pages from smaller components. Each component should do one thing.

## Styles

Keep styles in separate CSS files, not inline in RSX. Use `asset!()` to load them.

```rust
// ✅ Separate stylesheet
fn App() -> Element {
    rsx! {
        document::Stylesheet { href: asset!("/public/style.css") }
        Router::<Route> {}
    }
}

// ✅ Component-scoped class names
rsx! { div { class: "todo-item", /* ... */ } }
```

Organize CSS by component or feature, not in a single monolithic file:
- `public/style.css` for global resets and variables
- `public/components.css` for shared component styles
- `public/{feature}.css` for feature-specific styles

Avoid inline `style:` attributes in RSX except for truly dynamic values (e.g., computed widths). Prefer CSS classes for everything else.

## Mutation.fire()

The `Mutation` handle has `.fire(args)` for fire-and-forget mutations. It spawns the call internally and routes errors to the global `on_mutation_error` handler. No more clone-spawn ceremony:

```rust
// ❌ Old: clone-move-spawn-clone-await (6 lines per handler)
let on_create = {
    let create = create.clone();
    move |(title, status): (String, TaskStatus)| {
        let create = create.clone();
        spawn(async move { let _ = create.call(CreateTaskInput::new(title).status(status)).await; });
    }
};

// ✅ New: one-liner
let on_create = move |(title, status): (String, TaskStatus)| {
    create.fire(CreateTaskInput::new(title).status(status));
};
```

For one-off error handling use `.fire_with()`:

```rust
create.fire_with(args, |err| {
    error_signal.set(Some(err.message));
});
```

Register a global handler via the provider:

```rust
ForgeAuthProvider {
    url: "http://localhost:9081",
    on_mutation_error: move |err: ForgeClientError| {
        // Show toast, log to signals, etc.
    },
}
```

Use `.call()` when you need the return value or explicit error handling.

## Optimistic Updates

`use_optimistic` layers local patches over a live subscription. It returns an `OptimisticMutation` whose `.data()` reflects the optimistic state and whose `.fire()` applies the transform, sends the mutation, and auto-reverts on error or TTL expiry (3s):

```rust
let tasks_sub = use_list_tasks_live_signal();
let reorder = use_optimistic(
    use_reorder_task(),
    tasks_sub,
    |tasks, args: &ReorderTaskInput| {
        tasks.iter().map(|t| {
            if t.id == args.id {
                Task { status: args.status.clone(), position: args.position, ..t.clone() }
            } else { t.clone() }
        }).collect()
    },
);

// Read from the optimistic view, not the raw subscription
let tasks = reorder.data().unwrap_or_default();

// Fire applies the transform instantly, sends mutation to server
reorder.fire(ReorderTaskInput::new(id).status(status).position(pos));
```

The flow: `fire()` snapshots current data, applies the transform to the view signal, sends the mutation. On SSE update, subscription data replaces the optimistic patch. On error, the view reverts to the snapshot. A 3-second TTL ensures stale patches don't persist if SSE is delayed.

For manual optimistic updates without `use_optimistic`, overlay pending state on top of subscription data with a HashMap. **Critical: pending entries must expire** (2-3 second TTL) or stale entries permanently override server state, breaking cross-device sync.

## Common Mistakes

- Editing `frontend/src/forge/*` (overwritten by `forge generate`)
- Treating Dioxus like SvelteKit (different reactive model: signals, not stores)
- Adding manual refetch logic instead of using `_live` hooks
- Forgetting `ForgeProvider` at the app root
- Using `use_effect` for data fetching instead of generated hooks
- Doing frontend work before backend contract is confirmed
- Hardcoding `dioxus/web` feature instead of using separate feature flags
- Missing `reqwest` with `rustls-tls` for native targets
- Not cloning `Mutation` handles before moving into async closures (use `.fire()` to avoid this entirely)
- Using `{error}` (Display) instead of `{error:?}` (Debug) for `ForgeError` in RSX
- Calling `logout` directly in `with_auth_error_handler` (causes immediate logout on token expiry instead of refresh)
- Setting the refresh timer too close to the token lifetime (use ~2/3 of token lifetime, not 80%+)
- Reusing the authenticated `ForgeClient` for refresh calls (expired token in header causes `REQUEST_FAILED`)
- Using `auth.login()` without viewer then expecting `use_viewer()` to return data
