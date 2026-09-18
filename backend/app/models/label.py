"""Human feedback labels for sessions, scores, or peaks."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.peak import Peak
    from app.models.score import Score
    from app.models.session import MonitoringSession
    from app.models.user import User


class Label(Base):
    """User-provided label or feedback attached to monitoring artifacts."""

    __tablename__ = "labels"

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
    score_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scores.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    peak_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("peaks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    label_value: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    session: Mapped[MonitoringSession] = relationship(back_populates="labels")
    user: Mapped[User] = relationship(back_populates="labels")
    score: Mapped[Score | None] = relationship(back_populates="labels")
    peak: Mapped[Peak | None] = relationship(back_populates="labels")
