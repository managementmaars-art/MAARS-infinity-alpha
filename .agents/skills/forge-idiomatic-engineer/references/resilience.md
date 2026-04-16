# Resilience Patterns

Building Forge apps that survive weird, real-world failure modes. Load this before implementing any feature.

## Philosophy

Happy paths are easy. Production breaks on edge cases: deleted data, expired tokens, race conditions, network blips, concurrent users. Every feature must handle the question: "What if the world changed between when the user saw something and when they acted on it?"

Design principle: **assume the worst, degrade gracefully, never crash, always inform the user.**

---

## 1. Auth & Session Resilience

### User Row Deleted Mid-Session

User has valid JWT but their DB row is gone (admin deleted, cascade bug, DB wipe).

**Backend:**
```rust
#[forge::query]
pub async fn get_viewer(ctx: &QueryContext) -> Result<Viewer> {
    let user_id = ctx.user_id()?;
    sqlx::query_as!(Viewer, "SELECT id, email, name FROM users WHERE id = $1", user_id)
        .fetch_optional(ctx.db())
        .await?
        .ok_or_else(|| ForgeError::Unauthorized("Account no longer exists".into()))
}
```

**Frontend (Svelte):**
```typescript
// In ForgeProvider's onAuthError or global error handler
if (error.code === 'UNAUTHORIZED' && error.message.includes('no longer exists')) {
  auth.clearAuth();
  goto('/account-deleted');  // Explain what happened
}
```

**Frontend (Dioxus):**
```rust
// In ForgeAuthProvider's on_auth_error
if err.code == "UNAUTHORIZED" && err.message.contains("no longer exists") {
    auth.logout();
    navigator.push(Route::AccountDeleted);
}
```

### Refresh Token Revoked on Another Device

User logged out elsewhere, but this tab still has the old refresh token.

**Backend:** `rotate_refresh_token` returns `Unauthorized` when token is revoked.

**Frontend:** Catch refresh failure, clear auth, redirect to login with explanation.

```typescript
// auth refresh handler
try {
  await auth.tryRefresh();
} catch (e) {
  if (e.code === 'UNAUTHORIZED') {
    auth.clearAuth();
    goto('/login?reason=session-expired');
  }
}
```

### Roles Changed Mid-Session

User was admin, now they're not. They still have a valid JWT with old roles.

**Backend:** Always check roles server-side. Never trust JWT roles for authorization decisions.

```rust
#[forge::mutation(require_role("admin"))]
pub async fn delete_user(ctx: &MutationContext, id: Uuid) -> Result<()> {
    // require_role checks current JWT, but also verify against DB for critical ops
    let current_roles = get_user_roles(ctx.db(), ctx.user_id()?).await?;
    if !current_roles.contains(&"admin".to_string()) {
        return Err(ForgeError::Forbidden("Role revoked".into()));
    }
    // proceed
}
```

**Frontend:** Handle 403 gracefully, refresh auth state, redirect if needed.

### JWT Expires During Mutation

Request starts valid, JWT expires mid-flight.

**Backend:** Forge validates JWT at request start. If valid at start, request completes.

**Frontend:** If mutation returns 401, trigger refresh and retry once automatically.

```typescript
async function resilientMutation<T>(fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (e) {
    if (e.code === 'UNAUTHORIZED' && await auth.tryRefresh()) {
      return await fn();  // Retry once after refresh
    }
    throw e;
  }
}
```

### Multi-Tab Logout Desync

User logs out in tab A, tab B still shows authenticated UI with stale SSE.

**Frontend:** Use `BroadcastChannel` or `storage` event to sync auth state across tabs.

```typescript
// Listen for auth changes from other tabs
window.addEventListener('storage', (e) => {
  if (e.key === 'auth_token' && e.newValue === null) {
    auth.clearAuth();  // Another tab logged out
    goto('/login');
  }
});
```

### Tab Backgrounded for Hours

Refresh token expires while tab is inactive. User returns to dead session.

**Frontend:** Check token validity on visibility change.

```typescript
document.addEventListener('visibilitychange', async () => {
  if (document.visibilityState === 'visible') {
    const valid = await auth.tryRefresh();
    if (!valid) {
      auth.clearAuth();
      goto('/login?reason=session-expired');
    }
  }
});
```

### Clock Skew

Client clock is wrong, JWT math fails locally.

