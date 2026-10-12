# ADR-004: RAG con embeddings y pgvector

## Estado
Aceptado (11 de octubre de 2026)

## Contexto
La generación debe basarse en el material de la lección (PDF, palabras clave y contexto) y no en
el conocimiento general del modelo. Un PDF de hasta 50 páginas no cabe de forma fiable ni
económica entero en cada prompt, y además la recuperación debe estar **aislada por lección**
(OWASP LLM08).

## Alternativas consideradas
1. **Pasar el PDF completo en el prompt.** Es simple, pero caro, limitado por la ventana de
   contexto y sin citas precisas.
2. **Búsqueda de texto completo de PostgreSQL** (`tsvector`). Determinista y sin coste, pero no
   capta sinónimos ni paráfrasis: es un RAG débil.
3. **Embeddings con pgvector** en la misma PostgreSQL.
4. **Base de datos vectorial dedicada** (Pinecone, Qdrant…). Añade un servicio y credenciales sin
   aportar nada a este volumen.

## Decisión
**Alternativa 3.**
- **Ingesta:** pypdf extrae el texto por página y se divide en fragmentos de unos 800 caracteres
  con 100 de solapamiento, respetando párrafos. Cada fragmento se convierte en embedding con
  `EmbeddingProvider` (dimensión configurable, 768 por defecto) y se guarda en
  `document_chunks.embedding` con un índice HNSW (`vector_cosine_ops`).
- **Recuperación:** la consulta combina palabras clave, contexto y nivel, y se ordena por
  `embedding <=> :q` con el filtro **obligatorio** `lesson_id`, tomando k = 8. Además se garantiza al
  menos un fragmento por palabra clave cuando exista uno que la contenga.
- **Citas:** cada ítem generado referencia los `chunk_id` usados, y el validador comprueba que
  pertenecen a los recuperados.
- **Pruebas:** `FakeEmbeddingProvider` genera vectores deterministas a partir de un hash del texto,
  de modo que la CI no depende de la red.
- Imagen local y de CI: `pgvector/pgvector:pg16`. En producción, una PostgreSQL gestionada con la
  extensión `vector` (Cloud SQL y Neon la admiten).

## Consecuencias
- Es un RAG real y defendible, sin infraestructura adicional.
- Cambiar de modelo de embeddings obliga a reindexar (la dimensión está ligada al esquema). Se
  registra el modelo usado.
- Coste de embeddings: un PDF de 50 páginas genera unos 150 fragmentos por documento, lo cual es
  aceptable.
