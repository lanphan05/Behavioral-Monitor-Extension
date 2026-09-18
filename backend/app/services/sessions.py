"""Monitoring session create/stop operations (user-scoped)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import MonitoringSession
from app.models.user import User
from app.services.scoping import user_scoped_select


class SessionNotFoundError(Exception):
    """Raised when a session is missing within the caller's scope."""


class SessionAlreadyStoppedError(Exception):
    """Raised when attempting to stop a session that already has ended_at."""


async def create_session(
    db: AsyncSession,
    *,
    user: User,
    title: str | None = None,
    meta_json: dict | None = None,
) -> MonitoringSession:
    """Create a new monitoring session owned by ``user``."""
    now = datetime.now(UTC)
    session = MonitoringSession(
        user_id=user.id,
        title=title,
        meta_json=meta_json,
        started_at=now,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_user_session(
    db: AsyncSession,
    *,
    user: User,
    session_id: uuid.UUID,
) -> MonitoringSession | None:
    """Return a session owned by ``user``, or None if not in scope."""
    result = await db.execute(
        user_scoped_select(MonitoringSession, user.id).where(
            MonitoringSession.id == session_id
        )
    )
    return result.scalar_one_or_none()


async def stop_session(
    db: AsyncSession,
    *,
    user: User,
    session_id: uuid.UUID,
) -> MonitoringSession:
    """Stop a session owned by ``user`` by setting ``ended_at``.

    Raises:
        SessionNotFoundError: session does not exist for this user (or at all
            from the caller's perspective).
        SessionAlreadyStoppedError: ``ended_at`` is already set.
    """
    session = await get_user_session(db, user=user, session_id=session_id)
    if session is None:
        raise SessionNotFoundError("Session not found")
    if session.ended_at is not None:
        raise SessionAlreadyStoppedError("Session is already stopped")

    session.ended_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(session)
    return session
