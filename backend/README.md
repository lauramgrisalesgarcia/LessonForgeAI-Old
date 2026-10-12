# LessonForge AI — Backend

API FastAPI del monolito modular. Dependencias gestionadas con [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                  # crea .venv con Python 3.12 y dependencias de desarrollo
uv run uvicorn app.main:app --reload     # http://127.0.0.1:8000/docs
uv run pytest                            # pruebas
uv run ruff check . && uv run ruff format --check .
```

La configuración se lee de variables de entorno o de `backend/.env` (ver `.env.example`).
Con `ENVIRONMENT=production` la aplicación se niega a arrancar si `SECRET_KEY` o `AI_API_KEY`
conservan los valores ficticios de desarrollo.
