#!/usr/bin/env python3
import os
from pathlib import Path
import pyperclip
import sys

EXCLUDE_DIRS = {"tests", ".venv", ".github", ".git", ".pytest_cache", "migrations"}
EXCLUDE_FILES = {"___content.py"}


def collect_js_contents(root: Path) -> str:
    parts = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel_dir.parts):
            dirnames.clear()
            continue
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in sorted(filenames):
            if fname in EXCLUDE_FILES:
                continue
            if fname.lower().endswith((".js", ".py", ".css", ".html")):
                fpath = Path(dirpath) / fname
                rel = fpath.relative_to(root)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except Exception:
                    content = ""
                trimmed = content.lstrip("\ufeff").strip()
                if not trimmed:
                    content = "# Это пустой файл\n"
                parts.append(f"{rel}\n{content}\n")
    return "\n".join(parts)


if __name__ == "__main__":
    root = Path(".").resolve()
    result = collect_js_contents(root)
    try:
        pyperclip.copy(result)
        sys.stdout.write("Скопировано в буфер обмена\n")
    except Exception:
        sys.stdout.write("Не удалось скопировать в буфер обмена\n")
