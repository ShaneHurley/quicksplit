"""Flashcard set (deck) container."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.flashcard import Flashcard
    from app.models.profile import Profile


class FlashcardSet(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A collection of flashcards — the OO 'class' for a study unit."""

    __tablename__ = "flashcard_sets"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    accent: Mapped[str] = mapped_column(String(32), default="mint", nullable=False)
    owner_profile_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True
    )
    card_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    owner: Mapped[Optional["Profile"]] = relationship(back_populates="owned_sets")
    cards: Mapped[list["Flashcard"]] = relationship(
        back_populates="flashcard_set",
        cascade="all, delete-orphan",
        order_by="Flashcard.position",
    )
