from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    frontend_origin: str = "http://localhost:5173"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    rate_limit_per_hour: int = 10
    max_question_chars: int = 800
    cache_ttl_seconds: int = 86400
    database_url: str = "sqlite:///./data/pulse.db"
    public_base_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

