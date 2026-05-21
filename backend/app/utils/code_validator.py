"""Static analysis and light sanitization for user/AI-generated Manim code."""
from __future__ import annotations

import ast
import re
from typing import List, Optional, Set, Tuple


_FORBIDDEN_NAMES: Set[str] = {
    "__import__",
    "eval",
    "exec",
    "compile",
    "open",
    "input",
    "breakpoint",
    "globals",
    "locals",
    "vars",
    "getattr",
    "setattr",
    "delattr",
}

_FORBIDDEN_MODULES: Set[str] = {
    "os",
    "sys",
    "subprocess",
    "shutil",
    "socket",
    "requests",
    "urllib",
    "http",
    "pickle",
    "marshal",
    "ctypes",
    "multiprocessing",
    "threading",
    "signal",
    "pty",
    "resource",
    "importlib",
    "pathlib",
    "tempfile",
    "site",
    "code",
    "codeop",
    "pdb",
    "curses",
}


def extract_python_from_markdown(text: str) -> str:
    """If the model wrapped code in fences, strip them."""
    text = text.strip()
    fence = re.search(r"```(?:python)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return text


def find_scene_class_name(code: str) -> Optional[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                name = None
                if isinstance(base, ast.Name):
                    name = base.id
                elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                    name = f"{base.value.id}.{base.attr}"
                if name and (name == "Scene" or name.endswith(".Scene")):
                    return node.name
    return None


def _module_first_part(name: Optional[ast.expr]) -> Optional[str]:
    if isinstance(name, ast.Name):
        return name.id
    if isinstance(name, ast.Attribute) and isinstance(name.value, ast.Name):
        return name.value.id
    return None


def validate_manim_code(code: str) -> Tuple[bool, List[str]]:
    """
    Returns (ok, errors). Checks syntax, blocked imports/calls, and Scene subclass.
    """
    errors: List[str] = []
    code = extract_python_from_markdown(code)
    if not code.strip():
        return False, ["Empty code"]

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"Syntax error: {e}"]

    scene = find_scene_class_name(code)
    if not scene:
        errors.append("No Scene subclass found (define: class YourName(Scene):)")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod in _FORBIDDEN_MODULES:
                    errors.append(f"Forbidden import: {mod}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module.split(".")[0] if node.module else ""
            if mod in _FORBIDDEN_MODULES:
                errors.append(f"Forbidden import from: {mod}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN_NAMES:
                errors.append(f"Forbidden call: {node.func.id}()")

    if errors:
        return False, errors
    return True, []
