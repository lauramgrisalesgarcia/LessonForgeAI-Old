# ADR-003: Estrategia de Almacenamiento de Documentos PDF

## Estado
Propuesto

## Contexto y Problema
LessonForge AI permite a los docentes subir materiales educativos en formato PDF. El backend debe almacenar el archivo binario y asociarlo a la entidad `Document` correspondiente, extrayendo su texto de forma segura para RAG.

## Alternativas Consideradas

### Alternativa 1: Sistema de archivos local montado en volumen Docker
- **Ventajas**: Máxima simplicidad, sin costos ni credenciales externas, acceso directo por rutas locales.
- **Desventajas**: Requiere montaje persistente de volúmenes en contenedores; no es escalable automáticamente en entornos serverless multi-región.

### Alternativa 2: Object Storage compatible con S3 (MinIO / AWS S3 / Cloudflare R2)
- **Ventajas**: Escalabilidad ilimitada, URLs prefirmadas para descargas directas.
- **Desventajas**: Requiere contenedor adicional (MinIO) o credenciales de nube activas para desarrollo local.

## Decisión Propuesta y Justificación
Se adopta la **Alternativa 1** encapsulada tras una abstracción (`document_service.py`): almacenamiento en un directorio local montado `/app/uploads` con nombres de archivo hasheados (UUID) para prevenir colisiones y vulnerabilidades de path traversal.
