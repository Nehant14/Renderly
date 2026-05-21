from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from beanie.odm.fields import PydanticObjectId
from pydantic import Field


class Shot(Document):
    """A single Manim scene / timeline unit inside a project."""

    project_id: PydanticObjectId
    title: str = "New shot"
    user_prompt: Optional[str] = None
    generated_manim_code: Optional[str] = None
    scene_class_name: Optional[str] = None
    video_path: Optional[str] = None
    sort_order: int = 0
    render_log: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "shots"
