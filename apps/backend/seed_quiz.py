import asyncio
from app.db.session import engine
from app.models.quiz import QuizQuestion
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def seed_data():
    print("Seeding quiz data...")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if empty
        res = await session.execute(text("SELECT count(*) FROM quiz_questions"))
        count = res.scalar()
        
        if count == 0:
            print("Table is empty. Adding mock questions...")
            questions = [
                QuizQuestion(
                    question_text="Which word means 'kitap'?",
                    question_type="multiple_choice",
                    correct_answer="book",
                    options='["book", "apple", "car", "run"]',
                    level="A1",
                    category="vocabulary",
                    explanation="Book means kitap."
                ),
                QuizQuestion(
                    question_text="Which word means 'elma'?",
                    question_type="multiple_choice",
                    correct_answer="apple",
                    options='["apple", "book", "pen", "computer"]',
                    level="A1",
                    category="vocabulary",
                    explanation="Apple means elma."
                ),
                QuizQuestion(
                    question_text="Complete the sentence: I ___ a student.",
                    question_type="multiple_choice",
                    correct_answer="am",
                    options='["am", "is", "are", "be"]',
                    level="A1",
                    category="grammar",
                    explanation="I am..."
                ),
                 QuizQuestion(
                    question_text="Which word means 'koşmak'?",
                    question_type="multiple_choice",
                    correct_answer="run",
                    options='["run", "sleep", "eat", "drink"]',
                    level="A1",
                    category="vocabulary",
                    explanation="Run means koşmak."
                ),
                QuizQuestion(
                    question_text="Which word means 'gelmek'?",
                    question_type="multiple_choice",
                    correct_answer="come",
                    options='["come", "go", "sit", "stand"]',
                    level="A1",
                    category="vocabulary",
                    explanation="Come means gelmek."
                )
            ]
            session.add_all(questions)
            await session.commit()
            print("Seeded 5 questions.")
        else:
            print(f"Table already has {count} questions.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_data())
