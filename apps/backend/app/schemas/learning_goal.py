from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LearningGoalCreate(BaseModel):
    target_language: str = "en"
    level: str
    daily_minutes: int
    goal_type: str
    focus_topics: str | None = None


class LearningGoalRead(LearningGoalCreate):
    id: int
    user_id: UUID
    created_at: datetime
    current_xp: int = 0
    next_level_xp: int = 0
    next_level: str | None = None


