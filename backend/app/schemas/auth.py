"""Auth and API token schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenCreateRequest(BaseModel):
    """Request body for creating a new API token."""

    name: str | None = Field(default=None, max_length=255)
    expires_at: datetime | None = None


class TokenCreatedResponse(BaseModel):
    """Response returned once when a token is created.

    ``token`` is the plaintext secret and is never stored or returned again.
    """

    id: uuid.UUID
    name: str | None
    token: str
    created_at: datetime
    expires_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class TokenMetadataResponse(BaseModel):
    """Token metadata without plaintext or hash."""

    id: uuid.UUID
    name: str | None
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CurrentUserResponse(BaseModel):
    """Authenticated user profile."""

    id: uuid.UUID
    email: EmailStr
    display_name: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
