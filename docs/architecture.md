# Arquitectura — LessonForge AI

**Versión 2.0.**

## 1. Estilo arquitectónico: monolito modular

Hay un único código base de backend, desplegado como **dos procesos** a partir de la misma imagen:
- **API**: FastAPI con uvicorn.
- **Worker**: `python -m app.worker`.

Ambos comparten la misma PostgreSQL, que además actúa como cola (ADR-002) y almacén vectorial
(ADR-004).

```
             ┌───────────────────────────┐
             │  Frontend demo (React+TS)  │
             └─────────────┬─────────────┘
                           │ HTTPS · JSON · Bearer JWT
┌──────────────────────────▼───────────────────────────┐
│ API (FastAPI)                                         │
│  api/v1: auth · lessons · documents · activities ·    │
│          submissions · jobs   (routers /tutor y /student) │
│  core:   config · security · db · deps · rate_limit   │
│  services (dominio) ── repositories (SQLAlchemy)      │
└──────────────┬────────────────────────▲───────────────┘
               │ INSERT jobs             │ estado
┌──────────────▼────────────────────────┴───────────────┐
│ PostgreSQL 16 + pgvector                               │
│  datos de dominio · jobs (cola) · document_chunks      │
└──────────────▲────────────────────────────────────────┘
               │ SELECT … FOR UPDATE SKIP LOCKED
┌──────────────┴────────────────────────────────────────┐
│ Worker                                                 │
│  ingestion: pypdf → chunks → EmbeddingProvider         │
│  generation: Retriever → PromptBuilder → LLMProvider   │
│              → OutputValidator → activities            │
│  feedback:   LLMProvider → validación → submissions    │
└──────────────┬────────────────────────────────────────┘
               │ HTTPS (claves obtenidas de Secret Manager)
        ┌──────▼──────┐
        │ Proveedor IA │  real en local, demo y producción
        └─────────────┘  (solo las pruebas automáticas usan FakeLLM / FakeEmbedder)
```

## 2. Módulos del backend

| Módulo | Responsabilidad |
|---|---|
| `core/config.py` | Configuración tipada. Rechaza secretos ficticios en producción |
| `core/security.py` | Hash Argon2, emisión y verificación de JWT |
| `core/deps.py` | `get_db`, `get_current_user`, `require_role`, carga de recursos **con comprobación de propiedad** |
| `services/lesson_service.py` | Lecciones y relación tutor–alumno |
| `services/document_service.py` | Validación de la subida, ingesta, fragmentación |
| `services/rag/` | `EmbeddingProvider`, `Retriever` (filtrado por `lesson_id`), `PromptBuilder` |
| `services/llm/` | `LLMProvider` (real o falso), esquemas de salida y validación de dominio |
| `services/activity_service.py` | Solicitud, borrador, publicación, vistas por rol |
| `services/grading_service.py` | **Calificación determinista** (funciones puras) |
| `services/feedback_service.py` | Observaciones de IA y reencolado manual si fallan |
| `services/job_service.py` | Encolar, reclamar, completar, reintentar, recuperar huérfanos |
| `worker.py` | Bucle del worker y apagado ordenado |

## 3. API (v1)

Las rutas están **separadas por rol**. Así un esquema del tutor, que incluye respuestas, nunca
puede servirse a un alumno por error.

| Método y ruta | Rol | Descripción |
|---|---|---|
| `POST /auth/login` | público | Devuelve el JWT |
| `GET /me` | ambos | Perfil |
| `GET /tutor/students` | tutor | Sus alumnos |
| `POST /tutor/lessons` · `GET /tutor/lessons` · `GET /tutor/lessons/{id}` | tutor | Lecciones |
| `PUT /tutor/lessons/{id}/document` | tutor | Subida del PDF → `202 {job_id}` |
| `POST /tutor/lessons/{id}/activities` | tutor | Solicitud de generación → `202 {activity_id, job_id}` |
| `GET /tutor/activities/{id}` | tutor | Vista completa: ítems, claves y fuentes |
| `POST /tutor/activities/{id}/publish` · `POST …/discard` | tutor | Publicar o descartar el borrador |
| `GET /tutor/activities/{id}/submission` | tutor | Entrega del alumno con nota y observaciones |
| `GET /student/activities` | alumno | Actividades publicadas para él |
| `GET /student/activities/{id}` | alumno | Vista **sin claves** (`ActivityStudentView`) |
| `POST /student/activities/{id}/submission` | alumno | Entrega → `201` con nota y desglose |
| `GET /student/activities/{id}/submission` | alumno | Su resultado, claves y observaciones |
| `GET /jobs/{id}` | dueño | Estado del trabajo |
| `GET /health` | público | Comprobación de salud |

Si alguien pide un recurso que no es suyo, recibe **404**, no 403, para no revelar que existe.

## 4. Pipeline RAG de generación

1. **Consulta**: palabras clave + contexto del ejercicio + nivel.
2. **Recuperación**: embedding de la consulta y luego
   `ORDER BY embedding <=> :q WHERE lesson_id = :lesson LIMIT k` (k = 8). Además, para cada
   palabra clave se asegura al menos un fragmento que la contenga, si existe.
3. **Prompt**: instrucciones del sistema versionadas (`prompt_version`), los fragmentos entre
   delimitadores `<material id="…">` y los parámetros validados. Las observaciones del tutor solo
   se usan para la generación, que el tutor revisa antes de publicar.
4. **LLM**: salida JSON estructurada con un esquema, temperatura baja y límite de tokens.
5. **Validación**: esquema Pydantic y reglas de dominio. Se comprueba el número exacto de ítems,
   exactamente una opción correcta incluida en las opciones, un único `___` por frase, ninguna
   respuesta vacía y citas que pertenezcan a los fragmentos recuperados. Si falla, se reintenta y,
   agotados los intentos, el trabajo queda en `FAILED`.
6. **Persistencia**: actividad en estado `DRAFT`, ítems y claves en tablas separadas.

## 5. Despliegue (ADR-005)

| Entorno | Componentes |
|---|---|
| Local | Docker Compose: `pgvector/pgvector:pg16`, api, worker y frontend. **Proveedor de IA real**, con su clave en `backend/.env` (no versionado). El resto de secretos son ficticios |
| CI | GitHub Actions con un servicio PostgreSQL con pgvector. Proveedores de IA falsos, sin secretos |
| Producción (demo) | Cloud Run: servicio `api` y servicio `worker` (con CPU siempre asignada y 1 instancia mínima). Secret Manager para JWT, base de datos y claves de IA. PostgreSQL gestionada con pgvector. Frontend estático |

## 6. Principios de diseño

1. **OpenAPI como único contrato**, generado por FastAPI.
2. **Esquemas distintos por rol.** Ningún esquema de alumno contiene claves antes de la entrega.
3. **La IA propone, el backend decide.** La nota es determinista y la salida del LLM siempre se
   valida.
4. **Proveedores intercambiables** (`LLMProvider`, `EmbeddingProvider`). Los falsos son
   deterministas y se usan en TDD y CI.
5. **Todo acceso a recursos pasa por un loader que comprueba la propiedad** (A01).
