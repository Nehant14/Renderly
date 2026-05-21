"""Application settings from environment variables."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "animcursor"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    storage_path: str = "./storage"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    manim_quality: str = "ql"
    render_timeout_sec: int = 600

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