**Frontend:** Compare server time from response headers, adjust token expiry calculations.

```typescript
// On any response, track server time offset
const serverTime = new Date(response.headers.get('date')).getTime();
const clientTime = Date.now();
const clockOffset = serverTime - clientTime;

// When checking expiry, account for offset
function isTokenExpired(exp: number): boolean {
  const adjustedNow = Date.now() + clockOffset;
  return adjustedNow >= exp * 1000;
}
```

---

## 2. Database & Data Integrity

### Entity Deleted Between Read and Action

User loads list, clicks item, item was deleted by another user.

**Backend:** Return clear 404 with context.

```rust
#[forge::query]
pub async fn get_item(ctx: &QueryContext, id: Uuid) -> Result<Item> {
    sqlx::query_as!(Item, "SELECT * FROM items WHERE id = $1", id)
        .fetch_optional(ctx.db())
        .await?
        .ok_or_else(|| ForgeError::NotFound(format!("Item {} was deleted", id)))
}
```

**Frontend:** Handle 404 gracefully, remove from local state, show toast.

```typescript
if (error.code === 'NOT_FOUND') {
  // Item gone, SSE will update the list, just show feedback
  showToast('This item was deleted');
  goto('/items');  // Navigate away from detail view
}
```

### Optimistic Update Conflicts

User's optimistic update races with another user's change.

**Pattern:** Include version/etag in mutations. Reject stale updates.

```rust
#[forge::mutation(transactional)]
pub async fn update_item(ctx: &MutationContext, input: UpdateInput) -> Result<Item> {
    let mut conn = ctx.conn().await?;
    let current = sqlx::query_scalar!("SELECT version FROM items WHERE id = $1", input.id)
        .fetch_optional(&mut conn).await?
        .ok_or_else(|| ForgeError::NotFound("Item deleted".into()))?;
    
    if current != input.expected_version {
        return Err(ForgeError::Conflict("Item was modified. Refresh and try again.".into()));
    }
    
    sqlx::query_as!(Item,
        "UPDATE items SET title = $1, version = version + 1 WHERE id = $2 RETURNING *",
        input.title, input.id
    ).fetch_one(&mut conn).await.map_err(Into::into)
}
```

**Frontend:** On conflict, show diff or force refresh.

### Foreign Key Target Deleted

User submits form referencing entity that was just deleted.

**Backend:** Handle FK violation explicitly.

```rust
let result = sqlx::query!(
    "INSERT INTO tasks (title, project_id) VALUES ($1, $2)",
    input.title, input.project_id
).execute(&mut conn).await;

match result {
    Err(sqlx::Error::Database(e)) if e.is_foreign_key_violation() => {
        Err(ForgeError::Validation("Project no longer exists".into()))
    }
    Err(e) => Err(e.into()),
    Ok(_) => Ok(())
}
```

### Connection Pool Exhaustion

Under load, pool times out.

**Backend:** Configure isolated pools, fail fast with clear error.

```toml
[database.pools.default]
size = 30
timeout_secs = 5  # Fail fast, don't queue forever

[database.pools.jobs]
size = 10  # Isolated from user traffic
```

**Frontend:** Show "System busy, try again" not generic error.

```typescript
if (error.code === 'INTERNAL_ERROR' && error.message.includes('pool')) {
  showToast('System is busy. Please try again in a moment.');
}
```

### Read Replica Lag

User writes, immediately reads from replica, sees stale data.

**Backend:** Use `#[query(consistent)]` for read-after-write paths.

```rust
// After create/update, return the data directly or use consistent read
#[forge::mutation(transactional)]
pub async fn create_item(ctx: &MutationContext, input: Input) -> Result<Item> {
    let mut conn = ctx.conn().await?;
    // Return created item directly from the write connection
    sqlx::query_as!(Item, "INSERT INTO items ... RETURNING *", ...)
        .fetch_one(&mut conn).await.map_err(Into::into)
}

// If you must query after mutation, mark it consistent
#[forge::query(consistent)]
pub async fn get_item_consistent(ctx: &QueryContext, id: Uuid) -> Result<Item> { ... }
```

### Enum Mismatch (Migration vs Code)

DB has enum value that code doesn't recognize (partial deploy).

**Backend:** Use `#[serde(other)]` fallback variant.

```rust
#[forge::forge_enum]
pub enum TaskStatus {
    Pending,
    InProgress,
    Done,
    #[serde(other)]
    Unknown,  // Catches any unrecognized value
}
```

