import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models import UserRole
from tests.factories import TEST_PASSWORD, auth_headers, create_user

LOGIN_URL = "/api/v1/auth/login"


async def test_login_returns_bearer_token(client: AsyncClient, db_session: AsyncSession):
    teacher = await create_user(db_session, UserRole.TEACHER)

    response = await client.post(
        LOGIN_URL, data={"username": teacher.email, "password": TEST_PASSWORD}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] == 30 * 60


async def test_login_email_is_case_insensitive(client: AsyncClient, db_session: AsyncSession):
    await create_user(db_session, UserRole.STUDENT, email="alumno.case@example.com")

    response = await client.post(
        LOGIN_URL, data={"username": "  Alumno.CASE@example.com ", "password": TEST_PASSWORD}
    )

    assert response.status_code == 200


async def test_wrong_password_and_unknown_email_get_identical_401(
    client: AsyncClient, db_session: AsyncSession
):
    teacher = await create_user(db_session, UserRole.TEACHER)

    wrong_password = await client.post(
        LOGIN_URL, data={"username": teacher.email, "password": "not-the-password"}
    )
    unknown_email = await client.post(
        LOGIN_URL, data={"username": "nobody@example.com", "password": TEST_PASSWORD}
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.headers.get("www-authenticate") == "Bearer"


async def test_inactive_user_cannot_login(client: AsyncClient, db_session: AsyncSession):
    inactive = await create_user(db_session, UserRole.STUDENT, is_active=False)

    response = await client.post(
        LOGIN_URL, data={"username": inactive.email, "password": TEST_PASSWORD}
    )

    assert response.status_code == 401


async def test_me_requires_authentication(client: AsyncClient):
    response = await client.get("/api/v1/me")

    assert response.status_code == 401


async def test_me_rejects_malformed_token(client: AsyncClient):
    response = await client.get("/api/v1/me", headers={"Authorization": "Bearer not-a-jwt"})

    assert response.status_code == 401


async def test_me_returns_profile_without_password(client: AsyncClient, db_session: AsyncSession):
    teacher = await create_user(db_session, UserRole.TEACHER)

    response = await client.get("/api/v1/me", headers=await auth_headers(client, teacher))

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "id": str(teacher.id),
        "email": teacher.email,
        "full_name": teacher.full_name,
        "role": "teacher",
    }


async def test_token_of_deactivated_user_is_rejected(client: AsyncClient, db_session: AsyncSession):
    student = await create_user(db_session, UserRole.STUDENT)
    headers = await auth_headers(client, student)

    student.is_active = False
    await db_session.flush()

    response = await client.get("/api/v1/me", headers=headers)
    assert response.status_code == 401


async def test_token_whose_role_no_longer_matches_is_rejected(
    client: AsyncClient, db_session: AsyncSession
):
    student = await create_user(db_session, UserRole.STUDENT)
    forged_role_token = create_access_token(user_id=student.id, role="teacher")

    response = await client.get(
        "/api/v1/me", headers={"Authorization": f"Bearer {forged_role_token}"}
    )

    assert response.status_code == 401


async def test_token_for_nonexistent_user_is_rejected(client: AsyncClient):
    token = create_access_token(user_id=uuid.uuid4(), role="teacher")

    response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
