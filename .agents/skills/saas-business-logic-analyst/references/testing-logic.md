# Testing Business Logic — Strategic Approach

> Los tests de lógica de negocio no verifican que el código funcione. Verifican que el negocio no se rompa.

## Filosofía de Testing Senior

### Qué Testear (Prioridad)
1. **Invariantes de negocio** — Reglas que nunca deben violarse
2. **Transiciones de estado** — Caminos válidos e inválidos
3. **Edge cases con impacto económico** — Priorizados por severidad
4. **Comportamiento bajo falla** — Qué pasa cuando algo falla

### Qué NO Testear
- Implementación interna (mockear todo es anti-pattern)
- Bibliotecas de terceros
- Validaciones triviales
- Happy paths obvios

### Señal de Test Valioso
```
Si este test falla, ¿perdemos dinero o confianza?
Sí → Test valioso
No → Probablemente innecesario
```

---

## Tests de Invariantes (Críticos)

Cada invariante de negocio debe tener tests explícitos que la protegen.

### INV-F4: Trial = $0 cobrado
```javascript
describe('INV-F4: Trial Billing Invariant', () => {
  it('trial subscription NEVER generates charges', async () => {
    const sub = await createTrialSubscription({ plan: 'pro', days: 14 });

    // Simular paso de tiempo dentro del trial
    await advanceTime(7, 'days');
    await runBillingCycle();

    const invoices = await getInvoices(sub.customerId);
    const chargedInvoices = invoices.filter(i => i.amountPaid > 0);

    expect(chargedInvoices).toHaveLength(0);
    // Verificar también que no hay invoices pending
    expect(invoices.filter(i => i.status === 'pending' && i.amount > 0)).toHaveLength(0);
  });

  it('trial extended STILL never charges', async () => {
    const sub = await createTrialSubscription({ days: 14 });
    await extendTrial(sub.id, 7); // Ahora son 21 días

    await advanceTime(20, 'days');
    await runBillingCycle();

    expect(await getCharges(sub.customerId)).toHaveLength(0);
  });

  // Edge case: Trial que termina exactamente a medianoche
  it('trial ending at midnight boundary does not charge early', async () => {
    const sub = await createTrialSubscription({ endsAt: '2024-01-15T00:00:00Z' });

    await setTime('2024-01-14T23:59:59Z');
    await runBillingCycle();

    expect(await getCharges(sub.customerId)).toHaveLength(0);
  });
});
```

### INV-F5: Cancelled = No future billing
```javascript
describe('INV-F5: Cancellation Billing Invariant', () => {
  it('canceled subscription NEVER bills after cancel date', async () => {
    const sub = await createActiveSubscription();
    const canceledAt = await cancelSubscription(sub.id);

    // Avanzar más allá del período actual
    await advanceTime(60, 'days');
    await runBillingCycle();
    await runBillingCycle(); // Dos ciclos para asegurar

    const invoicesAfterCancel = await getInvoices(sub.customerId, {
      createdAfter: canceledAt
    });

    expect(invoicesAfterCancel).toHaveLength(0);
  });

  it('cancel then resubscribe creates NEW subscription', async () => {
    const sub1 = await createActiveSubscription();
    await cancelSubscription(sub1.id);

    const sub2 = await createActiveSubscription({ customerId: sub1.customerId });

    expect(sub2.id).not.toBe(sub1.id);
    // Verificar que el billing es del nuevo, no resurreción del viejo
    const invoices = await getInvoices(sub1.customerId);
    expect(invoices.every(i => i.subscriptionId === sub2.id || i.createdAt < sub1.canceledAt)).toBe(true);
  });
});
```

