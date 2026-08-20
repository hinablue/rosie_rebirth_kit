"""Inventory a caller-selected source directory without mutating its contents."""
from __future__ import annotations

from pathlib import Path

from scripts.common.hashes import sha256_file
from scripts.common.io_safe import require_within, write_json
from scripts.common.provenance import utc_now, validate_trust_tier

IGNORED_PARTS = frozenset({".git", ".venv", "__pycache__", ".pytest_cache", "indexes", "runtime"})
TEXT_SUFFIXES = frozenset({".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py"})


def classify(path: Path) -> str:
    if path.name == "SOUL.md":
        return "identity"
    if path.suffix.lower() == ".py":
        return "tooling"
    if any(part.lower() in {"skill", "skills"} for part in path.parts):
        return "capability"
    return "memory"


def default_tier(path: Path) -> str:
    if path.name == "SOUL.md":
        return "T0_core"
    if classify(path) == "capability":
        return "T1_curated"
    return "T2_observed"


def inventory(source_root: Path, *, trust_overrides: dict[str, str] | None = None) -> dict[str, object]:
    """Return deterministic source metadata. Symlinks and non-text files are excluded."""
    root = source_root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    overrides = trust_overrides or {}
    records: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        tier = overrides.get(relative, default_tier(path))
        validate_trust_tier(tier)
        stat = path.stat()
        records.append({
            "id": f"source:{relative}",
            "relative_path": relative,
            "kind": classify(path),
            "private": tier in {"T0_core", "T1_curated"},
            "provenance": {
                "source_uri": f"file://{relative}",
                "source_sha256": sha256_file(path),
                "source_mtime_ns": stat.st_mtime_ns,
                "generated_at": utc_now(),
                "generator_version": "inventory_sources/1",
                "trust_tier": tier,
            },
        })
    return {"schema_version": 1, "source_root_label": root.name, "sources": records}


def run(source_root: Path, output: Path, *, trust_overrides: dict[str, str] | None = None) -> dict[str, object]:
    require_within(output.parent, output)
    manifest = inventory(source_root, trust_overrides=trust_overrides)
    write_json(output, manifest)
    return manifest