**Frontend:** Handle unknown states gracefully.

```typescript
function getStatusLabel(status: TaskStatus): string {
  const labels: Record<string, string> = {
    pending: 'Pending',
    in_progress: 'In Progress',
    done: 'Done',
  };
  return labels[status] ?? 'Unknown';
}
```

---

## 3. SSE & Realtime Resilience

### Reconnection with Stale State

SSE drops, reconnects, client has stale local state.

**Frontend:** On reconnect, subscriptions automatically re-register and receive fresh data. Don't layer manual caching on top.

```typescript
// The store handles this automatically. Just react to the data:
{#if todos.stale}
  <Banner>Reconnecting...</Banner>
{/if}
```

### Update for Entity User Lost Access To

User's role changed, SSE pushes update for now-forbidden data.

**Backend:** Reactor re-executes queries with current auth. Forbidden data won't be pushed.

**Frontend:** If you receive 403 during subscription, the server dropped you. Handle gracefully.

### Out-of-Order Updates

Network causes update 3 to arrive before update 2.

**Backend:** Forge debounces and coalesces updates server-side (50ms quiet, 200ms max). Updates are eventually consistent, not ordered.

**Frontend:** Don't rely on update ordering. Treat each push as "current state" not "delta."

### Tab Hibernation

Browser suspends tab, SSE stale for hours.

**Frontend:** On visibility change, check connection health.

```typescript
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    // Connection auto-recovers, but you can force it:
    client.reconnect();
  }
});
```

### SSE Update for Deleted Entity

Entity deleted, but one last update propagates.

**Frontend:** Filter out entities that shouldn't exist.

```typescript
$effect(() => {
  // If viewing a deleted item, navigate away
  if (item.error?.code === 'NOT_FOUND') {
    goto('/items');
  }
});
```

### Update Flood

Rapid changes cause 100+ SSE updates/second.

**Backend:** Server debounces. Client receives coalesced updates.

**Frontend:** The 120ms client-side debounce prevents render thrashing. If still slow, paginate or virtualize lists.

---

## 4. Job & Workflow Resilience

### Job's Target Entity Deleted

Job queued, entity deleted before job runs.

**Backend:** Check existence at job start, exit gracefully.

```rust
#[forge::job]
pub async fn process_item(ctx: &JobContext, item_id: Uuid) -> Result<()> {
    let item = sqlx::query_as!(Item, "SELECT * FROM items WHERE id = $1", item_id)
        .fetch_optional(ctx.db()).await?;
    
    let Some(item) = item else {
        tracing::info!(item_id = %item_id, "Item deleted, skipping job");
        return Ok(());  // Success, nothing to do
    };
    
    // Process item...
    Ok(())
}
```

### Workflow Step Invalidated by State Change

Step 1 succeeds, but entity state makes step 2 impossible.

**Backend:** Validate preconditions at each step.

```rust
#[forge::workflow]
pub async fn fulfill_order(ctx: &WorkflowContext, order_id: Uuid) -> Result<()> {
    ctx.step("charge", || async {
        // Verify order still exists and is payable
        let order = get_order(order_id).await?;
        if order.status != OrderStatus::Pending {
            return Err(ForgeError::InvalidState("Order no longer pending".into()));
        }
        charge(order).await
    }).run().await?;
    
    ctx.step("ship", || async {
        // Re-verify before shipping
        let order = get_order(order_id).await?;
        if order.status != OrderStatus::Paid {
            return Err(ForgeError::InvalidState("Order not paid".into()));
        }
        ship(order).await
    }).run().await?;
    
    Ok(())
}
```

### Worker Crash Mid-Job

Job partially executed, worker dies, job retries.

**Backend:** Design jobs to be idempotent. Use `idempotent(key = "...")`.

```rust
#[forge::job(idempotent(key = "input.request_id"))]
pub async fn send_email(ctx: &JobContext, input: SendEmailInput) -> Result<()> {
    // Check if already sent
    let sent = sqlx::query_scalar!(
        "SELECT EXISTS(SELECT 1 FROM sent_emails WHERE request_id = $1)",
        input.request_id
    ).fetch_one(ctx.db()).await?;
    
    if sent.unwrap_or(false) {
        return Ok(());  // Already done
    }
    
    // Send and record atomically
    send_via_provider(&input).await?;
    sqlx::query!("INSERT INTO sent_emails (request_id) VALUES ($1)", input.request_id)
        .execute(ctx.db()).await?;
    
    Ok(())
}
```

