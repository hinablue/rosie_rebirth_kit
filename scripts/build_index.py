"""Build a versioned embedding index from semantic Markdown; provider integration pending."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.common.io_safe import atomic_write


def run(semantic_dir: Path, index_dir: Path, *, dry_run: bool = False) -> dict[str, object]:
    cards = sorted(str(path.relative_to(semantic_dir)) for path in semantic_dir.rglob("*.md"))
    plan = {"schema_version": 1, "status": "placeholder", "embedding_provider": None, "cards": cards}
    if not dry_run:
        atomic_write(index_dir / "index-plan.json", json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    return plan
