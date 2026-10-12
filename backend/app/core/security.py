import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

_password_hash = PasswordHash.recommended()  # Argon2id

VALID_ROLES = frozenset({"teacher", "student"})
REQUIRED_CLAIMS = ["sub", "role", "iat", "exp", "jti"]


class InvalidTokenError(Exception):
    """Token ausente, caducado, mal firmado o con claims inválidos."""


@dataclass(frozen=True)
class TokenClaims:
    user_id: uuid.UUID
    role: str


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return _password_hash.verify(password, hashed_password)


# Hash fijo para comparar cuando el email no existe: iguala el tiempo de respuesta (A07)
_DUMMY_HASH = hash_password("timing-equalizer-not-a-real-password")


def verify_password_dummy() -> None:
    verify_password("timing-equalizer-wrong", _DUMMY_HASH)


def create_access_token(
    *, user_id: uuid.UUID, role: str, expires_delta: timedelta | None = None
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    expires = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": expires,
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> TokenClaims:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": REQUIRED_CLAIMS},
        )
        user_id = uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError) as exc:
        raise InvalidTokenError from exc

    role = payload["role"]
    if role not in VALID_ROLES:
        raise InvalidTokenError
    return TokenClaims(user_id=user_id, role=role)
