"""Monitoring sessions owned by users."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.behavior_event import BehaviorEvent
    from app.models.feature_window import FeatureWindow
    from app.models.label import Label
    from app.models.peak import Peak
    from app.models.score import Score
    from app.models.user import User


class MonitoringSession(Base):
    """Editor/monitoring session that groups events and derived artifacts."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    meta_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="sessions")
    behavior_events: Mapped[list[BehaviorEvent]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    feature_windows: Mapped[list[FeatureWindow]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    scores: Mapped[list[Score]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    peaks: Mapped[list[Peak]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    labels: Mapped[list[Label]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
