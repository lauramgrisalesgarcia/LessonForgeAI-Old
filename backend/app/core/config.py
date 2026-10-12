from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración centralizada y tipada de LessonForge AI."""

    PROJECT_NAME: str = "LessonForge AI"
    ENVIRONMENT: str = "development"
    DOCS_ENABLED: bool = True

    # Servidor
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Base de datos (Valores por defecto para arranque y testing)
    DATABASE_URL: str = "postgresql+asyncpg://lessonforge_user:lessonforge_dummy_password@localhost:5432/lessonforge_db"

    # Seguridad y Autenticación (Valores ficticios)
    SECRET_KEY: str = "dummy-insecure-secret-key-for-development-only-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Almacenamiento de archivos
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Proveedor de IA (ficticio)
    AI_API_KEY: str = "dummy-ai-api-key-for-testing"
    AI_MODEL_NAME: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de la configuración."""
    return Settings()
