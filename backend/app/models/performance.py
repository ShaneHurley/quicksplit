"""Per learner + card FSRS / learning state."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin, utcnow

if TYPE_CHECKING:
    from app.models.flashcard import Flashcard
    from app.models.profile import Profile


class UserPerformance(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Isolates memory state so multiple profiles can share one set."""

    __tablename__ = "user_performances"
    __table_args__ = (
        UniqueConstraint("profile_id", "card_id", name="uq_profile_card_performance"),
    )

    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    card_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False
    )
    # new | learning | review | relearning
    state: Mapped[str] = mapped_column(String(16), default="new", nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    stability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    retrievability: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    learning_step_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lapses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fail_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_review_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    last_grade: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    profile: Mapped["Profile"] = relationship(back_populates="performances")
    card: Mapped["Flashcard"] = relationship(back_populates="performances")
