"""Append-only index rebuild with explicit active-index switch artifact."""
from __future__ import annotations

from pathlib import Path

from scripts.build_index import EmbeddingBackend, run as build_index
from scripts.common.io_safe import read_json, write_json


def run(semantic_dir: Path, indexes_root: Path, version: str, *, backend: EmbeddingBackend | None = None, activate: bool = False) -> dict[str, object]:
    if not version.startswith("embedding-v"):
        raise ValueError("Index version must start with embedding-v")
    target = indexes_root / version
    if (target / "index.json").exists():
        raise FileExistsError(f"Append-only index already exists: {target}")
    index = build_index(semantic_dir, target, backend=backend)
    if activate:
        write_json(indexes_root / "active-index.json", {"schema_version": 1, "active": version, "index_sha256": index["index_sha256"]})
    return index
