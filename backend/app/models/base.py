"""Shared SQLAlchemy mixins and helpers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


def utcnow() -> datetime:
    """Timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    """String UUID primary keys keep SQLite portable."""
    return str(uuid.uuid4())


class TimestampMixin:
    """created_at / updated_at columns for every durable entity."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class UUIDPrimaryKeyMixin:
    """String UUID primary key."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
