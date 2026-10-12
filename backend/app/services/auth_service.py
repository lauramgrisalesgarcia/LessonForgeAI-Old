from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, verify_password_dummy
from app.models import User


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def authenticate(session: AsyncSession, email: str, password: str) -> User | None:
    """Devuelve el usuario si las credenciales son válidas y está activo; si no, None.

    Siempre ejecuta una verificación Argon2 para no revelar por tiempo si el email existe.
    """
    user = await session.scalar(select(User).where(User.email == normalize_email(email)))
    if user is None:
        verify_password_dummy()
        return None
    if not verify_password(password, user.hashed_password) or not user.is_active:
        return None
    return user
