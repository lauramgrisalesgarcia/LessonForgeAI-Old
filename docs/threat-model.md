# Modelo de amenazas — LessonForge AI

**Versión 2.0.** Metodología: STRIDE sobre los flujos del MVP. Los controles se detallan en
[security-requirements.md](security-requirements.md).

## 1. Activos

- Respuestas correctas antes de entregar.
- Notas y observaciones de cada alumno.
- Observaciones privadas del tutor.
- Material PDF de cada lección.
- Secretos: clave JWT, credenciales de la base de datos, claves de la IA.
- Cuota y coste del proveedor de IA.

## 2. Límites de confianza

1. Navegador ↔ API (Internet).
2. API y worker ↔ proveedor de IA (salida no confiable).
3. Contenido del PDF ↔ prompt (datos no confiables).
4. Servicios de Cloud Run ↔ Secret Manager y base de datos.

## 3. Amenazas y mitigaciones

| STRIDE | Amenaza | Impacto | Mitigación |
|---|---|---|---|
| **S** Suplantación | Robo o falsificación de un JWT. Fuerza bruta en el inicio de sesión | Crítico | Firma HS256 con clave de Secret Manager, `alg` fijado, 30 min de vida, token en memoria (no `localStorage`), límite de peticiones en el inicio de sesión |
| **T** Manipulación | El alumno altera su nota o reenvía respuestas. El LLM devuelve claves incoherentes | Alto | Nota calculada solo en el backend (ADR-006). `UNIQUE(activity_id, student_id)`. Salida del LLM validada |
| **R** Repudio | El alumno niega haber entregado | Medio | `submitted_at` inmutable y log de auditoría con `request_id` |
| **I** Divulgación | El alumno ve las claves antes de entregar. El alumno o el tutor ven datos ajenos. Fuga por RAG entre lecciones. Las observaciones del tutor llegan al alumno vía la IA | Crítico | Rutas y esquemas por rol, claves en una tabla aparte, 404 en recursos ajenos, filtro `lesson_id` obligatorio, observaciones excluidas del prompt de retroalimentación |
| **D** Denegación de servicio | PDF bomb. Ráfagas de generación que agotan la cuota de la IA | Alto | Límites de tamaño y páginas, tiempos máximos, límites de tasa, cuota diaria de tokens, como máximo 3 intentos |
| **E** Elevación de privilegios | Un alumno invoca endpoints de tutor. Una inyección de prompts intenta que el LLM actúe | Crítico | `require_role` en los routers `/tutor`. El LLM no tiene herramientas ni acceso a la base de datos y no decide la nota |
