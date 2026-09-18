"""Peak strikes with optional code-at-peak context."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.label import Label
    from app.models.score import Score
    from app.models.session import MonitoringSession
    from app.models.user import User


class Peak(Base):
    """Detected peak in behavioral change with contextual snippet."""

    __tablename__ = "peaks"

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
    peaked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    peak_score: Mapped[float] = mapped_column(Float, nullable=False)
    code_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    context_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    session: Mapped[MonitoringSession] = relationship(back_populates="peaks")
    user: Mapped[User] = relationship(back_populates="peaks")
    score: Mapped[Score | None] = relationship(back_populates="peaks")
    labels: Mapped[list[Label]] = relationship(back_populates="peak")
