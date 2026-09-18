"""API token persistence and authentication."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.security import generate_api_token, hash_api_token
from app.models.api_token import ApiToken
from app.models.user import User
from app.services.scoping import user_scoped_select


class AuthenticationError(Exception):
    """Raised when a Bearer token cannot be authenticated."""


async def create_user_token(
    db: AsyncSession,
    *,
    user: User,
    name: str | None = None,
    plaintext: str | None = None,
    expires_at: datetime | None = None,
) -> tuple[ApiToken, str]:
    """Create an API token for ``user``.

    Returns ``(api_token_row, plaintext)``. Only the SHA-256 hash is stored;
    the plaintext is returned once for display to the caller.
    """
    token_plaintext = plaintext or generate_api_token()
    token = ApiToken(
        user_id=user.id,
        token_hash=hash_api_token(token_plaintext),
        name=name,
        expires_at=expires_at,
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token, token_plaintext


async def list_user_tokens(db: AsyncSession, user: User) -> list[ApiToken]:
    """List API tokens owned by ``user`` (no plaintext values)."""
    result = await db.execute(
        user_scoped_select(ApiToken, user.id).order_by(ApiToken.created_at.desc())
    )
    return list(result.scalars().all())


async def revoke_user_token(
    db: AsyncSession,
    *,
    user: User,
    token_id: uuid.UUID,
) -> ApiToken | None:
    """Revoke a token owned by ``user``. Returns None if not found in scope."""
    result = await db.execute(
        user_scoped_select(ApiToken, user.id).where(ApiToken.id == token_id)
    )
    token = result.scalar_one_or_none()
    if token is None:
        return None
    if token.revoked_at is None:
        token.revoked_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(token)
    return token


async def authenticate_bearer_token(
    db: AsyncSession,
    plaintext: str,
) -> tuple[User, ApiToken]:
    """Validate a plaintext Bearer token and return the owning active user.

    Rejects unknown, revoked, expired, or inactive-user tokens.
    """
    token_hash = hash_api_token(plaintext)
    result = await db.execute(
        select(ApiToken)
        .options(selectinload(ApiToken.user))
        .where(ApiToken.token_hash == token_hash)
    )
    token = result.scalar_one_or_none()
    if token is None:
        raise AuthenticationError("Invalid API token")
    if token.revoked_at is not None:
        raise AuthenticationError("API token has been revoked")
    if token.expires_at is not None and token.expires_at <= datetime.now(UTC):
        raise AuthenticationError("API token has expired")

    user = token.user
    if user is None or not user.is_active:
        raise AuthenticationError("User account is inactive")

    token.last_used_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(user)
    return user, token


async def get_or_create_user_by_email(
    db: AsyncSession,
    *,
    email: str,
    display_name: str | None = None,
) -> User:
    """Fetch a user by email or create one (used by bootstrap)."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is not None:
        return user
    user = User(email=email, display_name=display_name, is_active=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def find_token_by_hash(db: AsyncSession, token_hash: str) -> ApiToken | None:
    """Look up a token row by its SHA-256 hash."""
    result = await db.execute(select(ApiToken).where(ApiToken.token_hash == token_hash))
    return result.scalar_one_or_none()
