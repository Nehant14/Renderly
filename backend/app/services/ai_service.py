"""Google Gemini integration for Manim code generation, edits, and fixes."""
from __future__ import annotations

import asyncio
import logging
import re

import google.generativeai as genai
from google.generativeai import types as genai_types

from app.config.settings import get_settings
from app.utils.code_validator import extract_python_from_markdown

logger = logging.getLogger(__name__)

SYSTEM_GENERATE = """You are an expert Manim Community Edition animator.

Output rules (STRICT - MUST FOLLOW):
- Return ONLY valid Python source code for one file.
- No markdown, no code fences, no backticks.
- No explanations anywhere.
- No comments inside the code (# are NOT allowed).
- Use Manim Community Edition (from manim import *).
- Define exactly ONE class that inherits from Scene with a construct(self) method.
- The output must be a COMPLETE, fully executable Python file.
- Do NOT stop early. Always finish the full file.
- If the file is incomplete, it is invalid.
- Ensure the structure is always: imports → class → construct() → end of file.
- Animation length: 5–15 seconds.
- Self-contained only (no files, no network, no subprocess, no os/sys usage).
- Must be renderable as: manim scene.py SceneName -ql
- Choose a clear Scene class name (e.g. RunningBoyScene).
"""


SYSTEM_EDIT = """You revise Manim Community Edition Python based on the user.

Output rules (STRICT - MUST FOLLOW):
- Return ONLY the full updated Python file.
- No markdown, no code fences, no backticks.
- No explanations anywhere.
- No comments inside the code (# are NOT allowed).
- Keep a single Scene subclass; preserve the class name when reasonable.
- The output must always be a COMPLETE file, not a diff or partial code.
- Do NOT truncate or omit any part of the file.
- Ensure full structure: imports → class → construct() → end of file.
- No os, subprocess, sys, pathlib, tempfile, or network usage in user-facing code.
"""


SYSTEM_FIX = """You repair Manim Community Edition Python that failed to render.

Output rules (STRICT - MUST FOLLOW):
- Return ONLY the complete corrected Python file.
- No markdown, no code fences, no backticks.
- No explanations anywhere.
- No comments inside the code (# are NOT allowed).
- Fix all errors shown in the log while preserving original intent.
- The output must always be a FULL executable file, never partial.
- Do NOT stop early under any condition.
- Ensure structure is complete: imports → class → construct() → end of file.
"""

def _strip_noise(text: str) -> str:
    text = (text or "").strip()
    text = extract_python_from_markdown(text)
    text = re.sub(r"^```(?:python)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
    return text.strip()

class AIService:
    def __init__(self) -> None:
        s = get_settings()
        self._model_name = s.gemini_model
        self._fallback_models = [m.strip() for m in s.gemini_fallback_models.split(",") if m.strip()]
        genai.configure(api_key=s.gemini_api_key or None)

    def _generate_sync(self, system_instruction: str, user_text: str) -> str:
        model_names = [self._model_name] + [m for m in self._fallback_models if m != self._model_name]
        last_error: Exception | None = None
        for model_name in model_names:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
            )
            generation_config = genai_types.GenerationConfig(
                temperature=0.35,
                max_output_tokens=8192,   # choose this correctly (8192=2^13) which is a boundary
            )
            try:
                resp = model.generate_content(
                    user_text,
                    generation_config=generation_config,
                )  # here we willget the main response from the model
            except Exception as e:
                logger.error("Gemini API call failed for model %s: %s", model_name, e)
                last_error = e
                # CHANGED: Allow the loop to continue to fallback models for ALL exceptions (e.g. auth, quota, etc.)
                continue
            text = ""
            try:
                text = resp.text or ""
            except ValueError:
                if resp.candidates:
                    parts = []
                    for c in resp.candidates:
                        if c.content and c.content.parts:
                            for p in c.content.parts:
                                if hasattr(p, "text") and p.text:
                                    parts.append(p.text)
                    text = "\n".join(parts)
            if not text:
                # CHANGED: Don't raise instantly. Log it and let the loop check the next fallback model.
                logger.warning("Gemini model %s returned an empty response.", model_name)
                continue
            out = _strip_noise(text)
            logger.info("Gemini output chars=%s", len(out))
            return out   # it is the main output
        if last_error is not None:
            raise ValueError(
                "Gemini model not available."
            ) from last_error
        raise ValueError("Gemini returned empty response. Check API key and model name.")

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