"""Google Gemini integration for Manim code generation, edits, and fixes."""
from __future__ import annotations

import asyncio
import logging
import re

import google.generativeai as genai

from app.config.settings import get_settings
from app.utils.code_validator import extract_python_from_markdown

logger = logging.getLogger(__name__)

# Strong system prompts: raw Python only, no prose, no markdown.
SYSTEM_GENERATE = """You are an expert Manim Community Edition animator.
Output rules (strict):
- Return ONLY valid Python source code for one file.
- No markdown, no code fences, no backticks, no explanations, no comments outside the code.
- Use Manim Community Edition (typically: from manim import *).
- Define exactly ONE class that inherits from Scene, with a construct(self) method.
- Animation length roughly 5–15 seconds. Self-contained, no files, no network, no subprocess/os/sys.
- Must be renderable as: manim scene.py <SceneClassName> -ql
- Choose a clear Scene class name (e.g. RunningBoyScene)."""

SYSTEM_EDIT = """You revise Manim Community Edition Python based on the user.
Output rules (strict):
- Return ONLY the full updated Python file.
- No markdown, no fences, no backticks, no commentary before or after code.
- Keep a single Scene subclass; preserve the class name when reasonable.
- No os/subprocess/sys/pathlib/tempfile/network usage in user-facing code paths."""

SYSTEM_FIX = """You repair Manim Community Edition Python that failed to render.
Output rules (strict):
- Return ONLY the complete corrected Python file.
- No markdown, no fences, no backticks, no explanations.
- Fix errors shown in the log while preserving user intent."""


def _strip_noise(text: str) -> str:
    text = (text or "").strip()
    text = extract_python_from_markdown(text)
    # If model still wrapped single-line fences
    text = re.sub(r"^```(?:python)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
    return text.strip()


class AIService:
    def __init__(self) -> None:
        s = get_settings()
        self._model_name = s.gemini_model
        genai.configure(api_key=s.gemini_api_key or None)

    def _generate_sync(self, system_instruction: str, user_text: str) -> str:
        model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system_instruction,
        )
        resp = model.generate_content(
            user_text,
            generation_config={"temperature": 0.35, "max_output_tokens": 8192},
        )
        text = ""
        try:
            text = resp.text or ""
        except ValueError:
            # Blocked or empty candidates
            if resp.candidates:
                parts = []
                for c in resp.candidates:
                    if c.content and c.content.parts:
                        for p in c.content.parts:
                            if hasattr(p, "text") and p.text:
                                parts.append(p.text)
                text = "\n".join(parts)
        out = _strip_noise(text)
        logger.info("Gemini output chars=%s", len(out))
        return out

    async def generate_manim(self, user_prompt: str) -> str:
        user_text = f"User animation request:\n{user_prompt}\n\nProduce the full Manim Python file now."
        return await asyncio.to_thread(self._generate_sync, SYSTEM_GENERATE, user_text)

    async def edit_manim(self, current_code: str, message: str) -> str:
        user_text = (
            "Current Manim code:\n"
            f"{current_code}\n\n"
            "User change request:\n"
            f"{message}\n\n"
            "Return the complete updated Python file only."
        )
        return await asyncio.to_thread(self._generate_sync, SYSTEM_EDIT, user_text)

    async def fix_manim(self, code: str, log: str) -> str:
        user_text = (
            "Broken Manim code:\n"
            f"{code}\n\n"
            "Render / Python error log:\n"
            f"{log[:12000]}\n\n"
            "Return the full fixed Python file only."
        )
        return await asyncio.to_thread(self._generate_sync, SYSTEM_FIX, user_text)


def get_ai_service() -> AIService:
    return AIService()
