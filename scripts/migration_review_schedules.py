"""
Review Schedules Migration

Spaced Repetition için review schedule tablosu oluşturur.
SuperMemo SM-2 algoritması için gerekli alanları içerir.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ReviewSchedule(Base):
    """
    Kullanıcı kelime tekrar planları
    
    SM-2 algoritması ile optimal öğrenme zamanlaması için kullanılır.
    """
    __tablename__ = "review_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # İlişkiler
    word_id = Column(Integer, nullable=False, index=True, comment="Vocabulary word ID")
    user_id = Column(String, nullable=False, index=True, comment="User UUID")
    
    # SM-2 Parametreleri
    next_review = Column(DateTime, nullable=False, index=True, comment="Bir sonraki tekrar zamanı")
    interval = Column(Integer, nullable=False, default=1, comment="Tekrar aralığı (gün)")
    repetitions = Column(Integer, nullable=False, default=0, comment="Başarılı tekrar sayısı")
    easiness_factor = Column(Float, nullable=False, default=2.5, comment="Kolaylık faktörü (1.3-2.5)")
    
    # Tracking
    last_reviewed = Column(DateTime, nullable=True, comment="Son tekrar zamanı")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Oluşturulma zamanı")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Güncellenme zamanı")
    
    def __repr__(self):
        return f"<ReviewSchedule(word_id={self.word_id}, user_id={self.user_id}, next_review={self.next_review})>"


# SQL Migration Script
SQL_CREATE_TABLE = """
-- Spaced Repetition Review Schedules Table
CREATE TABLE IF NOT EXISTS review_schedules (
    id SERIAL PRIMARY KEY,
    
    -- İlişkiler
    word_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    
    -- SM-2 Parametreleri
    next_review TIMESTAMP NOT NULL,
    interval INTEGER NOT NULL DEFAULT 1,
    repetitions INTEGER NOT NULL DEFAULT 0,
    easiness_factor FLOAT NOT NULL DEFAULT 2.5,
    
    -- Tracking
    last_reviewed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- İndeksler için hazırlık
    CONSTRAINT check_interval_positive CHECK (interval > 0),
    CONSTRAINT check_easiness_range CHECK (easiness_factor >= 1.3 AND easiness_factor <= 2.5)
);

-- İndeksler (hızlı sorgulama için)
CREATE INDEX IF NOT EXISTS idx_review_schedules_user_id ON review_schedules(user_id);
CREATE INDEX IF NOT EXISTS idx_review_schedules_word_id ON review_schedules(word_id);
CREATE INDEX IF NOT EXISTS idx_review_schedules_next_review ON review_schedules(next_review);
CREATE INDEX IF NOT EXISTS idx_review_schedules_user_next ON review_schedules(user_id, next_review);

-- Updated_at için trigger (PostgreSQL)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_review_schedules_updated_at
BEFORE UPDATE ON review_schedules
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Örnek sorgular (dokümantasyon için)

-- Bugün tekrarı olan kelimeler
-- SELECT * FROM review_schedules 
-- WHERE user_id = 'user-uuid' AND next_review <= NOW()
-- ORDER BY next_review ASC;

-- Önümüzdeki 7 gün içindeki tekrarlar
-- SELECT * FROM review_schedules 
-- WHERE user_id = 'user-uuid' 
-- AND next_review BETWEEN NOW() AND NOW() + INTERVAL '7 days'
-- ORDER BY next_review ASC;
"""

SQL_DROP_TABLE = """
-- Review Schedules tablosunu sil (dikkatli kullan!)
DROP TRIGGER IF EXISTS update_review_schedules_updated_at ON review_schedules;
DROP FUNCTION IF EXISTS update_updated_at_column();
DROP TABLE IF EXISTS review_schedules CASCADE;
"""


if __name__ == "__main__":
    print("Review Schedules Migration")
    print("=" * 60)
    print("\nCreate table SQL:")
    print(SQL_CREATE_TABLE)
    print("\n" + "=" * 60)
    print("\nDrop table SQL (destructive):")
    print(SQL_DROP_TABLE)
