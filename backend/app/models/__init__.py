"""Modelos SQLAlchemy. Importar aquí cada modelo para que Alembic los detecte."""

from app.models.base import Base
from app.models.user import TutorStudent, User, UserRole

__all__ = ["Base", "TutorStudent", "User", "UserRole"]
