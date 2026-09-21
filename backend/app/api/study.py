"""Study session and review routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.study_session import StudySession
from app.schemas.flashcard import CardRead
from app.schemas.study import (
    ReviewCreate,
    ReviewResponse,
    SessionCreate,
    SessionStartResponse,
    SessionStats,
    PerformanceRead,
)
from app.services.review_pipeline import ReviewPipeline
from app.services.study_queue import StudyQueueService

router = APIRouter(prefix="/study", tags=["study"])
pipeline = ReviewPipeline()
queue_svc = StudyQueueService()


@router.post("/sessions", response_model=SessionStartResponse, status_code=201)
def start_session(body: SessionCreate, db: Session = Depends(get_db)) -> SessionStartResponse:
    try:
        session, cards = pipeline.start_session(db, body.profile_id, body.set_id)
        db.commit()
        db.refresh(session)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return SessionStartResponse(
        session=SessionStats.model_validate(session),
        queue=[CardRead.model_validate(c) for c in cards],
        queue_length=len(cards),
    )


@router.get("/sessions/{session_id}/queue", response_model=list[CardRead])
def get_queue(session_id: str, db: Session = Depends(get_db)) -> list[CardRead]:
    session = db.get(StudySession, session_id)
    if session is None:
        raise HTTPException(404, "Session not found")
    profile = session.profile
    settings = profile.settings if profile else None
    queue = queue_svc.due_queue(
        db,
        session.profile_id,
        session.set_id,
        new_limit=settings.new_cards_per_day if settings else 20,
        review_limit=settings.reviews_per_day if settings else 200,
    )
    return [CardRead.model_validate(c) for c, _ in queue]


@router.post("/reviews", response_model=ReviewResponse)
def submit_review(body: ReviewCreate, db: Session = Depends(get_db)) -> ReviewResponse:
    try:
        result = pipeline.submit_review(
            db,
            session_id=body.session_id,
            profile_id=body.profile_id,
            card_id=body.card_id,
            grade=body.grade,
            duration_ms=body.duration_ms,
            time_to_flip_ms=body.time_to_flip_ms,
            input_given=body.input_given,
            selected_index=body.selected_index,
            client_timezone=body.client_timezone,
            queue_position=body.queue_position,
            device_class=body.device_class,
        )
        db.commit()
        db.refresh(result["performance"])
        db.refresh(result["session"])
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    next_card = result["next_card"]
    return ReviewResponse(
        performance=PerformanceRead.model_validate(result["performance"]),
        next_card=CardRead.model_validate(next_card) if next_card else None,
        session_stats=SessionStats.model_validate(result["session"]),
        celebrated=result["celebrated"],
    )


@router.post("/sessions/{session_id}/end", response_model=SessionStats)
def end_session(
    session_id: str, interrupted: bool = False, db: Session = Depends(get_db)
) -> SessionStats:
    try:
        session = pipeline.end_session(db, session_id, interrupted=interrupted)
        db.commit()
        db.refresh(session)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return SessionStats.model_validate(session)
