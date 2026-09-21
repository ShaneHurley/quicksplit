"""Analytics endpoints for co-occurrence and future KT."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.cooccurrence import CoOccurrenceEdge
from app.schemas.study import CoOccurrenceRead

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sets/{set_id}/cooccurrence", response_model=list[CoOccurrenceRead])
def cooccurrence(
    set_id: str,
    profile_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> list[CoOccurrenceEdge]:
    q = db.query(CoOccurrenceEdge).filter(CoOccurrenceEdge.set_id == set_id)
    if profile_id:
        q = q.filter(CoOccurrenceEdge.profile_id == profile_id)
    return q.order_by(CoOccurrenceEdge.count.desc()).limit(200).all()
