from datetime import datetime
from uuid import UUID

from pydantic import BaseModel



class QuizQuestionRead(BaseModel):
    id: int
    word_id: int | None = None # Track the underlying word
    question_text: str
    question_type: str
    correct_answer: str
    options: str | None  # JSON string
    level: str
    category: str | None
    explanation: str | None
    created_at: datetime | None = None


class QuizQuestionList(BaseModel):
    questions: list[QuizQuestionRead]
    total: int

class QuizResultDetail(BaseModel):
    word_id: int | None
    word: str
    is_correct: bool

class QuizSessionCreate(BaseModel):
    score: float
    total_questions: int
    correct_answers: int
    category_breakdown: str | None = None  # JSON string
    results: list[QuizResultDetail] | None = None # Detailed results for SR update

class QuizSessionRead(QuizSessionCreate):
    id: int
    user_id: UUID
    completed_at: datetime
    created_at: datetime
    new_level: str | None = None # Field to return if user leveled up


