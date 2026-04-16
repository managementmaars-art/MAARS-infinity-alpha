# SaaS Domain Patterns

## Subscription States
```
trial → active → past_due → canceled → expired
              ↘ paused ↗
```

**State Invariants:**
- `trial`: No charges, limited features
- `active`: Valid payment, full access per plan
- `past_due`: Payment failed, grace period
- `canceled`: User initiated, access until period end
- `expired`: No access, no billing

## Billing Patterns

### Proration
```
prorated_amount = (days_remaining / total_days) * plan_price
```

**Edge cases:** Leap years, month-end boundaries, same-day changes, timezone cutoffs.

### Upgrade/Downgrade
- **Upgrade:** Immediate charge + access
- **Downgrade:** Schedule for period end, no refund

## Multi-Tenancy

### Isolation Levels
| Level | Method | Security |
|-------|--------|----------|
| Database | Separate DB | Highest |
| Schema | Same DB, diff schema | High |
| Row | Same table, tenant_id | Standard |

### Critical Rules
```sql
-- ALWAYS include tenant_id
SELECT * FROM data WHERE id = ? AND tenant_id = ?

-- NEVER trust user input
tenant_id = session.tenant_id  -- NOT req.body.tenant_id
```

## Feature Flags & Entitlements

### Check Hierarchy
1. Tenant override (custom deals)
2. Plan entitlement (standard)
3. Default (free tier)

### Anti-patterns
- Checking flags in frontend only
- Stale cache after plan change
- Hardcoded limits

## User & Roles

### Standard Hierarchy
```
Owner > Admin > Member > Viewer > Guest
```

### Edge Cases
- Last owner protection
- Pending invite expiration
- SSO role mapping conflicts
