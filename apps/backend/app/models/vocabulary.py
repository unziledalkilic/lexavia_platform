"""
Kelime kartları için model.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from app.models.learning_goal import Base


class VocabularyWord(Base):
    __tablename__ = "vocabulary_words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), nullable=False, index=True)
    translation = Column(String(200), nullable=False)
    level = Column(String(4), nullable=False, index=True)  # A1, A2, B1, vb.
    category = Column(String(50), nullable=True, index=True)  # verb, noun, adjective, vb.
    example_sentence = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class UserVocabularyProgress(Base):
    __tablename__ = "user_vocabulary_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    word_id = Column(Integer, ForeignKey("vocabulary_words.id"), nullable=False, index=True)
    last_reviewed = Column(DateTime(timezone=True), default=datetime.utcnow)
    next_review = Column(DateTime(timezone=True), nullable=False)
    review_count = Column(Integer, default=0)
    mastery_level = Column(Integer, default=0)  # 0-5 arası
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

