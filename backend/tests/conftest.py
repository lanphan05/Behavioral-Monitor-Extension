"""Shared pytest fixtures for API tests (SQLite in-memory)."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.security import hash_api_token
from app.database import Base, get_db
from app.main import app
from app.models.api_token import ApiToken
from app.models.session import MonitoringSession
from app.models.user import User
from app.services.tokens import create_user_token, get_or_create_user_by_email

# Only create tables required for session auth/isolation tests.
TEST_TABLES = [
    User.__table__,
    ApiToken.__table__,
    MonitoringSession.__table__,
]


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(sync_conn, tables=TEST_TABLES)
        )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_engine):
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def _override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def _create_user_with_token(
    session: AsyncSession,
    *,
    email: str,
    display_name: str,
) -> tuple[User, str]:
    user = await get_or_create_user_by_email(
        session,
        email=email,
        display_name=display_name,
    )
    _row, plaintext = await create_user_token(
        session,
        user=user,
        name=f"{display_name}-token",
    )
    return user, plaintext


@pytest_asyncio.fixture
async def user_a_token(db_engine) -> str:
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        _user, token = await _create_user_with_token(
            session,
            email="user-a@example.com",
            display_name="User A",
        )
        return token


@pytest_asyncio.fixture
async def user_b_token(db_engine) -> str:
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        _user, token = await _create_user_with_token(
            session,
            email="user-b@example.com",
            display_name="User B",
        )
        return token


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# Silence unused import warnings for helpers re-exported to tests.
__all__ = [
    "auth_header",
    "client",
    "db_engine",
    "db_session",
    "hash_api_token",
    "select",
    "user_a_token",
    "user_b_token",
]
