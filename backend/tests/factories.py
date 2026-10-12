import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import TutorStudent, User, UserRole

# Contraseña de prueba (solo para la base de datos de test)
TEST_PASSWORD = "Test-Password-123"


async def create_user(
    session: AsyncSession,
    role: UserRole,
    *,
    email: str | None = None,
    password: str = TEST_PASSWORD,
    is_active: bool = True,
) -> User:
    user = User(
        email=email or f"{role.value}-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=hash_password(password),
        full_name=f"{role.value.title()} de prueba",
        role=role,
        is_active=is_active,
    )
    session.add(user)
    await session.flush()
    return user


async def link_tutor_student(session: AsyncSession, teacher: User, student: User) -> None:
    session.add(TutorStudent(teacher_id=teacher.id, student_id=student.id))
    await session.flush()


async def login(client: AsyncClient, email: str, password: str = TEST_PASSWORD) -> str:
    response = await client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


async def auth_headers(client: AsyncClient, user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {await login(client, user.email)}"}
