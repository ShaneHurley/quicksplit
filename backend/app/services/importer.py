"""Parse pasted bulk card text into structured rows (Quizlet-style import)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional


FieldSep = Literal["tab", "comma", "custom"]
CardSep = Literal["newline", "semicolon", "custom"]


@dataclass
class ParsedCard:
    front: str
    back: str
    image_url: Optional[str] = None
    notes: Optional[str] = None


def _resolve_sep(kind: str, custom: Optional[str], *, for_cards: bool = False) -> str:
    if kind == "tab":
        return "\t"
    if kind == "comma":
        return ","
    if kind == "semicolon":
        return ";"
    if kind == "newline":
        return "\n"
    if kind == "custom":
        if not custom:
            raise ValueError("Custom separator requires a value")
        # Allow escape tokens from the UI
        return (
            custom.replace("\\t", "\t")
            .replace("\\n", "\n")
            .replace("\\r", "\r")
        )
    raise ValueError(f"Unknown separator kind: {kind}")


def parse_import_text(
    raw: str,
    *,
    field_sep: FieldSep = "tab",
    field_sep_custom: Optional[str] = None,
    card_sep: CardSep = "newline",
    card_sep_custom: Optional[str] = None,
) -> List[ParsedCard]:
    """
    Split pasted text into cards.

    Field order per card (trailing fields optional):
      title  {field_sep}  definition  [ {field_sep} image_url [ {field_sep} notes ] ]
    """
    text = (raw or "").strip()
    if not text:
        return []

    fsep = _resolve_sep(field_sep, field_sep_custom)
    csep = _resolve_sep(card_sep, card_sep_custom, for_cards=True)

    # Normalize Windows newlines before card split when using newline separator
    if csep == "\n":
        text = text.replace("\r\n", "\n").replace("\r", "\n")

    chunks = [c.strip() for c in text.split(csep) if c.strip()]
    cards: List[ParsedCard] = []
    for chunk in chunks:
        parts = [p.strip() for p in chunk.split(fsep)]
        # Allow empty trailing optionals but require front + back
        while parts and parts[-1] == "" and len(parts) > 2:
            parts.pop()
        if len(parts) < 2:
            continue
        front, back = parts[0], parts[1]
        if not front or not back:
            continue
        image_url = parts[2] if len(parts) > 2 and parts[2] else None
        notes = parts[3] if len(parts) > 3 and parts[3] else None
        cards.append(ParsedCard(front=front, back=back, image_url=image_url, notes=notes))
    return cards
