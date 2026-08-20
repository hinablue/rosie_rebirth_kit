"""Generate auditable semantic cards from an inventory manifest."""
from __future__ import annotations

from pathlib import Path

from scripts.common.io_safe import read_json, require_within, write_json
from scripts.common.markdown import first_heading, read_markdown, render_semantic_card
from scripts.common.provenance import provenance_from_dict


def _card_path(kind: str, source_id: str) -> Path:
    safe = source_id.removeprefix("source:").replace("/", "__").replace(".", "_")
    return Path(kind) / f"{safe}.semantic.md"


def semanticize(source_root: Path, manifest: dict[str, object], output_dir: Path) -> dict[str, object]:
    root = source_root.resolve()
    cards: list[dict[str, object]] = []
    for raw in manifest.get("sources", []):
        if not isinstance(raw, dict):
            raise ValueError("Malformed source record")
        relative = str(raw["relative_path"])
        source = require_within(root, root / relative)
        if not source.is_file():
            raise FileNotFoundError(source)
        provenance = provenance_from_dict(dict(raw["provenance"]))
        markdown = read_markdown(source)
        kind = str(raw["kind"])
        card_id = f"semantic:{relative}"
        target = output_dir / _card_path(kind, str(raw["id"]))
        metadata = {
            "id": card_id,
            "kind": kind,
            "source_uri": provenance.source_uri,
            "source_sha256": provenance.source_sha256,
            "trust_tier": provenance.trust_tier,
            "private": bool(raw.get("private", False)),
        }
        body = "## Source Material\n\n" + markdown
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_semantic_card(first_heading(markdown, relative), metadata, body), encoding="utf-8")
        cards.append({"id": card_id, "kind": kind, "markdown_path": target.relative_to(output_dir).as_posix(), "provenance": metadata})
    return {"schema_version": 1, "cards": cards}


def run(source_root: Path, manifest_path: Path, output_dir: Path, card_manifest_path: Path) -> dict[str, object]:
    manifest = read_json(manifest_path)
    result = semanticize(source_root, manifest, output_dir)
    write_json(card_manifest_path, result)
    return result
