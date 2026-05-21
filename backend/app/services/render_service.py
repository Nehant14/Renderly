"""Async facade over the Manim subprocess renderer."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from app.renderer.manim_runner import render_shot as _render_shot
from app.utils.file_storage import ensure_shot_dir


async def render_shot_video(
    project_id: str,
    shot_id: str,
    code: str,
) -> Tuple[bool, str, Optional[str]]:
    shot_dir = ensure_shot_dir(project_id, shot_id)
    return await _render_shot(project_id, shot_id, code, shot_dir)
