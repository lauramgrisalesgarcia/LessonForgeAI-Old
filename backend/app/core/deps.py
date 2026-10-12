from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import InvalidTokenError, decode_access_token
from app.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DbSession = Annotated[AsyncSession, Depends(get_db)]

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: DbSession
) -> User:
    """Valida el JWT y comprueba en BD que el usuario existe, está activo y conserva su rol."""
    try:
        claims = decode_access_token(token)
    except InvalidTokenError:
        raise _CREDENTIALS_ERROR from None

    user = await session.get(User, claims.user_id)
    if user is None or not user.is_active or user.role.value != claims.role:
        raise _CREDENTIALS_ERROR
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(role: UserRole) -> Callable[[User], Awaitable[User]]:
    """Dependencia que permite el acceso solo a usuarios con el rol indicado (403 si no)."""

    async def dependency(user: CurrentUser) -> User:
        if user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
        return user

    return dependency


CurrentTeacher = Annotated[User, Depends(require_role(UserRole.TEACHER))]
CurrentStudent = Annotated[User, Depends(require_role(UserRole.STUDENT))]
