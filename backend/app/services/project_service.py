from __future__ import annotations

import logging
from typing import List, Optional, Sequence

from beanie.odm.enums import SortDirection
from beanie.odm.fields import PydanticObjectId

from app.models.project import Project
from app.models.shot import Shot
from app.utils.file_storage import absolute_video_path, export_final_path, project_root, storage_root
from app.renderer.video_merge import merge_videos_moviepy

logger = logging.getLogger(__name__)


async def list_projects() -> Sequence[Project]:
    return await Project.find().sort(("created_at", SortDirection.DESCENDING)).to_list()


async def create_project(name: str) -> Project:
    p = Project(name=name)
    await p.insert()
    storage_root().joinpath("projects", str(p.id)).mkdir(parents=True, exist_ok=True)
    return p


async def get_project(project_id: PydanticObjectId) -> Optional[Project]:
    return await Project.get(project_id)


async def delete_project(project_id: PydanticObjectId) -> bool:
    p = await Project.get(project_id)
    if not p:
        return False
    await Shot.find(Shot.project_id == project_id).delete()
    await p.delete()
    return True


async def export_project_video(project_id: PydanticObjectId) -> tuple[bool, str, Optional[str]]:
    p = await Project.get(project_id)
    if not p:
        return False, "Project not found", None
    shots: List[Shot] = await Shot.find(Shot.project_id == project_id).sort(
        ("sort_order", SortDirection.ASCENDING)
    ).to_list()
    paths = []
    for s in shots:
        if s.video_path:
            paths.append(absolute_video_path(s.video_path))   # appending all shot paths
    if not paths:
        return False, "No rendered shots to export", None
    out = export_final_path(str(project_id))
    ok, log = await merge_videos_moviepy(paths, out)
    if not ok:
        logger.error("merge failed: %s", log)
        return False, log, None
    rel = f"projects/{project_id}/export/final_output.mp4"
    return True, "ok", rel
