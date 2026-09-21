"""Orchestrate a graded review: FSRS update + telemetry + co-occurrence + next card."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.models.flashcard import Flashcard
from app.models.performance import UserPerformance
from app.models.profile import Profile
from app.models.review_log import ReviewLog
from app.models.study_session import StudySession
from app.services.fsrs_engine import FSRSEngine, MemoryState
from app.services.misconception_tracker import MisconceptionTracker
from app.services.study_queue import StudyQueueService


class ReviewPipeline:
    """Transactional study review pipeline used by the REST layer."""

    def __init__(self) -> None:
        self.engine = FSRSEngine()
        self.queue = StudyQueueService()
        self.tracker = MisconceptionTracker()

    def start_session(
        self, db: Session, profile_id: str, set_id: str
    ) -> tuple[StudySession, List[Flashcard]]:
        profile = db.get(Profile, profile_id)
        if profile is None:
            raise ValueError("profile not found")

        settings = profile.settings
        new_limit = settings.new_cards_per_day if settings else 20
        review_limit = settings.reviews_per_day if settings else 200

        session = StudySession(profile_id=profile_id, set_id=set_id)
        db.add(session)
        db.flush()

        queue = self.queue.due_queue(
            db, profile_id, set_id, new_limit=new_limit, review_limit=review_limit
        )
        cards = [c for c, _ in queue]
        return session, cards

    def submit_review(
        self,
        db: Session,
        *,
        session_id: str,
        profile_id: str,
        card_id: str,
        grade: int,
        duration_ms: int = 0,
        time_to_flip_ms: Optional[int] = None,
        input_given: Optional[str] = None,
        selected_index: Optional[int] = None,
        client_timezone: Optional[str] = None,
        queue_position: Optional[int] = None,
        device_class: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        now = now or utcnow()
        session = db.get(StudySession, session_id)
        if session is None or session.profile_id != profile_id:
            raise ValueError("session not found")

        card = db.get(Flashcard, card_id)
        if card is None or card.set_id != session.set_id:
            raise ValueError("card not found in session set")

        perf = (
            db.query(UserPerformance)
            .filter_by(profile_id=profile_id, card_id=card_id)
            .one_or_none()
        )
        if perf is None:
            self.queue.ensure_performances(db, profile_id, session.set_id, now)
            perf = (
                db.query(UserPerformance)
                .filter_by(profile_id=profile_id, card_id=card_id)
                .one()
            )

        profile = db.get(Profile, profile_id)
        settings = profile.settings if profile else None
        retention = settings.request_retention if settings else 0.9
        steps_json = settings.learning_steps_json if settings else "[1,10,1440]"
        set_size = self.queue.set_size(db, session.set_id)
        due_count = self.queue.count_due(db, profile_id, session.set_id, now)

        mem = MemoryState(
            state=perf.state,
            difficulty=perf.difficulty,
            stability=perf.stability,
            retrievability=perf.retrievability,
            learning_step_index=perf.learning_step_index,
            reps=perf.reps,
            lapses=perf.lapses,
            fail_streak=perf.fail_streak,
            due_at=perf.due_at,
            last_review_at=perf.last_review_at,
            last_grade=perf.last_grade,
        )
        result = self.engine.review(
            mem,
            grade,
            now,
            set_size=set_size,
            request_retention=retention,
            learning_steps_json=steps_json,
        )
        ns = result.state

        # Option tracing / correctness
        was_correct = grade >= 3
        if card.card_type == "mc" and selected_index is not None and card.correct_index is not None:
            was_correct = selected_index == card.correct_index and grade >= 3

        interval_before = None
        if perf.last_review_at is not None:
            interval_before = (now - perf.last_review_at).total_seconds() / 86400.0

        log = ReviewLog(
            profile_id=profile_id,
            card_id=card_id,
            set_id=session.set_id,
            session_id=session.id,
            timestamp=now,
            local_hour=now.hour,
            day_of_week=now.weekday(),
            duration_ms=duration_ms,
            time_to_flip_ms=time_to_flip_ms,
            grade=grade,
            was_correct=was_correct,
            input_given=input_given,
            selected_index=selected_index,
            card_type=card.card_type,
            scheduler_state=mem.state,
            learning_step_index=mem.learning_step_index,
            pre_review_d=result.pre_d,
            pre_review_s=result.pre_s,
            pre_review_r=result.pre_r,
            post_review_d=ns.difficulty,
            post_review_s=ns.stability,
            post_review_r=ns.retrievability,
            delta_s=ns.stability - result.pre_s,
            interval_before_days=interval_before,
            scheduled_interval_days=result.scheduled_interval_days,
            due_at_before=perf.due_at,
            due_at_after=ns.due_at,
            review_number=ns.reps,
            lapse_count_before=mem.lapses,
            fail_streak_before=mem.fail_streak,
            queue_position=queue_position,
            cards_due_count=due_count,
            set_size=set_size,
            device_class=device_class,
            client_timezone=client_timezone,
        )
        db.add(log)

        # Apply performance mutation
        perf.state = ns.state
        perf.difficulty = ns.difficulty
        perf.stability = ns.stability
        perf.retrievability = ns.retrievability
        perf.learning_step_index = ns.learning_step_index
        perf.reps = ns.reps
        perf.lapses = ns.lapses
        perf.fail_streak = ns.fail_streak
        perf.due_at = ns.due_at
        perf.last_review_at = ns.last_review_at
        perf.last_grade = ns.last_grade

        # Session aggregates
        session.cards_reviewed += 1
        if grade == 1:
            session.again_count += 1
            session.failed_card_ids_json = MisconceptionTracker.append_fail(
                session.failed_card_ids_json, card_id
            )
        elif grade == 2:
            session.hard_count += 1
        elif grade == 3:
            session.good_count += 1
        else:
            session.easy_count += 1

        n = session.cards_reviewed
        session.mean_duration_ms = (
            (session.mean_duration_ms * (n - 1) + duration_ms) / n if n else duration_ms
        )

        db.flush()

        # Next card: rebuild due queue, skip immediate same-card when possible
        new_limit = settings.new_cards_per_day if settings else 20
        review_limit = settings.reviews_per_day if settings else 200
        queue = self.queue.due_queue(
            db, profile_id, session.set_id, now=now, new_limit=new_limit, review_limit=review_limit
        )
        next_card: Optional[Flashcard] = None
        if queue:
            # Prefer not showing the same card immediately after Again
            for c, _p in queue:
                if c.id != card_id:
                    next_card = c
                    break
            if next_card is None:
                next_card = queue[0][0]

        celebrated = next_card is None
        return {
            "performance": perf,
            "next_card": next_card,
            "session": session,
            "celebrated": celebrated,
            "log_id": log.id,
        }

    def end_session(self, db: Session, session_id: str, interrupted: bool = False) -> StudySession:
        session = db.get(StudySession, session_id)
        if session is None:
            raise ValueError("session not found")
        session.ended_at = utcnow()
        session.interrupted = interrupted
        failed = MisconceptionTracker.parse_failed_ids(session.failed_card_ids_json)
        self.tracker.record_session_failures(
            db, session.profile_id, session.set_id, failed
        )
        db.flush()
        return session
