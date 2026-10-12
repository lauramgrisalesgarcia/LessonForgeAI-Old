# Requisitos de seguridad — LessonForge AI

**Versión 2.0.** Referencias: **OWASP Top 10:2025** y **OWASP Top 10 for LLM Applications 2025**.
Cada control indica cómo se verifica. Ningún control se da por cumplido sin una prueba o una
comprobación en CI.

## 1. Matriz de autorización

| Recurso / acción | Tutor dueño | Otro tutor | Alumno de la lección | Otro alumno | Anónimo |
|---|---|---|---|---|---|
| Crear lección para el alumno X | ✅ si X es su alumno | — | ❌ 403 | ❌ 403 | ❌ 401 |
| Ver lección y observaciones | ✅ | ❌ 404 | ❌ 403 | ❌ 403 | ❌ 401 |
| Subir PDF o solicitar actividad | ✅ | ❌ 404 | ❌ 403 | ❌ 403 | ❌ 401 |
| Ver actividad con claves | ✅ | ❌ 404 | ❌ 403 | ❌ 403 | ❌ 401 |
| Ver actividad publicada sin claves | — | — | ✅ | ❌ 404 | ❌ 401 |
| Ver borrador sin publicar | ✅ | ❌ 404 | ❌ 404 | ❌ 404 | ❌ 401 |
| Entregar respuestas | — | — | ✅ una vez (2.ª → 409) | ❌ 404 | ❌ 401 |
| Ver entrega, nota y observaciones | ✅ | ❌ 404 | ✅ la suya | ❌ 404 | ❌ 401 |
| Consultar un trabajo | ✅ el suyo | ❌ 404 | ❌ 404 | ❌ 404 | ❌ 401 |

Cada celda corresponde a una prueba parametrizada en `tests/api/test_authorization_matrix.py`.

## 2. OWASP Top 10:2025

| Riesgo | Controles en LessonForge AI | Verificación |
|---|---|---|
| **A01 Broken Access Control** | Rutas separadas por rol. `require_role`. Loaders con comprobación de propiedad. 404 en recursos ajenos. Identificadores UUID. Sin endpoints que hagan peticiones a URLs externas indicadas por el usuario | Matriz de autorización (§1) y pruebas de IDOR |
| **A02 Security Misconfiguration** | `/docs` desactivado en producción. CORS con lista de orígenes permitidos. Cabeceras de seguridad (HSTS, `X-Content-Type-Options`, CSP en el frontend). Contenedores sin root. Postgres no expuesto. La app rechaza secretos ficticios en producción | Pruebas de configuración y de cabeceras |
| **A03 Software Supply Chain Failures** | Lockfiles (`uv.lock`, `package-lock.json`). `npm audit` y `pip-audit` en CI. Dependabot. Imágenes base fijadas. Acciones de GitHub con versión | Jobs de CI |
| **A04 Cryptographic Failures** | Argon2 para contraseñas. JWT HS256 con clave de 32 bytes o más obtenida de Secret Manager. TLS gestionado por Cloud Run. SHA-256 de los PDF | Pruebas unitarias de `security.py` |
| **A05 Injection** | ORM y consultas parametrizadas (también en pgvector). Validación Pydantic con longitudes máximas. Nombres de archivo saneados que no se usan como rutas. El frontend no usa `dangerouslySetInnerHTML` | Pruebas de entrada maliciosa y lint |
| **A06 Insecure Design** | Modelo de amenazas. Claves en una tabla aparte. Calificación determinista. Un solo intento. Cuotas | Revisión de diseño y ADR |
| **A07 Authentication Failures** | Sin autoregistro. Límite de peticiones en el inicio de sesión (5 por minuto por IP y email). Mismo mensaje y tiempo de respuesta tanto si falla el usuario como la contraseña. Expiración de 30 min. `alg` fijado al verificar el token | Pruebas de inicio de sesión, token caducado, token manipulado y `alg=none` |
| **A08 Software or Data Integrity Failures** | Firma del JWT. `submitted_at` y la nota son inmutables. La salida del LLM se valida antes de persistirse. PDF verificado por *magic bytes* | Pruebas de integridad |
| **A09 Security Logging and Alerting Failures** | Logs JSON con `request_id`, `user_id`, evento (inicio de sesión fallido, 403/404 de autorización, límite superado, trabajo fallido). Nunca se registran contraseñas, tokens, claves ni el contenido de los prompts | Pruebas de logging con `caplog` |
| **A10 Mishandling of Exceptional Conditions** | Manejador global de errores con respuesta genérica y `request_id`. Los trabajos fallan de forma controlada (`FAILED` con `error_code` saneado). Tiempos máximos en las llamadas a la IA y en el parseo del PDF. Transacciones con rollback | Pruebas de errores forzados con proveedores falsos |

