# Respuestas Sobre Tus Proyectos

Scripts para explicar HostelOS, Digitaliza y tu experiencia.

## HostelOS - PMS para Hostales

### Pitch de 2 minutos

```
"HostelOS es un sistema de gestion hotelera que construi para resolver
un problema real: hostales pequenos usando Excel y WhatsApp para
manejar reservas.

Es una plataforma SaaS completa con 17 modulos integrados:
- Reservas y disponibilidad en tiempo real
- Sincronizacion con Booking, Airbnb via iCal
- Gestion de pagos y comisiones
- Staff management
- Reportes financieros

El mayor desafio tecnico fue la sincronizacion con OTAs. iCal es un
protocolo de los 90s que solo tiene bloques de tiempo, sin estados
ni metadata. Tuve que disenar un reconciliador que detecta diferencias
y resuelve conflictos automaticamente.

Stack: Node.js, React, PostgreSQL, Redis
Resultado: 18 meses en produccion, cero overbookings."
```

### Preguntas frecuentes

**"Por que elegiste ese stack?"**
```
"React porque es lo que mejor domino para interfaces complejas con
mucho estado. Node.js porque permite full-stack JavaScript y tiene
excelente ecosistema para APIs REST. PostgreSQL porque los datos son
altamente relacionales (reservas, huespedes, propiedades, habitaciones)
y necesitaba transactions confiables para pagos. Redis para cache de
disponibilidad que se consulta constantemente."
```

**"Como manejaste la multi-tenancy?"**
```
"Use el modelo pool: una base de datos compartida con tenant_id en
cada tabla. Implemente:

1. Middleware que extrae tenant del JWT
2. Query builder que inyecta tenant_id automaticamente
3. Row-level security en PostgreSQL como backup
4. Cache con namespace por tenant en Redis

No use schema-per-tenant porque la escala no lo justificaba y complica
migrations. Tampoco database-per-tenant porque el costo seria prohibitivo
para hostales pequenos."
```

**"Explica la sincronizacion iCal"**
```
"iCal es basicamente un archivo de texto con eventos. El problema:
- No tiene estados (confirmed, cancelled, etc.)
- No tiene IDs unicos confiables
- Timezones son un infierno

Mi solucion:

1. SYNC ENGINE
   - Polling cada 5 minutos (push no existe en iCal)
   - Parseo del archivo iCal
   - Comparacion con estado interno

2. RECONCILIADOR
   - Detecta: nuevas reservas, cancelaciones, modificaciones
   - Usa hashing del contenido para detectar cambios
   - Genera lista de acciones

3. CONFLICT RESOLVER
   - Regla: internal system is source of truth
   - Si hay conflicto, aplica interno y notifica
   - Log de todas las decisiones para audit

4. RETRY LOGIC
   - Exponential backoff: 1s, 2s, 4s, 8s, 16s
   - Max 5 intentos
   - Dead letter queue para failures persistentes"
```

**"Que harias diferente si empezaras de nuevo?"**
```
"Tres cosas:

1. TESTING desde el dia 1. Empece sin tests y despues fue doloroso
   agregarlos. Ahora siempre empiezo con test infrastructure.

2. SEPARAR SYNC SERVICE. Esta acoplado al monolito. Deberia ser un
   servicio independiente que se comunica via eventos.

3. GRAPHQL para queries complejas. El frontend hace muchas llamadas
   para armar vistas. Con GraphQL podria pedir exactamente lo que
   necesita en una llamada."
```

---

## Digitaliza - Plataforma para PyMEs

### Pitch de 2 minutos

```
"Digitaliza es una plataforma que ayuda a PyMEs a tener presencia
digital sin complejidad: menu digital + link-in-bio + sistema de
reservas, todo integrado.

El target son negocios pequenos que usan WhatsApp para todo: restaurantes,
peluquerias, clinicas. No tienen tiempo ni conocimiento para manejar
multiples herramientas.

El desafio tecnico fue crear una arquitectura multi-tenant que escale
a miles de negocios con costos minimos. Use:
- Templates optimizados para mobile de gama baja
- Edge caching agresivo (contenido casi estatico)
- Stripe Connect para pagos en pesos colombianos

Aprendizaje clave: reduje onboarding de 8 pasos a 3 y la conversion
subio 340%. Less is more."
```

### Preguntas frecuentes

**"Como manejas Stripe con pesos colombianos?"**
```
"Colombia no usa centavos, pero Stripe internamente trabaja en la
unidad minima de la moneda. Entonces 50,000 COP se envia como 5000000.

Implemente una capa de conversion:
- INPUT: usuario ingresa 50000
- STORAGE: guardo 50000 (como lo ve el usuario)
- STRIPE: envio 5000000 (multiplicado x100)
- DISPLAY: muestro 50000 con formato colombiano

Tambien tuve que manejar que Stripe Colombia tiene features limitados
comparado con USA. Por ejemplo, no hay Stripe Billing automatico,
entonces construi mi propio sistema de subscripciones sobre Stripe
Payments."
```

