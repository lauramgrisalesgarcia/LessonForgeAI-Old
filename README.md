# LessonForge AI

Aplicación web para docentes de idiomas: cargan material de clase en PDF y generan, mediante IA,
actividades de refuerzo (opción múltiple y completar espacios). Los estudiantes las resuelven,
reciben una **calificación determinista** (calculada en el backend, sin IA) y retroalimentación
pedagógica generada por IA.

Proyecto final de maestría — entrega: 26 de octubre de 2026. Solo usa datos ficticios.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | React 18, Vite, TypeScript estricto, Vitest + Testing Library |
| Backend | Python 3.12, FastAPI, SQLAlchemy async, Alembic, pytest + HTTPX |
| Datos | PostgreSQL 16 |
| Infra | Docker Compose, GitHub Actions |

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

Con Docker (incluye PostgreSQL):

```bash
docker compose -f infra/docker-compose.yml up --build
```

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
- ADR: [001 Autenticación](docs/adr/ADR-001-auth-and-session.md) · [002 Trabajos asíncronos](docs/adr/ADR-002-async-job-queue.md) · [003 Almacenamiento PDF](docs/adr/ADR-003-pdf-storage-strategy.md)
