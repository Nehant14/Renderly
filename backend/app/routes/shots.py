from fastapi import APIRouter, HTTPException

from app.config.settings import get_settings
from app.routes.deps import parse_object_id
from app.routes.serialization import shot_read
from app.schemas import EditBody, GenerateBody, RegenerateBody, ShotCreate, ShotRead, ShotUpdate
from app.services import project_service, shot_service

router = APIRouter(prefix="/shots", tags=["shots"])


def _require_gemini() -> None:
    if not get_settings().gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured on the server.",
        )


@router.post("/{shot_id}/generate", response_model=ShotRead)
async def generate_manim(shot_id: str, body: GenerateBody):
    _require_gemini()
    sid = parse_object_id(shot_id, name="shot_id")
    try:
        s = await shot_service.generate_code_for_shot(sid, body.prompt)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return shot_read(s)


@router.post("/{shot_id}/edit", response_model=ShotRead)
async def edit_manim(shot_id: str, body: EditBody):
    _require_gemini()
    sid = parse_object_id(shot_id, name="shot_id")
    try:
        s = await shot_service.edit_code_for_shot(sid, body.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return shot_read(s)


@router.post("/{shot_id}/regenerate", response_model=ShotRead)
async def regenerate_manim(shot_id: str, body: RegenerateBody):
    _require_gemini()
    sid = parse_object_id(shot_id, name="shot_id")
    try:
        s = await shot_service.regenerate_shot(sid, prompt=body.prompt)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return shot_read(s)


@router.post("/{shot_id}/render", response_model=ShotRead)
async def render_manim(shot_id: str, try_fix: bool = False):
    sid = parse_object_id(shot_id, name="shot_id")
    try:
        s = await shot_service.render_shot_task(sid, try_fix=try_fix)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return shot_read(s)


@router.get("/{shot_id}", response_model=ShotRead)
async def get_shot(shot_id: str):
    sid = parse_object_id(shot_id, name="shot_id")
    s = await shot_service.get_shot(sid)
    if not s:
        raise HTTPException(status_code=404, detail="Shot not found")
    return shot_read(s)


@router.patch("/{shot_id}", response_model=ShotRead)
async def patch_shot(shot_id: str, body: ShotUpdate):
    sid = parse_object_id(shot_id, name="shot_id")
    s = await shot_service.update_shot(
        sid,
        title=body.title,
        user_prompt=body.user_prompt,
        sort_order=body.sort_order,
    )
    if not s:
        raise HTTPException(status_code=404, detail="Shot not found")
    return shot_read(s)


@router.delete("/{shot_id}")
async def delete_shot(shot_id: str):
    sid = parse_object_id(shot_id, name="shot_id")
    ok = await shot_service.delete_shot(sid)
    if not ok:
        raise HTTPException(status_code=404, detail="Shot not found")
    return {"ok": True}


project_shots_router = APIRouter(prefix="/projects/{project_id}/shots", tags=["shots"])


@project_shots_router.get("", response_model=list[ShotRead])
async def list_shots(project_id: str):
    pid = parse_object_id(project_id, name="project_id")
    p = await project_service.get_project(pid)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    rows = await shot_service.list_shots(pid)
    return [shot_read(s) for s in rows]


@project_shots_router.post("", response_model=ShotRead)
async def create_shot(project_id: str, body: ShotCreate):
    pid = parse_object_id(project_id, name="project_id")
    p = await project_service.get_project(pid)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    s = await shot_service.create_shot(pid, title=body.title)
    if body.user_prompt:
        await shot_service.update_shot(s.id, user_prompt=body.user_prompt)
        s = await shot_service.get_shot(s.id)
    return shot_read(s)
