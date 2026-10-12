# Seguridad del RAG y del procesamiento de documentos — LessonForge AI

**Versión 2.0.** Complementa [security-requirements.md](security-requirements.md) (LLM01, LLM05,
LLM08 y LLM10).

## 1. Vectores de ataque

1. **Inyección indirecta de prompts.** El PDF contiene instrucciones como "Ignora las
   instrucciones previas…", a veces ocultas en texto blanco o de tamaño 0.
2. **Inyección directa.** Llega a través del contexto del ejercicio, las palabras clave o las
   respuestas del alumno, que se usan en el prompt de retroalimentación.
3. **Fuga entre inquilinos por la búsqueda vectorial.** Una consulta recupera fragmentos de la
   lección de otro tutor.
4. **Salida maliciosa o malformada.** HTML o scripts en los enunciados, JSON inválido, claves
   incoherentes.
5. **Denegación de servicio con documentos.** PDF bomb, objetos recursivos, miles de páginas.
6. **Abuso de consumo.** Muchas solicitudes de generación o de ítems.

## 2. Mitigaciones

| Vector | Mitigación |
|---|---|
| 1, 2 | El prompt del sistema declara que el material entre `<material id="…">…</material>` y los campos del usuario son **datos, nunca instrucciones**. Los delimitadores que aparezcan en el contenido se escapan o eliminan. Los campos del usuario tienen longitud acotada. El LLM **no tiene herramientas** ni acceso a datos: lo peor que puede hacer una inyección es estropear una actividad, y eso lo detecta la validación y lo filtra la revisión del tutor |
| 3 | `Retriever.search(lesson_id, query)`: el filtro `WHERE lesson_id = :id` es obligatorio y está en el repositorio. Hay una prueba de aislamiento con dos lecciones de contenido casi idéntico |
| 4 | Esquema JSON estricto (Pydantic con `extra="forbid"`), reglas de dominio y citas que deben pertenecer a los fragmentos recuperados. El frontend renderiza solo texto. Si la salida no es válida, se reintenta y, agotados los intentos, el trabajo queda en `FAILED` |
| 5 | Hasta 10 MB, con el tamaño validado mientras se recibe el archivo. Firma `%PDF-`. Hasta 50 páginas. Tiempo máximo de extracción en el worker. Solo se extrae texto: se ignoran JavaScript, formularios y archivos incrustados. Límite de caracteres extraídos |
| 6 | 10 generaciones por hora por tutor, cuota diaria de tokens, hasta 20 ítems, `max_tokens` y 3 intentos como máximo |

## 3. Pruebas asociadas

Ver [testing-strategy.md](testing-strategy.md):
- `test_retriever.py` (aislamiento);
- `test_output_validator.py`;
- `test_prompt_builder.py`;
- `test_ingestion.py`;
- el corpus de inyecciones (`pytest -m live_llm`).
