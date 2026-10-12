# Requisitos de LessonForge AI

**Versión 2.0 — 11 de octubre de 2026.** Sustituye a la versión 1 (modelo de "clases" grupales).
Entrega final: **26 de octubre de 2026**. Proyecto académico: **solo datos ficticios**.

## 1. Visión del producto

LessonForge AI es una **API** para una plataforma de tutorías de idiomas **1:1** (un tutor, un
alumno por clase), al estilo de los marketplaces de tutores en línea.

Después de cada clase, el tutor registra la lección: el **PDF** trabajado, las **palabras
clave** vistas y sus **observaciones** sobre el alumno. A partir de esa información puede pedir
**material de refuerzo generado por IA**, un cuestionario interactivo o un ejercicio de completar
frases. La IA usa **RAG** sobre el material de esa lección como fuente principal de información.

El alumno resuelve la actividad y recibe una **nota determinista**, que calcula el backend sin IA,
junto con **observaciones de la IA** sobre los puntos a mejorar. El tutor puede consultar la
actividad resuelta y las observaciones.

El valor del proyecto está en el **backend**. El frontend es una demo React mínima que solo sirve
para mostrar el flujo.

## 2. Actores

| Actor | Descripción |
|---|---|
| Tutor (`teacher`) | Registra lecciones, sube material, solicita y publica actividades, consulta resultados de **sus** alumnos |
| Alumno (`student`) | Resuelve las actividades publicadas para él y consulta **sus** resultados |
| Worker | Proceso en segundo plano que ejecuta ingesta, generación y retroalimentación |
| Proveedor de IA | LLM y modelo de embeddings externos. Su salida se trata como **no confiable** |

## 3. Flujo principal

1. El tutor inicia sesión.
2. Crea una **lección** para uno de sus alumnos, indicando idioma, nivel MCER, palabras clave y
   observaciones.
3. Sube el **PDF** de la clase. La ingesta es asíncrona: extracción, fragmentación y embeddings.
4. Solicita una **actividad** indicando tipo, número de ítems y contexto del ejercicio. La API
   responde `202` con el identificador del trabajo.
5. El worker recupera los fragmentos relevantes de **esa lección** (RAG), genera la actividad con
   el LLM y valida la salida. El resultado queda como **borrador**.
6. El tutor revisa el borrador, donde ve las respuestas correctas y las fuentes, y lo **publica**.
7. El alumno ve la actividad **sin respuestas correctas** y envía sus respuestas una sola vez.
8. El backend **califica de forma determinista** en ese momento y encola la retroalimentación de IA.
9. El alumno ve su nota, las respuestas correctas y las observaciones. El tutor ve lo mismo para
   cada uno de sus alumnos.

## 4. Requisitos funcionales

