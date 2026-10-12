# Requisitos de Seguridad - LessonForge AI

## 1. Control de Acceso Basado en Roles (RBAC)
- **Docente (`teacher`)**:
  - Puede subir documentos y crear clases.
  - Puede disparar la generación de actividades y visualizar respuestas correctas.
  - Puede revisar las entregas y retroalimentaciones de los estudiantes inscritos en sus clases.
  - No puede acceder a documentos ni clases de otros docentes.
- **Estudiante (`student`)**:
  - Puede inscribirse en clases para las que tenga invitación o pertenencia autorizada.
  - Puede ver y resolver actividades asignadas a sus clases.
  - **No puede acceder a las respuestas correctas** antes de enviar su intento.
  - No puede ver entregas, calificaciones ni observaciones de otros estudiantes.

## 2. Protección de Secretos y Configuración
- Todas las variables sensibles se inyectan mediante variables de entorno validadas con `pydantic-settings`.
- En entornos de producción, la documentación interactiva (`/docs`, `/redoc` y `/openapi.json`) debe poder deshabilitarse mediante la bandera `DOCS_ENABLED=false`.

## 3. Manejo Seguro de Contraseñas
- Hashing criptográfico mediante Argon2 o bcrypt con salting automático en `core/security.py`.
- Las contraseñas en texto plano nunca se registran en logs ni se exponen en esquemas de respuesta Pydantic (`UserResponse`).
