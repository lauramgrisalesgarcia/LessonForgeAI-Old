# ADR-003: Almacenamiento de los PDF

## Estado
Aceptado (11 de octubre de 2026). Sustituye a la propuesta anterior de usar un volumen local.

## Contexto
El tutor sube un PDF (hasta 10 MB) por lección. La API lo recibe, pero lo procesa el **worker**,
que es otro proceso y, en producción, otro servicio de Cloud Run. El sistema de archivos de Cloud
Run es **efímero** y no se comparte entre servicios, así que un volumen local no sirve en
producción. Una vez extraído el texto, los fragmentos y los embeddings quedan en PostgreSQL y el
binario ya no se necesita.

## Alternativas consideradas
1. **Volumen local** (la propuesta anterior). Funciona con Docker Compose, pero **no en Cloud Run**.
2. **Google Cloud Storage** con una abstracción `BlobStorage`. Escalable, pero requiere un bucket,
   IAM, una implementación falsa para las pruebas y un emulador o credenciales en local.
3. **Tabla `document_blobs` (BYTEA) en PostgreSQL, temporal.** El blob se elimina cuando la
   ingesta termina bien.

## Decisión
**Alternativa 3**, detrás de una pequeña interfaz `BlobStorage` (`put`, `get`, `delete`):
- Funciona igual en local, CI y Cloud Run, sin servicios adicionales.
- **Minimización de datos:** el PDF original no se conserva. Se guardan `sha256`, tamaño, número de
  páginas, nombre de archivo saneado y los fragmentos.
- Ninguna ruta del sistema de archivos depende de datos del usuario, lo que elimina el riesgo de
  *path traversal*.

## Consecuencias
- No se puede volver a descargar el PDF original. Se acepta: no es un requisito.
- Hasta 10 MB por fila durante la ingesta es aceptable para el volumen del MVP.
- Si en el futuro hiciera falta conservar los originales, se implementaría `BlobStorage` sobre GCS
  sin cambiar los servicios.
