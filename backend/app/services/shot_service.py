from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Sequence

from beanie.odm.enums import SortDirection
from beanie.odm.fields import PydanticObjectId

from app.models.shot import Shot
from app.services.ai_service import AIService, get_ai_service
from app.services.render_service import render_shot_video
from app.utils.code_validator import find_scene_class_name
from app.utils.file_storage import ensure_shot_dir


async def list_shots(project_id: PydanticObjectId) -> Sequence[Shot]:
    return await Shot.find(Shot.project_id == project_id).sort(
        ("sort_order", SortDirection.ASCENDING)
    ).to_list()


async def create_shot(project_id: PydanticObjectId, title: str = "New shot") -> Shot:
    existing = await Shot.find(Shot.project_id == project_id).sort(
        ("sort_order", SortDirection.DESCENDING)
    ).limit(1).to_list()
    next_ord = (existing[0].sort_order + 1) if existing else 0
    s = Shot(project_id=project_id, title=title, sort_order=next_ord)
    await s.insert()
    ensure_shot_dir(str(project_id), str(s.id))
    return s


async def get_shot(shot_id: PydanticObjectId) -> Optional[Shot]:
    return await Shot.get(shot_id)


async def update_shot(
    shot_id: PydanticObjectId,
    *,
    title: Optional[str] = None,
    user_prompt: Optional[str] = None,
    sort_order: Optional[int] = None,
) -> Optional[Shot]:
    s = await Shot.get(shot_id)
    if not s:
        return None
    if title is not None:
        s.title = title
    if user_prompt is not None:
        s.user_prompt = user_prompt
    if sort_order is not None:
        s.sort_order = sort_order
    s.updated_at = datetime.now(timezone.utc)
    await s.save()
    return s


async def delete_shot(shot_id: PydanticObjectId) -> bool:
    s = await Shot.get(shot_id)
    if not s:
        return False
    await s.delete()
    return True


async def save_generated_code(s: Shot, code: str, prompt: Optional[str] = None) -> Shot:
    s.generated_manim_code = code
    s.scene_class_name = find_scene_class_name(code)
    if prompt is not None:
        s.user_prompt = prompt
    s.updated_at = datetime.now(timezone.utc)
    await s.save()
    return s


async def save_render_result(s: Shot, video_rel: Optional[str], log: str) -> Shot:
    s.video_path = video_rel
    s.render_log = log
    s.updated_at = datetime.now(timezone.utc)
    await s.save()
    return s


async def generate_code_for_shot(shot_id: PydanticObjectId, prompt: str, ai: Optional[AIService] = None) -> Shot:
    ai = ai or get_ai_service()
    s = await Shot.get(shot_id)
    if not s:
        raise ValueError("Shot not found")
    code = await ai.generate_manim(prompt)
    return await save_generated_code(s, code, prompt=prompt)


async def edit_code_for_shot(shot_id: PydanticObjectId, message: str, ai: Optional[AIService] = None) -> Shot:
    ai = ai or get_ai_service()
    s = await Shot.get(shot_id)
    if not s:
        raise ValueError("Shot not found")
    if not s.generated_manim_code:
        raise ValueError("No existing code to edit")
    code = await ai.edit_manim(s.generated_manim_code, message)
    return await save_generated_code(s, code, prompt=None)


async def regenerate_shot(
    shot_id: PydanticObjectId,
    prompt: Optional[str] = None,
    ai: Optional[AIService] = None,
) -> Shot:
    ai = ai or get_ai_service()
    s = await Shot.get(shot_id)
    if not s:
        raise ValueError("Shot not found")
    base_prompt = prompt or s.user_prompt
    if not base_prompt:
        raise ValueError("No prompt available for regeneration")
    code = await ai.generate_manim(base_prompt)
    return await save_generated_code(s, code, prompt=base_prompt)


async def render_shot_task(shot_id: PydanticObjectId, try_fix: bool = False) -> Shot:
    ai = get_ai_service() if try_fix else None
    s = await Shot.get(shot_id)
    if not s:
        raise ValueError("Shot not found")
    if not s.generated_manim_code:
        raise ValueError("No code to render")
    ok, log, rel = await render_shot_video(str(s.project_id), str(s.id), s.generated_manim_code)
    if ok:
        return await save_render_result(s, rel, log)
    if try_fix and ai:
        fixed = await ai.fix_manim(s.generated_manim_code, log)
        s = await save_generated_code(s, fixed, prompt=None)
        ok2, log2, rel2 = await render_shot_video(str(s.project_id), str(s.id), s.generated_manim_code)
        log = log + "\n--- AUTO-FIX ATTEMPT ---\n" + log2
        if ok2:
            return await save_render_result(s, rel2, log)
    await save_render_result(s, s.video_path, log)
    return s
