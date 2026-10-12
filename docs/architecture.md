# Arquitectura del Sistema - LessonForge AI

## 1. Estilo Arquitectónico: Monolito Modular
LessonForge AI está estructurado como un monolito modular con clara separación de responsabilidades dentro de un único repositorio (código y base de datos relacional compartida pero con límites lógicos estrictos).

## 2. Componentes Principales

```
+-----------------------------------------------------------+
|                    Frontend (React + TS)                 |
|      Vistas de Docente / Estudiante + Servicios API       |
+-----------------------------+-----------------------------+
                              | HTTP (JSON / OpenAPI)
+-----------------------------v-----------------------------+
|               Backend FastAPI (Monolito Modular)          |
|                                                           |
|  [ API Layer: Routers v1 ]                                |
|        |                                                  |
|  [ Core: Config, Security, DB, Dependencies ]             |
|        |                                                  |
|  [ Services Layer ]                                       |
|    - document_service.py     -> Extracción PDF & Chunking |
|    - activity_generator.py   -> Pipeline de IA            |
|    - job_service.py          -> Máquina de estados jobs   |
|    - grading_service.py      -> Corrección determinista   |
|    - pedagogical_feedback.py-> Observaciones con IA     |
|        |                                                  |
|  [ Schemas Layer (Pydantic) ] -> Validación & OpenAPI     |
|  [ Models Layer (SQLAlchemy) ]-> Persistencia             |
+-----------------------------+-----------------------------+
                              |
+-----------------------------v-----------------------------+
|               Base de Datos: PostgreSQL                   |
|   Users, Classrooms, Documents, Chunks, Jobs, Submissions |
+-----------------------------------------------------------+
```

## 3. Principios de Diseño
1. **Contrato Único con OpenAPI**: FastAPI infiere el 100% de los esquemas desde Pydantic. No existen definiciones manuales en YAML/JSON.
2. **Separación de Vistas por Rol**: Esquemas Pydantic específicos para estudiantes que omiten deliberadamente campos sensibles como `correct_answer`.
3. **Desacoplamiento Determinista vs Heurístico**: El motor de calificación no invoca a la IA. La IA solo genera retroalimentación y sugerencias pedagógicas.
