"""
Örnek içerik seed scripti.
Kullanım: python -m scripts.seed_content
"""
import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.models.quiz import QuizQuestion
from app.models.vocabulary import VocabularyWord
from app.models.learning_goal import Base
from sqlalchemy import select


# Örnek kelimeler
VOCABULARY_WORDS = [
    # A1 seviyesi kelimeler
    {"word": "hello", "translation": "merhaba", "level": "A1", "category": "greeting", "example_sentence": "Hello, how are you?"},
    {"word": "goodbye", "translation": "hoşça kal", "level": "A1", "category": "greeting", "example_sentence": "Goodbye, see you tomorrow."},
    {"word": "please", "translation": "lütfen", "level": "A1", "category": "common", "example_sentence": "Please help me."},
    {"word": "thank you", "translation": "teşekkür ederim", "level": "A1", "category": "greeting", "example_sentence": "Thank you for your help."},
    {"word": "yes", "translation": "evet", "level": "A1", "category": "common", "example_sentence": "Yes, I understand."},
    {"word": "no", "translation": "hayır", "level": "A1", "category": "common", "example_sentence": "No, I don't know."},
    {"word": "water", "translation": "su", "level": "A1", "category": "noun", "example_sentence": "I need a glass of water."},
    {"word": "food", "translation": "yiyecek", "level": "A1", "category": "noun", "example_sentence": "I like Italian food."},
    {"word": "house", "translation": "ev", "level": "A1", "category": "noun", "example_sentence": "This is my house."},
    {"word": "friend", "translation": "arkadaş", "level": "A1", "category": "noun", "example_sentence": "She is my best friend."},
    {"word": "book", "translation": "kitap", "level": "A1", "category": "noun", "example_sentence": "I am reading a book."},
    {"word": "school", "translation": "okul", "level": "A1", "category": "noun", "example_sentence": "I go to school every day."},
    {"word": "work", "translation": "çalışmak", "level": "A1", "category": "verb", "example_sentence": "I work in an office."},
    {"word": "study", "translation": "çalışmak", "level": "A1", "category": "verb", "example_sentence": "I study English every day."},
    {"word": "learn", "translation": "öğrenmek", "level": "A1", "category": "verb", "example_sentence": "I want to learn Spanish."},
    # B1 seviyesi kelimeler
    {"word": "achieve", "translation": "başarmak", "level": "B1", "category": "verb", "example_sentence": "I want to achieve my goals."},
    {"word": "benefit", "translation": "fayda", "level": "B1", "category": "noun", "example_sentence": "Exercise has many benefits."},
    {"word": "challenge", "translation": "meydan okuma", "level": "B1", "category": "noun", "example_sentence": "This is a big challenge."},
    {"word": "develop", "translation": "geliştirmek", "level": "B1", "category": "verb", "example_sentence": "We need to develop new skills."},
    {"word": "effective", "translation": "etkili", "level": "B1", "category": "adjective", "example_sentence": "This method is very effective."},
    {"word": "opportunity", "translation": "fırsat", "level": "B1", "category": "noun", "example_sentence": "This is a great opportunity."},
    {"word": "improve", "translation": "iyileştirmek", "level": "B1", "category": "verb", "example_sentence": "I want to improve my English."},
    {"word": "knowledge", "translation": "bilgi", "level": "B1", "category": "noun", "example_sentence": "Knowledge is power."},
    {"word": "successful", "translation": "başarılı", "level": "B1", "category": "adjective", "example_sentence": "She is a successful entrepreneur."},
    {"word": "experience", "translation": "deneyim", "level": "B1", "category": "noun", "example_sentence": "I have 5 years of experience."},
    {"word": "ability", "translation": "yetenek", "level": "B2", "category": "noun", "example_sentence": "She has the ability to learn quickly."},
    {"word": "accomplish", "translation": "tamamlamak", "level": "B2", "category": "verb", "example_sentence": "We need to accomplish this task."},
    {"word": "analyze", "translation": "analiz etmek", "level": "B2", "category": "verb", "example_sentence": "Let's analyze the data."},
    {"word": "approach", "translation": "yaklaşım", "level": "B2", "category": "noun", "example_sentence": "This is a new approach."},
    {"word": "assess", "translation": "değerlendirmek", "level": "B2", "category": "verb", "example_sentence": "We need to assess the situation."},
]

