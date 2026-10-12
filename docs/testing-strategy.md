# Estrategia de Pruebas - LessonForge AI

## 1. Niveles de Prueba y Herramientas

- **Backend**:
  - Motor de pruebas: `pytest`
  - Cliente de integración asíncrono/síncrono: `httpx`
  - Base de datos de pruebas: PostgreSQL transaccional aislada (con rollback por prueba o SQLite en memoria para unit tests rápidos)
- **Frontend**:
  - Motor de pruebas: `vitest` + `@testing-library/react`
  - Verificación estricta de tipos: `tsc --noEmit`

## 2. Cobertura del Plan de Pruebas

### 2.1 Pruebas Unitarias (`backend/tests/unit/`)
- `test_grading_service.py`:
  - Calificación exacta de preguntas de selección múltiple (100% determinista).
  - Normalización y tolerancia básica (mayúsculas/minúsculas, espacios) en ejercicios de completar espacios.
  - Validación de que errores en entradas no provoquen excepciones no controladas.

### 2.2 Pruebas de API y Autorización (`backend/tests/api/`)
- `test_openapi_contract.py`:
  - Obtención de `/openapi.json`.
  - Validación de coherencia entre los esquemas declarados y las respuestas reales.
  - Verificación de ausencia de campos de contraseñas o datos sensibles en los esquemas generados.
- `test_authorization.py`:
  - **Pertenencia a clase**: Un estudiante solo puede acceder a clases a las que pertenece (403 Forbidden en clases ajenas).
  - **Propiedad de recursos**: Un docente no puede editar ni borrar documentos/actividades de otro docente.
  - **Privacidad de intentos**: Un estudiante no puede ver las notas ni observaciones de otros estudiantes.
  - **Protección de respuestas correctas**: Un estudiante que consulta una actividad antes de enviarla recibe un esquema `ActivityStudentView` que no contiene el atributo `correct_answer`.

### 2.3 Prueba de Integración de Flujo Completo (`backend/tests/integration/`)
- `test_full_workflow.py`:
  - 1. Creación de lección y clase por docente autenticado.
  - 2. Carga y procesamiento de documento PDF de prueba.
  - 3. Disparo y finalización del trabajo asíncrono de generación de actividad.
  - 4. Consulta de la actividad por el estudiante (verificando que no ve respuestas correctas).
  - 5. Envío de respuestas por el estudiante (`Submission`).
  - 6. Verificación de cálculo de calificación determinista.
  - 7. Verificación de generación de observaciones pedagógicas por IA.
