# System Design Questions para Senior Full-Stack Developer

## Preguntas Comunes + Como Abordarlas

### 1. "Diseña un sistema de reservas como Booking.com"

**Relevancia:** Directamente relacionado con HostelOS

**Approach:**
```
Requirements (5 min):
- Usuarios: huespedes + propietarios
- Funcionalidades: buscar, reservar, pagar, gestionar
- Escala: 100K propiedades, 1M reservas/mes
- Constraints: no double-booking, multi-timezone

High-Level Design:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   API GW    │────▶│  Services   │
│  (React)    │     │  (Nginx)    │     │  (Node.js)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
             ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
             │  Bookings   │          │  Inventory  │          │  Payments   │
             │  Service    │          │  Service    │          │  Service    │
             └─────────────┘          └─────────────┘          └─────────────┘
                    │                         │                         │
                    ▼                         ▼                         ▼
             ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
             │ PostgreSQL  │          │   Redis     │          │   Stripe    │
             │ (bookings)  │          │ (availability)│        │   (ext)     │
             └─────────────┘          └─────────────┘          └─────────────┘

Deep Dive - Preventing Double Booking:
1. Optimistic locking con version field
2. Redis para availability check rapido
3. PostgreSQL transaction con SELECT FOR UPDATE
4. Idempotency key para reintentos seguros

Trade-offs:
- Redis vs pure DB: velocidad vs consistencia
- Sync vs async booking: UX vs reliability
```

**Tu experiencia para mencionar:**
"En HostelOS resolvi exactamente esto. Usamos PostgreSQL con row-level locking y Redis para cache de disponibilidad. El challenge fue sincronizar con OTAs externas via iCal..."

---

### 2. "Diseña un sistema multi-tenant SaaS"

**Relevancia:** Core de tu experiencia (HostelOS, Digitaliza)

**Approach:**
```
Requirements:
- Isolation: datos de tenants separados
- Customization: features por plan
- Scale: 1000 tenants, variable load

Estrategias de Tenancy:

1. SILO (database per tenant)
   Pros: isolation total, compliance facil
   Cons: caro, migrations complejas
   Usar cuando: datos sensibles (healthcare, finance)

2. POOL (shared database, tenant_id column)
   Pros: simple, economico
   Cons: risk de data leak, noisy neighbor
   Usar cuando: startups, low compliance

3. BRIDGE (schema per tenant)
   Pros: balance isolation/costo
   Cons: connection management complejo
   Usar cuando: mid-size, moderate compliance

Mi eleccion para escala media: POOL con row-level security

Implementation:
- Middleware que extrae tenant_id del JWT
- PostgreSQL RLS policies por tabla
- Redis cache con namespace por tenant
- Feature flags por tenant/plan
```

**Tu experiencia:**
"En HostelOS use pool model con tenant_id en cada tabla. Implemente middleware que inyecta el tenant context automaticamente. Para Digitaliza, donde hay mas negocios pequenos, el mismo approach pero con feature flags por plan..."

---

### 3. "Diseña un sistema de notificaciones multi-canal"

**Relevancia:** Tu experiencia con WhatsApp, email, SMS

**Approach:**
```
Requirements:
- Canales: email, SMS, WhatsApp, push
- Escala: 100K notifs/dia
- Reliability: guaranteed delivery
- Preferences: usuarios eligen canales

Architecture:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Producer   │────▶│   Queue     │────▶│  Workers    │
│  (API)      │     │  (Redis)    │     │  (Node.js)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                    ┌─────────────────────────┼───────────────┐
                    ▼                         ▼               ▼
             ┌─────────────┐          ┌─────────────┐  ┌─────────────┐
             │  Email      │          │  WhatsApp   │  │    SMS      │
             │  (SendGrid) │          │  (Meta API) │  │  (Twilio)   │
             └─────────────┘          └─────────────┘  └─────────────┘

Key Decisions:
1. Queue per channel vs unified queue
   → Unified con routing logic (simpler)

2. Retry strategy
   → Exponential backoff: 1s, 2s, 4s, 8s, 16s
   → Dead letter queue despues de 5 intentos

3. Delivery tracking
   → Webhook handlers para status updates
   → Estado: pending → sent → delivered/failed

4. Rate limiting
   → Per-provider limits (WhatsApp: 1000/min)
   → Token bucket algorithm
```

