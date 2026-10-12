import base64
import json
import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def _b64(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()


def test_hash_password_does_not_store_plaintext_and_verifies():
    hashed = hash_password("S3cret-pass")
    assert "S3cret-pass" not in hashed
    assert hashed.startswith("$argon2")
    assert verify_password("S3cret-pass", hashed)
    assert not verify_password("wrong-pass", hashed)


def test_access_token_roundtrip_contains_subject_and_role():
    user_id = uuid.uuid4()
    token = create_access_token(user_id=user_id, role="teacher")
    claims = decode_access_token(token)
    assert claims.user_id == user_id
    assert claims.role == "teacher"


def test_expired_token_is_rejected():
    token = create_access_token(
        user_id=uuid.uuid4(), role="student", expires_delta=timedelta(seconds=-1)
    )
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_token_signed_with_other_key_is_rejected():
    now = datetime.now(UTC)
    payload = {
        "sub": str(uuid.uuid4()),
        "role": "teacher",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "jti": uuid.uuid4().hex,
    }
    forged = jwt.encode(payload, "another-key-that-is-at-least-32-bytes!!", algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        decode_access_token(forged)


def test_tampered_payload_is_rejected():
    token = create_access_token(user_id=uuid.uuid4(), role="student")
    header, _, signature = token.split(".")
    now = int(datetime.now(UTC).timestamp())
    tampered_payload = _b64(
        {"sub": str(uuid.uuid4()), "role": "teacher", "iat": now, "exp": now + 300, "jti": "x"}
    )
    with pytest.raises(InvalidTokenError):
        decode_access_token(f"{header}.{tampered_payload}.{signature}")


def test_alg_none_token_is_rejected():
    now = int(datetime.now(UTC).timestamp())
    header = _b64({"alg": "none", "typ": "JWT"})
    payload = _b64(
        {"sub": str(uuid.uuid4()), "role": "teacher", "iat": now, "exp": now + 300, "jti": "x"}
    )
    with pytest.raises(InvalidTokenError):
        decode_access_token(f"{header}.{payload}.")


@pytest.mark.parametrize("missing", ["sub", "role", "exp", "jti"])
def test_token_missing_required_claim_is_rejected(missing: str):
    now = datetime.now(UTC)
    payload = {
        "sub": str(uuid.uuid4()),
        "role": "teacher",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "jti": uuid.uuid4().hex,
    }
    del payload[missing]
    token = jwt.encode(payload, get_settings().SECRET_KEY, algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_token_with_unknown_role_is_rejected():
    now = datetime.now(UTC)
    payload = {
        "sub": str(uuid.uuid4()),
        "role": "admin",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "jti": uuid.uuid4().hex,
    }
    token = jwt.encode(payload, get_settings().SECRET_KEY, algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)
