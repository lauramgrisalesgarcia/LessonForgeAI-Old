# ADR-002: Mecanismo de Cola y Gestión de Trabajos Asíncronos

## Estado
Propuesto

## Contexto y Problema
La generación de actividades mediante IA (extracción de fragmentos de texto, preparación de prompts y llamada al LLM) puede demorar entre 5 y 20 segundos. Una llamada síncrona bloquearía los workers HTTP o causaría timeouts en la interfaz de usuario.
El sistema requiere persistencia de estados (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`), reintentos limitados y recuperación ante caídas, sin introducir infraestructura innecesaria para el MVP.

## Alternativas Consideradas

### Alternativa 1: Redis + Celery / ARQ
- **Ventajas**: Estándar de la industria para colas distribuidas, manejo robusto de backoff y retries.
- **Desventajas**: Requiere un servicio de infraestructura adicional (Redis), mayor sobrecarga operativa, gestión de fallos de sincronización entre PostgreSQL y el broker de Redis. Innecesario para el volumen del MVP.

### Alternativa 2: Tabla `GenerationJob` en PostgreSQL con ejecución en BackgroundTasks de FastAPI
- **Ventajas**: Cero infraestructura adicional (usa la misma PostgreSQL del proyecto), persistencia garantizada, trazabilidad completa de cada trabajo y metadatos de IA (modelo, prompt, tiempo de ejecución).
- **Desventajas y Límites**: Adecuado para un único nodo backend en desarrollo/evaluación. Si el servidor se apaga durante `PROCESSING`, la tarea queda huérfana (se mitiga con un chequeo de stale jobs al iniciar el servicio).
- **Mitigación**: Frontend realiza polling ligero cada 2 segundos a `GET /api/v1/jobs/{job_id}`.

## Decisión Propuesta y Justificación
Se adopta la **Alternativa 2**: Tabla persistente `generation_jobs` en PostgreSQL orquestada mediante un servicio de dominio (`job_service.py`) y ejecutada con tareas en segundo plano. Esto cumple al 100% con los requerimientos de persistencia, reintentos limitados y trazabilidad sin inflar la complejidad del proyecto.
