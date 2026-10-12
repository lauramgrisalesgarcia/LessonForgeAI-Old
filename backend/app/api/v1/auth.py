from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.core.security import create_access_token
from app.schemas.auth import TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import authenticate

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], session: DbSession
) -> TokenResponse:
    """Inicio de sesión con email (campo `username`) y contraseña. Devuelve un JWT Bearer."""
    user = await authenticate(session, form.username, form.password)
    if user is None:
        # Mismo mensaje para email inexistente, contraseña errónea o usuario inactivo (A07)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    return TokenResponse(
        access_token=create_access_token(user_id=user.id, role=user.role.value),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserRead, tags=["users"])
async def read_me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
