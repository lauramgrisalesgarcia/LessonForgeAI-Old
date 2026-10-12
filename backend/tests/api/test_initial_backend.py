import pytest
from httpx import AsyncClient

from app.core.config import get_settings


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Verifica que el endpoint raíz responda correctamente."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "LessonForge AI" in data["message"]


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    """Verifica que el endpoint de salud de api/v1 responda según el esquema HealthResponse."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "LessonForge AI"
    assert data["environment"] == get_settings().ENVIRONMENT


@pytest.mark.asyncio
async def test_openapi_schema_generated(async_client: AsyncClient):
    """Verifica que FastAPI genere automáticamente el contrato OpenAPI."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert openapi["info"]["title"] == "LessonForge AI"
    assert "/api/v1/health" in openapi["paths"]