### Cron Fires Twice (Clock Drift)

Different nodes think they're the leader, cron runs twice.

**Backend:** Forge uses `UNIQUE(cron_name, scheduled_time)` constraint. Second execution fails to insert and skips.

**Extra safety:** Make cron handlers idempotent anyway.

### Workflow Waits Forever

`wait_for_event` never receives signal, no timeout.

**Backend:** Always specify timeout. Handle `None` result.

```rust
let decision: Option<Approval> = ctx.wait_for_event("approval", Duration::from_days(3)).await?;

match decision {
    Some(d) if d.approved => { /* proceed */ }
    Some(d) => {
        // Rejected, compensate
        ctx.compensate().await?;
    }
    None => {
        // Timeout, escalate or fail
        tracing::warn!("Approval timeout for workflow");
        return Err(ForgeError::Timeout("Approval not received in 3 days".into()));
    }
}
```

### Job Dispatched in Rolled-Back Transaction

Mutation fails after `dispatch_job`, job shouldn't exist.

**Backend:** Forge buffers job dispatches until transaction commits. If rollback, jobs never inserted. This requires `transactional` flag.

```rust
// Correct: jobs only created if mutation succeeds
#[forge::mutation(transactional)]
pub async fn start_export(ctx: &MutationContext, input: Input) -> Result<Uuid> {
    // Do work that might fail...
    validate(&input)?;
    
    // Job only dispatched if we reach here and transaction commits
    ctx.dispatch_job("export_data", json!({"id": input.id})).await
}
```

### Compensation Handler Fails

Workflow needs to rollback, compensation throws.

**Backend:** Log and continue compensating other steps. Don't let one failure prevent others.

```rust
ctx.step("charge", || async { charge(order_id).await })
    .compensate(|charge_result| async move {
        if let Err(e) = refund(charge_result.charge_id).await {
            // Log but don't fail compensation
            tracing::error!(error = %e, "Refund failed, manual intervention needed");
            // Could dispatch a job for manual review
        }
        Ok(())
    })
    .run().await?;
```

---

## 5. Client & Browser Resilience

### Form Submitted, Tab Closed

Mutation completes but user never sees result.

**Frontend:** For critical actions, show confirmation before allowing navigation.

```typescript
let submitting = false;

beforeNavigate(({ cancel }) => {
  if (submitting) {
    if (!confirm('Your action is still processing. Leave anyway?')) {
      cancel();
    }
  }
});
```

### Double-Click Duplicate Mutation

User clicks submit twice, two mutations fire.

**Frontend:** Disable button during submission. Use mutation loading state.

```svelte
<button disabled={mutation.loading} onclick={handleSubmit}>
  {mutation.loading ? 'Saving...' : 'Save'}
</button>
```

**Backend:** Use idempotency for critical mutations.

```rust
#[forge::mutation(transactional)]
pub async fn create_order(ctx: &MutationContext, input: CreateOrderInput) -> Result<Order> {
    // Use client-provided idempotency key
    let existing = sqlx::query_as!(Order,
        "SELECT * FROM orders WHERE idempotency_key = $1",
        input.idempotency_key
    ).fetch_optional(&mut conn).await?;
    
    if let Some(order) = existing {
        return Ok(order);  // Return existing, don't create duplicate
    }
    
    // Create new order...
}
```

### Navigation During Upload

User leaves page while file uploading.

**Frontend:** Warn before navigation, or use background upload queue.

```typescript
let uploading = false;

beforeNavigate(({ cancel }) => {
  if (uploading && !confirm('Upload in progress. Cancel it?')) {
    cancel();
  }
});
```

### Back Button to Stale State

User navigates back to page showing deleted data.

**Frontend:** Use live subscriptions. When user returns, SSE pushes current state.

### LocalStorage Full

Auth tokens can't persist.

**Frontend:** Catch storage errors, fall back to session-only auth.

```typescript
function safeSetItem(key: string, value: string): boolean {
  try {
    localStorage.setItem(key, value);
    return true;
  } catch (e) {
    console.warn('localStorage full, using session storage');
    sessionStorage.setItem(key, value);
    return false;
  }
}
```

### Incognito Mode

