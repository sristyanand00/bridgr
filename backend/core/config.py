# backend/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Anthropic (Claude AI)
    ANTHROPIC_API_KEY: str

    # Supabase (database + auth)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # O*NET dataset paths
    ONET_ZIP_PATH: str = "data/raw/db_30_2_text.zip"
    ONET_EXTRACT_PATH: str = "data/"

    # ML tuning
    SEMANTIC_THRESHOLD: float = 0.75
    HIGH_DEMAND_THRESHOLD: float = 0.15

    # App
    APP_NAME: str = "Bridgr"
    DEBUG: bool = False
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Cached — reads .env only once."""
    return Settings()