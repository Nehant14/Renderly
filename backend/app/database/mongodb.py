"""Motor async MongoDB client (singleton)."""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config.settings import get_settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(get_settings().mongodb_url)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[get_settings().database_name]


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
