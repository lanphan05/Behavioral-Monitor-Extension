"""Health check response schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness payload returned by GET /health."""

    status: str = Field(examples=["ok"])
