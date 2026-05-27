from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import Field


class Project(Document):
    """Top-level animation project."""

    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) # lamdba function is defined as datetime.now

    class Settings:
        name = "projects"
