"""User accounts that own sessions, tokens, and labeled data."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.api_token import ApiToken
    from app.models.behavior_event import BehaviorEvent
    from app.models.feature_window import FeatureWindow
    from app.models.label import Label
    from app.models.peak import Peak
    from app.models.score import Score
    from app.models.session import MonitoringSession


class User(Base):
    """Application user that owns monitoring data."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    api_tokens: Mapped[list[ApiToken]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list[MonitoringSession]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    behavior_events: Mapped[list[BehaviorEvent]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    feature_windows: Mapped[list[FeatureWindow]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    scores: Mapped[list[Score]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    peaks: Mapped[list[Peak]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    labels: Mapped[list[Label]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
