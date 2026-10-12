# ADR-001: Estrategia de autenticación y manejo de sesión

## Estado
Aceptado (11 de octubre de 2026)

## Contexto
LessonForge AI necesita autenticación real y autorización por rol (tutor o alumno), verificadas en
el backend. Los usuarios son ficticios, pero los mecanismos deben ser completamente funcionales.
El cliente es una SPA de demostración y el foco del proyecto es la API.

## Alternativas consideradas
1. **JWT Bearer** en `Authorization`. Sin estado, integrado con OpenAPI y Swagger
   (`OAuth2PasswordBearer`), fácil de usar en pruebas con HTTPX. Revocar un token antes de que
   caduque es difícil.
2. **Cookie de sesión `HttpOnly`** con sesiones en PostgreSQL. Inmune a la lectura desde
   JavaScript y revocable al instante. Exige protección CSRF y una consulta a la base de datos por
   petición.
3. **Token de acceso en memoria y *refresh token* en cookie `HttpOnly`.** Es la opción más
   robusta, pero también la más compleja para el plazo.

## Decisión
**Alternativa 1**, con estas condiciones:
- **PyJWT** con `HS256`. La lista de algoritmos se fija al verificar, así que `alg=none` se
  rechaza. Se incluyen las *claims* `sub`, `role`, `exp`, `iat` y `jti`.
- Expiración de **30 min** y sin *refresh token*: al caducar, el usuario vuelve a iniciar sesión.
- `SECRET_KEY` de al menos 32 bytes, obtenida de Secret Manager en producción (ADR-005).
- Contraseñas con **Argon2** mediante `pwdlib`. Se descartan `python-jose` y `passlib` porque
  están sin mantenimiento.
- El frontend guarda el token **solo en memoria**, no en `localStorage`.
- `get_current_user` comprueba en cada petición que el usuario sigue activo y que su rol coincide
  con el del token.

## Consecuencias
- Simplicidad y buena integración con Swagger y las pruebas.
- Un token robado sirve hasta que caduca (como mucho 30 min). Se acepta para el MVP; la mejora
  natural sería la alternativa 3.
