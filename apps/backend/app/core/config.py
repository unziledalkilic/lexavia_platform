from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str
    supabase_service_role: str | None = None
    supabase_jwt_secret: str | None = None
    access_token_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"
    
    # AI API Keys (optional)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


