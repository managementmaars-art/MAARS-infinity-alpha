# Technical Deep Dives - Preguntas por Area

Preguntas tecnicas profundas que validan tu nivel senior.

## JavaScript/TypeScript

### "Explica el Event Loop"

**Respuesta Senior:**
```
"El event loop es el mecanismo que permite a Node.js manejar operaciones
asincronas siendo single-threaded.

Funciona asi:
1. Call Stack ejecuta codigo sincronico
2. Operaciones async (I/O, timers) van a la Web API
3. Cuando completan, callbacks van a la Task Queue
4. Event loop mueve tasks al stack cuando esta vacio

Hay dos queues:
- Microtask queue (Promises, queueMicrotask) - prioridad alta
- Macrotask queue (setTimeout, I/O) - prioridad normal

Ejemplo practico que me ha mordido:

setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => console.log('promise'));
console.log('sync');

Output: sync, promise, timeout

Porque? Promise es microtask, se ejecuta antes que setTimeout (macrotask).

En produccion esto importa cuando mezclas callbacks con promises. Por
ejemplo, en HostelOS tuve un bug donde un callback de Stripe se ejecutaba
antes de que el Promise de la DB terminara porque no entendia el orden."
```

---

### "Diferencia entre == y ==="

**Respuesta Senior:**
```
"== hace type coercion, === no.

Pero lo importante no es la definicion, es por que siempre usar ===:

1. Predictibilidad
   '1' == 1  // true (coercion)
   '1' === 1 // false (expected)

2. Bugs sutiles
   null == undefined  // true
   null === undefined // false

En mi codigo, uso === siempre. La unica excepcion es:
   if (value == null) // catch both null and undefined

ESLint rule eqeqeq esta siempre habilitada en mis proyectos."
```

---

### "Como manejas errores en async/await?"

**Respuesta Senior:**
```
"Hay 3 patterns que uso dependiendo del contexto:

1. TRY-CATCH (para flujos criticos)
async function processPayment(orderId) {
  try {
    const order = await getOrder(orderId);
    const result = await stripe.charges.create({...});
    return result;
  } catch (error) {
    logger.error('Payment failed', { orderId, error });
    throw new PaymentError(error.message);
  }
}

2. WRAPPER FUNCTION (para multiples awaits)
const [error, result] = await to(riskyOperation());
if (error) handleError(error);

3. GLOBAL ERROR HANDLER (para Express)
app.use((err, req, res, next) => {
  logger.error(err);
  res.status(500).json({ error: 'Internal error' });
});

En HostelOS uso combinacion: try-catch para operaciones criticas (pagos),
wrapper para operaciones que pueden fallar gracefully, y global handler
como safety net."
```

---

## Node.js

### "Como manejas memory leaks?"

**Respuesta Senior:**
```
"Los memory leaks en Node son sutiles. Mis estrategias:

PREVENCION:
1. Evitar closures que retengan objetos grandes
2. Limpiar event listeners (removeListener)
3. Usar WeakMap para caches cuando apropiado
4. Streams para archivos grandes (no leer todo a memoria)

DETECCION:
1. Monitoring con process.memoryUsage()
2. Heapdump para analisis
3. --inspect flag + Chrome DevTools

CASO REAL:
En HostelOS tuve un leak en el scheduler de sync. Cada sync creaba un
nuevo interval sin limpiar el anterior. Despues de dias, el proceso
crecia indefinidamente.

Solucion: patron de cleanup
class SyncScheduler {
  start() {
    this.stop(); // siempre limpiar antes
    this.interval = setInterval(this.sync, 5 * 60 * 1000);
  }
  stop() {
    if (this.interval) clearInterval(this.interval);
  }
}
```

---

### "Explica como funciona require vs import"

**Respuesta Senior:**
```
"Dos sistemas de modulos:

CommonJS (require):
- Sincronico
- Carga en runtime
- Puede ser condicional: if (x) require('y')
- module.exports / exports

ES Modules (import):
- Asincrono
- Carga en tiempo de parse
- Static analysis posible (tree shaking)
- Hoisted al top

En proyectos nuevos uso ESM porque:
1. Tree shaking reduce bundle size
2. Es el estandar del lenguaje
3. Mejor soporte de tooling

Pero tengo proyectos legacy con CommonJS. La migracion no es trivial
porque algunas librerias no soportan ESM bien.

Truco: puedes usar dynamic import() en ESM para carga condicional:
const module = await import('./module.js');
```

