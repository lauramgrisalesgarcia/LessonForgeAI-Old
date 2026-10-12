import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TutorStudent, User, UserRole
from tests.factories import create_user


async def test_email_must_be_unique(db_session: AsyncSession):
    await create_user(db_session, UserRole.STUDENT, email="dup@example.com")

    with pytest.raises(IntegrityError):
        await create_user(db_session, UserRole.TEACHER, email="dup@example.com")


async def test_email_must_be_stored_lowercase(db_session: AsyncSession):
    db_session.add(
        User(email="Upper@Example.com", hashed_password="x", full_name="X", role=UserRole.STUDENT)
    )

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_tutor_student_link_is_unique(db_session: AsyncSession):
    tutor = await create_user(db_session, UserRole.TEACHER)
    student = await create_user(db_session, UserRole.STUDENT)
    db_session.add(TutorStudent(teacher_id=tutor.id, student_id=student.id))
    await db_session.flush()

    db_session.add(TutorStudent(teacher_id=tutor.id, student_id=student.id))
    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_vector_extension_is_installed(db_session: AsyncSession):
    from sqlalchemy import text

    installed = await db_session.scalar(
        text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
    )
    assert installed is not None
