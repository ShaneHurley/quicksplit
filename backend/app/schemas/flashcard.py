"""Pydantic schemas for sets and cards."""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class CardCreate(BaseModel):
    card_type: Literal["text", "mc"] = "text"
    front: str = Field(min_length=1)
    back: str = Field(min_length=1)
    hint: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None
    position: Optional[int] = None
    answer_mode: Optional[Literal["flip", "exact"]] = "flip"
    acceptable_answers: Optional[List[str]] = None
    choices: Optional[List[str]] = None
    correct_index: Optional[int] = None


class CardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    hint: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None
    position: Optional[int] = None
    answer_mode: Optional[Literal["flip", "exact"]] = None
    acceptable_answers: Optional[List[str]] = None
    choices: Optional[List[str]] = None
    correct_index: Optional[int] = None


class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    set_id: str
    card_type: str
    front: str
    back: str
    hint: Optional[str]
    image_url: Optional[str] = None
    notes: Optional[str] = None
    position: int
    answer_mode: Optional[str] = None
    choices_json: Optional[str] = None
    correct_index: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class SetCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    accent: str = "mint"
    owner_profile_id: Optional[str] = None


class SetUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    accent: Optional[str] = None


class SetSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    accent: str
    owner_profile_id: Optional[str]
    card_count: int
    created_at: datetime
    updated_at: datetime
    due_count: int = 0


class SetDetail(SetSummary):
    cards: List[CardRead] = []


class ImportPreviewCard(BaseModel):
    front: str
    back: str
    image_url: Optional[str] = None
    notes: Optional[str] = None


class ImportRequest(BaseModel):
    raw_text: str = ""
    field_sep: Literal["tab", "comma", "custom"] = "tab"
    field_sep_custom: Optional[str] = None
    card_sep: Literal["newline", "semicolon", "custom"] = "newline"
    card_sep_custom: Optional[str] = None
    preview_only: bool = False


class ImportResult(BaseModel):
    imported_count: int
    cards: List[ImportPreviewCard]
    set: Optional[SetDetail] = None
