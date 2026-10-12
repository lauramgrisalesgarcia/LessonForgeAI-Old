# Requerimientos de LessonForge AI (MVP)

## 1. Visión del Producto
LessonForge AI es una aplicación web independiente diseñada como un monolito modular para generar actividades de refuerzo del aprendizaje de idiomas a partir de materiales didácticos, con evaluación determinista y retroalimentación pedagógica enriquecida por IA.

## 2. Requerimientos Funcionales (RF)

- **RF-01 Gestión de Usuarios y Roles**: Soporte para roles de Docente y Estudiante con autenticación funcional y autorización basada en roles (RBAC) validada en backend.
- **RF-02 Clases y Membresías**: Los docentes pueden crear clases y asociar estudiantes de demostración a sus clases.
- **RF-03 Registro de Lecciones y Carga de Material**: Carga de materiales educativos en formato PDF, extracción y segmentación de texto en fragmentos (chunks).
- **RF-04 Generación Asíncrona de Actividades**:
  - Generación de actividades de opción múltiple (MCQ) y completar espacios a partir de los chunks seleccionados.
  - Trazabilidad y persistencia del trabajo en base de datos con estados (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`), límite de reintentos y consulta de estado.
- **RF-05 Entrega de Actividades y Protección de Respuestas**:
  - Los estudiantes inscritos pueden consultar la actividad y enviar sus respuestas.
  - Las respuestas correctas están estrictamente protegidas y no se exponen al estudiante antes de la entrega final.
- **RF-06 Calificación Determinista**: Corrección de respuestas mediante algoritmos deterministas (sin depender de alucinaciones del modelo de lenguaje).
- **RF-07 Observaciones Pedagógicas por IA**: Generación de retroalimentación cualitativa y formativa para el estudiante basada en sus errores y el material fuente.

## 3. Requerimientos No Funcionales (RNF)

- **RNF-01 Seguridad**: Control de acceso granular (aislamiento multi-tenant entre docentes, clases y entregas).
- **RNF-02 Documentación y Contrato API**: Contrato OpenAPI generado 100% de manera automática por FastAPI a partir de esquemas Pydantic. Swagger UI (`/docs`) y ReDoc (`/redoc`) configurables según entorno.
- **RNF-03 Verificabilidad y TDD**: Cobertura de pruebas unitarias, de integración y de autorización con pytest y HTTPX para backend, y Vitest para frontend.
- **RNF-04 Desempeño y Resiliencia**: Respuesta rápida de la API mediante delegación de tareas pesadas de IA a procesos en segundo plano con persistencia en PostgreSQL.
