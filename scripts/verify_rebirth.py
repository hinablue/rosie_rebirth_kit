"""Archive verification: provenance, semantic card references, and index structure."""
from __future__ import annotations

from pathlib import Path

from scripts.common.hashes import sha256_file
from scripts.common.io_safe import read_json


def verify_archive(source_root: Path, manifest_path: Path, cards_path: Path, index_path: Path | None = None) -> list[str]:
    failures: list[str] = []
    manifest = read_json(manifest_path)
    for raw in manifest.get("sources", []):
        source = source_root / str(raw["relative_path"])
        if not source.is_file():
            failures.append(f"Missing source: {source}")
        elif sha256_file(source) != raw["provenance"]["source_sha256"]:
            failures.append(f"Source hash mismatch: {source}")
    cards = read_json(cards_path)
    for card in cards.get("cards", []):
        card_path = cards_path.parent.parent / "semantic" / str(card["markdown_path"])
        if not card_path.is_file():
            failures.append(f"Missing semantic card: {card_path}")
    if index_path is not None:
        index = read_json(index_path)
        if index.get("dimension", 0) < 1:
            failures.append("Invalid index dimension")
        for chunk in index.get("chunks", []):
            if len(chunk.get("vector", [])) != index["dimension"]:
                failures.append(f"Invalid vector dimension: {chunk.get('id')}")
    return failures
