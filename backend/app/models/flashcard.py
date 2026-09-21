"""Polymorphic flashcard content units."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.flashcard_set import FlashcardSet
    from app.models.performance import UserPerformance


class Flashcard(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Base educational unit.

    Subclasses (single-table inheritance) hold type-specific fields while
    sharing performance links for every learner.
    """

    __tablename__ = "flashcards"

    set_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("flashcard_sets.id", ondelete="CASCADE"), nullable=False
    )
    card_type: Mapped[str] = mapped_column(String(16), nullable=False)  # text | mc
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Optional extras (import + editor)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # TextCard fields
    answer_mode: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # flip|exact
    acceptable_answers_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # MultipleChoiceCard fields
    choices_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correct_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __mapper_args__ = {
        "polymorphic_on": "card_type",
        "polymorphic_identity": "base",
    }

    flashcard_set: Mapped["FlashcardSet"] = relationship(back_populates="cards")
    performances: Mapped[list["UserPerformance"]] = relationship(
        back_populates="card", cascade="all, delete-orphan"
    )


class TextCard(Flashcard):
    """Front/back card; optional exact string matching for option tracing."""

    __mapper_args__ = {"polymorphic_identity": "text"}


class MultipleChoiceCard(Flashcard):
    """Multiple-choice card for distractor / CWA logging."""

    __mapper_args__ = {"polymorphic_identity": "mc"}