No persistence, refresh loses auth.

**Frontend:** Detect and warn user.

```typescript
// Detect private browsing (imperfect but catches most)
async function isPrivateBrowsing(): Promise<boolean> {
  try {
    localStorage.setItem('test', 'test');
    localStorage.removeItem('test');
    return false;
  } catch {
    return true;
  }
}

// Show notice
if (await isPrivateBrowsing()) {
  showBanner('Private browsing detected. You will be logged out on refresh.');
}
```

### Payload Too Large

User pastes huge content, exceeds limit.

**Backend:** Return clear error with limit info.

**Frontend:** Validate client-side before sending.

```typescript
const MAX_CONTENT_LENGTH = 1_000_000;  // 1MB

function handleInput(value: string) {
  if (value.length > MAX_CONTENT_LENGTH) {
    showError(`Content too large. Maximum ${MAX_CONTENT_LENGTH / 1000}KB.`);
    return;
  }
  content = value;
}
```

---

## 6. Concurrent Users & Multi-Device

### Same Document Edited on Two Devices

User edits on phone and laptop simultaneously.

**Pattern:** Last-write-wins with conflict notification, or operational transforms for real-time collab.

Simple approach (last-write-wins with notification):
```rust
#[forge::mutation(transactional)]
pub async fn update_document(ctx: &MutationContext, input: Input) -> Result<Document> {
    let mut conn = ctx.conn().await?;
    let current = sqlx::query!("SELECT version, updated_at FROM documents WHERE id = $1", input.id)
        .fetch_one(&mut conn).await?;
    
    if input.base_version != current.version {
        // Conflict: document changed since user loaded it
        return Err(ForgeError::Conflict(format!(
            "Document was modified at {}. Refresh to see changes.",
            current.updated_at
        )));
    }
    
    // Update with new version
    sqlx::query_as!(Document,
        "UPDATE documents SET content = $1, version = version + 1 WHERE id = $2 RETURNING *",
        input.content, input.id
    ).fetch_one(&mut conn).await.map_err(Into::into)
}
```

### Delete on One Device, View on Another

Phone deletes item, desktop still showing detail view.

**Frontend:** SSE pushes updated list. Detail view handles missing item.

```svelte
{#if item.error?.code === 'NOT_FOUND'}
  <EmptyState message="This item was deleted" />
{:else}
  <!-- normal view -->
{/if}
```

### Optimistic Update vs Other Device's Change

Device A applies optimistic update, device B's change arrives via SSE.

**Frontend:** SSE data replaces optimistic patches. That's correct behavior. Use `createOptimisticMutation` / `use_optimistic` which handles this automatically.

Key: optimistic patches have short TTL (3s default). If SSE is slower than that, increase TTL.

---

## 7. Deployment & Migration Edge Cases

### Partial Migration

Some nodes ran migration, some didn't. Schema inconsistent.

**Prevention:** Forge uses advisory locks for migrations. Only one node migrates. Others wait.

**If it happens:** Use `forge migrate status` to check state. Manually resolve inconsistency.

### Enum Value Mismatch (Code vs DB)

New enum variant in code, not in DB. Or DB has value code doesn't know.

**Forward compatibility:** Always add `#[serde(other)] Unknown` variant.

**Backward compatibility:** Add DB enum value before deploying code that uses it.

```sql
-- Migration: add enum value first
ALTER TYPE task_status ADD VALUE 'archived';
```

Then deploy code that uses `TaskStatus::Archived`.

### Workflow Version Mismatch

Workflow handler changed, in-flight runs can't resume.

**Prevention:** Bump version on any contract change. Keep deprecated version until runs drain.

**Detection:** `/_api/ready` returns 503 if blocked runs exist.

**Recovery:** Either restore old handler or use operator tools to retire stuck runs.

---

## Checklist

Before marking a feature complete:

- [ ] What if the user's auth is revoked mid-action?
- [ ] What if the target entity is deleted before action completes?
- [ ] What if another user modifies the same data concurrently?
- [ ] What if the network drops during the operation?
- [ ] What if the user double-clicks / submits twice?
- [ ] What if the browser tab is backgrounded for hours?
- [ ] What if localStorage/IndexedDB is unavailable?
- [ ] What if a job/workflow step fails halfway?
- [ ] What if the user sees stale data and acts on it?
- [ ] What error message does the user see for each failure mode?
