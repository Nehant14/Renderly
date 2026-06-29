"""Filesystem helpers for per-project / per-shot storage."""
from __future__ import annotations

from pathlib import Path

from app.config.settings import get_settings


def project_root(project_id: str) -> Path:
    settings = get_settings()
    root = Path(settings.storage_path).resolve()
    d = root / "projects" / str(project_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def ensure_shot_dir(project_id: str, shot_id: str) -> Path:
    d = project_root(project_id) / "shots" / str(shot_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def shot_scene_path(project_id: str, shot_id: str) -> Path:
    return ensure_shot_dir(project_id, shot_id) / "scene.py"


def shot_video_file(project_id: str, shot_id: str) -> Path:
    return ensure_shot_dir(project_id, shot_id) / "render.mp4"


def shot_video_path(project_id: str, shot_id: str) -> str:
    return f"projects/{project_id}/shots/{shot_id}/render.mp4"


def export_final_path(project_id: str) -> Path:
    d = project_root(project_id) / "export"
    d.mkdir(parents=True, exist_ok=True)
    return d / "final_output.mp4"


def storage_root() -> Path:
    return Path(get_settings().storage_path).resolve()


def absolute_video_path(relative: str) -> Path:
    return storage_root() / relative