**"Por que templates y no builder drag-and-drop?"**
```
"Tome esa decision basado en el target user. Los duenos de PyMEs:
- No tienen tiempo para disenar
- No saben que se ve 'bien'
- Quieren algo que funcione YA

Un builder agrega complejidad y decision fatigue. Con templates:
- Eligen uno, cambian logo y colores, listo
- 12 minutos promedio de setup
- Resultado profesional garantizado

Es la diferencia entre 'herramienta' y 'solucion'. Mi target quiere
solucion."
```

**"Como optimizaste para mobile de gama baja?"**
```
"El 82% de mi trafico viene de mobile, muchos con conexiones lentas y
dispositivos economicos.

Optimizaciones:
1. HTML minimo, CSS critico inline, JS diferido
2. Imagenes: WebP con fallback, lazy loading, srcset
3. No frameworks pesados: vanilla JS para interactividad
4. Service worker para cache offline
5. Fuentes: system fonts primero, custom como mejora progresiva

Resultado: LCP < 2s incluso en 3G, Lighthouse 90+."
```

---

## Pathfinders Labs - Consultoria

### Pitch de 1 minuto

```
"Pathfinders Labs es mi consultoria donde ayudo a emprendedores a
construir productos digitales.

Lo que me diferencia: no solo codifico, diseño la solucion completa.
Desde entender el problema de negocio hasta tener el producto en
produccion con usuarios reales.

He entregado 50+ proyectos en 7 anos, trabajando remoto desde 25 paises.
Mis clientes van desde startups early-stage hasta empresas establecidas
que necesitan expertise tecnico especifico.

Stack principal: React, Node.js, PostgreSQL. Especialidad: SaaS y
plataformas transaccionales."
```

### Preguntas frecuentes

**"Por que dejar consultoria por un empleo?"**
```
"No lo veo como 'dejar' sino como evolucionar. La consultoria me dio:
- Autonomia y ownership total
- Exposicion a problemas diversos
- Habilidad de comunicar con no-tecnicos

Pero hay cosas que extraño:
- Trabajar en sistemas de mayor escala
- Colaborar con otros seniors
- Impacto en millones de usuarios vs docenas de clientes

Busco un rol donde pueda aportar mi experiencia de 'hacer todo' pero
con el apoyo y escala de un equipo."
```

**"Como manejas multiples clientes?"**
```
"Timeboxing estricto + comunicacion clara.

1. ESTRUCTURA
   - Max 2-3 proyectos activos simultaneos
   - Bloques de 4 horas por proyecto
   - Dias dedicados cuando hay deadline

2. COMUNICACION
   - Expectativas claras desde el inicio
   - Updates semanales aun sin pedir
   - Disponibilidad definida (no 24/7)

3. PRIORIZACION
   - Deadline > Urgencia percibida
   - Si todo es urgente, nada es urgente
   - Digo NO a proyectos que no puedo hacer bien"
```

---

## Preguntas Generales

**"Por que desarrollo y no management?"**

```
"Porque me energiza resolver problemas tecnicos, no gestionar personas.

He tenido oportunidades de management y las rechace. Lo que me hace
levantarme motivado es:
- Disenar una arquitectura elegante
- Debuggear un problema complejo
- Ver codigo en produccion resolviendo problemas reales

Soy mejor contribuidor individual. Aporto mas valor escribiendo codigo
que coordinando a otros que escriben codigo. Y eso esta bien - no todos
tienen que ser managers."
```

**"Cual es tu mayor fortaleza tecnica?"**

```
"Disenar sistemas end-to-end. No solo escribir codigo, sino:
- Entender el problema de negocio
- Disenar arquitectura apropiada
- Implementar con calidad
- Deployar y mantener en produccion

Muchos developers son buenos en una fase. Yo puedo tomar un proyecto
desde 'tengo esta idea' hasta 'esta corriendo con usuarios reales'.
Eso viene de años de consultoria donde no habia nadie mas."
```

**"Cual es tu debilidad?"**

```
"Over-engineering cuando trabajo solo demasiado tiempo.

Sin code reviews o feedback, a veces construyo abstracciones que no
necesito. Me doy cuenta despues cuando mantengo el codigo.

Como lo manejo:
- Me pregunto '¿necesito esto HOY o es para un futuro hipotetico?'
- Reviso mi codigo 24h despues con ojos frescos
- Busco feedback de comunidades cuando no tengo equipo

Es una razon por la que quiero trabajar en equipo: el feedback constante
previene esto."
```
