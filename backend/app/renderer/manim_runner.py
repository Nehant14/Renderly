"""Run Manim in an isolated working directory (per shot)."""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple

from app.config.settings import get_settings
from app.utils.code_validator import find_scene_class_name, validate_manim_code

logger = logging.getLogger(__name__)


async def render_shot(
    project_id: str,
    shot_id: str,
    code: str,
    shot_dir: Path,
) -> Tuple[bool, str, Optional[str]]:
    """
    Writes scene.py, runs manim, copies output to render.mp4 under shot_dir.
    Returns (success, log_text, relative_video_path or None).
    """
    settings = get_settings()
    ok, errs = validate_manim_code(code)
    if not ok:
        log = "Validation failed:\n" + "\n".join(errs)
        return False, log, None

    scene_name = find_scene_class_name(code)
    if not scene_name:
        return False, "Could not detect Scene class name", None

    shot_dir.mkdir(parents=True, exist_ok=True)
    scene_path = shot_dir / "scene.py"
    scene_path.write_text(code, encoding="utf-8")

    quality = settings.manim_quality.lstrip("-")

    # using no -p for preview
    quality_flag = f"-{quality}"
    
    cmd = [
        "manim",
        str(scene_path.name),
        scene_name,
        quality_flag,
        "--media_dir",
        ".",
    ]
    logger.info("Running manim: cwd=%s cmd=%s", shot_dir, cmd)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(shot_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=_subprocess_env(),
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=settings.render_timeout_sec)
    except asyncio.TimeoutError:
        proc.kill()
        return False, "Render timed out", None

    out = (stdout or b"").decode(errors="replace")
    err = (stderr or b"").decode(errors="replace")
    log = f"STDOUT:\n{out}\nSTDERR:\n{err}"
    if proc.returncode != 0:
        return False, log, None

    mp4s = sorted(shot_dir.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not mp4s:
        return False, log + "\nNo mp4 produced.", None

    dest = shot_dir / "render.mp4"
    shutil.copyfile(mp4s[0], dest)
    rel = f"projects/{project_id}/shots/{shot_id}/render.mp4"
    return True, log, rel


def _subprocess_env() -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env