---

## React

### "Cuando usas useCallback/useMemo?"

**Respuesta Senior:**
```
"La respuesta corta: menos de lo que la gente piensa.

useCallback - memoriza funciones:
- USAR cuando pasas callback a componente memoizado (React.memo)
- USAR cuando callback es dependencia de useEffect
- NO USAR para 'optimizar' cada funcion

useMemo - memoriza valores:
- USAR para calculos costosos (filter/sort de arrays grandes)
- USAR para objetos que son dependencias de effects
- NO USAR para valores simples

Mi regla: profile primero, optimiza despues.

Ejemplo donde SI importa:
// Lista de 1000 items que se re-renderiza en cada keystroke
const filteredItems = useMemo(
  () => items.filter(i => i.name.includes(search)),
  [items, search]
);

Ejemplo donde NO importa:
// Funcion simple que no causa re-renders
const handleClick = () => setCount(c => c + 1);
// useCallback aqui es overhead innecesario
```

---

### "Como manejas estado global?"

**Respuesta Senior:**
```
"Depende de la complejidad:

SIMPLE (2-3 pieces of state):
→ Context + useReducer
→ Suficiente para auth, theme, user preferences

MEDIO (multiple features, some async):
→ Zustand o Jotai
→ Menos boilerplate que Redux, buen DX

COMPLEJO (large app, time travel, middleware):
→ Redux Toolkit
→ Cuando necesitas el ecosistema completo

En mis proyectos uso Zustand por defecto:
- API simple
- No providers necesarios
- Selectores incluidos
- TypeScript friendly

const useStore = create((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));

// En componente
const user = useStore((state) => state.user);
```

---

## PostgreSQL

### "Como optimizas una query lenta?"

**Respuesta Senior:**
```
"Mi proceso de 5 pasos:

1. EXPLAIN ANALYZE
   EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...

   Busco:
   - Seq Scan en tablas grandes (deberia ser Index Scan)
   - Nested Loop con muchas filas
   - High cost estimates

2. IDENTIFICAR PROBLEMA
   Comunes:
   - Missing index
   - Index no usado (mal tipo, funcion en columna)
   - N+1 queries
   - Over-fetching columnas

3. APLICAR FIX
   - Agregar indice apropiado
   - Reescribir query (JOINs en vez de subqueries)
   - Eager loading en ORM
   - Agregar LIMIT

4. VERIFICAR
   Re-ejecutar EXPLAIN, comparar tiempos

5. MONITOREAR
   Asegurar que fix funciona en produccion con carga real

EJEMPLO REAL:
En HostelOS, query de disponibilidad tardaba 800ms. EXPLAIN mostro
Seq Scan en tabla de 50K reservas. Agregue indice compuesto:

CREATE INDEX idx_reservations_property_dates
ON reservations (property_id, check_in, check_out);

Bajo a 50ms. Pero despues descubri que con mas datos necesitaba
partial index:

CREATE INDEX idx_active_reservations
ON reservations (property_id, check_in, check_out)
WHERE status = 'confirmed';
```

---

### "Explica indices compuestos"

**Respuesta Senior:**
```
"Un indice compuesto incluye multiples columnas en orden especifico.

REGLA CLAVE: orden importa.

INDEX (A, B, C) sirve para:
✅ WHERE A = 1
✅ WHERE A = 1 AND B = 2
✅ WHERE A = 1 AND B = 2 AND C = 3
✅ WHERE A = 1 ORDER BY B
❌ WHERE B = 2 (no usa el indice)
❌ WHERE C = 3 (no usa el indice)

Es como un directorio telefonico: ordenado por apellido, luego nombre.
Puedes buscar por apellido, o apellido+nombre. Pero no por nombre solo.

CUANDO USAR:
- Queries frecuentes con multiples columnas en WHERE
- Combinaciones de WHERE + ORDER BY

EJEMPLO:
-- Query frecuente
SELECT * FROM orders
WHERE user_id = ? AND status = 'pending'
ORDER BY created_at DESC;

-- Indice optimo
CREATE INDEX idx_user_status_date
ON orders (user_id, status, created_at DESC);
```

