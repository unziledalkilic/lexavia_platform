from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class VocabularyWordRead(BaseModel):
    id: int
    word: str
    translation: str
    level: str
    category: str | None
    example_sentence: str | None
    created_at: datetime | None = None


class VocabularyWordList(BaseModel):
    words: list[VocabularyWordRead]
    total: int

