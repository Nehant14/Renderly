"""Application settings from environment variables."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    mongodb_url: str 
    database_name: str = "renderly"

    gemini_api_key: str 
    gemini_model: str 
    gemini_fallback_models : str


    storage_path: str 
    cors_origins: str 
    manim_quality: str = "qm"   # medium quality  # value from .env will override value here
    render_timeout_sec: int = 600

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
    
    # above convert :
    # CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

    # to:
    # [
    # "http://localhost:5173",
    # "http://127.0.0.1:5173"
    # ]


# caching it using functools
# this is main function that returns the above settings
@lru_cache
def get_settings() -> Settings:
    return Settings()
