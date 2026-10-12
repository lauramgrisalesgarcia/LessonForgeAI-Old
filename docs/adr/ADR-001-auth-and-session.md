# ADR-001: Estrategia de Autenticación y Manejo de Sesión

## Estado
Propuesto

## Contexto y Problema
LessonForge AI requiere autenticación real y autorización basada en roles (docente y estudiante) validada estrictamente en el backend. Los datos y usuarios serán ficticios (datos de demostración), pero los mecanismos de control de acceso, verificación de tokens o sesiones y protección contra accesos indebidos deben ser completamente funcionales.

Se debe elegir una estrategia para el transporte y validación de la identidad entre la SPA (React + TypeScript) y el backend (FastAPI).

## Alternativas Consideradas

### Alternativa 1: JWT (JSON Web Tokens) en cabecera `Authorization: Bearer <token>`
- **Ventajas**: Stateless (fácil escalabilidad horizontal sin consultar DB en cada verificación básica), estándar ampliamente adoptado, soporte nativo de FastAPI con OpenAPI (`OAuth2PasswordBearer`).
- **Desventajas y Riesgos**: Si se almacena en `localStorage` en la SPA, es vulnerable a robo mediante ataques XSS (Cross-Site Scripting). La revocación inmediata de un token activo requiere mantener una lista de revocación (blacklist) o TTLs muy cortos.
- **Mitigación**: Expiración corta (e.g. 15-30 minutos).

### Alternativa 2: Cookies de sesión `HttpOnly`, `Secure` y `SameSite=Lax` con almacenamiento en PostgreSQL
- **Ventajas**: Inmune a lectura directa desde JavaScript (mitigación total de exfiltración vía XSS), revocación instantánea eliminando el registro de sesión en la base de datos.
- **Desventajas y Riesgos**: Requiere protección estricta contra CSRF (Cross-Site Request Forgery) si se maneja con cookies sin SameSite estricto, overhead de consulta a DB por cada petición protegida.
- **Mitigación**: Uso de cabeceras personalizadas de API y atributos de cookie modernos.

### Alternativa 3: Tokens de acceso en memoria con Cookie HttpOnly para refresh
- **Ventajas**: Combina la protección contra XSS en reposo con la verificación rápida de tokens.
- **Desventajas**: Mayor complejidad de implementación y sincronización en la SPA para el MVP de maestría.

## Decisión Propuesta y Justificación
Para el MVP de LessonForge AI se propone **Tokens de acceso Bearer (JWT) gestionados mediante esquema OAuth2 de FastAPI con expiración corta**, complementados con validación estricta de permisos en backend mediante dependencias tipadas de FastAPI (`get_current_user`, `require_role`).
- Justificación: Proporciona integración natural de autenticación interactiva en Swagger UI (`/docs`), simplicidad de consumo en pruebas con HTTPX y una arquitectura limpia sin requerir almacenamiento complejo de sesiones distribuidas para el plazo del 26 de octubre de 2026.
