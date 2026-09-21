"""Parse pasted bulk card text into structured rows (Quizlet-style import)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional, Sequence


FieldSep = Literal["tab", "comma", "pipe", "custom"]
CardSep = Literal["newline", "semicolon", "blankline", "custom"]
ColumnRole = Literal["front", "back", "image_url", "notes", "ignore"]


@dataclass
class ParsedCard:
    front: str
    back: str
    image_url: Optional[str] = None
    notes: Optional[str] = None


def _resolve_sep(kind: str, custom: Optional[str]) -> str:
    if kind == "tab":
        return "\t"
    if kind == "comma":
        return ","
    if kind == "pipe":
        return "|"
    if kind == "semicolon":
        return ";"
    if kind == "newline":
        return "\n"
    if kind == "blankline":
        return "\n\n"
    if kind == "custom":
        if not custom:
            raise ValueError("Custom separator requires a value")
        return (
            custom.replace("\\t", "\t")
            .replace("\\n", "\n")
            .replace("\\r", "\r")
        )
    raise ValueError(f"Unknown separator kind: {kind}")


def _map_row(
    parts: Sequence[str],
    column_map: Sequence[ColumnRole],
) -> Optional[ParsedCard]:
    """Map split columns onto card fields using an explicit role list."""
    bucket: dict[str, str] = {}
    for idx, role in enumerate(column_map):
        if role == "ignore" or idx >= len(parts):
            continue
        value = parts[idx].strip()
        if value:
            bucket[role] = value

    # Fallback: if no map provided effectively, classic 0=front 1=back 2=image 3=notes
    if "front" not in bucket and "back" not in bucket and len(parts) >= 2:
        bucket["front"] = parts[0].strip()
        bucket["back"] = parts[1].strip()
        if len(parts) > 2 and parts[2].strip():
            bucket["image_url"] = parts[2].strip()
        if len(parts) > 3 and parts[3].strip():
            bucket["notes"] = parts[3].strip()

    front = bucket.get("front", "").strip()
    back = bucket.get("back", "").strip()
    if not front or not back:
        return None
    return ParsedCard(
        front=front,
        back=back,
        image_url=bucket.get("image_url") or None,
        notes=bucket.get("notes") or None,
    )


def parse_import_text(
    raw: str,
    *,
    field_sep: FieldSep = "tab",
    field_sep_custom: Optional[str] = None,
    card_sep: CardSep = "newline",
    card_sep_custom: Optional[str] = None,
    skip_header: bool = False,
    column_map: Optional[Sequence[ColumnRole]] = None,
) -> List[ParsedCard]:
    """
    Split pasted text into cards.

    Default field order: title · definition · image URL · notes
    Override with column_map, e.g. ["front","back","notes","image_url"].
    """
    text = (raw or "").strip()
    if not text:
        return []

    fsep = _resolve_sep(field_sep, field_sep_custom)
    csep = _resolve_sep(card_sep, card_sep_custom)

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if csep == "\n":
        chunks = [c.strip() for c in text.split("\n") if c.strip()]
    elif csep == "\n\n":
        chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    else:
        chunks = [c.strip() for c in text.split(csep) if c.strip()]

    if skip_header and chunks:
        chunks = chunks[1:]

    roles: Sequence[ColumnRole] = column_map or (
        "front",
        "back",
        "image_url",
        "notes",
    )

    cards: List[ParsedCard] = []
    for chunk in chunks:
        # Respect quoted CSV-ish commas lightly: only simple split for MVP
        parts = [p.strip().strip('"') for p in chunk.split(fsep)]
        while parts and parts[-1] == "" and len(parts) > 2:
            parts.pop()
        parsed = _map_row(parts, roles)
        if parsed:
            cards.append(parsed)
    return cards
