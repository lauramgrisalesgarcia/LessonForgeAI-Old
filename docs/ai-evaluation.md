# Evaluación de IA - LessonForge AI

## 1. Objetivos de la Evaluación
Asegurar que los componentes de IA (generación de preguntas y generación de observaciones pedagógicas) cumplan con criterios rigurosos de:
1. Relevancia y fidelidad al documento fuente.
2. Dificultad adecuada al nivel pedagógico.
3. Formato estructurado estricto (cero errores de parsing JSON).
4. Retroalimentación formativa constructiva sin alucinaciones.

## 2. Métricas e Indicadores
- **Fidelidad al contexto (Groundedness)**: ¿Las preguntas y respuestas correctas se fundamentan de forma demostrable en los fragmentos de texto del documento?
- **Tasa de conformidad estructural**: Porcentaje de respuestas del LLM que se parsean exitosamente mediante el esquema Pydantic a la primera iteración vs tras reintentos.
- **Tono y valor pedagógico**: Evaluación cualitativa de las observaciones generadas ante respuestas incorrectas del estudiante (¿explica la regla gramatical o vocabulario relevante sin ser despectivo ni confuso?).
