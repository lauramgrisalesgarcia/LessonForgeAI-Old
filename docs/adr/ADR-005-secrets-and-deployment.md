# ADR-005: Gestión de secretos y despliegue en Google Cloud

## Estado
Aceptado (11 de octubre de 2026). Queda pendiente elegir la base de datos gestionada.

## Contexto
La app maneja secretos: `SECRET_KEY` del JWT, `DATABASE_URL` y las claves del proveedor de IA. No
pueden estar en el repositorio, la imagen ni los logs (OWASP A02 y A04). El proyecto se presentará
desplegado en Google Cloud.

## Alternativas consideradas
1. **Variables de entorno definidas a mano en Cloud Run.** Quedan visibles en la configuración del
   servicio y sin control de versiones ni de acceso.
2. **Secret Manager leído desde el código con el SDK** (`google-cloud-secret-manager`). Es
   explícito, pero acopla la app a GCP y complica el arranque local y las pruebas.
3. **Secret Manager con referencias nativas de Cloud Run**, que inyecta cada secreto como variable
   de entorno al arrancar la instancia.

## Decisión
**Alternativa 3.**
- Secretos en Secret Manager: `lf-secret-key`, `lf-database-url` y `lf-ai-api-key`. Los nombres se
  definen en el despliegue.
- Cloud Run los monta como variables de entorno (`--set-secrets=SECRET_KEY=lf-secret-key:latest,…`).
  La app los lee con `pydantic-settings`, **sin depender de GCP**.
- Una **cuenta de servicio dedicada** por servicio (api y worker) con
  `roles/secretmanager.secretAccessor` **solo sobre esos secretos**.
- En local y CI se usan valores ficticios en `.env` y proveedores falsos. La app **se niega a
  arrancar** en `ENVIRONMENT=production` si detecta valores ficticios (ya implementado en
  `core/config.py`).
- Rotación: se crea una nueva versión del secreto y se vuelve a desplegar.

### Despliegue
- **api**: Cloud Run con la imagen del backend, `ENVIRONMENT=production` y `DOCS_ENABLED=false`.
- **worker**: Cloud Run con la misma imagen, el comando `python -m app.worker`, CPU siempre asignada
  y 1 instancia mínima (ver ADR-002).
- **Frontend**: build estático servido desde Cloud Run, Firebase Hosting o Cloud Storage.
- **Base de datos (pendiente):** Cloud SQL para PostgreSQL (unos 10 USD al mes, con conexión
  privada) o Neon (plan gratuito). Ambas admiten pgvector.
- Imágenes en Artifact Registry. El despliegue es manual con `gcloud` para el MVP; automatizarlo
  desde CI con Workload Identity Federation (sin claves JSON) queda como mejora.

## Consecuencias
- Hay cero secretos en el código y la imagen, el acceso es auditable en Cloud Audit Logs y la app
  sigue siendo portable.
- Rotar un secreto exige volver a desplegar, lo que es aceptable.
- Coste continuo del worker con instancia mínima y de la base de datos gestionada.