### INV-D1: Tenant Isolation
```javascript
describe('INV-D1: Tenant Isolation Invariant', () => {
  let tenantA, tenantB, userA, userB;

  beforeEach(async () => {
    tenantA = await createTenant();
    tenantB = await createTenant();
    userA = await createUser({ tenantId: tenantA.id });
    userB = await createUser({ tenantId: tenantB.id });
  });

  it('user CANNOT access other tenant data via direct ID', async () => {
    const dataA = await createData({ tenantId: tenantA.id, content: 'secret' });

    await loginAs(userB);
    await expect(getData(dataA.id)).rejects.toThrow(/not found|forbidden/i);
  });

  it('user CANNOT access other tenant data via list', async () => {
    await createData({ tenantId: tenantA.id, content: 'secretA' });
    await createData({ tenantId: tenantB.id, content: 'secretB' });

    await loginAs(userB);
    const list = await listData();

    expect(list.every(d => d.tenantId === tenantB.id)).toBe(true);
    expect(list.some(d => d.content === 'secretA')).toBe(false);
  });

  it('bulk export ONLY includes own tenant data', async () => {
    await createData({ tenantId: tenantA.id, count: 100 });
    await createData({ tenantId: tenantB.id, count: 50 });

    await loginAs(userB);
    const exported = await bulkExport();

    expect(exported).toHaveLength(50);
    expect(exported.every(d => d.tenantId === tenantB.id)).toBe(true);
  });

  it('background job respects tenant context', async () => {
    const job = await queueJob('processData', {
      tenantId: tenantA.id,
      dataId: 'some-id'
    });

    await processJob(job);

    // Verificar que el job no accedió a datos de otro tenant
    const auditLog = await getAuditLog({ jobId: job.id });
    expect(auditLog.every(log => log.tenantId === tenantA.id)).toBe(true);
  });
});
```

---

## Tests de Transiciones de Estado

```javascript
describe('Subscription State Machine', () => {
  const validTransitions = {
    trial:    ['active', 'canceled'],
    active:   ['past_due', 'canceled', 'paused'],
    past_due: ['active', 'canceled'],
    paused:   ['active', 'canceled'],
    canceled: [], // Terminal state
    expired:  [], // Terminal state
  };

  Object.entries(validTransitions).forEach(([fromState, allowedStates]) => {
    describe(`from ${fromState}`, () => {
      allowedStates.forEach(toState => {
        it(`CAN transition to ${toState}`, async () => {
          const sub = await createSubscriptionInState(fromState);
          await expect(transitionTo(sub.id, toState)).resolves.toBeDefined();
        });
      });

      const allStates = ['trial', 'active', 'past_due', 'paused', 'canceled', 'expired'];
      const disallowedStates = allStates.filter(s => s !== fromState && !allowedStates.includes(s));

      disallowedStates.forEach(toState => {
        it(`CANNOT transition to ${toState}`, async () => {
          const sub = await createSubscriptionInState(fromState);
          await expect(transitionTo(sub.id, toState)).rejects.toThrow(/invalid transition/i);
        });
      });
    });
  });
});
```

---

## Tests de Edge Cases con Impacto Económico

### Proration (P1 — Revenue Leak)
```javascript
describe('Proration Edge Cases', () => {
  it('upgrade on last day of cycle charges minimal prorated amount', async () => {
    const sub = await createSubscription({ plan: 'basic', price: 100 });
    await setToLastDayOfBillingCycle(sub);

    const result = await upgradePlan(sub.id, 'pro', { price: 200 });

    // Debería cobrar ~1/30 de la diferencia, no el monto completo
    expect(result.proratedCharge).toBeLessThan(10); // Menos de $10
    expect(result.proratedCharge).toBeGreaterThan(0);
  });

  it('same-day upgrade then downgrade results in correct net charge', async () => {
    const sub = await createSubscription({ plan: 'basic', price: 100 });

    await upgradePlan(sub.id, 'pro', { price: 200 });
    await downgradePlan(sub.id, 'basic', { price: 100 });

    const totalCharges = await getTodayCharges(sub.customerId);
    // Downgrade es schedulado, upgrade es inmediato
    // Net debería ser solo el upgrade proration
    expect(totalCharges.length).toBe(1);
  });

  it('leap year February 29 proration is correct', async () => {
    await setDate('2024-02-29'); // Leap year
    const sub = await createSubscription({ plan: 'basic' });

    const proration = calculateProration(sub, 'pro', { from: '2024-02-29' });

    // Febrero 2024 tiene 29 días, no 28
    expect(proration.daysInPeriod).toBe(29);
  });
});
```

