# Behavioral Questions para Senior IC

Framework STAR Tecnico + respuestas modelo basadas en tu experiencia.

## Preguntas Mas Comunes

### 1. "Cuentame sobre ti" (Pitch de 2-3 min)

**Estructura:** Presente → Pasado → Futuro

**Tu respuesta modelo:**
```
"Soy Full-Stack Developer con 8+ años de experiencia, especializado en
plataformas SaaS. Actualmente dirijo Pathfinders Labs, mi consultoria
donde construyo productos digitales end-to-end.

He entregado 50+ proyectos para clientes en LATAM, Europa y USA. Mi
especialidad es transformar ideas de negocio en productos funcionales,
desde la arquitectura hasta produccion.

Mis proyectos mas recientes son HostelOS, un PMS completo para hostales
con integraciones complejas, y Digitaliza, una plataforma multi-tenant
para PyMEs.

Estoy buscando un rol senior donde pueda aportar mi experiencia en SaaS
y arquitectura, trabajando de forma autonoma en proyectos de impacto."
```

---

### 2. "Describe un proyecto tecnico desafiante"

**Usar:** HostelOS - Sincronizacion OTAs

**Respuesta STAR:**
```
SITUACION:
"En HostelOS, necesitabamos sincronizar reservas con OTAs como Booking
y Airbnb. El problema es que usan iCal, un formato muy basico que solo
tiene bloques de tiempo sin estados ni metadata."

TASK:
"Como unico developer, tenia que disenar e implementar un sistema de
sincronizacion bidireccional que previniera overbookings y manejara
conflictos automaticamente."

ACTION:
"Primero, analice los edge cases: que pasa si Booking y Airbnb tienen
reservas conflictivas? Que pasa con timezones diferentes?

Diseñe una arquitectura con tres componentes:
1. Sync Engine que hace polling cada 5 minutos
2. Reconciliator que detecta diferencias
3. Conflict Resolver que aplica reglas de prioridad

Implemente retry logic con exponential backoff para manejar failures
de APIs externas, y un sistema de notificaciones para conflictos que
requieren intervencion manual."

RESULT:
"El sistema lleva 18 meses en produccion con cero overbookings.
Sincroniza miles de reservas mensuales con 99% success rate. El 1%
restante son conflictos legitimos que se notifican al usuario."
```

---

### 3. "Cuentame de una decision tecnica dificil"

**Usar:** Arquitectura API-first vs Monolito

**Respuesta STAR:**
```
SITUACION:
"Cuando empece HostelOS, tenia un monolito que funcionaba pero era
dificil de mantener. Cada deploy requeria bajar todo el sistema, y
los cambios en frontend afectaban backend."

TASK:
"Necesitaba decidir si refactorizar a microservicios, mantener monolito
mejorado, o encontrar un punto medio."

ACTION:
"Analice trade-offs:
- Microservicios: muy complejo para un solo developer, overhead de
  infraestructura
- Monolito mejorado: no resuelve el problema de deploys acoplados
- API-first separation: simplicidad de monolito + flexibilidad

Elegi separar frontend/backend con APIs REST bien definidas. No es
microservicios completo, pero permite:
- Deploys independientes
- Escalar backend sin tocar frontend
- Potencial de agregar otros clientes (mobile) en futuro"

RESULT:
"Tiempo de deploy se redujo 60%. Puedo hacer cambios en frontend sin
tocar backend. La base de codigo es mas mantenible y preparada para
escalar cuando sea necesario."
```

---

### 4. "Como trabajas sin supervision?"

**Respuesta:**
```
"He trabajado remoto los ultimos 8 años, asi que tengo un sistema
probado:

1. COMUNICACION PROACTIVA
   - Updates diarios/semanales dependiendo del proyecto
   - Anticipo blockers antes de que se vuelvan problemas
   - Documento decisiones tecnicas para referencia

2. AUTONOMIA CON ACCOUNTABILITY
   - Propongo soluciones, no solo reporto problemas
   - Defino milestones claros y los cumplo
   - Si algo cambia, comunico impacto inmediatamente

3. ESTRUCTURA PERSONAL
   - Uso timeboxing para tareas
   - Bloqueo tiempo para deep work
   - Tengo rituales de inicio/fin de jornada

Un ejemplo: en un proyecto para cliente en USA, trabajamos con 6 horas
de diferencia. Estructure mi dia para tener 2 horas de overlap para
sync, y el resto trabajo autonomo con updates asincrono."
```

---

### 5. "Describe un conflicto tecnico con un colega"

