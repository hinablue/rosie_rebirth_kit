"""Generate a dry-run restoration plan; never writes to a target runtime."""
from __future__ import annotations

from pathlib import Path


def run(manifest_path: Path, runtime_report_path: Path) -> dict[str, object]:
    if not manifest_path.is_file() or not runtime_report_path.is_file():
        raise FileNotFoundError("Source manifest and runtime report are required")
    return {"schema_version": 1, "status": "placeholder", "actions": [], "requires_human_approval": True}