---

## APIs/REST

### "Como diseñas una API REST?"

**Respuesta Senior:**
```
"Mis principios:

1. RECURSOS, NO ACCIONES
   ❌ POST /createUser
   ✅ POST /users

2. VERBOS HTTP CORRECTOS
   GET - leer (idempotente)
   POST - crear
   PUT - reemplazar completo
   PATCH - update parcial
   DELETE - eliminar

3. NAMING CONSISTENTE
   - Plurales: /users, /orders
   - Nested para relaciones: /users/123/orders
   - Query params para filtros: /orders?status=pending

4. RESPONSES CONSISTENTES
   {
     "data": {...},
     "meta": { "page": 1, "total": 100 },
     "errors": null
   }

5. VERSIONING
   - URL: /v1/users (mi preferido, explicito)
   - Header: Accept-Version (mas RESTful, menos practico)

6. ERROR HANDLING
   - HTTP codes correctos (404, 422, 500)
   - Body con detalles:
   {
     "error": {
       "code": "VALIDATION_ERROR",
       "message": "Email is invalid",
       "field": "email"
     }
   }
```

---

### "Como implementas idempotencia?"

**Respuesta Senior:**
```
"Idempotencia = misma request multiples veces = mismo resultado.

IMPORTANTE PARA:
- Pagos (evitar doble cobro)
- Creacion de recursos (evitar duplicados)
- Cualquier operacion con side effects

IMPLEMENTACION:

1. Idempotency Key (patron Stripe)

   Cliente envia header: Idempotency-Key: uuid-123

   Server:
   - Primera vez: procesa, guarda resultado con key
   - Siguientes: retorna resultado guardado

   async function handlePayment(key, data) {
     const existing = await cache.get(key);
     if (existing) return existing;

     const result = await processPayment(data);
     await cache.set(key, result, { ttl: 24h });
     return result;
   }

2. Unico natural (para creacion)

   POST /orders con order_reference: "ORD-123"
   - DB tiene UNIQUE constraint en order_reference
   - Segundo POST con misma reference falla o retorna existente

3. Conditional requests

   PUT /resource con If-Match: etag
   - Solo aplica si version coincide
```

---

## Docker/DevOps

### "Como estructuras un Dockerfile para produccion?"

**Respuesta Senior:**
```
"Multi-stage builds para imagen minima:

# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

# Non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs

EXPOSE 3000
CMD ["node", "dist/main.js"]

PRINCIPIOS:
1. Alpine para imagen pequeña (~100MB vs ~1GB)
2. Multi-stage: builder tiene devDeps, prod solo lo necesario
3. Non-root user por seguridad
4. .dockerignore para excluir node_modules, .git, etc.
5. npm ci en vez de npm install (deterministico)

OPTIMIZACIONES:
- Cache de layers: COPY package.json antes que codigo
- Healthcheck: HEALTHCHECK CMD curl -f http://localhost:3000/health
```

---

## Preguntas "Gotcha"

### "Cual es la diferencia entre null y undefined?"

```
undefined: variable declarada sin valor, o propiedad no existente
null: ausencia intencional de valor

Cuando uso cual:
- undefined: dejar que JS lo maneje naturalmente
- null: explicitamente "no hay valor aqui"

function getUser(id) {
  const user = db.find(id);
  return user || null; // explicito: no encontrado
}
```

### "Que es closure?"

```
"Una funcion que recuerda su scope lexico incluso cuando se ejecuta
fuera de ese scope.

function createCounter() {
  let count = 0; // variable en closure
  return () => ++count;
}

const counter = createCounter();
counter(); // 1
counter(); // 2

Uso practico: factory functions, modulos, callbacks con estado.
Peligro: memory leaks si el closure retiene objetos grandes."
```