| ID | Requisito | Criterios de aceptación |
|---|---|---|
| RF-01 | **Autenticación** | Inicio de sesión con email y contraseña, que devuelve un JWT de 30 min. Sin autoregistro: los usuarios ficticios se crean con un script de datos de prueba. Contraseñas con Argon2 |
| RF-02 | **Relación tutor–alumno** | El tutor solo ve y opera sobre los alumnos vinculados a él. En el MVP los vínculos se crean con el script de datos de prueba |
| RF-03 | **Lecciones** | El tutor crea una lección para uno de sus alumnos con: título, idioma objetivo, nivel MCER (A1–C2), fecha, palabras clave (1–20, de hasta 50 caracteres cada una) y observaciones (hasta 2000 caracteres, **privadas del tutor**). Puede listar y consultar solo las suyas |
| RF-04 | **Material PDF** | Un PDF por lección, de hasta 10 MB y 50 páginas, con texto extraíble. Se validan la firma `%PDF-` y el tamaño mientras se recibe el archivo. La ingesta es asíncrona y su estado se puede consultar. El PDF original se elimina tras una ingesta correcta (minimización de datos) |
| RF-05 | **Solicitud de generación** | El tutor indica: tipo (`quiz` o `fill_blank`), número de ítems (1–20), contexto del ejercicio (hasta 1000 caracteres), palabras clave (por defecto las de la lección) y nivel (por defecto el de la lección). Requiere que el documento esté `READY`. Responde `202` con `job_id` |
| RF-06 | **Generación con RAG** | Se recuperan los *top-k* fragmentos **filtrados por la lección** según su similitud con la consulta (palabras clave + contexto). El material se pasa al prompt entre delimitadores. La salida es JSON con un esquema estricto que se valida con Pydantic y reglas de dominio. Cada ítem cita los fragmentos en que se basa |
| RF-07 | **Trabajos asíncronos** | Estados `PENDING`, `PROCESSING`, `COMPLETED` y `FAILED`. Máximo 3 intentos con espera creciente entre ellos. Los bloqueos huérfanos se recuperan. `GET /jobs/{id}` solo responde al dueño. El mensaje de error que se muestra está saneado |
| RF-08 | **Revisión y publicación** | El tutor ve el borrador con las respuestas correctas y las fuentes, y puede **publicarlo** o **descartarlo**. El alumno solo ve actividades publicadas |
| RF-09 | **Resolución** | El alumno lista las actividades publicadas para él y las obtiene **sin respuestas correctas**. Envía sus respuestas **una sola vez** |
| RF-10 | **Calificación determinista** | Se califica de inmediato al recibir la entrega. En `quiz`, la opción elegida debe ser exactamente la correcta. En `fill_blank`, la respuesta se normaliza (mayúsculas, espacios y puntuación final; **las tildes sí cuentan**) y se compara con la lista de respuestas aceptadas. Nota de 0 a 100 con 2 decimales y desglose por ítem. **El LLM no interviene** |
| RF-11 | **Observaciones de IA** | Después de calificar, un trabajo genera un resumen y puntos a mejorar para cada ítem fallado, a partir de los ítems, las respuestas y los fragmentos fuente. **No modifica la nota.** Si fallan todos los intentos, `feedback_status = FAILED`: el alumno ve su nota y un aviso de "observaciones no disponibles", y el tutor puede volver a encolar el trabajo. No hay retroalimentación sustituta sin IA. Las observaciones privadas del tutor **no** se incluyen en este prompt |
| RF-12 | **Resultados** | El alumno ve su nota, las respuestas correctas (solo después de entregar) y las observaciones. El tutor ve las entregas de **sus** alumnos |
| RF-13 | **Frontend de demostración** | Pantallas: inicio de sesión, crear lección y subir PDF, solicitar actividad y consultar su estado, revisar y publicar, resolver (alumno) y ver resultado (ambos roles) |

## 5. Requisitos no funcionales

| ID | Requisito |
|---|---|
| RNF-01 | **Seguridad**: controles para OWASP Top 10:2025 y OWASP Top 10 for LLM Applications 2025 (ver [security-requirements.md](security-requirements.md)) |
| RNF-02 | **TDD**: cada caso de uso empieza por una prueba que falla. La CI bloquea los cambios si las pruebas no pasan (ver [testing-strategy.md](testing-strategy.md)) |
| RNF-03 | **Contrato OpenAPI** generado por FastAPI a partir de Pydantic. `/docs` se desactiva en producción |
| RNF-04 | **Secretos** en Google Cloud Secret Manager. Ningún secreto real en el repositorio, la imagen ni los logs (ver ADR-005) |
| RNF-05 | **Consumo acotado**: límite de peticiones en el inicio de sesión y en la generación, cuota diaria de tokens por tutor y alerta de presupuesto en la facturación de GCP o del proveedor de IA |
| RNF-06 | **Observabilidad**: logs JSON con `request_id`. Por cada llamada a la IA se registran modelo, versión del prompt, tokens y latencia, **sin** registrar el contenido ni los secretos |
| RNF-07 | **Reproducibilidad**: Docker Compose en local, lockfiles (`uv.lock`, `package-lock.json`) y CI en GitHub Actions |
| RNF-08 | **Rendimiento**: los endpoints síncronos responden en menos de 500 ms p95 en local (la subida de archivos no cuenta). Una generación típica tarda menos de 60 s |
| RNF-09 | **IA real en ejecución**: embeddings, generación de actividades y observaciones usan **siempre** el proveedor de IA real, en desarrollo local, en la demo y en producción. Los proveedores falsos existen **solo para las pruebas automáticas**, y la aplicación se niega a arrancar con `AI_PROVIDER=fake` salvo con `ENVIRONMENT=test` |