### Idempotency (P0 — Double Charge)
```javascript
describe('Webhook Idempotency', () => {
  it('processing invoice.paid twice does NOT double-credit', async () => {
    const webhook = createWebhook('invoice.paid', { invoiceId: 'inv_123', amount: 100 });

    await processWebhook(webhook);
    const stateAfterFirst = await getSubscriptionState('inv_123');

    await processWebhook(webhook); // Same webhook again
    const stateAfterSecond = await getSubscriptionState('inv_123');

    expect(stateAfterFirst).toEqual(stateAfterSecond);
    expect(await getTotalCreditsApplied('inv_123')).toBe(100); // Not 200
  });

  it('concurrent webhook processing is safe', async () => {
    const webhook = createWebhook('invoice.paid', { invoiceId: 'inv_456', amount: 100 });

    // Procesar el mismo webhook en paralelo (simula race condition)
    await Promise.all([
      processWebhook(webhook),
      processWebhook(webhook),
      processWebhook(webhook),
    ]);

    expect(await getTotalCreditsApplied('inv_456')).toBe(100);
  });
});
```

---

## Property-Based Testing

Para reglas que deben cumplirse siempre:

```javascript
import fc from 'fast-check';

describe('Proration Properties', () => {
  it('prorated amount is ALWAYS between 0 and full price', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 31 }),    // days remaining
        fc.integer({ min: 1, max: 31 }),    // total days
        fc.integer({ min: 100, max: 100000 }), // price in cents
        (remaining, total, price) => {
          if (remaining > total) return true; // Skip invalid
          const prorated = calculateProration(remaining, total, price);
          return prorated >= 0 && prorated <= price;
        }
      )
    );
  });

  it('refund NEVER exceeds original payment', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 100, max: 100000 }), // original amount
        fc.integer({ min: 1, max: 100 }),       // refund percentage requested
        (original, percentage) => {
          const refund = calculateRefund(original, percentage);
          return refund <= original;
        }
      )
    );
  });
});
```

---

## Test Smells (Qué Evitar)

### ❌ Test de Implementación (Frágil)
```javascript
// MALO: Se rompe si cambiamos la implementación
it('calls Stripe with correct params', async () => {
  await upgradeSubscription(subId, 'pro');
  expect(mockStripe.createSubscription).toHaveBeenCalledWith({
    customer: 'cus_123',
    items: [{ price: 'price_pro' }]
  });
});
```

### ✅ Test de Comportamiento (Robusto)
```javascript
// BUENO: Verifica el resultado de negocio
it('upgrade changes plan and access', async () => {
  const result = await upgradeSubscription(subId, 'pro');

  expect(result.plan).toBe('pro');
  expect(await hasAccess(subId, 'pro_feature')).toBe(true);
  expect(await hasAccess(subId, 'basic_feature')).toBe(true);
});
```

### ❌ Test sin Valor de Negocio
```javascript
// MALO: ¿Quién pierde dinero si esto falla?
it('returns correct HTTP status', async () => {
  const res = await request.get('/subscriptions');
  expect(res.status).toBe(200);
});
```

### ✅ Test con Impacto Claro
```javascript
// BUENO: Claramente protege revenue
it('expired subscription denies access to paid features', async () => {
  const sub = await expireSubscription(activeSubId);
  await expect(accessPaidFeature(sub.userId)).rejects.toThrow(/upgrade required/i);
});
```

---

## Cobertura Mínima Recomendada

| Área | Tests Críticos | Por Qué |
|------|----------------|---------|
| Cada invariante INV-Fx | 2-5 tests | Protegen revenue |
| Cada invariante INV-Dx | 3-5 tests | Protegen datos |
| State machine completa | 1 test por transición | Evitan estados inválidos |
| Top 5 edge cases P0/P1 | 1-2 tests cada uno | ROI más alto |
| Idempotency de webhooks | 3-5 tests | Evitan double-charge |

### Pregunta de Auditoría de Tests
```
Para cada invariante de negocio:
□ ¿Hay al menos un test que la verifica explícitamente?
□ ¿El test fallaría si alguien rompe la invariante?
□ ¿El test es legible para alguien de producto/finanzas?
```
