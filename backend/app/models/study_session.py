"""Study session aggregate for a continuous study run."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin, utcnow

if TYPE_CHECKING:
    from app.models.flashcard_set import FlashcardSet
    from app.models.profile import Profile
    from app.models.review_log import ReviewLog


class StudySession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """One continuous study run for a profile on a set."""

    __tablename__ = "study_sessions"

    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    set_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("flashcard_sets.id", ondelete="CASCADE"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cards_reviewed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    again_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hard_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    good_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    easy_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mean_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    interrupted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # JSON list of card ids failed in this session (for co-occurrence flush)
    failed_card_ids_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    profile: Mapped["Profile"] = relationship(back_populates="sessions")
    flashcard_set: Mapped["FlashcardSet"] = relationship()
    reviews: Mapped[list["ReviewLog"]] = relationship(back_populates="session")
