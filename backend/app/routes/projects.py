from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.routes.deps import parse_object_id
from app.routes.serialization import project_read, shot_read
from app.schemas import ExportResponse, ProjectCreate, ProjectDetail, ProjectRead
from app.services import project_service, shot_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
async def list_projects() -> list[ProjectRead]:
    rows = await project_service.list_projects()
    return [project_read(r) for r in rows]


@router.post("", response_model=ProjectRead)
async def create_project(body: ProjectCreate) -> ProjectRead:
    p = await project_service.create_project(body.name)
    return project_read(p)


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: str) -> ProjectDetail:
    pid = parse_object_id(project_id, name="project_id")
    p = await project_service.get_project(pid)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    shots = await shot_service.list_shots(pid)
    return ProjectDetail(
        id=str(p.id),
        name=p.name,
        created_at=p.created_at,
        shots=[shot_read(s) for s in shots],
    )


@router.delete("/{project_id}")
async def delete_project(project_id: str) -> dict:
    pid = parse_object_id(project_id, name="project_id")
    ok = await project_service.delete_project(pid)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"ok": True}


@router.post("/{project_id}/export", response_model=ExportResponse)
async def export_project(project_id: str) -> ExportResponse:
    pid = parse_object_id(project_id, name="project_id")
    ok, msg, rel = await project_service.export_project_video(pid)
    if not ok or not rel:
        raise HTTPException(status_code=400, detail=str(msg)[:2000])
    return ExportResponse(export_path=rel, video_url=f"/media/{rel}")
