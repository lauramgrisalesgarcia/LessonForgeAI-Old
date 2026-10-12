from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TutorStudent, User


async def list_students(session: AsyncSession, teacher: User) -> Sequence[User]:
    """Alumnos vinculados al tutor, ordenados por email."""
    result = await session.scalars(
        select(User)
        .join(TutorStudent, TutorStudent.student_id == User.id)
        .where(TutorStudent.teacher_id == teacher.id)
        .order_by(User.email)
    )
    return result.all()
