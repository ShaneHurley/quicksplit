"""Local learner profiles (no cloud auth — Option 1B)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.flashcard_set import FlashcardSet
    from app.models.performance import UserPerformance
    from app.models.study_session import StudySession


class Profile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A named local learner who can study any flashcard set."""

    __tablename__ = "profiles"

    display_name: Mapped[str] = mapped_column(String(80), nullable=False)
    avatar_emoji: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    accent_hue: Mapped[str] = mapped_column(String(32), default="mint", nullable=False)
    # Site-wide UI mode for this learner — "dark" | "light" (palette is accent_hue)
    theme: Mapped[str] = mapped_column(String(16), default="light", nullable=False)
    # PBKDF2 salt$hash; None means unlocked profile (legacy / optional)
    password_hash: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    settings: Mapped["ProfileSettings"] = relationship(
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    owned_sets: Mapped[list["FlashcardSet"]] = relationship(back_populates="owner")
    performances: Mapped[list["UserPerformance"]] = relationship(back_populates="profile")
    sessions: Mapped[list["StudySession"]] = relationship(back_populates="profile")


class ProfileSettings(Base):
    """Per-profile scheduler preferences."""

    __tablename__ = "profile_settings"

    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True
    )
    request_retention: Mapped[float] = mapped_column(Float, default=0.9, nullable=False)
    # Minutes: first step, scaled mid step placeholder, then 1 day.
    learning_steps_json: Mapped[str] = mapped_column(
        Text, default="[1,10,1440]", nullable=False
    )
    new_cards_per_day: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    reviews_per_day: Mapped[int] = mapped_column(Integer, default=200, nullable=False)
    show_timer: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    profile: Mapped[Profile] = relationship(back_populates="settings")
