"""Session request and response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SessionCreateRequest(BaseModel):
    """Optional metadata when starting a monitoring session."""

    title: str | None = Field(default=None, max_length=255)
    meta_json: dict[str, Any] | None = None


class SessionResponse(BaseModel):
    """Monitoring session owned by the authenticated user."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    started_at: datetime
    ended_at: datetime | None
    meta_json: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