**Respuesta:**
```
SITUACION:
"En un proyecto de consultoria, el cliente tenia un desarrollador
interno que insistia en usar MongoDB para todo, incluyendo datos
altamente relacionales como reservas y disponibilidad."

TASK:
"Necesitaba convencerlo de que PostgreSQL era mejor opcion sin crear
conflicto ni parecer que descartaba su experiencia."

ACTION:
"En lugar de debatir teoricamente, propuse un approach practico:
1. Hice un prototipo rapido de ambas opciones
2. Documenté las queries que necesitariamos (joins complejos)
3. Mostre la complejidad de implementar en MongoDB vs la simplicidad
   en PostgreSQL

No dije 'estas equivocado'. Dije 'miremos los datos juntos'."

RESULT:
"El developer vio que MongoDB requeria denormalizacion excesiva y
codigo adicional para mantener consistencia. Acordamos usar PostgreSQL
para datos core y MongoDB solo para logs y analytics donde si tiene
sentido."

LEARNING:
"Aprendi que los debates tecnicos se ganan con evidencia, no argumentos.
Y que es importante dejar espacio para que la otra persona llegue a la
conclusion."
```

---

### 6. "Que haces cuando no sabes algo?"

**Respuesta:**
```
"Mi proceso tiene 4 pasos:

1. INVESTIGAR (30-60 min)
   - Documentacion oficial primero
   - Stack Overflow para casos especificos
   - GitHub issues para edge cases

2. PROTOTIPAR
   - Crear un POC minimo
   - Testear assumptions
   - Medir si funciona

3. PREGUNTAR ESTRATEGICAMENTE
   - Si despues de 2 horas no tengo progreso
   - Formulo pregunta especifica, no 'como hago X'
   - Muestro lo que ya intente

4. DOCUMENTAR
   - Escribo lo que aprendi
   - Para mi futuro yo y el equipo

Ejemplo: cuando tuve que implementar iCal sync, nunca habia trabajado
con ese protocolo. Investigue el RFC, encontre librerias en npm, hice
un prototipo, y cuando tuve duda sobre timezone handling, busque en
issues de la libreria donde encontre la solucion."
```

---

### 7. "Cuentame de un error que cometiste"

**Respuesta:**
```
SITUACION:
"En Digitaliza, el MVP original tenia un onboarding de 8 pasos. Pense
que mas opciones de customizacion era mejor para los usuarios."

ERROR:
"Asumi que los usuarios querian control total. No valide con usuarios
reales antes de construir. El resultado: conversion muy baja, usuarios
abandonaban en paso 3."

COMO LO DESCUBRI:
"Agregue analytics y vi el drop-off. Hice 5 llamadas con usuarios que
abandonaron. Todos dijeron lo mismo: 'muy complicado, quiero algo
rapido'."

COMO LO ARREGLE:
"Rediseñe el onboarding a 3 pasos con defaults inteligentes. Las
opciones avanzadas las movi a settings post-registro."

RESULTADO:
"Conversion subio 340%. Setup promedio bajo de 25 min a 12 min."

LEARNING:
"Ahora siempre empiezo con el MVP mas simple posible. Prefiero agregar
features que los usuarios piden que construir lo que creo que necesitan."
```

---

### 8. "Por que quieres dejar tu trabajo actual/situacion?"

**Respuesta (para tu caso como founder):**
```
"Pathfinders Labs me ha dado experiencia invaluable en construir
productos end-to-end y trabajar con clientes diversos. Pero hay cosas
que extraño de trabajar en equipo:

1. ESCALA - Como founder individual, estoy limitado en el tamaño de
   proyectos que puedo tomar. Quiero trabajar en sistemas de mayor
   escala y complejidad.

2. COLABORACION - Extraño code reviews, pair programming, y aprender
   de otros seniors. Cuando eres solo, te pierdes esa perspectiva.

3. IMPACTO - Quiero que mi trabajo afecte a millones de usuarios, no
   solo decenas de clientes.

No estoy escapando de algo malo. Estoy buscando el siguiente nivel de
crecimiento profesional."
```

---

## Template de Respuesta STAR

```
"Dejame contarte sobre [situacion especifica]...

SITUACION: [2-3 oraciones de contexto]

TASK: [Cual era mi responsabilidad especifica]

ACTION: [Que hice YO - verbos en primera persona]
- Primero, [accion 1]
- Luego, [accion 2]
- Finalmente, [accion 3]

RESULT: [Metrica o impacto concreto]

LEARNING: [Que aprendi - opcional pero recomendado]"
```

## Red Flags en Behavioral

```
❌ Culpar a otros ("el equipo no cooperaba")
✅ Ownership ("tome la iniciativa de...")

❌ Respuestas genericas ("trabajo bien en equipo")
✅ Ejemplos especificos ("en proyecto X, colabore con Y...")

❌ Solo exitos, ningun error
✅ Errores con learning claro

❌ "Nosotros" para todo
✅ "YO hice X, el equipo hizo Y"
```
