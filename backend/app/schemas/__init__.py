from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    created_at: datetime


class ProjectDetail(ProjectRead):
    shots: List["ShotRead"] = Field(default_factory=list)


class ShotCreate(BaseModel):
    title: str = Field(default="New shot", min_length=1, max_length=255)
    user_prompt: Optional[str] = None


class ShotUpdate(BaseModel):
    title: Optional[str] = None
    user_prompt: Optional[str] = None
    sort_order: Optional[int] = None


class ShotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    user_prompt: Optional[str]
    generated_manim_code: Optional[str]
    scene_class_name: Optional[str]
    video_path: Optional[str]
    video_url: Optional[str] = None
    sort_order: int
    render_log: Optional[str]
    created_at: datetime
    updated_at: datetime


class GenerateBody(BaseModel):
    prompt: str = Field(..., min_length=1)


class EditBody(BaseModel):
    message: str = Field(..., min_length=1)


class RegenerateBody(BaseModel):
    prompt: Optional[str] = None


class ExportResponse(BaseModel):
    export_path: str
    video_url: str


ProjectDetail.model_rebuild()
