from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Sequence

from beanie.odm.enums import SortDirection
from beanie.odm.fields import PydanticObjectId

from app.models.shot import Shot
import re
from app.services.ai_service import AIService, get_ai_service
from app.services.render_service import render_shot_video
from app.utils.code_validator import find_scene_class_name, validate_manim_code
from app.utils.file_storage import ensure_shot_dir


async def list_shots(project_id: PydanticObjectId) -> Sequence[Shot]:
    return await Shot.find(Shot.project_id == project_id).sort(
        ("sort_order", SortDirection.ASCENDING)
    ).to_list()


async def create_shot(project_id: PydanticObjectId, title: str = "New shot") -> Shot:
    # Determine next sort order
    existing = await Shot.find(Shot.project_id == project_id).sort(
        ("sort_order", SortDirection.DESCENDING)
    ).limit(1).to_list()
    next_ord = (existing[0].sort_order + 1) if existing else 0

    # If the caller passed a generic title like "Shot" or "New shot",
    # auto-generate a sequential title: "Shot 1", "Shot 2", ...
    if (title or "").strip().lower() in ("shot", "new shot", ""):
        # Fetch all shots for this project and look for existing "Shot N" titles
        all_shots = await Shot.find(Shot.project_id == project_id).to_list()
        max_n = 0
        for sh in all_shots:
            if not sh.title:
                continue
            m = re.match(r"(?i)^shot\s*(\d+)$", sh.title.strip())
            if m:
                try:
                    n = int(m.group(1))
                except Exception:
                    continue
                if n > max_n:
                    max_n = n
        title = f"Shot {max_n + 1}"

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
    # Clear previous render artifacts when code changes
    s.video_path = None
    s.render_log = None
    s.updated_at = datetime.now(timezone.utc)
    await s.save()
    # Validate generated code; if syntax issues are detected, ask AI to fix it
    ok, errs = validate_manim_code(code)
    if not ok:
        ai = get_ai_service()
        combined_log = "\n".join(errs)
        # Try up to 2 automatic fix attempts
        for _ in range(2):
            try:
                fixed = await ai.fix_manim(code, combined_log)
            except Exception:
                break
            if not fixed or fixed.strip() == code.strip():
                break
            code = fixed
            s = await Shot.get(s.id)
            s.generated_manim_code = code
            s.scene_class_name = find_scene_class_name(code)
            s.updated_at = datetime.now(timezone.utc)
            await s.save()
            ok, errs = validate_manim_code(code)
            combined_log = combined_log + "\n--- AI FIX ATTEMPT ---\n" + ("\n".join(errs) if errs else "")
            if ok:
                break
    return s


async def save_render_result(s: Shot, video_rel: Optional[str], log: str) -> Shot:
    s.video_path = video_rel
    s.render_log = log
    s.updated_at = datetime.now(timezone.utc)
    await s.save()
    return s


async def generate_code_for_shot(
    shot_id: PydanticObjectId, prompt: str, ai: Optional[AIService] = None
) -> Shot:
    ai = ai or get_ai_service()
    s = await Shot.get(shot_id)
    if not s:
        raise ValueError("Shot not found")
    code = await ai.generate_manim(prompt)
    if not code:
        raise ValueError("AI returned empty code. Check your GEMINI_API_KEY.")
    return await save_generated_code(s, code, prompt=prompt)


async def edit_code_for_shot(
    shot_id: PydanticObjectId, message: str, ai: Optional[AIService] = None
) -> Shot:
    ai = ai or get_ai_service()
    s = await Shot.get(shot_id)
    if not s:
        raise ValueError("Shot not found")
    if not s.generated_manim_code:
        raise ValueError("No existing code to edit — send a prompt first.")
    code = await ai.edit_manim(s.generated_manim_code, message)
    if not code:
        raise ValueError("AI returned empty code during edit.")
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
        raise ValueError("No prompt available for regeneration.")
    code = await ai.generate_manim(base_prompt)
    if not code:
        raise ValueError("AI returned empty code during regeneration.")
    return await save_generated_code(s, code, prompt=base_prompt)


async def render_shot_task(shot_id: PydanticObjectId, try_fix: bool = False) -> Shot:
    ai = get_ai_service()
    # Always fetch fresh from DB to avoid stale state
    s = await Shot.get(shot_id)
    if not s:
        raise ValueError("Shot not found")
    if not s.generated_manim_code:
        raise ValueError("No code to render — generate code first.")

    current_code = s.generated_manim_code
    combined_log = ""
    fix_attempts = 0
    render_attempts = 0

    while render_attempts < 3:
        render_attempts += 1
        ok, log, rel = await render_shot_video(str(s.project_id), str(s.id), current_code)
        combined_log = log if not combined_log else combined_log + "\n--- RENDER RETRY ---\n" + log
        if ok:
            return await save_render_result(s, rel, combined_log)

        if fix_attempts >= 2:
            break

        fix_attempts += 1
        fixed_code = await ai.fix_manim(current_code, combined_log)
        if not fixed_code or fixed_code.strip() == current_code.strip():
            break

        s = await Shot.get(shot_id)
        s = await save_generated_code(s, fixed_code, prompt=None)
        current_code = fixed_code

        # If the user requested an explicit fix, allow a second repair attempt.
        if not try_fix:
            break

    return await save_render_result(s, None, combined_log)
