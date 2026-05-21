"""Merge shot videos using MoviePy (FFmpeg-backed encoding)."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def _merge_sync(video_paths: List[Path], output: Path) -> tuple[bool, str]:
    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips
    except ImportError as e:
        return False, f"moviepy import failed: {e}"

    if not video_paths:
        return False, "No videos to merge"
    output.parent.mkdir(parents=True, exist_ok=True)

    clips = []
    try:
        for p in video_paths:
            if not p.is_file():
                return False, f"Missing file: {p}"
            clips.append(VideoFileClip(str(p)))
        if not clips:
            return False, "No clips loaded"
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            str(output),
            codec="libx264",
            audio=False,
            logger=None,
        )
        final.close()
        return True, "ok"
    except Exception as e:
        logger.exception("moviepy merge failed")
        return False, str(e)
    finally:
        for c in clips:
            try:
                c.close()
            except Exception:
                pass


async def merge_videos_moviepy(video_paths: List[Path], output: Path) -> tuple[bool, str]:
    """Run MoviePy merge in a worker thread to avoid blocking the event loop."""
    return await asyncio.to_thread(_merge_sync, video_paths, output)
