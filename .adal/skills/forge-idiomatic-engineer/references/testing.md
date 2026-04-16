# Testing Reference

Writing integration tests that prove your app survives failure. Focus on what breaks, not just what works.

## Philosophy

Happy path tests prove nothing. Real bugs hide in edge cases: expired tokens, deleted data, race conditions, network failures. Every test should answer: "Does this fail gracefully when the world is hostile?"

**Test the failures first.** If you only have time for one test, make it the failure case.

---

## Backend Tests

### Auth Boundary Tests

```rust
#[tokio::test]
async fn rejects_missing_auth() {
    let ctx = TestQueryContext::minimal();
    let result = get_user_profile(&ctx).await;
    assert_err_variant!(result, ForgeError::Unauthorized(_));
}

#[tokio::test]
async fn rejects_wrong_role() {
    let ctx = TestQueryContext::builder()
        .as_user(Uuid::new_v4())
        .with_role("user")
        .build();
    let result = admin_dashboard(&ctx).await;
    assert_err_variant!(result, ForgeError::Forbidden(_));
}
```

### Missing Data Tests

```rust
#[tokio::test]
async fn get_item_returns_not_found() {
    let db = IsolatedTestDb::setup("missing_item", ...).await.unwrap();
    let ctx = TestQueryContext::builder()
        .as_user(Uuid::new_v4())
        .with_pool(db.pool().clone())
        .build();
    
    let result = get_item(&ctx, Uuid::new_v4()).await;
    assert_err_variant!(result, ForgeError::NotFound(_));
}

#[tokio::test]
async fn update_fails_if_deleted_concurrently() {
    let db = IsolatedTestDb::setup("concurrent_delete", ...).await.unwrap();
    let ctx = TestMutationContext::builder()
        .as_user(Uuid::new_v4())
        .with_pool(db.pool().clone())
        .build();
    
    let item = create_item(&ctx, CreateItemInput::new("Test")).await.unwrap();
    
    // Another user deletes it
    sqlx::query!("DELETE FROM items WHERE id = $1", item.id)
        .execute(db.pool()).await.unwrap();
    
    let result = update_item(&ctx, UpdateItemInput::new(item.id).title("New")).await;
    assert_err_variant!(result, ForgeError::NotFound(_));
}
```

### Ownership Tests

```rust
#[tokio::test]
async fn cannot_view_other_users_items() {
    let db = IsolatedTestDb::setup("ownership", ...).await.unwrap();
    
    // User A creates item
    let ctx_a = TestMutationContext::builder()
        .as_user(Uuid::new_v4())
        .with_pool(db.pool().clone())
        .build();
    let item = create_item(&ctx_a, CreateItemInput::new("A's item")).await.unwrap();
    
    // User B tries to view
    let ctx_b = TestQueryContext::builder()
        .as_user(Uuid::new_v4())
        .with_pool(db.pool().clone())
        .build();
    let result = get_item(&ctx_b, item.id).await;
    
    assert_err_variant!(result, ForgeError::NotFound(_));
}
```

### Job Tests

```rust
#[tokio::test]
async fn job_handles_missing_target() {
    let db = IsolatedTestDb::setup("job_missing", ...).await.unwrap();
    let ctx = TestJobContext::builder("process_item")
        .with_pool(db.pool().clone())
        .build();
    
    // Job should succeed (no-op), not fail
    let result = process_item(&ctx, Uuid::new_v4()).await;
    assert_ok!(result);
}

#[tokio::test]
async fn job_is_idempotent() {
    let db = IsolatedTestDb::setup("idempotent", ...).await.unwrap();
    let ctx = TestJobContext::builder("send_email")
        .with_pool(db.pool().clone())
        .build();
    
    let input = SendEmailInput::new("test@example.com");
    
    // Run twice, should only send once
    assert_ok!(send_email(&ctx, input.clone()).await);
    assert_ok!(send_email(&ctx, input).await);
    
    let count: i64 = sqlx::query_scalar!("SELECT COUNT(*) FROM sent_emails")
        .fetch_one(db.pool()).await.unwrap().unwrap_or(0);
    assert_eq!(count, 1);
}
```

---

## Frontend Tests (Playwright)

All frontend tests use real UI interactions. Never call RPC directly in tests.

### Fixtures

```typescript
// tests/fixtures.ts
import { test as base, expect } from '@playwright/test';

export const test = base.extend({
  authedPage: async ({ page }, use) => {
    await page.goto('/register');
    await page.getByLabel('Email').fill(`test-${Date.now()}@example.com`);
    await page.getByLabel('Password').fill('testpass123');
    await page.getByRole('button', { name: 'Register' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
  },
});

export async function waitForSSE(page: Page) {
  await page.waitForResponse(r => r.url().includes('/_api/subscribe'));
}

export const TIMEOUT = process.env.CI ? 15000 : 5000;
```

### Auth Failure Tests

