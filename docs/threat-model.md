# Modelo de Amenazas - LessonForge AI

## 1. Alcance y Metodología
Análisis de amenazas basado en la metodología STRIDE para el MVP de LessonForge AI.

## 2. Amenazas Identificadas y Mitigaciones

| Categoría STRIDE | Amenaza Concreta | Impacto | Mitigación en LessonForge AI |
| :--- | :--- | :--- | :--- |
| **Spoofing** (Suplantación) | Un estudiante intenta acceder con la identidad de un docente o de otro estudiante. | Crítico | Validación de tokens firmados y verificación de identidad y rol en cada endpoint mediante inyección de dependencias (`get_current_user`). |
| **Tampering** (Manipulación) | Modificación de calificaciones o respuestas durante el envío. | Alto | Cálculo de calificación determinista exclusivamente en el backend (`grading_service.py`). Las respuestas no son alterables una vez enviadas. |
| **Repudiation** (Repudio) | Un estudiante niega haber entregado un intento. | Medio | Registro de fecha y hora (`submitted_at`) inmutable en la base de datos junto al ID del estudiante. |
| **Information Disclosure** (Fuga de Información) | **1.** Un estudiante inspecciona el payload JSON para ver las respuestas correctas antes de entregar.<br>**2.** Un docente consulta actividades de otro docente. | Crítico | **1.** Esquemas Pydantic diferenciados (`ActivityStudentView` omite campos de respuestas correctas).<br>**2.** Verificación de pertenencia a clase y propiedad de recursos en el backend. |
| **Denial of Service** (Denegación de Servicio) | Carga masiva de PDFs gigantes o peticiones excesivas de generación por IA. | Alto | Validación de tamaño máximo de archivo PDF (e.g. 10MB), saneamiento previo de texto y límite de reintentos en trabajos asíncronos (`max_retries=3`). |
| **Elevation of Privilege** (Elevación de Privilegios) | Un estudiante invoca el endpoint de creación de clases o generación de actividades. | Crítico | Dependencia `require_role('teacher')` que bloquea solicitudes no autorizadas con código HTTP 403 Forbidden. |
