# ADR-006: Calificación determinista; la IA solo redacta observaciones

## Estado
Aceptado (11 de octubre de 2026)

## Contexto
El alumno resuelve un cuestionario (`quiz`) o un ejercicio de completar frases (`fill_blank`) y
debe recibir una nota y observaciones. Se planteó que el LLM pusiera la nota.

## Alternativas consideradas
1. **El LLM califica.** No es reproducible (la misma entrega puede recibir notas distintas), se
   puede manipular con inyección en las respuestas del alumno (LLM01), delega una decisión con
   impacto en el modelo (LLM06, LLM09) y es difícil de probar con TDD.
2. **Híbrida.** El LLM propone aceptar respuestas que no coinciden. Es más flexible, pero
   reintroduce la falta de determinismo.
3. **Determinista.** El backend compara con las claves guardadas al generar la actividad, que el
   tutor revisó antes de publicar.

## Decisión
**Alternativa 3.**
- `quiz`: es correcto si `answer == correct_option_id`.
- `fill_blank`: `normalize(answer) ∈ {normalize(a) for a in accepted_answers}`, donde `normalize`
  convierte a minúsculas, recorta y colapsa espacios y quita la puntuación final. **Las tildes y
  la ortografía cuentan**, porque son parte del aprendizaje del idioma.
- Nota = aciertos / total × 100, con 2 decimales. Se acompaña de un desglose por ítem.
- La calificación es **síncrona** al entregar. Las observaciones de IA son un trabajo asíncrono
  que **lee** la nota pero **nunca la modifica**. Si fallan, `feedback_status = FAILED` y el tutor
  puede volver a encolar el trabajo. La nota sigue disponible.
- `grading_service` contiene funciones puras sin E/S y es lo primero que se desarrolla con TDD.

## Consecuencias
- La nota es reproducible, auditable y no se puede manipular desde el prompt.
- En `fill_blank` una respuesta válida que no esté en `accepted_answers` cuenta como incorrecta.
  Se mitiga pidiendo al LLM de 1 a 3 variantes aceptadas y con la revisión del tutor. Como mejora
  futura, el tutor podría ajustar la nota a mano.
