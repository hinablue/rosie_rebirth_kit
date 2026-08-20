"""Inventory source artifacts and write a reproducible manifest."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.common.hashes import sha256_file
from scripts.common.io_safe import atomic_write


def inventory(project_root: Path) -> dict[str, object]:
    """Return a source manifest. Placeholder: only inventories SOUL.md."""
    soul = project_root / "SOUL.md"
    if not soul.is_file():
        raise FileNotFoundError(f"Missing trust root: {soul}")
    return {"schema_version": 1, "sources": [{"path": "SOUL.md", "sha256": sha256_file(soul), "trust_tier": "T0_core"}]}


def run(project_root: Path, output: Path) -> dict[str, object]:
    manifest = inventory(project_root)
    atomic_write(output, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest
