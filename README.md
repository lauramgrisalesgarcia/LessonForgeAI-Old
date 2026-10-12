# LessonForge AI

API para tutorías de idiomas 1:1. Tras cada clase, el tutor registra la lección (PDF, palabras
clave, observaciones) y genera con IA material de refuerzo (cuestionario o completar frases)
usando **RAG** sobre ese material. El alumno lo resuelve y recibe una **nota determinista**
(calculada en el backend, sin IA) y observaciones de la IA; el tutor consulta los resultados.
El foco es el backend; el frontend es una demo mínima. Ver [requisitos](docs/requirements.md).

Proyecto final de maestría — entrega: 26 de octubre de 2026. Solo usa datos ficticios.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | React 18, Vite, TypeScript estricto, Vitest + Testing Library |
| Backend | Python 3.12, FastAPI, SQLAlchemy async, Alembic, pytest + HTTPX |
| Datos | PostgreSQL 16 + pgvector |
| Infra | Docker Compose, GitHub Actions, Cloud Run + Secret Manager |

## Estructura

```
backend/    API FastAPI (app/) y pruebas (tests/)
frontend/   SPA React + Vite
infra/      docker-compose.yml y Dockerfiles
docs/       requisitos, arquitectura, modelo de datos, seguridad, pruebas y ADR
```

## Desarrollo local

Requisitos: [uv](https://docs.astral.sh/uv/) (instala Python 3.12 automáticamente) y Node.js ≥ 22.12.

```bash
# Backend — http://127.0.0.1:8000/docs
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend — http://localhost:5173
cd frontend
npm ci
npm run dev
```

Con Docker (PostgreSQL 16 + pgvector; el backend aplica las migraciones al arrancar):

```bash
docker compose -f infra/docker-compose.yml up --build
docker exec lessonforge_backend python -m app.scripts.seed   # usuarios ficticios de demo
```

Sin Docker para el backend, con la base de datos del compose levantada
(`docker compose -f infra/docker-compose.yml up -d db`):

```bash
cd backend
uv run alembic upgrade head
uv run python -m app.scripts.seed
```

El seed crea 2 tutores (`tutora.ana@example.com`, `tutor.bruno@example.com`) y 6 alumnos
(`alumno1..6@example.com`) con la contraseña `SEED_DEMO_PASSWORD` de `backend/.env.example`.
Las pruebas del backend usan una base de datos aparte (`lessonforge_db_test`) que se crea y migra
sola.

Copia `backend/.env.example` a `backend/.env` y `frontend/.env.example` a `frontend/.env` si
necesitas cambiar valores. Los valores incluidos son ficticios; nunca subas secretos reales.

## Verificación

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest
cd frontend && npm run typecheck && npm test && npm run build
```

La misma batería se ejecuta en GitHub Actions (`.github/workflows/ci.yml`), junto con la
construcción de las imágenes Docker.

## Documentación

- [Requisitos](docs/requirements.md) · [Arquitectura](docs/architecture.md) · [Modelo de datos](docs/data-model.md)
- [Requisitos de seguridad](docs/security-requirements.md) · [Modelo de amenazas](docs/threat-model.md) · [Seguridad RAG](docs/rag-security.md)
- [Estrategia de pruebas](docs/testing-strategy.md) · [Evaluación de IA](docs/ai-evaluation.md)
- ADR: [001 Autenticación](docs/adr/ADR-001-auth-and-session.md) · [002 Trabajos asíncronos](docs/adr/ADR-002-async-job-queue.md) · [003 Almacenamiento PDF](docs/adr/ADR-003-pdf-storage-strategy.md) · [004 RAG con pgvector](docs/adr/ADR-004-rag-pgvector.md) · [005 Secretos y despliegue](docs/adr/ADR-005-secrets-and-deployment.md) · [006 Calificación determinista](docs/adr/ADR-006-deterministic-grading.md)
