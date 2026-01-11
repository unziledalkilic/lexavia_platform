import asyncio
import io
import zipfile
import urllib.request
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.db.session import engine
from app.models.vocabulary import VocabularyWord
from app.models.quiz import QuizQuestion

# URL for English-Turkish sentence pairs (Tatoeba Project via ManyThings.org)
DATASET_URL = "http://www.manythings.org/anki/tur-eng.zip"
DATA_DIR = "data"
TXT_FILE = os.path.join(DATA_DIR, "tur.txt")

async def download_and_extract():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if os.path.exists(TXT_FILE):
        print(f"File {TXT_FILE} already exists. Skipping download.")
        return

    print(f"Downloading dataset from {DATASET_URL}...")
    try:
        with urllib.request.urlopen(DATASET_URL) as response:
            zip_content = response.read()
            
        print("Extracting zip file...")
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            z.extract("tur.txt", path=DATA_DIR)
        print("Download and extraction complete.")
    except Exception as e:
        print(f"Failed to download dataset: {e}")
        raise

async def import_data():
    await download_and_extract()
    
    print("Connecting to database...")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Clear existing generic data (Optional - maybe keep for now or wipe for clean slate)
        # print("Cleaning old data...")
        # await session.execute(text("TRUNCATE TABLE word_sentences, sentences, vocabulary_words CASCADE"))
        
        print(f"Reading {TXT_FILE}...")
        count = 0
        batch_size = 100
        
        # We need to map words to sentences. 
        # Strategy:
        # 1. Insert Sentences
        # 2. Extract simple words from English sentence
        # 3. Insert Word if not exists
        # 4. Link Word <-> Sentence
        
        # NOTE: Inserting 500k rows might be too slow for this script without bulk insert.
        # We will take the top 1000 shortest/simplest sentences for the MVP to ensure speed.
        
        with open(TXT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # Sort by length to get simple sentences first (usually better for learning)
        lines.sort(key=len)
        
        # Take a subset
        selected_lines = lines[:2000] 
        print(f"Selected {len(selected_lines)} sentences for import.")

        from app.models.learning_goal import Base
        # Raw SQL might be faster or just efficient ORM usage
        
        # Helper to check/insert sentence
        # We will use raw SQL for performance and to avoid circular dependency issues if models aren't perfect
        
        for line in selected_lines:
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
                
            eng_text = parts[0].strip()
            tr_text = parts[1].strip()
            
            # 1. Insert Sentence
            # Check if exists first to avoid dupes if running multiple times? 
            # For MVP, just insert.
            
            # Insert Sentence and get ID
            res = await session.execute(
                text("INSERT INTO sentences (english_text, turkish_text) VALUES (:eng, :tr) RETURNING id"),
                {"eng": eng_text, "tr": tr_text}
            )
            sentence_id = res.scalar()
            
            # 2. Process Words (Simple Tokenization)
            words = set(eng_text.lower().split())
            
            for w in words:
                # Clean word
                clean_word = "".join(c for c in w if c.isalnum())
                if len(clean_word) < 3: # Skip 'a', 'is', 'to' etc for now to avoid noise
                    continue
                    
                # Insert Word (Duplicate key ignore)
                # First check if exists
                res_w = await session.execute(
                    text("SELECT id FROM vocabulary_words WHERE word = :word"),
                    {"word": clean_word}
                )
                word_id = res_w.scalar()
                
                if not word_id:
                    # Guess Level based on length (Naive but working for now)
                    level = "A1"
                    if len(clean_word) > 5: level = "A2"
                    if len(clean_word) > 8: level = "B1"
                    
                    res_ins = await session.execute(
                        text("INSERT INTO vocabulary_words (word, translation, level, category) VALUES (:word, :trans, :lvl, 'general') RETURNING id"),
                        {"word": clean_word, "trans": "...", "lvl": level} # Trans is placeholder, user learns from context
                    )
                    word_id = res_ins.scalar()
                
                # 3. Link
                await session.execute(
                    text("INSERT INTO word_sentences (word_id, sentence_id) VALUES (:wid, :sid) ON CONFLICT DO NOTHING"),
                    {"wid": word_id, "sid": sentence_id}
                )

            count += 1
            if count % 100 == 0:
                print(f"Processed {count} sentences...")
                await session.commit()
        
        await session.commit()
        print("Import completed successfully!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(import_data())
