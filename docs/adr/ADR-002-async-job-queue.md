# ADR-002: Cola y gestión de trabajos asíncronos

## Estado
Aceptado (11 de octubre de 2026). Sustituye a la propuesta anterior basada en `BackgroundTasks`.

## Contexto
La ingesta (extracción y embeddings), la generación de actividades y la retroalimentación llaman
a la IA y pueden tardar entre 5 y 60 s. Los requisitos piden estados persistidos, reintentos
limitados y recuperación ante caídas. El despliegue es en Cloud Run (ADR-005), donde la API y el
worker son servicios separados y las instancias pueden reiniciarse en cualquier momento.

## Alternativas consideradas
1. **Redis con Celery o ARQ.** Es el estándar, pero añade un servicio y la sincronización entre
   dos almacenes. Sobra para el volumen del MVP.
2. **`BackgroundTasks` de FastAPI.** No necesita infraestructura, pero la tarea vive en el proceso
   HTTP: se pierde al reiniciar (incluido cada `--reload` y cada escalado a cero de Cloud Run), los
   reintentos con espera bloquean el proceso y probarla es poco determinista.
3. **Tabla `jobs` en PostgreSQL con un worker dedicado** que reclama trabajos con
   `SELECT … FOR UPDATE SKIP LOCKED`.

## Decisión
**Alternativa 3.**
- La API inserta el trabajo en la misma transacción que la entidad (actividad, documento o entrega)
  y responde `202`.
- El worker (`python -m app.worker`) ejecuta en bucle:
  `SELECT … WHERE status='PENDING' AND run_after <= now() ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1`.
  Después marca el trabajo como `PROCESSING` con `locked_at` y `locked_by`, y lo ejecuta.
- Si tiene éxito, el estado pasa a `COMPLETED`. Si falla y `attempts < max_attempts` (3), vuelve a
  `PENDING` con `run_after = now() + 2^attempts × 10 s`. En caso contrario pasa a `FAILED` con un
  `last_error_code` saneado.
- **Recuperación de huérfanos:** un trabajo en `PROCESSING` con `locked_at` de hace más de
  5 min se vuelve a encolar (si quedan intentos).
- El frontend consulta `GET /jobs/{id}` cada 2 s.
- Las pruebas llaman a `process_next_job(session)` directamente: son deterministas y no esperan.

## Consecuencias
- No se añade infraestructura: es la misma PostgreSQL. Hay trazabilidad completa y las pruebas son
  sencillas.
- En Cloud Run el worker necesita **CPU siempre asignada y 1 instancia mínima** (coste pequeño pero
  continuo), o bien *worker pools*. Hay que verificarlo al desplegar.
- El rendimiento está limitado por la base de datos, lo cual es más que suficiente para el MVP.
