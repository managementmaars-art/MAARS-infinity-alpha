# SaaS Edge Cases — Strategic Framework

> Un edge case no es interesante por su rareza técnica, sino por su potencial de destrucción silenciosa del negocio.

## Invariantes de Negocio (Eje Central)

Toda auditoría parte de aquí. Estas reglas NUNCA deben violarse:

### Financieras (P0 — Violación = Crisis)
```
INV-F1: Cliente nunca paga más de lo acordado
        Violación → Chargebacks ($15-25 por disputa) + pérdida de trust + legal
        Ejemplo: 100 overcharges/mes × $20 = $2,000 directo + churn cascada

INV-F4: Trial = $0 cobrado
        Violación → Chargebacks masivos, 1-star reviews, PR crisis
        Ejemplo: 1,000 trials × 5% error × $50 cargo = $2,500 + reputación

INV-F5: Cancelled = no billing futuro
        Violación → Demandas colectivas, multas regulatorias, muerte de confianza
        Ejemplo: Un solo caso viral en Twitter = crisis existencial
```

### De Datos (P0 — Violación = Muerte)
```
INV-D1: Datos Tenant A nunca visibles para Tenant B
        Violación → Pérdida de clientes enterprise, demandas, fin del negocio
        Costo promedio de breach: $4.45M (IBM 2024)
        Para startup: 30-50% de clientes enterprise se van inmediatamente

INV-D2: Delete = irrecuperable (GDPR)
        Violación → Multas hasta 4% revenue global + pérdida de mercado EU
```

### De Acceso (P1 — Violación = Revenue Leak)
```
INV-A1: Sin pago válido = sin features de pago
        Violación → Revenue leakage silencioso
        Ejemplo: 5% de cuentas con acceso indebido × $100 ARPU × 1,000 cuentas = $5,000/mes

INV-A2: Role X = solo acciones de Role X
        Violación → Escalación de privilegios, potencial breach
```

---

## Severidad con Justificación Económica

### P0 — Existencial
| Edge Case | Por Qué P0 | Impacto Calculado |
|-----------|------------|-------------------|
| Trial cobra dinero | INV-F4 + chargebacks + reviews | $2K-10K directo + reputación incalculable |
| Billing post-cancel | INV-F5 + legal + reguladores | Un caso viral = crisis existencial |
| Data leak cross-tenant | INV-D1 + breach | $100K-$4M + pérdida 30-50% enterprise |
| Overcharge sistemático | INV-F1 + disputes | $15-25/disputa + 2% processing fee risk |

### P1 — Crítico ($10K-$100K/mes)
| Edge Case | Por Qué P1 | Impacto Calculado |
|-----------|------------|-------------------|
| No dunning retries | 0.5-1% MRR en churn involuntario | MRR $100K → $500-1,000/mes perdido |
| Proration undercharge | 1-3% revenue leak si sistemático | MRR $100K → $1,000-3,000/mes leak |
| Seat limit bypass | Revenue no cobrado | 5% accounts × $20/seat = $1,000/mes |
| Cache sin tenant key | Exposición de datos potencial | Pre-breach, pero un error = P0 |

### P2 — Significativo ($1K-$10K/mes)
| Edge Case | Por Qué P2 | Impacto Calculado |
|-----------|------------|-------------------|
| Trial abuse (emails) | 2-5% trials fraudulentos | 1,000 trials × 3% × 15% conv × $100 = $450/mes |
| Timezone billing errors | Support tickets + confusion | 10 tickets/mes × $50/ticket = $500/mes |
| Same-day plan changes | Complejidad + support | Costo operativo, no revenue directo |

### P3 — Deuda Aceptable (<$1K/mes)
| Edge Case | Por Qué P3 | Impacto |
|-----------|------------|---------|
| Feb 29 edge case | Afecta <0.3% de usuarios | Bajo volumen |
| Webhook ordering raro | Reconciliable manualmente | Costo operativo menor |

---

## Billing Edge Cases (Detalle)

### Trial
| Caso | Invariante | Impacto Económico | Detección |
|------|------------|-------------------|-----------|
| Trial cobra | INV-F4 **P0** | Chargebacks + reviews + legal | Query: invoices WHERE trial=true AND amount>0 |
| Trial extension error | - P2 | Confusion, 5-10 tickets/mes | Logs de extensiones |
| Multi-trial abuse | - P2 | 2-5% revenue leak en conversiones | Fingerprinting, domain analysis |

### Proration
| Caso | Invariante | Impacto Económico | Detección |
|------|------------|-------------------|-----------|
| Overcharge | INV-F1 **P0** | Disputes a $20/cada + trust | Reconciliación: charged vs calculated |
| Undercharge sistemático | - **P1** | 1-3% MRR si frecuente | Audit mensual: expected vs actual |
| Same-day changes | - P2 | Complejidad, no revenue | Logs de cambios múltiples |

