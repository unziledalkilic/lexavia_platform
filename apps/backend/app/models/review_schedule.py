"""
Review Schedule model for Spaced Repetition (SM-2).
Maps to the 'review_schedules' table created by init_db.py.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from app.models.learning_goal import Base

class ReviewSchedule(Base):
    __tablename__ = "review_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True) # UUID as string from Supabase
    word_id = Column(Integer, ForeignKey("vocabulary_words.id"), nullable=False)
    next_review = Column(DateTime(timezone=True), nullable=False)
    interval = Column(Integer, default=1)
    repetitions = Column(Integer, default=0)
    easiness_factor = Column(Float, default=2.5)
    last_reviewed = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationship
    # word = relationship("VocabularyWord") 
