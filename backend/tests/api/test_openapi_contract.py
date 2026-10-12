import json

from httpx import AsyncClient

SENSITIVE_FIELDS = ("hashed_password", "password_hash")


async def test_no_response_schema_exposes_password_hashes(async_client: AsyncClient):
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200

    schemas = json.dumps(response.json().get("components", {}).get("schemas", {}))
    for field in SENSITIVE_FIELDS:
        assert field not in schemas


async def test_login_is_exposed_as_oauth2_password_flow(async_client: AsyncClient):
    openapi = (await async_client.get("/openapi.json")).json()

    schemes = openapi["components"]["securitySchemes"]
    flow = next(iter(schemes.values()))["flows"]["password"]
    assert flow["tokenUrl"] == "/api/v1/auth/login"
