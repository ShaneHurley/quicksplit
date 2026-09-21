"""Misconception co-occurrence edges for future knowledge tracing."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CoOccurrenceEdge(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Undirected fail-pair count within a profile + set.

    Always store card_a_id < card_b_id lexicographically to avoid duplicates.
    """

    __tablename__ = "cooccurrence_edges"
    __table_args__ = (
        UniqueConstraint(
            "profile_id",
            "set_id",
            "card_a_id",
            "card_b_id",
            name="uq_cooccurrence_pair",
        ),
    )

    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    set_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("flashcard_sets.id", ondelete="CASCADE"), nullable=False
    )
    card_a_id: Mapped[str] = mapped_column(String(36), nullable=False)
    card_b_id: Mapped[str] = mapped_column(String(36), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
