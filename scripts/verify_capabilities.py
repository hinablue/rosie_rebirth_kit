"""Verify capability source provenance and generated card boundaries."""
from __future__ import annotations

from pathlib import Path

from scripts.common.hashes import sha256_file
from scripts.common.io_safe import read_json
from scripts.common.markdown import split_frontmatter

REQUIRED_METADATA = frozenset({"id", "kind", "source_id", "source_sha256", "source_uri", "trust_tier"})
FORBIDDEN_CARD_MARKERS = ("authorization: bearer", "api_key=", "password=", "secret=")


def verify_capabilities(manifest_path: Path, cards_path: Path, cards_dir: Path) -> list[str]:
    failures: list[str] = []
    manifest = read_json(manifest_path)
    by_id = {str(item["id"]): item for item in manifest.get("sources", []) if isinstance(item, dict)}
    cards = read_json(cards_path)
    for source_id, record in by_id.items():
        root = Path(str(record["source_root"])).resolve()
        source = (root / str(record["relative_path"])).resolve()
        if root not in source.parents or not source.is_file():
            failures.append(f"Missing capability source: {source_id}")
        elif sha256_file(source) != record["provenance"]["source_sha256"]:
            failures.append(f"Source hash mismatch: {source_id}")
    for card in cards.get("cards", []):
        if not isinstance(card, dict):
            failures.append("Malformed capability card record")
            continue
        source_id = str(card.get("source_id"))
        if source_id not in by_id:
            failures.append(f"Unknown card source: {source_id}")
            continue
        path = cards_dir / str(card.get("markdown_path"))
        if not path.is_file():
            failures.append(f"Missing capability card: {path}")
            continue
        metadata, text = split_frontmatter(path.read_text(encoding="utf-8"))
        missing = REQUIRED_METADATA - metadata.keys()
        if missing:
            failures.append(f"Missing card metadata {sorted(missing)}: {path}")
        elif metadata["source_sha256"] != by_id[source_id]["provenance"]["source_sha256"]:
            failures.append(f"Card source hash mismatch: {path}")
        lowered = text.lower()
        if any(marker in lowered for marker in FORBIDDEN_CARD_MARKERS):
            failures.append(f"Potential secret marker in generated card: {path}")
    return failures
