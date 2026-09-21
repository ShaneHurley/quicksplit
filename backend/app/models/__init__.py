"""Export all ORM models so metadata registers for create_all / Alembic."""

from app.models.cooccurrence import CoOccurrenceEdge
from app.models.flashcard import Flashcard, MultipleChoiceCard, TextCard
from app.models.flashcard_set import FlashcardSet
from app.models.performance import UserPerformance
from app.models.profile import Profile, ProfileSettings
from app.models.review_log import ReviewLog
from app.models.study_session import StudySession

__all__ = [
    "Profile",
    "ProfileSettings",
    "FlashcardSet",
    "Flashcard",
    "TextCard",
    "MultipleChoiceCard",
    "UserPerformance",
    "StudySession",
    "ReviewLog",
    "CoOccurrenceEdge",
]
