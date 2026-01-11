"""
Quiz soruları ve sonuçları için modeller.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from app.models.learning_goal import Base


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, fill_blank, vb.
    correct_answer = Column(String(200), nullable=False)
    options = Column(Text, nullable=True)  # JSON string: ["option1", "option2", ...]
    level = Column(String(4), nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)  # grammar, vocabulary, vb.
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0-100 arası
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    category_breakdown = Column(Text, nullable=True)  # JSON string
    completed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

