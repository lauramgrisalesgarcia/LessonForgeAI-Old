# Estrategia de pruebas — LessonForge AI

**Versión 2.0.** El desarrollo sigue **TDD**.

## 1. Ciclo de trabajo

Para cada caso de uso (por ejemplo "el tutor solicita una actividad"):
1. Escribir la **lista de pruebas**: camino feliz, validaciones, autorización y errores.
2. **Rojo**: escribir una prueba y comprobar que falla por el motivo esperado.
3. **Verde**: escribir el código mínimo para que pase.
4. **Refactorizar** con todas las pruebas en verde.
5. Hacer commit con la CI en verde. No se fusionan cambios con pruebas fallando.

Los commits pueden seguir el patrón `test: …` → `feat: …` para que el historial muestre el ciclo.

## 2. Herramientas

| Ámbito | Herramientas |
|---|---|
| Backend | pytest, pytest-asyncio, HTTPX (`ASGITransport`), pytest-cov |
| Base de datos | **PostgreSQL real con pgvector** (`pgvector/pgvector:pg16`) en Docker o como servicio en CI. Cada prueba se ejecuta en una transacción que se revierte al terminar. **No se usa SQLite**, porque no admite JSONB, ARRAY, ENUM ni `vector` |
| IA | `FakeLLMProvider` (devuelve salidas programadas, incluidas inválidas y maliciosas) y `FakeEmbeddingProvider` (vectores deterministas a partir de un hash del texto) |
| Frontend | Vitest, Testing Library y happy-dom |
| E2E | Playwright: un flujo completo con los proveedores falsos |
| Calidad | ruff (lint y formato), mypy, `tsc --noEmit`, `pip-audit`, `npm audit` |

## 3. Pirámide de pruebas

### 3.1 Unitarias (`backend/tests/unit/`)
- `test_grading_service.py`: `quiz` exacto; normalización de `fill_blank` (mayúsculas, espacios,
  puntuación final; las tildes **sí** cuentan); variantes aceptadas; respuestas ausentes o
  inválidas; nota con 2 decimales; propiedad: la nota está siempre en [0, 100].
- `test_output_validator.py`: número de ítems, exactamente una opción correcta, un solo `___`,
  citas válidas, JSON malformado, campos extra.
- `test_prompt_builder.py`: delimitadores; escapado de los campos del usuario; las observaciones
  **no** aparecen en el prompt de retroalimentación.
- `test_chunker.py`: tamaño y solapamiento de fragmentos; página de origen.
- `test_security.py`: hash y verificación; JWT caducado, manipulado y con `alg=none`.
- `test_config.py`: rechazo de secretos ficticios en producción.

### 3.2 Integración con base de datos (`backend/tests/integration/`)
- `test_job_queue.py`: reclamar con `SKIP LOCKED` (dos workers nunca toman el mismo trabajo),
  reintentos con espera, `FAILED` tras `max_attempts`, recuperación de bloqueos huérfanos.
- `test_retriever.py`: **aislamiento por lección** (LLM08) y orden por similitud.
- `test_ingestion.py`: PDF válido; PDF sin texto; demasiadas páginas; PDF corrupto; el blob se
  elimina tras la ingesta.

### 3.3 API (`backend/tests/api/`)
- `test_authorization_matrix.py`: cada celda de la matriz de
  [security-requirements.md](security-requirements.md), con pruebas parametrizadas.
- `test_activity_student_view.py`: la respuesta del alumno **no contiene** `correct_option_id`,
  `accepted_answers` ni `explanation` antes de entregar (se comprueba recorriendo todo el JSON).
- `test_submission.py`: un solo intento (409), validación de las respuestas, nota inmediata.
- `test_auth.py`: inicio de sesión, límite de peticiones, mensajes uniformes.
- `test_openapi_contract.py`: ningún esquema de respuesta expone `hashed_password` ni claves en
  las rutas `/student`.
- `test_uploads.py`: firma `%PDF-`, tamaño máximo, tipo MIME falso.

### 3.4 Flujo completo
- `tests/integration/test_full_workflow.py`, con proveedores falsos y el worker ejecutado en
  proceso:
  lección → PDF → ingesta → solicitud → generación → publicación → vista del alumno sin claves →
  entrega → nota determinista → retroalimentación → consulta del tutor.
- Una E2E con Playwright recorre el mismo flujo desde el frontend de demostración.

### 3.5 Seguridad de la IA (manual y semiautomática)
- Corpus de PDFs con inyecciones ("ignora las instrucciones…", texto oculto, instrucciones en
  otro idioma). Criterio: la salida sigue siendo válida, está en el idioma pedido y no revela el
  prompt.
- Se ejecuta contra el proveedor real **fuera de CI**, con `pytest -m live_llm`, porque consume
  cuota.

## 4. Criterios de calidad

- Cobertura de líneas igual o superior al **85 %** en `app/services` e igual o superior al
  **75 %** en el total del backend.
- CI en verde con: lint, formato, mypy, pruebas, auditoría de dependencias y build de Docker.
- Ninguna prueba de CI depende de red externa ni de secretos.
