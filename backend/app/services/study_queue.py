"""Build the due study queue for a profile + set."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.flashcard import Flashcard
from app.models.flashcard_set import FlashcardSet
from app.models.performance import UserPerformance
from app.models.base import utcnow
from app.services.fsrs_engine import default_new_state


class StudyQueueService:
    """Orders cards by due urgency for an active study session."""

    def ensure_performances(
        self, db: Session, profile_id: str, set_id: str, now: Optional[datetime] = None
    ) -> None:
        """Create UserPerformance rows for any card the profile has never seen."""
        now = now or utcnow()
        cards = db.query(Flashcard).filter(Flashcard.set_id == set_id).all()
        existing = {
            p.card_id
            for p in db.query(UserPerformance)
            .filter(
                UserPerformance.profile_id == profile_id,
                UserPerformance.card_id.in_([c.id for c in cards] or ["__none__"]),
            )
            .all()
        }
        for card in cards:
            if card.id in existing:
                continue
            fresh = default_new_state(now)
            db.add(
                UserPerformance(
                    profile_id=profile_id,
                    card_id=card.id,
                    state=fresh.state,
                    difficulty=fresh.difficulty,
                    stability=fresh.stability,
                    retrievability=fresh.retrievability,
                    learning_step_index=fresh.learning_step_index,
                    reps=fresh.reps,
                    lapses=fresh.lapses,
                    fail_streak=fresh.fail_streak,
                    due_at=fresh.due_at,
                    last_review_at=fresh.last_review_at,
                    last_grade=fresh.last_grade,
                )
            )
        db.flush()

    def due_queue(
        self,
        db: Session,
        profile_id: str,
        set_id: str,
        now: Optional[datetime] = None,
        new_limit: int = 20,
        review_limit: int = 200,
    ) -> List[Tuple[Flashcard, UserPerformance]]:
        """Return (card, performance) pairs due now, sorted by urgency."""
        now = now or utcnow()
        self.ensure_performances(db, profile_id, set_id, now)

        rows = (
            db.query(Flashcard, UserPerformance)
            .join(UserPerformance, UserPerformance.card_id == Flashcard.id)
            .filter(
                Flashcard.set_id == set_id,
                UserPerformance.profile_id == profile_id,
                UserPerformance.due_at <= now,
            )
            .order_by(
                UserPerformance.due_at.asc(),
                UserPerformance.fail_streak.desc(),
                Flashcard.created_at.asc(),
            )
            .all()
        )

        newish: List[Tuple[Flashcard, UserPerformance]] = []
        reviews: List[Tuple[Flashcard, UserPerformance]] = []
        for card, perf in rows:
            if perf.state in ("new",) or (perf.reps == 0):
                newish.append((card, perf))
            else:
                reviews.append((card, perf))

        return reviews[:review_limit] + newish[:new_limit]

    def count_due(
        self, db: Session, profile_id: str, set_id: str, now: Optional[datetime] = None
    ) -> int:
        now = now or utcnow()
        self.ensure_performances(db, profile_id, set_id, now)
        return (
            db.query(UserPerformance)
            .join(Flashcard, Flashcard.id == UserPerformance.card_id)
            .filter(
                Flashcard.set_id == set_id,
                UserPerformance.profile_id == profile_id,
                UserPerformance.due_at <= now,
            )
            .count()
        )

    @staticmethod
    def set_size(db: Session, set_id: str) -> int:
        s = db.get(FlashcardSet, set_id)
        if s is None:
            return 0
        return s.card_count or db.query(Flashcard).filter(Flashcard.set_id == set_id).count()
