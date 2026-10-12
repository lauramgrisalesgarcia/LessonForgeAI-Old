from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Valores ficticios permitidos solo en desarrollo y pruebas
DEV_SECRET_KEY = "dummy-insecure-secret-key-for-development-only-change-in-prod"
DEV_AI_API_KEY = "dummy-ai-api-key-for-testing"


class Settings(BaseSettings):
    """Configuración centralizada y tipada de LessonForge AI."""

    PROJECT_NAME: str = "LessonForge AI"
    ENVIRONMENT: str = "development"
    DOCS_ENABLED: bool = True

    # Servidor
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Base de datos (Valores por defecto para arranque y testing)
    DATABASE_URL: str = (
        "postgresql+asyncpg://lessonforge_user:lessonforge_dummy_password"
        "@localhost:5432/lessonforge_db"
    )

    # Seguridad y Autenticación (Valores ficticios)
    SECRET_KEY: str = DEV_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Almacenamiento de archivos
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Proveedor de IA (ficticio)
    AI_API_KEY: str = DEV_AI_API_KEY
    AI_MODEL_NAME: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def reject_dev_secrets_in_production(self) -> "Settings":
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == DEV_SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY debe definirse con un valor seguro en producción")
            if self.AI_API_KEY == DEV_AI_API_KEY:
                raise ValueError("AI_API_KEY debe definirse en producción")
        return self


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de la configuración."""
    return Settings()
