"""Co-occurrence matrix updates for misconception mapping."""

from __future__ import annotations

import json
from itertools import combinations
from typing import Iterable, List

from sqlalchemy.orm import Session

from app.models.cooccurrence import CoOccurrenceEdge


class MisconceptionTracker:
    """Increments undirected fail-pair edges for cards missed in the same session."""

    def record_session_failures(
        self,
        db: Session,
        profile_id: str,
        set_id: str,
        failed_card_ids: Iterable[str],
    ) -> int:
        """Upsert co-occurrence edges for every unordered pair. Returns pairs touched."""
        unique = sorted({cid for cid in failed_card_ids if cid})
        if len(unique) < 2:
            return 0

        touched = 0
        for a, b in combinations(unique, 2):
            card_a, card_b = (a, b) if a < b else (b, a)
            edge = (
                db.query(CoOccurrenceEdge)
                .filter_by(
                    profile_id=profile_id,
                    set_id=set_id,
                    card_a_id=card_a,
                    card_b_id=card_b,
                )
                .one_or_none()
            )
            if edge is None:
                edge = CoOccurrenceEdge(
                    profile_id=profile_id,
                    set_id=set_id,
                    card_a_id=card_a,
                    card_b_id=card_b,
                    count=1,
                )
                db.add(edge)
            else:
                edge.count += 1
            touched += 1
        return touched

    @staticmethod
    def parse_failed_ids(failed_card_ids_json: str) -> List[str]:
        try:
            data = json.loads(failed_card_ids_json or "[]")
            return [str(x) for x in data]
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    def append_fail(failed_card_ids_json: str, card_id: str) -> str:
        ids = MisconceptionTracker.parse_failed_ids(failed_card_ids_json)
        if card_id not in ids:
            ids.append(card_id)
        return json.dumps(ids)
