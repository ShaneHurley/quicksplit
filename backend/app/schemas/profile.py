"""Pydantic schemas for profiles."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProfileSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: str
    request_retention: float
    learning_steps_json: str
    new_cards_per_day: int
    reviews_per_day: int
    show_timer: bool


class ProfileSettingsUpdate(BaseModel):
    request_retention: Optional[float] = Field(default=None, ge=0.7, le=0.99)
    learning_steps_json: Optional[str] = None
    new_cards_per_day: Optional[int] = Field(default=None, ge=1, le=500)
    reviews_per_day: Optional[int] = Field(default=None, ge=1, le=2000)
    show_timer: Optional[bool] = None


class ProfileCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)
    accent_hue: str = "mint"
    avatar_emoji: Optional[str] = None
    theme: Literal["dark", "light"] = "dark"
    # Any string accepted — no length/complexity rules (empty = no password)
    password: Optional[str] = None


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    accent_hue: Optional[str] = None
    avatar_emoji: Optional[str] = None
    theme: Optional[Literal["dark", "light"]] = None
    password: Optional[str] = None  # set/replace password when provided


class ProfileUnlock(BaseModel):
    password: str = ""


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    display_name: str
    avatar_emoji: Optional[str]
    accent_hue: str
    theme: str
    has_password: bool = False
    created_at: datetime
    updated_at: datetime
    settings: Optional[ProfileSettingsRead] = None
