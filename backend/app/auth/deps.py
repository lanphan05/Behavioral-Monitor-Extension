"""FastAPI authentication dependencies."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.api_token import ApiToken
from app.models.user import User
from app.services.tokens import AuthenticationError, authenticate_bearer_token

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(slots=True)
class AuthContext:
    """Authenticated request context with user-scoped DB session."""

    user: User
    token: ApiToken
    db: AsyncSession


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve and return the user for a valid Bearer API token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Not authenticated")
    try:
        user, _token = await authenticate_bearer_token(db, credentials.credentials)
    except AuthenticationError as exc:
        raise _unauthorized(str(exc)) from exc
    return user


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    """Return authenticated user, token row, and DB session for scoped queries."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Not authenticated")
    try:
        user, token = await authenticate_bearer_token(db, credentials.credentials)
    except AuthenticationError as exc:
        raise _unauthorized(str(exc)) from exc
    return AuthContext(user=user, token=token, db=db)
