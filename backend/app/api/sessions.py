"""Monitoring session endpoints (Bearer auth required)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.deps import AuthContext, get_auth_context
from app.schemas.sessions import SessionCreateRequest, SessionResponse
from app.services import sessions as session_service

router = APIRouter(tags=["sessions"])


@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_session(
    body: SessionCreateRequest = SessionCreateRequest(),
    auth: AuthContext = Depends(get_auth_context),
) -> SessionResponse:
    """Start a new monitoring session for the authenticated user."""
    row = await session_service.create_session(
        auth.db,
        user=auth.user,
        title=body.title,
        meta_json=body.meta_json,
    )
    return SessionResponse.model_validate(row)


@router.post(
    "/sessions/{session_id}/stop",
    response_model=SessionResponse,
)
async def stop_session(
    session_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
) -> SessionResponse:
    """Stop a monitoring session owned by the authenticated user."""
    try:
        row = await session_service.stop_session(
            auth.db,
            user=auth.user,
            session_id=session_id,
        )
    except session_service.SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except session_service.SessionAlreadyStoppedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return SessionResponse.model_validate(row)