```typescript
test('redirects to login when session expires', async ({ authedPage: page }) => {
  await page.goto('/dashboard');
  await waitForSSE(page);
  
  // Clear auth
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  
  await expect(page).toHaveURL(/\/login/);
});

test('shows message when account deleted', async ({ authedPage: page }) => {
  await page.goto('/settings');
  await waitForSSE(page);
  
  // Delete own account
  await page.getByRole('button', { name: 'Delete Account' }).click();
  await page.getByRole('button', { name: 'Confirm' }).click();
  
  // Should redirect with explanation
  await expect(page).toHaveURL(/\/login|\/goodbye/);
});
```

### Data Race Tests

```typescript
test('handles item deleted while viewing', async ({ authedPage: page }) => {
  // Create item via UI
  await page.goto('/items');
  await page.getByRole('button', { name: 'New Item' }).click();
  await page.getByLabel('Title').fill('To Delete');
  await page.getByRole('button', { name: 'Save' }).click();
  
  // Click into detail view
  await page.getByText('To Delete').click();
  await expect(page.getByRole('heading')).toContainText('To Delete');
  
  // Open second tab, delete the item
  const page2 = await page.context().newPage();
  await page2.goto('/items');
  await page2.getByText('To Delete').click();
  await page2.getByRole('button', { name: 'Delete' }).click();
  await page2.getByRole('button', { name: 'Confirm' }).click();
  await page2.close();
  
  // First tab should handle deletion gracefully
  await expect(page.locator('[data-deleted]')).toBeVisible({ timeout: TIMEOUT });
  // Or redirects away
});

test('list updates when item deleted elsewhere', async ({ authedPage: page }) => {
  // Create two items
  await page.goto('/items');
  for (const title of ['Item 1', 'Item 2']) {
    await page.getByRole('button', { name: 'New Item' }).click();
    await page.getByLabel('Title').fill(title);
    await page.getByRole('button', { name: 'Save' }).click();
  }
  
  await expect(page.getByTestId('item')).toHaveCount(2);
  
  // Delete one in another tab
  const page2 = await page.context().newPage();
  await page2.goto('/items');
  await page2.getByText('Item 1').click();
  await page2.getByRole('button', { name: 'Delete' }).click();
  await page2.getByRole('button', { name: 'Confirm' }).click();
  await page2.close();
  
  // SSE updates first tab
  await expect(page.getByTestId('item')).toHaveCount(1, { timeout: TIMEOUT });
});
```

### Double Submit Tests

```typescript
test('prevents double form submission', async ({ authedPage: page }) => {
  await page.goto('/items/new');
  await page.getByLabel('Title').fill('Single Item');
  
  const submit = page.getByRole('button', { name: 'Save' });
  
  // Double click
  await Promise.all([submit.click(), submit.click()]);
  
  // Wait for navigation
  await page.waitForURL(/\/items\//);
  
  // Go to list, verify only one created
  await page.goto('/items');
  const items = page.getByText('Single Item');
  await expect(items).toHaveCount(1);
});

test('button disabled during submission', async ({ authedPage: page }) => {
  await page.goto('/items/new');
  await page.getByLabel('Title').fill('Test');
  
  const submit = page.getByRole('button', { name: 'Save' });
  await submit.click();
  
  await expect(submit).toBeDisabled();
});
```

### Network Failure Tests

```typescript
test('shows offline state', async ({ authedPage: page }) => {
  await page.goto('/dashboard');
  await waitForSSE(page);
  
  await page.context().setOffline(true);
  await page.waitForTimeout(1000);
  
  await expect(page.getByTestId('offline-indicator')).toBeVisible();
});

test('mutation fails gracefully when offline', async ({ authedPage: page }) => {
  await page.goto('/items');
  await waitForSSE(page);
  
  await page.context().setOffline(true);
  
  await page.getByRole('button', { name: 'New Item' }).click();
  await page.getByLabel('Title').fill('Offline Item');
  await page.getByRole('button', { name: 'Save' }).click();
  
  await expect(page.getByText(/network|offline|connection/i)).toBeVisible();
});
```

### SSE Reconnection Tests

```typescript
test('data stays fresh after reconnect', async ({ authedPage: page }) => {
  await page.goto('/items');
  await waitForSSE(page);
  
  // Create initial item
  await page.getByRole('button', { name: 'New Item' }).click();
  await page.getByLabel('Title').fill('Before');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByTestId('item')).toHaveCount(1);
  
  // Block SSE briefly
  await page.route('**/_api/events*', route => route.abort());
  await page.waitForTimeout(2000);
  await page.unroute('**/_api/events*');
  
  // Create item in another tab during "disconnect"
  const page2 = await page.context().newPage();
  await page2.goto('/items');
  await page2.getByRole('button', { name: 'New Item' }).click();
  await page2.getByLabel('Title').fill('During');
  await page2.getByRole('button', { name: 'Save' }).click();
  await page2.close();
  
  // First tab should catch up
  await expect(page.getByTestId('item')).toHaveCount(2, { timeout: TIMEOUT });
});
```

---

## Checklist

**Backend:**
- [ ] Missing auth returns 401
- [ ] Wrong role returns 403
- [ ] Missing entity returns 404
- [ ] User can only access own data
- [ ] Job handles missing target
- [ ] Idempotent operations are idempotent

**Frontend:**
- [ ] Handles auth expiry
- [ ] Handles deleted data gracefully
- [ ] No double submit
- [ ] Handles offline
- [ ] SSE reconnection works