### Cancellation
| Caso | Invariante | Impacto Económico | Detección |
|------|------------|-------------------|-----------|
| Billing post-cancel | INV-F5 **P0** | Legal + reguladores + PR | Query: invoices.created_at > subscription.canceled_at |
| No win-back flow | - P2 | 5-10% de churned recuperable | Funnel analysis post-cancel |

### Dunning
| Caso | Invariante | Impacto Económico | Detección |
|------|------------|-------------------|-----------|
| Double charge on retry | INV-F1 **P0** | Disputes masivos | Idempotency key tracking |
| No retry configured | - **P1** | 0.5-1% MRR en involuntary churn | Dunning sequence audit |
| Grace period muy corto | - P1 | Churn evitable, LTV reducido | Benchmark: <3 días es problema |

---

## Multi-Tenancy Edge Cases

| Caso | Invariante | Impacto | Detección |
|------|------------|---------|-----------|
| Query sin tenant_id | INV-D1 **P0** | Breach potencial | Static analysis, query logging |
| Cache key sin tenant | INV-D1 **P0** | Data exposure | Code review de cache layer |
| Bulk export sin filter | INV-D1 **P0** | Data masivo expuesto | Audit de export functions |
| Background job sin context | - **P1** | Operación en tenant equivocado | Job logging + tenant validation |
| Search index leak | INV-D3 **P1** | PII visible | Search query analysis |

---

## Evolution Risks — Preparación y Costo

| Cambio Futuro | Qué Se Rompe | Señales de Fragilidad | Costo de Adaptación |
|---------------|--------------|----------------------|---------------------|
| Nuevo tier de pricing | if (plan === 'pro') | Hardcoded plan names en código | 2-4 semanas dev + testing |
| Multi-currency | amount × 1 asumido | Sin currency field en DB | 4-8 semanas + migración |
| Enterprise SSO | Auth propio | Sin support para SAML/OIDC | 6-12 semanas + certificaciones |
| Geographic expansion | Sin data residency | Single region, no GDPR | 8-16 semanas + legal |
| Usage-based billing | Flat rate everywhere | Sin metering infrastructure | 12-24 semanas + rewrite |

### Evaluación de Deuda de Evolución
```
Para cada área crítica, evaluar:
□ ¿Cuántas líneas de código asumen el modelo actual?
□ ¿Cuántos tests se romperían con el cambio?
□ ¿Quién entiende el código lo suficiente para cambiarlo?
□ ¿Hay documentación del "por qué" de las decisiones?

Score:
- 0-2: Sistema flexible, pivot viable
- 3-5: Esfuerzo significativo pero manejable
- 6+: Rewrite probable, planificar con anticipación
```

---

## Discovery Questions — Framework Estratégico

### Nivel Técnico (Baseline)
- ¿Qué pasa si esto falla?
- ¿Qué pasa si esto se ejecuta dos veces?
- ¿Qué pasa al final del mes?

### Nivel Operativo (Senior)
- ¿Cuántos tickets de soporte genera esto al mes?
- ¿Cuánto revenue perdemos si esto falla silenciosamente?
- ¿Tenemos alertas cuando esto falla?
- ¿Podemos detectar fallas silenciosas?

### Nivel Estratégico (15+ años)
- **¿Qué parte del negocio depende de que esto funcione?**
- **¿Esto nos bloquea para enterprise?**
- **¿Sobrevive esto al próximo pivot de pricing?**
- **¿Qué pasa cuando tengamos 10x usuarios?**
- **¿Quién más entiende esta lógica si el autor se va?**

### Nivel Ejecutivo (Principal/Staff)
- ¿Cuál es el impacto en MRR si esto falla un día completo?
- ¿Esto afecta nuestra valoración o due diligence?
- ¿Cumplimos SOC2/GDPR con esto?
- ¿Podemos vender a enterprise con esta arquitectura?

---

## Checklist de Auditoría por Invariante

### Para cada INV-Fx (Financiera):
```
□ ¿Hay código que protege explícitamente esta invariante?
□ ¿Hay tests que verifican que nunca se viole?
□ ¿Hay alertas que detectan violaciones en producción?
□ ¿Hay reconciliación periódica que la valida?
□ ¿Cuántas personas entienden esta protección?
```

### Para cada INV-Dx (Datos):
```
□ ¿Está el aislamiento en un layer central o disperso?
□ ¿Hay forma de bypass no autorizado?
□ ¿Los tests cubren intentos de acceso cross-tenant?
□ ¿Hay audit log de accesos?
□ ¿Qué pasa en background jobs y async operations?
```
