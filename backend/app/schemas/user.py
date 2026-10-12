import uuid

from pydantic import BaseModel, ConfigDict

from app.models import UserRole


class UserRead(BaseModel):
    """Perfil público. Nunca incluye el hash de la contraseña."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
