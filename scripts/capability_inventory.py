"""Inventory caller-selected Skill and Tool sources without executing them."""
from __future__ import annotations

from pathlib import Path

from scripts.common.hashes import sha256_file
from scripts.common.io_safe import write_json
from scripts.common.provenance import utc_now, validate_trust_tier

TEXT_SUFFIXES = frozenset({".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"})
IGNORED_PARTS = frozenset({".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"})
SECRET_NAMES = frozenset({".env", "credentials", "credential", "secrets", "secret", "tokens", "token"})


def _safe_files(root: Path) -> list[Path]:
    resolved = root.resolve()
    if not resolved.is_dir():
        raise NotADirectoryError(resolved)
    files: list[Path] = []
    for path in sorted(resolved.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        lowered = {part.lower() for part in path.parts}
        if lowered & IGNORED_PARTS or lowered & SECRET_NAMES:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        files.append(path)
    return files


def inventory_capabilities(
    skill_roots: list[Path], tool_roots: list[Path], *, trust_tier: str = "T2_observed"
) -> dict[str, object]:
    """Return a deterministic, provenance-preserving manifest for selected roots.

    This stage only reads metadata and hashes. It neither executes source code nor
    copies source contents, invokes adapters, or discovers arbitrary host paths.
    Selecting `T1_curated` is an explicit caller assertion that the roots have
    already received human review; the default is `T2_observed`.
    """
    if not skill_roots and not tool_roots:
        raise ValueError("At least one Skill or Tool source root is required")
    validate_trust_tier(trust_tier)
    if trust_tier in {"T0_core", "T3_untrusted"}:
        raise ValueError("Capability sources must use T1_curated or T2_observed")
    records: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    for source_kind, roots in (("skill", skill_roots), ("tool", tool_roots)):
        for root in roots:
            resolved = root.resolve()
            for path in _safe_files(resolved):
                relative = path.relative_to(resolved).as_posix()
                key = (source_kind, resolved.as_posix(), relative)
                if key in seen:
                    continue
                seen.add(key)
                stat = path.stat()
                root_label = resolved.name
                records.append(
                    {
                        "id": f"capability-source:{source_kind}:{root_label}:{relative}",
                        "source_kind": source_kind,
                        "relative_path": relative,
                        "source_root": resolved.as_posix(),
                        "private": trust_tier == "T1_curated",
                        "provenance": {
                            "source_uri": f"file://{source_kind}/{root_label}/{relative}",
                            "source_sha256": sha256_file(path),
                            "source_mtime_ns": stat.st_mtime_ns,
                            "generated_at": utc_now(),
                            "generator_version": "capability_inventory/1",
                            "trust_tier": trust_tier,
                        },
                    }
                )
    records.sort(key=lambda record: str(record["id"]))
    return {"schema_version": 1, "sources": records}


def run(
    skill_roots: list[Path], tool_roots: list[Path], output: Path, *, trust_tier: str = "T2_observed"
) -> dict[str, object]:
    result = inventory_capabilities(skill_roots, tool_roots, trust_tier=trust_tier)
    write_json(output, result)
    return result
