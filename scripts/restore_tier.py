"""Apply an approved restoration plan. Not implemented by the scaffold."""
from __future__ import annotations

from pathlib import Path


def run(approved_plan: Path, tier: str) -> None:
    raise NotImplementedError("Restore is intentionally disabled until approval and target adapters exist")