## 6. Fuera del alcance del MVP

Quedan fuera del MVP, de forma justificada para cumplir el plazo:
- autoregistro y recuperación de contraseña;
- pagos, agenda y videollamada;
- varios PDF por lección y OCR de PDF escaneados;
- edición manual de los ítems generados;
- varios intentos por actividad;
- notificaciones, WebSockets y panel de administración;
- interfaz con diseño cuidado o multilenguaje.

## 7. Decisiones de arquitectura

| ADR | Decisión |
|---|---|
| [ADR-001](adr/ADR-001-auth-and-session.md) | JWT Bearer de corta duración (PyJWT) y Argon2 (pwdlib) |
| [ADR-002](adr/ADR-002-async-job-queue.md) | Cola en PostgreSQL con worker `FOR UPDATE SKIP LOCKED` |
| [ADR-003](adr/ADR-003-pdf-storage-strategy.md) | PDF guardado temporalmente en PostgreSQL y eliminado tras la ingesta |
| [ADR-004](adr/ADR-004-rag-pgvector.md) | RAG con embeddings y pgvector en la misma PostgreSQL |
| [ADR-005](adr/ADR-005-secrets-and-deployment.md) | Cloud Run con Secret Manager |
| [ADR-006](adr/ADR-006-deterministic-grading.md) | Calificación determinista; la IA solo redacta observaciones |

## 8. Plan de entrega

| Fecha | Entregable |
|---|---|
| 12 oct | PostgreSQL con pgvector, Alembic, usuarios, inicio de sesión, datos de prueba y relación tutor–alumno |
| 13 oct | Lecciones y matriz de pruebas de autorización. **Fecha límite para elegir el proveedor de IA** |
| 14 oct | Adaptadores reales `LLMProvider` y `EmbeddingProvider`, con prueba de humo contra la API real. Medición de tokens y alerta de presupuesto |
| 14–15 oct | Subida de PDF, worker e ingesta con **embeddings reales** |
| 16–17 oct | Generación con RAG y **LLM real**, validación, revisión y publicación |
| **18 oct** | Entrega, calificación y retroalimentación con **IA real**. 🎯 **Backend completo con IA real** |
| 19 oct | Límites y cuotas. Corpus de inyección de prompts contra el proveedor real |
| 20–21 oct | Frontend de demostración. 🎯 **Demo completa en el navegador** |
| 22 oct | Cloud Run, Secret Manager y base de datos gestionada |
| **23 oct** | E2E, revisión OWASP. **Congelación de funcionalidades** |
| 24–25 oct | Documentación, evaluación de la IA y guion de la demo |
| 26 oct | Entrega |

**Recortes si hay retraso.** Se aplican en este orden:
1. Se elimina `fill_blank`.
2. Solo se despliega el backend.
3. La E2E se sustituye por una prueba de integración HTTPX del flujo completo.

**No se recortan:** uso de IA real, autorización, protección de respuestas, calificación
determinista, trabajos con reintentos y defensas frente a inyección de prompts.

## 9. Decisiones pendientes

- **Proveedor de LLM y embeddings.** Hay que decidirlo antes del **13 de octubre**, en evaluación
  por coste. Criterios: precio por token de entrada y salida y de embeddings; salida JSON
  estructurada; calidad en los idiomas objetivo; latencia; integración con GCP. El LLM y los
  embeddings pueden ser de proveedores distintos: algunos no ofrecen embeddings, y entonces hace
  falta un segundo proveedor (y otro secreto). El código siempre va detrás de las interfaces
  `LLMProvider` / `EmbeddingProvider`.
- **Base de datos gestionada:** Cloud SQL para PostgreSQL o Neon. Ambas admiten pgvector.
- **Idiomas objetivo admitidos** en el MVP (por ejemplo `en`, `es`, `fr`, `de`, `it`, `pt`).
