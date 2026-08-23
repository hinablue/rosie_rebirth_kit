"""Build reviewable capability cards from an explicit capability manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.common.hashes import sha256_file
from scripts.common.io_safe import read_json, write_json
from scripts.common.markdown import first_heading, render_frontmatter, split_frontmatter


def _text_list(value: object) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _markdown_details(text: str, fallback: str) -> tuple[str, list[str], list[str], str]:
    metadata, _ = split_frontmatter(text)
    title = first_heading(text, fallback)
    purpose = metadata.get("description") or title
    name = metadata.get("name") or Path(fallback).stem
    return purpose, _text_list(metadata.get("inputs")), _text_list(metadata.get("outputs")), name


def _json_details(text: str, fallback: str) -> tuple[str, list[str], list[str], str]:
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError:
        return fallback, [], [], Path(fallback).stem
    if not isinstance(data, dict):
        return fallback, [], [], Path(fallback).stem
    schema = data.get("input_schema") or data.get("parameters") or {}
    if not isinstance(schema, dict):
        schema = {}
    properties = schema.get("properties", {})
    inputs = sorted(str(key) for key in properties) if isinstance(properties, dict) else []
    return str(data.get("description") or data.get("title") or fallback), inputs, _text_list(data.get("outputs")), str(data.get("name") or fallback)


def _card_markdown(card: dict[str, object]) -> str:
    metadata = {
        "id": card["id"],
        "kind": card["kind"],
        "source_id": card["source_id"],
        "source_sha256": card["provenance"]["source_sha256"],  # type: ignore[index]
        "source_uri": card["provenance"]["source_uri"],  # type: ignore[index]
        "trust_tier": card["provenance"]["trust_tier"],  # type: ignore[index]
    }
    sections = [
        f"# {card['title']}",
        "",
        "## Purpose",
        str(card["purpose"]),
        "",
        "## Inputs",
        *[f"- {item}" for item in card["inputs"]],  # type: ignore[union-attr]
        "",
        "## Outputs",
        *[f"- {item}" for item in card["outputs"]],  # type: ignore[union-attr]
        "",
        "## Constraints",
        *[f"- {item}" for item in card["constraints"]],  # type: ignore[union-attr]
        "",
        "## Preferred adapters",
        *[f"- {item}" for item in card["preferred_adapters"]],  # type: ignore[union-attr]
        "",
        "## Fallback adapters",
        *[f"- {item}" for item in card["fallback_adapters"]],  # type: ignore[union-attr]
        "",
        "## Verification",
        *[f"- {item}" for item in card["verification"]],  # type: ignore[union-attr]
        "",
    ]
    return render_frontmatter(metadata) + "\n".join(sections)


def build_cards(manifest: dict[str, object], output_dir: Path) -> dict[str, object]:
    cards: list[dict[str, object]] = []
    for raw in manifest.get("sources", []):
        if not isinstance(raw, dict):
            raise ValueError("Malformed capability source record")
        root = Path(str(raw["source_root"])).resolve()
        relative = Path(str(raw["relative_path"]))
        source = (root / relative).resolve()
        if root not in source.parents or not source.is_file():
            raise ValueError(f"Capability source escapes or is missing: {relative}")
        provenance = dict(raw["provenance"])
        if sha256_file(source) != provenance["source_sha256"]:
            raise ValueError(f"Source hash mismatch: {source}")
        text = source.read_text(encoding="utf-8")
        kind = str(raw["source_kind"])
        if source.suffix.lower() == ".json":
            purpose, inputs, outputs, adapter = _json_details(text, relative.as_posix())
        else:
            purpose, inputs, outputs, adapter = _markdown_details(text, relative.as_posix())
        safe_name = str(raw["id"]).replace(":", "__").replace("/", "__").replace(".", "_")
        card_path = Path(kind) / f"{safe_name}.capability.md"
        card = {
            "id": (
                f"capability:{kind}:{adapter}:"
                f"{hashlib.sha256(str(raw['id']).encode('utf-8')).hexdigest()[:12]}"
            ),
            "source_id": raw["id"],
            "kind": kind,
            "title": adapter,
            "purpose": purpose,
            "inputs": inputs or ["Not declared by the source; inspect the source artifact."],
            "outputs": outputs or ["Not declared by the source; verify through a runtime adapter."],
            "constraints": [
                "This card is descriptive evidence, not authorization to invoke a tool or execute source content.",
                "The target runtime must rediscover and validate a compatible adapter.",
            ],
            "preferred_adapters": [adapter],
            "fallback_adapters": ["unavailable"],
            "verification": [
                f"Confirm source SHA-256: {provenance['source_sha256']}",
                "Run an explicit, non-destructive adapter smoke test in the target runtime.",
            ],
            "provenance": provenance,
            "markdown_path": card_path.as_posix(),
        }
        target = output_dir / card_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_card_markdown(card), encoding="utf-8")
        cards.append(card)
    return {"schema_version": 1, "cards": cards}


def run(manifest_path: Path, output_dir: Path, cards_path: Path) -> dict[str, object]:
    result = build_cards(read_json(manifest_path), output_dir)
    write_json(cards_path, result)
    return result