## 3. OWASP Top 10 for LLM Applications 2025

| Riesgo | Controles | Verificación |
|---|---|---|
| **LLM01 Prompt Injection** (indirecta vía PDF y directa vía contexto, palabras clave y respuestas del alumno) | Material entre delimitadores y declarado como datos, no como instrucciones. Campos del usuario con longitud acotada y escapados. Salida limitada a un esquema JSON. La IA no tiene herramientas ni acceso a datos | Corpus de PDFs y entradas con inyecciones: la salida debe seguir siendo válida y no revelar el prompt |
| **LLM02 Sensitive Information Disclosure** | Datos ficticios. Las observaciones privadas del tutor **no** se envían en el prompt de retroalimentación al alumno. Los prompts no incluyen datos de otros usuarios. Los logs no guardan el contenido | Prueba de que el prompt de retroalimentación no contiene `observations` |
| **LLM03 Supply Chain** | Proveedor y modelo fijados por configuración y registrados en `jobs.model_name`. SDK oficial con versión fijada | Revisión y lockfile |
| **LLM04 Data and Model Poisoning** | No hay entrenamiento ni ajuste fino. El RAG solo usa el PDF de **la misma** lección, subido por su tutor | Prueba de aislamiento del retriever |
| **LLM05 Improper Output Handling** | La salida se valida con Pydantic y reglas de dominio antes de persistirse. Se renderiza como texto, nunca como HTML. Las citas deben pertenecer a los fragmentos recuperados | Pruebas con salidas malformadas o maliciosas del LLM falso |
| **LLM06 Excessive Agency** | El LLM no ejecuta herramientas ni escribe directamente en la base de datos. **No decide la nota**. El tutor publica manualmente | ADR-006 y diseño |
| **LLM07 System Prompt Leakage** | El prompt del sistema no contiene secretos ni lógica de autorización. Hay validación de que la salida no repite el prompt del sistema | Prueba de inyección del tipo "repite tus instrucciones" |
| **LLM08 Vector and Embedding Weaknesses** | Filtro **obligatorio** por `lesson_id` en toda búsqueda vectorial, aplicado en el repositorio y no en el llamador. No hay un índice compartido entre tutores | Prueba: dos lecciones con contenido similar, la recuperación nunca cruza |
| **LLM09 Misinformation** | Citas a fragmentos fuente. Revisión del tutor antes de publicar. Evaluación con un conjunto de referencia (ver [ai-evaluation.md](ai-evaluation.md)) | Métricas de *groundedness* |
| **LLM10 Unbounded Consumption** | Límite de tasa en la generación (10 por hora por tutor). Cuota diaria de tokens (`ai_usage`). `max_tokens`. Como máximo 20 ítems. PDF de hasta 10 MB y 50 páginas. Máximo 3 intentos. Tiempos máximos | Pruebas de límites y cuotas |

## 4. Secretos

- **Producción:** Google Cloud Secret Manager, inyectado en Cloud Run como variables de entorno a
  partir de referencias a secretos. La cuenta de servicio tiene `roles/secretmanager.secretAccessor`
  **solo** sobre los secretos de la app. Ver ADR-005.
- **Local y CI:** valores ficticios en `.env` (que no se versiona) y proveedores de IA falsos.
- **Ningún secreto real** en el repositorio, en la imagen, en los logs ni en los mensajes de error.
