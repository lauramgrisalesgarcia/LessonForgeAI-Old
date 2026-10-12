import pytest
from pydantic import ValidationError

from app.core.config import DEV_AI_API_KEY, DEV_SECRET_KEY, Settings

SECURE_KEY = "x" * 48


def make_settings(**overrides: object) -> Settings:
    # _env_file=None aísla la prueba de cualquier backend/.env local
    return Settings(_env_file=None, **overrides)  # type: ignore[call-arg]


def test_development_accepts_dummy_secrets():
    settings = make_settings(ENVIRONMENT="development")
    assert settings.SECRET_KEY == DEV_SECRET_KEY


def test_production_rejects_dummy_secret_key():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        make_settings(ENVIRONMENT="production", AI_API_KEY="real-looking-key")


def test_production_rejects_short_secret_key():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        make_settings(ENVIRONMENT="production", SECRET_KEY="short", AI_API_KEY="k")


def test_production_rejects_dummy_ai_key():
    with pytest.raises(ValidationError, match="AI_API_KEY"):
        make_settings(ENVIRONMENT="production", SECRET_KEY=SECURE_KEY, AI_API_KEY=DEV_AI_API_KEY)


def test_production_accepts_real_secrets():
    settings = make_settings(
        ENVIRONMENT="production", SECRET_KEY=SECURE_KEY, AI_API_KEY="provider-key"
    )
    assert settings.ENVIRONMENT == "production"
