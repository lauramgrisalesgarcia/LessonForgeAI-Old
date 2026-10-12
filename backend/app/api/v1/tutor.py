from fastapi import APIRouter

from app.core.deps import CurrentTeacher, DbSession
from app.schemas.user import StudentRead
from app.services import tutor_service

router = APIRouter(prefix="/tutor", tags=["tutor"])


@router.get("/students", response_model=list[StudentRead])
async def list_my_students(teacher: CurrentTeacher, session: DbSession) -> list[StudentRead]:
    """Alumnos vinculados al tutor autenticado."""
    students = await tutor_service.list_students(session, teacher)
    return [StudentRead.model_validate(student) for student in students]
