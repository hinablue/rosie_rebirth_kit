"""Verify archive integrity and report failures through explicit exit codes."""
from __future__ import annotations

from pathlib import Path


def verify_archive(project_root: Path) -> list[str]:
    failures: list[str] = []
    for required in ("SOUL.md", "sources/manifest.json", "semantic/identity/soul.semantic.md"):
        if not (project_root / required).is_file():
            failures.append(f"Missing required artifact: {required}")
    return failures