# Örnek quiz soruları
QUIZ_QUESTIONS = [
    # A1 seviyesi sorular
    {
        "question_text": "Hello, _____ are you?",
        "question_type": "multiple_choice",
        "correct_answer": "how",
        "options": json.dumps(["how", "what", "where", "when"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'How are you?' selamlaşma için kullanılır.",
    },
    {
        "question_text": "I _____ a student.",
        "question_type": "multiple_choice",
        "correct_answer": "am",
        "options": json.dumps(["am", "is", "are", "be"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'I' ile 'am' kullanılır.",
    },
    {
        "question_text": "What is your _____?",
        "question_type": "multiple_choice",
        "correct_answer": "name",
        "options": json.dumps(["name", "age", "color", "food"]),
        "level": "A1",
        "category": "vocabulary",
        "explanation": "'What is your name?' isim sormak için kullanılır.",
    },
    {
        "question_text": "I _____ English every day.",
        "question_type": "multiple_choice",
        "correct_answer": "study",
        "options": json.dumps(["study", "studies", "studying", "studied"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "Present simple tense için 'study' kullanılır.",
    },
    {
        "question_text": "This is _____ book.",
        "question_type": "multiple_choice",
        "correct_answer": "a",
        "options": json.dumps(["a", "an", "the", "is"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'Book' sessiz harfle başlar, 'a' kullanılır.",
    },
    {
        "question_text": "I like _____ food.",
        "question_type": "multiple_choice",
        "correct_answer": "Italian",
        "options": json.dumps(["Italian", "Italy", "Italians", "Italy's"]),
        "level": "A1",
        "category": "vocabulary",
        "explanation": "'Italian' sıfat olarak kullanılır.",
    },
    # B1 seviyesi sorular
    {
        "question_text": "I _____ to the store yesterday.",
        "question_type": "multiple_choice",
        "correct_answer": "went",
        "options": json.dumps(["go", "went", "gone", "going"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Past tense için 'went' kullanılır.",
    },
    {
        "question_text": "She _____ English for 5 years.",
        "question_type": "multiple_choice",
        "correct_answer": "has studied",
        "options": json.dumps(["studies", "has studied", "is studying", "study"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Present Perfect tense için 'has studied' kullanılır.",
    },
    {
        "question_text": "Choose the correct word: The _____ of the book is interesting.",
        "question_type": "multiple_choice",
        "correct_answer": "content",
        "options": json.dumps(["content", "contain", "container", "containing"]),
        "level": "B1",
        "category": "vocabulary",
        "explanation": "'Content' kelimesi 'içerik' anlamına gelir.",
    },
    {
        "question_text": "If I _____ rich, I would travel the world.",
        "question_type": "multiple_choice",
        "correct_answer": "were",
        "options": json.dumps(["am", "was", "were", "be"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "Second conditional'da 'were' kullanılır.",
    },
    {
        "question_text": "He is _____ than his brother.",
        "question_type": "multiple_choice",
        "correct_answer": "taller",
        "options": json.dumps(["tall", "taller", "tallest", "more tall"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Karşılaştırma için 'taller' kullanılır.",
    },
    {
        "question_text": "The company decided to _____ new employees.",
        "question_type": "multiple_choice",
        "correct_answer": "hire",
        "options": json.dumps(["hire", "fire", "retire", "admire"]),
        "level": "B1",
        "category": "vocabulary",
        "explanation": "'Hire' kelimesi 'işe almak' anlamına gelir.",
    },
    {
        "question_text": "I haven't seen him _____ last week.",
        "question_type": "multiple_choice",
        "correct_answer": "since",
        "options": json.dumps(["since", "for", "from", "during"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Belirli bir zaman noktası için 'since' kullanılır.",
    },
    {
        "question_text": "She is _____ in mathematics.",
        "question_type": "multiple_choice",
        "correct_answer": "excellent",
        "options": json.dumps(["excellent", "excellence", "excel", "excellently"]),
        "level": "B2",
        "category": "vocabulary",
        "explanation": "'Excellent' sıfat olarak kullanılır.",
    },
]


async def seed_content():
    """Veritabanına örnek içerik ekler."""
    engine = create_async_engine(settings.database_url, echo=True)
    
    async with engine.begin() as conn:
        # Tabloları oluştur
        await conn.run_sync(Base.metadata.create_all)
    
    async with engine.begin() as conn:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Kelimeleri ekle - sadece yeni olanları ekle
            added_count = 0
            for word_data in VOCABULARY_WORDS:
                # Bu kelime zaten var mı kontrol et
                existing = await session.execute(
                    select(VocabularyWord).where(
                        VocabularyWord.word == word_data["word"],
                        VocabularyWord.level == word_data["level"]
                    )
                )
                if existing.scalar_one_or_none() is None:
                    word = VocabularyWord(**word_data)
                    session.add(word)
                    added_count += 1
            
            if added_count > 0:
                print(f"✅ {added_count} yeni kelime eklendi")
            else:
                print("ℹ️  Tüm kelimeler zaten mevcut")
            
            # Quiz sorularını ekle - sadece yeni olanları ekle
            added_questions = 0
            for question_data in QUIZ_QUESTIONS:
                # Bu soru zaten var mı kontrol et
                existing = await session.execute(
                    select(QuizQuestion).where(
                        QuizQuestion.question_text == question_data["question_text"],
                        QuizQuestion.level == question_data["level"]
                    )
                )
                if existing.scalar_one_or_none() is None:
                    question = QuizQuestion(**question_data)
                    session.add(question)
                    added_questions += 1
            
            if added_questions > 0:
                print(f"✅ {added_questions} yeni quiz sorusu eklendi")
            else:
                print("ℹ️  Tüm quiz soruları zaten mevcut")
            
            await session.commit()
    
    print("✅ İçerik seed işlemi tamamlandı!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_content())

