import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = logging.getLogger(__name__)

# Database URL validation
if not settings.database_url:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it in your .env file. "
        "Format: postgresql+asyncpg://user:password@host:port/database"
    )

# Log database URL (masked for security)
db_url_masked = settings.database_url.split("@")[-1] if "@" in settings.database_url else "***"
logger.info(f"Connecting to database: ***@{db_url_masked}")

try:
    engine = create_async_engine(
        settings.database_url,
        future=True,
        echo=False,
        pool_pre_ping=True,  # Verify connections before using
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session() as session:
            yield session
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise


