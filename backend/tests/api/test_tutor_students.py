from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserRole
from tests.factories import auth_headers, create_user, link_tutor_student

STUDENTS_URL = "/api/v1/tutor/students"


async def test_tutor_lists_only_own_students(client: AsyncClient, db_session: AsyncSession):
    tutor = await create_user(db_session, UserRole.TEACHER)
    other_tutor = await create_user(db_session, UserRole.TEACHER)
    mine = await create_user(db_session, UserRole.STUDENT, email="b-mine@example.com")
    also_mine = await create_user(db_session, UserRole.STUDENT, email="a-mine@example.com")
    not_mine = await create_user(db_session, UserRole.STUDENT)
    await link_tutor_student(db_session, tutor, mine)
    await link_tutor_student(db_session, tutor, also_mine)
    await link_tutor_student(db_session, other_tutor, not_mine)

    response = await client.get(STUDENTS_URL, headers=await auth_headers(client, tutor))

    assert response.status_code == 200
    emails = [student["email"] for student in response.json()]
    assert emails == ["a-mine@example.com", "b-mine@example.com"]


async def test_student_cannot_list_tutor_students(client: AsyncClient, db_session: AsyncSession):
    student = await create_user(db_session, UserRole.STUDENT)

    response = await client.get(STUDENTS_URL, headers=await auth_headers(client, student))

    assert response.status_code == 403


async def test_anonymous_cannot_list_tutor_students(client: AsyncClient):
    response = await client.get(STUDENTS_URL)

    assert response.status_code == 401
