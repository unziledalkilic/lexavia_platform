"""
Veritabanı tablolarını oluşturan migration scripti.
Kullanım: python -m scripts.init_db
"""
import asyncio
import sys
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
# Tüm modelleri import et ki Base.metadata'ya eklensinler
from app.models.learning_goal import Base, LearningGoal
from app.models.user import User  # noqa: F401
from app.models.vocabulary import VocabularyWord, UserVocabularyProgress  # noqa: F401
from app.models.quiz import QuizQuestion, QuizSession  # noqa: F401


async def init_db():
    """Veritabanı tablolarını oluşturur."""
    engine = create_async_engine(settings.database_url, echo=True)
    
    async with engine.begin() as conn:
        # Tüm tabloları oluştur
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Veritabanı tabloları başarıyla oluşturuldu!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())

