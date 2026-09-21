"""Immutable append-only review telemetry ledger."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import UUIDPrimaryKeyMixin, utcnow

if TYPE_CHECKING:
    from app.models.study_session import StudySession


class ReviewLog(Base, UUIDPrimaryKeyMixin):
    """One graded interaction — over-gather now for future KT / ML."""

    __tablename__ = "review_logs"

    profile_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    card_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    set_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("study_sessions.id", ondelete="SET NULL"), nullable=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )
    local_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_to_flip_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    was_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    input_given: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    selected_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    card_type: Mapped[str] = mapped_column(String(16), nullable=False)
    scheduler_state: Mapped[str] = mapped_column(String(16), nullable=False)
    learning_step_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pre_review_d: Mapped[float] = mapped_column(Float, nullable=False)
    pre_review_s: Mapped[float] = mapped_column(Float, nullable=False)
    pre_review_r: Mapped[float] = mapped_column(Float, nullable=False)
    post_review_d: Mapped[float] = mapped_column(Float, nullable=False)
    post_review_s: Mapped[float] = mapped_column(Float, nullable=False)
    post_review_r: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    delta_s: Mapped[float] = mapped_column(Float, nullable=False)
    interval_before_days: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    scheduled_interval_days: Mapped[float] = mapped_column(Float, nullable=False)
    due_at_before: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    due_at_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    review_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lapse_count_before: Mapped[int] = mapped_column(Integer, nullable=False)
    fail_streak_before: Mapped[int] = mapped_column(Integer, nullable=False)
    queue_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cards_due_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    set_size: Mapped[int] = mapped_column(Integer, nullable=False)
    device_class: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    app_version: Mapped[str] = mapped_column(String(32), default="0.1.0", nullable=False)
    client_timezone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    session: Mapped[Optional["StudySession"]] = relationship(back_populates="reviews")
