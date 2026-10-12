from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1 import auth, tutor
from app.core.config import Settings, get_settings
from app.schemas.common import HealthResponse

router = APIRouter()
router.include_router(auth.router)
router.include_router(tutor.router)


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    """Comprobación de salud básica del backend de LessonForge AI."""
    return HealthResponse(
        status="ok",
        app_name=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
    )
