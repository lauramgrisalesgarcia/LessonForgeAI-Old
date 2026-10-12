"""Crea usuarios ficticios de demostración (tutores, alumnos y sus vínculos).

Uso: python -m app.scripts.seed   (la contraseña se toma de SEED_DEMO_PASSWORD)
Idempotente. Se niega a ejecutarse con ENVIRONMENT=production.
"""

import asyncio
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_sessionmaker
from app.core.security import hash_password
from app.models import TutorStudent, User, UserRole


class SeedNotAllowedError(RuntimeError):
    pass


@dataclass(frozen=True)
class DemoUser:
    email: str
    full_name: str


# Dominio reservado example.com: ningún dato personal real
DEMO_TEACHERS = (
    DemoUser("tutora.ana@example.com", "Ana Tutora (demo)"),
    DemoUser("tutor.bruno@example.com", "Bruno Tutor (demo)"),
)
DEMO_STUDENTS = tuple(DemoUser(f"alumno{i}@example.com", f"Alumno {i} (demo)") for i in range(1, 7))
# alumnos 1-3 → Ana; alumnos 4-6 → Bruno
DEMO_LINKS = tuple(
    (DEMO_TEACHERS[0 if i < 3 else 1].email, student.email)
    for i, student in enumerate(DEMO_STUDENTS)
)


async def _get_or_create(
    session: AsyncSession, demo: DemoUser, role: UserRole, hashed_password: str
) -> User:
    user = await session.scalar(select(User).where(User.email == demo.email))
    if user is None:
        user = User(
            email=demo.email,
            full_name=demo.full_name,
            role=role,
            hashed_password=hashed_password,
        )
        session.add(user)
        await session.flush()
    return user


async def seed_demo_data(session: AsyncSession, *, password: str, environment: str) -> None:
    if environment == "production":
        raise SeedNotAllowedError("El seed de demostración no se ejecuta en producción")

    hashed = hash_password(password)
    users: dict[str, User] = {}
    for demo in DEMO_TEACHERS:
        users[demo.email] = await _get_or_create(session, demo, UserRole.TEACHER, hashed)
    for demo in DEMO_STUDENTS:
        users[demo.email] = await _get_or_create(session, demo, UserRole.STUDENT, hashed)

    for teacher_email, student_email in DEMO_LINKS:
        key = (users[teacher_email].id, users[student_email].id)
        if await session.get(TutorStudent, key) is None:
            session.add(TutorStudent(teacher_id=key[0], student_id=key[1]))
    await session.flush()


async def main() -> None:
    settings = get_settings()
    async with get_sessionmaker()() as session:
        await seed_demo_data(
            session, password=settings.SEED_DEMO_PASSWORD, environment=settings.ENVIRONMENT
        )
        await session.commit()
    print(f"Seed completado: {len(DEMO_TEACHERS)} tutores, {len(DEMO_STUDENTS)} alumnos.")


if __name__ == "__main__":
    asyncio.run(main())
