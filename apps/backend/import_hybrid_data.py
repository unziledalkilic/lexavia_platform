import asyncio
import json
import os
import sys

# Ensure app module is found
sys.path.append(os.getcwd())

from dotenv import load_dotenv
# Load .env explicitly
load_dotenv(".env")

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.db.session import engine

DATA_FILE = os.path.join("data", "curated_vocabulary.json")

async def import_data():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found!")
        return

    print("Connecting to database...")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("Cleaning old data (Creating fresh state)...")
        # Cascade delete to clear words, sentences, and links
        await session.execute(text("TRUNCATE TABLE word_sentences, sentences, vocabulary_words, review_schedules, quiz_questions CASCADE"))
        
        print(f"Reading {DATA_FILE}...")
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        print(f"Found {len(data)} words. Importing...")
        
        for item in data:
            word = item["word"]
            translation = item["translation"]
            level = item["level"]
            category = item["category"]
            ctx_sent_eng = item["context_sentence"]
            ctx_sent_tr = item["turkish_sentence"]
            
            # 1. Insert Word
            res_w = await session.execute(
                text("INSERT INTO vocabulary_words (word, translation, level, category) VALUES (:w, :t, :l, :c) RETURNING id"),
                {"w": word, "t": translation, "l": level, "c": category}
            )
            word_id = res_w.scalar()
            
            # 2. Insert Sentence
            res_s = await session.execute(
                text("INSERT INTO sentences (english_text, turkish_text) VALUES (:e, :t) RETURNING id"),
                {"e": ctx_sent_eng, "t": ctx_sent_tr}
            )
            sentence_id = res_s.scalar()
            
            # 3. Link them
            await session.execute(
                text("INSERT INTO word_sentences (word_id, sentence_id) VALUES (:wid, :sid)"),
                {"wid": word_id, "sid": sentence_id}
            )
            
        await session.commit()
        print("Import completed successfully! Gold Standard Dataset is live.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(import_data())
