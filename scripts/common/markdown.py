"""Minimal dependency-free Markdown/frontmatter helpers."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_FRONTMATTER = re.compile(r"\A---\n(?P<data>.*?)\n---\n", re.DOTALL)


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(markdown: str) -> tuple[dict[str, str], str]:
    match = _FRONTMATTER.match(markdown)
    if not match:
        return {}, markdown
    metadata: dict[str, str] = {}
    for line in match.group("data").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    return metadata, markdown[match.end() :]


def render_frontmatter(metadata: dict[str, Any]) -> str:
    lines = ["---"]
    for key in sorted(metadata):
        value = metadata[key]
        if isinstance(value, (list, tuple)):
            rendered = "[" + ", ".join(str(item) for item in value) + "]"
        else:
            rendered = str(value).replace("\n", " ")
        lines.append(f"{key}: {rendered}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def render_semantic_card(title: str, metadata: dict[str, Any], body: str) -> str:
    return render_frontmatter(metadata) + f"# {title}\n\n{body.rstrip()}\n"


def first_heading(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback
