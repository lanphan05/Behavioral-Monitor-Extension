"""API token management endpoints (Bearer auth required)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.deps import AuthContext, get_auth_context
from app.schemas.auth import (
    CurrentUserResponse,
    TokenCreateRequest,
    TokenCreatedResponse,
    TokenMetadataResponse,
)
from app.services import tokens as token_service

router = APIRouter(tags=["auth"])


@router.get("/me", response_model=CurrentUserResponse)
async def read_current_user(
    auth: AuthContext = Depends(get_auth_context),
) -> CurrentUserResponse:
    """Return the authenticated user."""
    return CurrentUserResponse.model_validate(auth.user)


@router.post(
    "/tokens",
    response_model=TokenCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_token(
    body: TokenCreateRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> TokenCreatedResponse:
    """Create a new API token for the authenticated user.

    The plaintext token is returned only in this response.
    """
    row, plaintext = await token_service.create_user_token(
        auth.db,
        user=auth.user,
        name=body.name,
        expires_at=body.expires_at,
    )
    return TokenCreatedResponse(
        id=row.id,
        name=row.name,
        token=plaintext,
        created_at=row.created_at,
        expires_at=row.expires_at,
    )


@router.get("/tokens", response_model=list[TokenMetadataResponse])
async def list_tokens(
    auth: AuthContext = Depends(get_auth_context),
) -> list[TokenMetadataResponse]:
    """List metadata for tokens owned by the authenticated user."""
    rows = await token_service.list_user_tokens(auth.db, auth.user)
    return [TokenMetadataResponse.model_validate(row) for row in rows]


@router.delete("/tokens/{token_id}", response_model=TokenMetadataResponse)
async def revoke_token(
    token_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
) -> TokenMetadataResponse:
    """Revoke a token owned by the authenticated user."""
    row = await token_service.revoke_user_token(
        auth.db,
        user=auth.user,
        token_id=token_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )
    return TokenMetadataResponse.model_validate(row)
