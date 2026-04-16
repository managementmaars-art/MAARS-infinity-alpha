# Technical Questions (Tech Lead)

## Apertura (2 min)

```
"Hola [Nombre], soy [Marcus], Tech Lead del equipo de [X].
Hoy vamos a hablar sobre tu experiencia tecnica y resolver
algunos problemas juntos. La idea es entender como piensas,
no buscar respuestas perfectas. Listo?"
```

---

## Arquitectura y Sistema (15 min)

### Preguntas Base

```
"Describe el sistema mas complejo que has construido."

"Walk me through la arquitectura de [proyecto mencionado]."

"Como manejarias [problema de escala] en tu sistema actual?"

"Que decisiones de arquitectura tomaste y por que?"
```

### Follow-ups de Profundidad

```
- "Por que elegiste [tecnologia X] sobre [alternativa Y]?"
- "Que trade-offs consideraste?"
- "Que harias diferente si empezaras de nuevo?"
- "Como manejaste [caso edge especifico]?"
- "Cuanto trafico/datos manejaba?"
```

### Para Multi-Tenancy (Senior Full-Stack SaaS)

```
"Explica tu approach de multi-tenancy."

"Como garantizas aislamiento de datos entre tenants?"

"Que pasa si un tenant grande afecta performance de otros?"

"Como manejas migrations en un sistema multi-tenant?"
```

### Red Flags

```
[ ] No puede explicar decisiones, solo "asi estaba"
[ ] No menciona trade-offs o alternativas consideradas
[ ] Buzzwords sin sustancia
[ ] No puede profundizar en su propia arquitectura
```

---

## Codigo y Problem Solving (20 min)

### Debugging

```
"Tienes un endpoint que a veces tarda 5 segundos y a veces 50ms.
Como lo investigarias?"

"Un usuario reporta que ve datos de otro usuario.
Cual es tu proceso de debugging?"

"La base de datos esta al 100% CPU.
Que haces en los primeros 10 minutos?"
```

### Optimizacion

```
"Este query tarda 800ms. Como lo optimizarias?"
[Mostrar query con JOIN y WHERE sin indice]

"Tienes un N+1 en este codigo. Identificalo y arreglalo."
[Mostrar codigo con loop + query]

"Esta pagina carga lento. Por donde empezarias?"
```

### Follow-ups

```
- "Que mostraria EXPLAIN ANALYZE?"
- "Que indice crearias exactamente?"
- "Hay algun edge case que tu solucion no maneja?"
- "Como testearías este cambio antes de produccion?"
```

### Preguntas de Codigo Real

```
"Muestrame codigo del que estes orgulloso. Explícame por que."

"Muestrame codigo que te de verguenza. Que aprendiste?"

"Como estructurarías un nuevo microservicio desde cero?"
```

---

## Tecnologias Especificas

### JavaScript/Node.js

```
"Explica el event loop de Node.js."

"Que es un memory leak comun en Node? Como lo detectas?"

"Promise.all vs Promise.allSettled - cuando usas cada uno?"

"Como manejas errores en async/await de forma consistente?"
```

### React

```
"Cuando usas useCallback vs useMemo?"

"Describe un bug de useEffect que hayas tenido."

"Como optimizas renders innecesarios?"

"Que estrategia usas para state management?"
```

### PostgreSQL

```
"Explica la diferencia entre indices B-tree y GIN."

"Cuando usarias un partial index?"

"Como debuggeas un query lento?"

"Que es un deadlock y como lo prevenís?"
```

### APIs/Integraciones

```
"Como manejas rate limiting de APIs externas?"

"Que pasa cuando un webhook falla?"

"Como implementas idempotency en pagos?"

"Describe tu estrategia de retry para integraciones."
```

---

## System Design (15 min)

### Problema Tipo

```
"Disenemos un sistema de reservas como Booking.com.
Multiples hoteles, usuarios concurrentes, prevencion de overbooking."

FOLLOW-UPS:
- "Como manejas la concurrencia en reservas?"
- "Que pasa si el pago falla despues de reservar?"
- "Como sincronizas con channels externos (Expedia, etc)?"
- "Como escalas esto a 100x usuarios?"
```

### Otros Problemas

```
"Disena un sistema de notificaciones en tiempo real."

"Disena un rate limiter distribuido."

"Disena un sistema de feature flags."

"Disena un job queue con retry y dead letter."
```

### Que Evaluar

```
- Clarifica requirements antes de disenar
- Considera trade-offs explicitamente
- Piensa en failure modes
- Escala apropiadamente (no over-engineer)
- Conoce sus limitaciones
```

---

## Preguntas Tricky

```
"Que tecnologia popular crees que esta sobrevalorada? Por que?"

"Cuentame sobre una decision tecnica que tomaste y resulto mal."

"Que haces cuando no estas de acuerdo con una decision del equipo?"

"Como te mantienes actualizado tecnicamente?"
```

---

## Scorecard Tecnica

```
CRITERIO                    | 1 | 2 | 3 | 4 | 5 |
----------------------------|---|---|---|---|---|
Profundidad tecnica         |   |   |   |   |   |
Problem solving             |   |   |   |   |   |
Comunicacion tecnica        |   |   |   |   |   |
System design               |   |   |   |   |   |
Conoce sus limitaciones     |   |   |   |   |   |

NIVEL EVALUADO:
[ ] Junior (necesita mentoria constante)
[ ] Mid (autonomo en tareas definidas)
[ ] Senior (autonomo end-to-end, puede mentorear)
[ ] Staff (influencia arquitectura, lidera iniciativas)

DECISION:
[ ] Strong hire
[ ] Hire
[ ] No hire
[ ] Need another opinion

NOTAS:
_________________________________
```
