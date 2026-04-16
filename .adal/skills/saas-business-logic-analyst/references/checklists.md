# Audit Checklists

## Billing Audit
```
□ Trial status checked before any charge?
□ Cancel date checked before generating invoices?
□ Proration calculated correctly at boundaries?
□ Webhooks idempotent (idempotency key)?
□ Grace period for failed payments?
□ Dunning retries scheduled?
□ Refund validated against original charge?
```

## Multi-Tenant Audit
```
□ EVERY query includes tenant_id in WHERE?
□ tenant_id from session, never user input?
□ Cache keys prefixed with tenant_id?
□ Background jobs receive tenant context?
□ Search indices filtered by tenant?
□ File paths namespaced by tenant?
□ Admin bypasses documented?
```

## Authorization Audit
```
□ Permissions checked server-side?
□ Last-owner protection exists?
□ Seat limits enforced atomically?
□ Role changes audited?
□ API endpoints validate permissions?
```

## Integration Audit
```
□ Webhook handlers idempotent?
□ Retry logic for API failures?
□ Webhook vs API response race handled?
□ API timeouts graceful?
□ Eventual consistency reconciliation?
```

## Scaling Audit
```
□ Plan names NOT hardcoded?
□ Multi-currency supported?
□ Timezone NOT hardcoded?
□ No N+1 queries in critical paths?
□ List endpoints paginated?
□ Expensive operations async/queued?
```

## Compliance Audit
```
□ User data fully deletable (GDPR)?
□ PII encrypted at rest?
□ Audit logs comprehensive?
□ Data retention policy exists?
□ Consent records maintained?
```

## Organizational Health
```
□ >2 people understand billing logic?
□ WHY decisions documented?
□ Critical code reviewed <1 year ago?
□ No "untouchable" code?
□ Onboarding to billing <2 weeks?
```

## Due Diligence
```
□ MRR reported vs calculated match?
□ Revenue leakage risks identified?
□ Bus factor for critical systems?
□ Compliance gaps (GDPR, SOC2)?
□ What breaks at 10x scale?
□ What blocks enterprise sales?
```
