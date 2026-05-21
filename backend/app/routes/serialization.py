from __future__ import annotations

from app.models.project import Project
from app.models.shot import Shot
from app.schemas import ProjectRead, ShotRead


def shot_read(shot: Shot) -> ShotRead:
    video_url = f"/media/{shot.video_path}" if shot.video_path else None
    sid = str(shot.id)
    pid = str(shot.project_id)
    return ShotRead(
        id=sid,
        project_id=pid,
        title=shot.title,
        user_prompt=shot.user_prompt,
        generated_manim_code=shot.generated_manim_code,
        scene_class_name=shot.scene_class_name,
        video_path=shot.video_path,
        video_url=video_url,
        sort_order=shot.sort_order,
        render_log=shot.render_log,
        created_at=shot.created_at,
        updated_at=shot.updated_at,
    )


def project_read(project: Project) -> ProjectRead:
    return ProjectRead(
        id=str(project.id),
        name=project.name,
        created_at=project.created_at,
    )
