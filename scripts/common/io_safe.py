"""Filesystem writes with explicit workspace boundaries."""
from __future__ import annotations

from pathlib import Path


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def require_within(root: Path, candidate: Path) -> Path:
    resolved_root = root.resolve()
    resolved_candidate = candidate.resolve()
    if resolved_root not in (resolved_candidate, *resolved_candidate.parents):
        raise ValueError(f"Path escapes workspace: {candidate}")
    return resolved_candidate
