# SvelteKit Reference

Load when the repo has `frontend/package.json` with Svelte deps and generated bindings in `frontend/src/lib/forge/`.

## Generated Naming Patterns

For a backend function `list_todos`:

| Export | File | Returns | Usage |
|---|---|---|---|
| `listTodos()` | api.ts | `Promise<Vec<Todo>>` | One-shot RPC |
| `listTodosStore$()` | api.ts | `SubscriptionStore<Todo[]>` | Svelte store subscription |
| `listTodos$()` | reactive.svelte.ts | `ReactiveQuery<Todo[]>` | Svelte 5 runes reactive |

Mutations: `createTodo()` → `Promise<Todo>` (no Store$ variant).

Jobs: `trackExportUsers(args)` → `JobStore<Output>` (`track` + PascalCase).

Workflows: `trackOnboardUser(args)` → `WorkflowStore<Output>`.

Upload mutations (args contain `Upload` type): `call()` auto-detects `File`/`Blob` and routes to multipart endpoint. No special import needed.

## Store Contract

```typescript
interface SubscriptionResult<T> {
  loading: boolean;
  data: T | null;
  error: ForgeError | null;  // { code, message, details? }
  stale: boolean;
}

// Store methods
store.refetch()      // force re-fetch
store.unsubscribe()  // stop updates
store.reset()        // clear data, set loading
```

Auto-cleanup: subscriptions stop when all Svelte subscribers detach.

`createQueryStore(fn, args)` is the underlying factory; generated `listTodosStore$()` calls this internally. Use for custom store wrappers.

## Svelte 5 Runes

Use `$state`, `$derived`, `$effect` (sparingly). The `$`-suffixed reactive wrappers (`listTodos$()`) return `ReactiveQuery<T>` which is `$state`-backed.

```svelte
<script>
  import { listTodos$ } from '$lib/forge';
  const todos = listTodos$();
</script>

{#if todos.loading}
  <p>Loading...</p>
{:else if todos.error}
  <p>{todos.error.message}</p>
{:else}
  {#each todos.data ?? [] as todo}
    <p>{todo.title}</p>
  {/each}
{/if}
```

## App Setup

Root layout (`+layout.svelte`):
```svelte
<script>
  import { ForgeProvider } from '$lib/forge';
  import { getToken } from '$lib/auth';
</script>

<ForgeProvider url="http://localhost:9081" getToken={getToken}>
  {@render children()}
</ForgeProvider>
```

Disable SSR: `+layout.ts` with `export const ssr = false;`

## Auth Store

Generated `auth.svelte.ts` provides:
```typescript
class AuthStore {
  get token(): string | null
  get refreshToken(): string | null
  get user(): User | null
  get isAuthenticated(): boolean
  setAuth(token: string, refreshToken: string, user: User): void  // persists to localStorage, reconnects SSE
  updateTokens(token: string, refreshToken: string): void          // updates tokens, preserves user
  updateUser(user: User): void                                     // updates user, preserves tokens
  clearAuth(): void                                                // clears localStorage, stops refresh, reconnects SSE
  startRefreshLoop(apiUrl: string, intervalMs?: number): void      // periodic token refresh (default 40min)
  stopRefreshLoop(): void
  tryRefresh(): Promise<boolean>                                   // manual refresh attempt
  handleAuthError(): Promise<void>                                 // call from ForgeProvider's onAuthError
}
export const auth: AuthStore;
export function getToken(): string | null;
```

`setForgeClient(client)` and `setAuthState(state)` manually set context values. Normally handled by `ForgeProvider`.

```typescript
// After login/register:
auth.setAuth(response.access_token, response.refresh_token, response.user);

// In root layout (once):
auth.startRefreshLoop("http://localhost:9081");

// Logout:
auth.clearAuth();
```

SSE reconnects automatically on `setAuth` and `clearAuth`. The `user` property persists to localStorage alongside tokens, similar to Dioxus `login_with_viewer`.

## Navigation

Use `resolve()` from `$app/paths` for all hrefs and goto calls:
```svelte
<script>
  import { resolve } from '$app/paths';
</script>
<a href={resolve('/settings')}>Settings</a>
```

## Route Structure

```
frontend/src/
  routes/
    +layout.svelte          # ForgeProvider, nav
    +layout.ts              # export const ssr = false
    +page.svelte            # landing
    (auth)/
      login/+page.svelte
      register/+page.svelte
    (app)/
      +layout.svelte        # auth guard
      dashboard/+page.svelte
  lib/
    components/             # reusable UI
    forge/                  # GENERATED, never edit
    auth.ts                 # auth store helpers
```

## Type Mappings

| Rust | TypeScript (args) | TypeScript (returns) |
|---|---|---|
| `String`, `Uuid` | `string` | `string` |
| `DateTime<Utc>` | `string` | `string` (ISO 8601) |
| `i32`, `i64`, `f32`, `f64` | `number` | `number` |
| `bool` | `boolean` | `boolean` |
| `Option<T>` | `T \| null` | `T \| null` |
| `Vec<T>` | `T[]` | `T[]` |
| `Upload` | `File \| Blob` | `File \| Blob` |
| `serde_json::Value` | `unknown` | `unknown` |
| `Bytes` | `Uint8Array` | `Blob` |

## SSE Internals

- Connects to `/_api/events?token=<jwt>`
- Receives `session_id` + `session_secret` on connect
- Subscriptions register via POST to `/_api/subscribe`
- Reconnection: exponential backoff with jitter, base 1s, cap 30s, max 10 attempts
- Events: `connected`, `update` (with target routing), `error`

## Datetime Utility

```typescript
import { dt } from '@forge-rs/svelte';
dt.now()                    // UTC ISO string
dt.parse(input)             // Date
dt.format(input, opts?)     // Intl.DateTimeFormat
dt.relative(input, base?)   // Intl.RelativeTimeFormat
```

## fireMutation

Fire-and-forget wrapper for mutations. Errors route to the global `onMutationError` handler on ForgeProvider:

```typescript
import { fireMutation } from '@forge-rs/svelte';
import { createTodo, deleteTodo } from '$lib/forge';

// Fire-and-forget (errors go to global handler)
fireMutation(createTodo, { title: 'New task' });

// One-off error handling
fireMutation(deleteTodo, { id }, (err) => {
  errorMessage = err.message;
});
```

Register the global handler on the provider:

```svelte
<ForgeProvider url={apiUrl} onMutationError={(err) => showToast(err.message)}>
```

Use direct `await` when you need the return value.

## Optimistic Mutations

`createOptimisticMutation` layers local patches over a live subscription store:

```typescript
import { createOptimisticMutation } from '@forge-rs/svelte';
import { reorderTask, listTodosStore$ } from '$lib/forge';

const todos = listTodosStore$();
const reorder = createOptimisticMutation(
  reorderTask,
  todos,
  (data, args) => data.map(t =>
    t.id === args.id ? { ...t, status: args.status, position: args.position } : t
  ),
);

// Read from the optimistic view
// reorder.data is a Readable<Todo[] | null>

// Fire applies transform instantly, sends mutation to server
reorder.fire({ id, status: 'done', position: 10000 });
```

On SSE update, subscription data replaces the optimistic patch. On error, the view reverts. Default TTL is 3s, configurable via `{ ttlMs: 5000 }` options.

## Dynamic Subscriptions

When a subscription depends on a dynamic parameter (route param, selected item), use `$effect` with explicit cleanup. Do NOT create stores inside `$derived` -- each re-evaluation leaks a subscription.

```svelte
<script lang="ts">
  import { createSubscriptionStore } from '@forge-rs/svelte';
  import { toReactive, type ReactiveQuery } from '$lib/forge/runes.svelte';
  import { onDestroy } from 'svelte';

  let { id } = $props();
  let item: ReactiveQuery<any> | null = $state(null);
  let prevId = "";

  $effect(() => {
    if (id === prevId) return;
    prevId = id;
    item?.unsubscribe();
    item = null;
    if (!id) return;
    item = toReactive(createSubscriptionStore("get_item", { id }));
  });

  onDestroy(() => item?.unsubscribe());
</script>
```

For static subscriptions (no changing params), use the generated `$`-suffixed reactive functions at module scope:
```svelte
<script>
  import { listTodos$ } from '$lib/forge';
  const todos = listTodos$();
</script>
```

## Custom Auth with ForgeProvider Remount

When rolling your own auth store (not using the generated `auth.svelte.ts`), the SSE session won't automatically reconnect on login/logout. Wrap `ForgeProvider` in a `{#key}` block keyed to an auth generation counter:

```typescript
// lib/auth.svelte.ts
let authGeneration = $state(0);
export function getAuthGeneration(): number { return authGeneration; }

export function setAuth(accessToken: string, refreshToken: string, userId: string, email: string) {
  // ... persist to localStorage ...
  authGeneration++;  // triggers ForgeProvider remount
}

export function clearAuth() {
  // ... clear localStorage ...
  authGeneration++;
}
```

```svelte
<!-- +layout.svelte -->
{#key getAuthGeneration()}
<ForgeProvider url={apiUrl} {getToken} onMutationError={handleError}>
  {@render children()}
</ForgeProvider>
{/key}
```

Without this, logging in shows stale anonymous data, and logging out continues streaming the previous user's data until a full page reload.

## Common Mistakes

- Editing `$lib/forge/*` (overwritten on `forge generate`)
- Manual refetch loops instead of using `Store$` subscriptions
- Forgetting `ForgeProvider` in root layout
- Using `$effect` for data fetching instead of reactive stores (except dynamic subscriptions, see above)
- Creating subscription stores inside `$derived` (leaks subscriptions on every re-evaluation)
- Not handling `loading` and `error` states in UI
- Silently dropping mutation errors (use `fireMutation` with a global handler instead)
- Custom auth without `{#key}` remount on ForgeProvider (SSE bound to stale principal)