**Tu experiencia:**
"Implemente esto en HostelOS para confirmaciones de reserva. El mayor challenge fue manejar los diferentes rate limits de cada provider y asegurar que si WhatsApp falla, el usuario recibe email como fallback..."

---

### 4. "Diseña sincronizacion con APIs externas (OTAs)"

**Relevancia:** Tu experiencia con iCal sync

**Approach:**
```
Challenges:
- APIs inconsistentes (formatos, timezones)
- Rate limits variados
- Estados conflictivos
- Latencia variable

Architecture:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Internal   │◀───▶│   Sync      │◀───▶│  External   │
│  System     │     │   Engine    │     │   APIs      │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                    ┌─────┴─────┐
                    ▼           ▼
             ┌─────────────┐  ┌─────────────┐
             │  Sync Log   │  │  Conflict   │
             │  (history)  │  │  Resolution │
             └─────────────┘  └─────────────┘

Sync Strategies:
1. Push-based (webhooks)
   Pros: real-time
   Cons: requires partner support

2. Pull-based (polling)
   Pros: works with any API
   Cons: delay, resource intensive

3. Hybrid (mi approach)
   → Webhooks when available
   → Polling como fallback
   → Periodic reconciliation job

Conflict Resolution:
- Last-write-wins (simple, risky)
- Source-of-truth (designar master)
- Manual resolution (queue para review)
→ Elegi source-of-truth: internal system wins, notify of conflicts
```

**Tu experiencia:**
"En HostelOS, la sincronizacion iCal con Booking/Airbnb fue el challenge mas complejo. iCal no tiene estados, solo bloques de tiempo. Tuve que implementar un reconciliador que detecta diferencias y las resuelve automaticamente, notificando solo conflictos reales..."

---

### 5. "Diseña un sistema de pagos"

**Relevancia:** Tu experiencia con Stripe

**Approach:**
```
Requirements:
- Procesar pagos one-time y subscriptions
- Multi-currency
- Refunds, disputes
- PCI compliance

Architecture (Stripe-based):
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │────▶│   Stripe    │
│  (React)    │     │   (Node)    │     │   API       │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                    │
      │              ┌────┴────┐               │
      │              ▼         ▼               │
      │       ┌──────────┐ ┌──────────┐        │
      │       │  Orders  │ │ Payments │        │
      │       │   DB     │ │  Events  │◀───────┘
      │       └──────────┘ └──────────┘   (webhooks)
      │                         │
      └─────────────────────────┘
        (Stripe Elements - PCI compliant)

Key Decisions:
1. Never store card data → Stripe Elements
2. Webhook reliability
   → Verify signatures
   → Idempotent handlers (payment_intent_id as key)
   → Retry logic para failures
3. Currency handling
   → Store in cents (integer)
   → Format display with locale
```

**Tu experiencia:**
"En Digitaliza integre Stripe para Colombia, que tiene formato sin decimales (COP). El challenge fue que Stripe espera centavos pero Colombia no usa centavos. Implemente conversion layer que maneja esto transparentemente..."

---

## Template de Respuesta System Design

```
1. "Antes de disenar, quiero clarificar algunos requirements..."
   - Escala esperada (usuarios, requests/sec)
   - Funcionalidades core vs nice-to-have
   - Constraints especiales (latencia, compliance)

2. "Dejame dibujar el high-level design..."
   - Dibujar componentes principales
   - Explicar data flow
   - Identificar servicios criticos

3. "Quiero profundizar en [componente critico]..."
   - Elegir el mas complejo
   - Explicar decisiones de diseño
   - Mencionar trade-offs

4. "Sobre escalabilidad y reliability..."
   - Single points of failure
   - Scaling strategy
   - Monitoring/alerting

5. "Si tuviera mas tiempo, mejoraria..."
   - Optimizaciones pendientes
   - Features adicionales
```

## Errores Comunes a Evitar

```
❌ Saltar a solucion sin clarificar requirements
❌ Over-engineer para escala que no necesitas
❌ Ignorar failure scenarios
❌ No mencionar trade-offs
❌ Olvidar monitoring/observability
```
