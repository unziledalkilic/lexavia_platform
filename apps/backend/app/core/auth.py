"""
Supabase JWT token doğrulama ve kullanıcı bilgisi çıkarma.
"""
import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> UUID:
    """
    JWT token'dan user_id çıkarır.
    Supabase JWT token formatını kullanır.
    """
    token = credentials.credentials
    logger.info(f"Received token (first 20 chars): {token[:20] if token else 'None'}...")
    logger.info(f"SUPABASE_JWT_SECRET is set: {bool(settings.supabase_jwt_secret)}")

    if not settings.supabase_jwt_secret:
        logger.warning("SUPABASE_JWT_SECRET not set, skipping token validation (development mode)")
        # Development için geçici olarak token'dan user_id çıkarmayı dene
        try:
            # Token'ı decode et (secret olmadan, sadece payload için)
            decoded = jwt.decode(
                token,
                options={"verify_signature": False},
            )
            user_id = decoded.get("sub")
            if user_id:
                logger.info(f"Development mode: Using user_id from token: {user_id}")
                return UUID(user_id)
        except Exception as e:
            logger.error(f"Error decoding token in development mode: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token format: {str(e)}",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user_id",
        )

    try:
        # Supabase JWT secret ile token'ı doğrula
        # Audience kontrolünü kapatıyoruz çünkü Supabase token'ları farklı audience değerleri kullanabilir
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_aud": False},
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        logger.info(f"Successfully decoded token for user_id: {user_id}")
        return UUID(user_id)
    except JWTError as e:
        logger.error(f"JWT decode error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


async def get_or_create_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Kullanıcıyı veritabanında bulur, yoksa JWT token'dan bilgileri alarak oluşturur.
    """
    token = credentials.credentials
    
    # Token'dan user_id ve email'i al
    user_id: UUID | None = None
    email: str | None = None
    
    try:
        if settings.supabase_jwt_secret:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=[settings.jwt_algorithm],
                options={"verify_aud": False},
            )
        else:
            # Development mode
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
            )
        
        user_id_str = payload.get("sub")
        if user_id_str:
            user_id = UUID(user_id_str)
        email = payload.get("email") or payload.get("user_email") or f"user_{user_id}@temp.local"
    except Exception as e:
        logger.error(f"Error decoding token in get_or_create_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user_id",
        )
    
    # Önce kullanıcıyı kontrol et
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user:
        return user
    
    # Kullanıcı yoksa oluştur
    new_user = User(
        id=user_id,
        email=email,
        full_name=payload.get("full_name") or payload.get("name") or None,
    )
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
        logger.info(f"Created new user in database: {user_id} with email: {email}")
        return new_user
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı oluşturulurken bir hata oluştu",
        )

