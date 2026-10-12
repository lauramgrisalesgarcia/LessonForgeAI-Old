import asyncio
import os
from collections.abc import AsyncIterator
from pathlib import Path

import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.db import get_db
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _test_database_url() -> str:
    """TEST_DATABASE_URL o, por defecto, DATABASE_URL con el sufijo _test."""
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        return explicit
    url = make_url(get_settings().DATABASE_URL)
    return url.set(database=f"{url.database}_test").render_as_string(hide_password=False)


async def _ensure_database_exists(url: str) -> None:
    parsed = make_url(url)
    conn = await asyncpg.connect(
        user=parsed.username,
        password=parsed.password,
        host=parsed.host,
        port=parsed.port or 5432,
        database="postgres",
    )
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", parsed.database
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{parsed.database}"')
    finally:
        await conn.close()


@pytest.fixture(scope="session")
def database_url() -> str:
    """Crea (si hace falta) la base de datos de pruebas y aplica las migraciones de Alembic."""
    url = _test_database_url()
    asyncio.run(_ensure_database_exists(url))
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(alembic_cfg, "head")
    return url


@pytest.fixture
async def db_session(database_url: str) -> AsyncIterator[AsyncSession]:
    """Sesión dentro de una transacción que se revierte al terminar cada prueba."""
    engine = create_async_engine(database_url, poolclass=NullPool)
    async with engine.connect() as conn:
        transaction = await conn.begin()
        session = AsyncSession(
            bind=conn, join_transaction_mode="create_savepoint", expire_on_commit=False
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Cliente HTTP cuya dependencia get_db usa la sesión transaccional de la prueba."""

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """Cliente HTTP sin base de datos (endpoints que no la usan)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client
