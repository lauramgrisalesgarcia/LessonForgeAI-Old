from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Fábrica de la aplicación FastAPI para LessonForge AI."""
    settings = get_settings()

    docs_url = "/docs" if settings.DOCS_ENABLED else None
    redoc_url = "/redoc" if settings.DOCS_ENABLED else None
    openapi_url = "/openapi.json" if settings.DOCS_ENABLED else None

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        description=(
            "API del monolito modular LessonForge AI para generación de actividades de idiomas"
        ),
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    # Middleware de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registro de rutas de API v1
    app.include_router(api_v1_router, prefix="/api/v1")

    @app.get("/", tags=["root"])
    async def root():
        return {
            "message": f"Bienvenido a la API de {settings.PROJECT_NAME}",
            "docs": docs_url,
        }

    return app


app = create_app()
