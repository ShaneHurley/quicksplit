"""Pydantic schemas for study sessions and reviews."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.flashcard import CardRead


class SessionCreate(BaseModel):
    profile_id: str
    set_id: str


class PerformanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    profile_id: str
    card_id: str
    state: str
    difficulty: float
    stability: float
    retrievability: float
    learning_step_index: int
    reps: int
    lapses: int
    fail_streak: int
    due_at: datetime
    last_review_at: Optional[datetime]
    last_grade: Optional[int]


class SessionStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cards_reviewed: int
    again_count: int
    hard_count: int
    good_count: int
    easy_count: int
    mean_duration_ms: float
    interrupted: bool
    ended_at: Optional[datetime] = None


class SessionStartResponse(BaseModel):
    session: SessionStats
    queue: List[CardRead]
    queue_length: int


class ReviewCreate(BaseModel):
    session_id: str
    profile_id: str
    card_id: str
    grade: int = Field(ge=1, le=4)
    duration_ms: int = 0
    time_to_flip_ms: Optional[int] = None
    input_given: Optional[str] = None
    selected_index: Optional[int] = None
    client_timezone: Optional[str] = None
    queue_position: Optional[int] = None
    device_class: Optional[str] = None


class ReviewResponse(BaseModel):
    performance: PerformanceRead
    next_card: Optional[CardRead]
    session_stats: SessionStats
    celebrated: bool


class CoOccurrenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    card_a_id: str
    card_b_id: str
    count: int
