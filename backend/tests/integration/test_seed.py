import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import verify_password
from app.models import TutorStudent, User, UserRole
from app.scripts.seed import DEMO_STUDENTS, DEMO_TEACHERS, SeedNotAllowedError, seed_demo_data

DEMO_PASSWORD = "Seed-Test-Password-1"


async def _count(session: AsyncSession, model) -> int:
    return (await session.execute(select(func.count()).select_from(model))).scalar_one()


async def test_seed_creates_demo_tutors_students_and_links(db_session: AsyncSession):
    await seed_demo_data(db_session, password=DEMO_PASSWORD, environment="development")

    teachers = (await db_session.scalars(select(User).where(User.role == UserRole.TEACHER))).all()
    students = (await db_session.scalars(select(User).where(User.role == UserRole.STUDENT))).all()
    assert {t.email for t in teachers} >= {t.email for t in DEMO_TEACHERS}
    assert {s.email for s in students} >= {s.email for s in DEMO_STUDENTS}
    assert all(u.email.endswith("@example.com") for u in [*teachers, *students])
    assert verify_password(DEMO_PASSWORD, teachers[0].hashed_password)
    assert await _count(db_session, TutorStudent) == len(DEMO_STUDENTS)


async def test_seed_is_idempotent(db_session: AsyncSession):
    await seed_demo_data(db_session, password=DEMO_PASSWORD, environment="development")
    users_before = await _count(db_session, User)
    links_before = await _count(db_session, TutorStudent)

    await seed_demo_data(db_session, password=DEMO_PASSWORD, environment="development")

    assert await _count(db_session, User) == users_before
    assert await _count(db_session, TutorStudent) == links_before


async def test_seed_refuses_to_run_in_production(db_session: AsyncSession):
    with pytest.raises(SeedNotAllowedError):
        await seed_demo_data(db_session, password=DEMO_PASSWORD, environment="production")


def test_settings_reject_unknown_environment():
    with pytest.raises(ValueError):
        Settings(_env_file=None, ENVIRONMENT="staging")  # type: ignore[call-arg]
