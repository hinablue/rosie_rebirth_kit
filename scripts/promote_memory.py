"""Promote a semantic card only with a review-approved promotion record."""
from __future__ import annotations

from pathlib import Path

from scripts.common.io_safe import read_json, write_json
from scripts.common.markdown import render_semantic_card, split_frontmatter
from scripts.common.provenance import can_promote, utc_now


def run(card_path: Path, review_path: Path) -> dict[str, object]:
    review = read_json(review_path)
    if not review.get("approved", False):
        raise PermissionError("Promotion review is not approved")
    metadata, body = split_frontmatter(card_path.read_text(encoding="utf-8"))
    source, target = str(metadata.get("trust_tier")), str(review["target_tier"])
    if not can_promote(source, target):
        raise ValueError(f"Cannot promote {source} to {target}")
    metadata["trust_tier"], metadata["promoted_at"], metadata["review_id"] = target, utc_now(), str(review["review_id"])
    card_path.write_text(render_semantic_card(str(metadata.get("id", card_path.stem)), metadata, body), encoding="utf-8")
    return {"card": str(card_path), "from": source, "to": target, "review_id": review["review_id"]}
