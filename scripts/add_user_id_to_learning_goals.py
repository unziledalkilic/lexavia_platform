"""
learning_goals tablosuna user_id kolonu ekler.
Kullanım: python -m scripts.add_user_id_to_learning_goals
"""
import asyncio
import sys
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def add_user_id_column():
    """learning_goals tablosuna user_id kolonu ekler."""
    engine = create_async_engine(settings.database_url, echo=True)
    
    async with engine.begin() as conn:
        # Önce users tablosunun var olup olmadığını kontrol et
        users_check = text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name='users'
        """)
        users_result = await conn.execute(users_check)
        users_exists = users_result.scalar() > 0
        
        if not users_exists:
            print("⚠️  users tablosu bulunamadı. Önce init_db scriptini çalıştırın!")
            return
        
        # Önce kolonun var olup olmadığını kontrol et
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='learning_goals' AND column_name='user_id'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none() is not None
        
        if exists:
            print("ℹ️  user_id kolonu zaten mevcut, atlanıyor.")
        else:
            # user_id kolonunu ekle
            # Önce mevcut verileri temizle (user_id olmadan veri tutamayız)
            await conn.execute(text("DELETE FROM learning_goals"))
            print("✅ Eski veriler temizlendi (user_id olmadan veri tutulamaz)")
            
            # user_id kolonunu ekle
            await conn.execute(text("""
                ALTER TABLE learning_goals 
                ADD COLUMN user_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::UUID
            """))
            
            # Foreign key constraint ekle
            await conn.execute(text("""
                ALTER TABLE learning_goals 
                ADD CONSTRAINT fk_learning_goals_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id)
            """))
            
            # Index ekle
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_learning_goals_user_id 
                ON learning_goals(user_id)
            """))
            
            # Default değeri kaldır (artık zorunlu)
            await conn.execute(text("""
                ALTER TABLE learning_goals 
                ALTER COLUMN user_id DROP DEFAULT
            """))
            
            print("✅ user_id kolonu başarıyla eklendi!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_user_id_column())

