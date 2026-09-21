"""Flashcard set and card CRUD routes."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.flashcard import Flashcard, MultipleChoiceCard, TextCard
from app.models.flashcard_set import FlashcardSet
from app.schemas.flashcard import (
    CardCreate,
    CardRead,
    CardUpdate,
    ImportPreviewCard,
    ImportRequest,
    ImportResult,
    SetCreate,
    SetDetail,
    SetSummary,
    SetUpdate,
)
from app.services.importer import parse_import_text
from app.services.study_queue import StudyQueueService

router = APIRouter(tags=["sets"])
queue_svc = StudyQueueService()


def _card_entity(body: CardCreate, set_id: str, position: int) -> Flashcard:
    if body.card_type == "mc":
        return MultipleChoiceCard(
            set_id=set_id,
            front=body.front,
            back=body.back,
            hint=body.hint,
            image_url=body.image_url,
            notes=body.notes,
            position=position,
            choices_json=json.dumps(body.choices or []),
            correct_index=body.correct_index if body.correct_index is not None else 0,
        )
    return TextCard(
        set_id=set_id,
        front=body.front,
        back=body.back,
        hint=body.hint,
        image_url=body.image_url,
        notes=body.notes,
        position=position,
        answer_mode=body.answer_mode or "flip",
        acceptable_answers_json=json.dumps(body.acceptable_answers or []),
    )


@router.get("/sets", response_model=list[SetSummary])
def list_sets(
    profile_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> list[SetSummary]:
    sets = db.query(FlashcardSet).order_by(FlashcardSet.updated_at.desc()).all()
    out: list[SetSummary] = []
    for s in sets:
        due = 0
        if profile_id:
            due = queue_svc.count_due(db, profile_id, s.id)
        out.append(
            SetSummary(
                id=s.id,
                title=s.title,
                description=s.description,
                accent=s.accent,
                owner_profile_id=s.owner_profile_id,
                card_count=s.card_count,
                created_at=s.created_at,
                updated_at=s.updated_at,
                due_count=due,
            )
        )
    return out


@router.post("/sets", response_model=SetDetail, status_code=201)
def create_set(body: SetCreate, db: Session = Depends(get_db)) -> SetDetail:
    s = FlashcardSet(
        title=body.title.strip(),
        description=body.description,
        accent=body.accent,
        owner_profile_id=body.owner_profile_id,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return SetDetail(
        id=s.id,
        title=s.title,
        description=s.description,
        accent=s.accent,
        owner_profile_id=s.owner_profile_id,
        card_count=s.card_count,
        created_at=s.created_at,
        updated_at=s.updated_at,
        due_count=0,
        cards=[],
    )


@router.get("/sets/{set_id}", response_model=SetDetail)
def get_set(
    set_id: str,
    profile_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> SetDetail:
    s = db.get(FlashcardSet, set_id)
    if s is None:
        raise HTTPException(404, "Set not found")
    due = queue_svc.count_due(db, profile_id, s.id) if profile_id else 0
    return SetDetail(
        id=s.id,
        title=s.title,
        description=s.description,
        accent=s.accent,
        owner_profile_id=s.owner_profile_id,
        card_count=s.card_count,
        created_at=s.created_at,
        updated_at=s.updated_at,
        due_count=due,
        cards=[CardRead.model_validate(c) for c in s.cards],
    )


@router.patch("/sets/{set_id}", response_model=SetSummary)
def update_set(set_id: str, body: SetUpdate, db: Session = Depends(get_db)) -> SetSummary:
    s = db.get(FlashcardSet, set_id)
    if s is None:
        raise HTTPException(404, "Set not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return SetSummary(
        id=s.id,
        title=s.title,
        description=s.description,
        accent=s.accent,
        owner_profile_id=s.owner_profile_id,
        card_count=s.card_count,
        created_at=s.created_at,
        updated_at=s.updated_at,
        due_count=0,
    )


@router.delete("/sets/{set_id}", status_code=204)
def delete_set(set_id: str, db: Session = Depends(get_db)) -> None:
    s = db.get(FlashcardSet, set_id)
    if s is None:
        raise HTTPException(404, "Set not found")
    db.delete(s)
    db.commit()


@router.post("/sets/{set_id}/cards", response_model=CardRead, status_code=201)
def add_card(set_id: str, body: CardCreate, db: Session = Depends(get_db)) -> Flashcard:
    s = db.get(FlashcardSet, set_id)
    if s is None:
        raise HTTPException(404, "Set not found")
    position = body.position if body.position is not None else s.card_count
    card = _card_entity(body, set_id, position)
    db.add(card)
    s.card_count += 1
    db.commit()
    db.refresh(card)
    return card


@router.patch("/cards/{card_id}", response_model=CardRead)
def update_card(card_id: str, body: CardUpdate, db: Session = Depends(get_db)) -> Flashcard:
    card = db.get(Flashcard, card_id)
    if card is None:
        raise HTTPException(404, "Card not found")
    data = body.model_dump(exclude_unset=True)
    if "acceptable_answers" in data:
        card.acceptable_answers_json = json.dumps(data.pop("acceptable_answers") or [])
    if "choices" in data:
        card.choices_json = json.dumps(data.pop("choices") or [])
    for k, v in data.items():
        setattr(card, k, v)
    db.commit()
    db.refresh(card)
    return card


@router.delete("/cards/{card_id}", status_code=204)
def delete_card(card_id: str, db: Session = Depends(get_db)) -> None:
    card = db.get(Flashcard, card_id)
    if card is None:
        raise HTTPException(404, "Card not found")
    s = db.get(FlashcardSet, card.set_id)
    db.delete(card)
    if s and s.card_count > 0:
        s.card_count -= 1
    db.commit()


@router.post("/sets/{set_id}/import", response_model=ImportResult)
def import_cards(
    set_id: str, body: ImportRequest, db: Session = Depends(get_db)
) -> ImportResult:
    """Bulk-import pasted text into a set (Quizlet-style separators + optional image/notes)."""
    s = db.get(FlashcardSet, set_id)
    if s is None:
        raise HTTPException(404, "Set not found")
    try:
        parsed = parse_import_text(
            body.raw_text,
            field_sep=body.field_sep,
            field_sep_custom=body.field_sep_custom,
            card_sep=body.card_sep,
            card_sep_custom=body.card_sep_custom,
            skip_header=body.skip_header,
            column_map=body.column_map,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    preview = [
        ImportPreviewCard(
            front=p.front, back=p.back, image_url=p.image_url, notes=p.notes
        )
        for p in parsed
    ]
    if body.preview_only or not parsed:
        return ImportResult(imported_count=0, cards=preview, set=None)

    for p in parsed:
        card = TextCard(
            set_id=set_id,
            front=p.front,
            back=p.back,
            image_url=p.image_url,
            notes=p.notes,
            position=s.card_count,
            answer_mode="flip",
        )
        db.add(card)
        s.card_count += 1
    db.commit()
    db.refresh(s)
    return ImportResult(
        imported_count=len(parsed),
        cards=preview,
        set=SetDetail(
            id=s.id,
            title=s.title,
            description=s.description,
            accent=s.accent,
            owner_profile_id=s.owner_profile_id,
            card_count=s.card_count,
            created_at=s.created_at,
            updated_at=s.updated_at,
            due_count=0,
            cards=[CardRead.model_validate(c) for c in s.cards],
        ),
    )


@router.post("/import", response_model=ImportResult, status_code=201)
def import_new_set(body: ImportRequest, db: Session = Depends(get_db)) -> ImportResult:
    """Create a new set from pasted data in one step."""
    title = (body.new_set_title or "").strip() or "Imported set"
    try:
        parsed = parse_import_text(
            body.raw_text,
            field_sep=body.field_sep,
            field_sep_custom=body.field_sep_custom,
            card_sep=body.card_sep,
            card_sep_custom=body.card_sep_custom,
            skip_header=body.skip_header,
            column_map=body.column_map,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    preview = [
        ImportPreviewCard(
            front=p.front, back=p.back, image_url=p.image_url, notes=p.notes
        )
        for p in parsed
    ]
    if body.preview_only:
        return ImportResult(imported_count=0, cards=preview, set=None)
    if not parsed:
        raise HTTPException(400, "Nothing to import — check separators and paste format.")

    s = FlashcardSet(
        title=title,
        description=body.new_set_description or "",
        accent=body.accent or "mint",
        owner_profile_id=body.owner_profile_id,
        card_count=0,
    )
    db.add(s)
    db.flush()
    for p in parsed:
        db.add(
            TextCard(
                set_id=s.id,
                front=p.front,
                back=p.back,
                image_url=p.image_url,
                notes=p.notes,
                position=s.card_count,
                answer_mode="flip",
            )
        )
        s.card_count += 1
    db.commit()
    db.refresh(s)
    return ImportResult(
        imported_count=len(parsed),
        cards=preview,
        set=SetDetail(
            id=s.id,
            title=s.title,
            description=s.description,
            accent=s.accent,
            owner_profile_id=s.owner_profile_id,
            card_count=s.card_count,
            created_at=s.created_at,
            updated_at=s.updated_at,
            due_count=0,
            cards=[CardRead.model_validate(c) for c in s.cards],
        ),
    )
