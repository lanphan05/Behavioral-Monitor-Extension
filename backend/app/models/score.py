"""Behavioral change scores produced by registered models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.feature_window import FeatureWindow
    from app.models.label import Label
    from app.models.model_registry import ModelRegistry
    from app.models.peak import Peak
    from app.models.session import MonitoringSession
    from app.models.user import User


class Score(Base):
    """Behavioral change score (0–100 proxy) for a session window."""

    __tablename__ = "scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    feature_window_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feature_windows.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    model_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("model_registry.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    score_value: Mapped[float] = mapped_column(Float, nullable=False)
    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    details_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    session: Mapped[MonitoringSession] = relationship(back_populates="scores")
    user: Mapped[User] = relationship(back_populates="scores")
    feature_window: Mapped[FeatureWindow | None] = relationship(back_populates="scores")
    model: Mapped[ModelRegistry | None] = relationship(back_populates="scores")
    peaks: Mapped[list[Peak]] = relationship(back_populates="score")
    labels: Mapped[list[Label]] = relationship(back_populates="score")
