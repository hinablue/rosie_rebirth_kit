"""Stable Markdown and frontmatter rendering placeholders."""
from __future__ import annotations

from pathlib import Path


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_semantic_card(title: str, body: str) -> str:
    return f"# {title}\n\n{body.rstrip()}\n"
