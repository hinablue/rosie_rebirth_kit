"""Convert raw sources into auditable semantic Markdown cards."""
from __future__ import annotations

from pathlib import Path

from scripts.common.io_safe import atomic_write
from scripts.common.markdown import read_markdown, render_semantic_card


def run(project_root: Path, output_dir: Path) -> Path:
    """Placeholder semanticization for the human-readable trust root only."""
    source = project_root / "SOUL.md"
    body = "## Source\n\n`SOUL.md`\n\n## Content\n\n" + read_markdown(source)
    target = output_dir / "identity" / "soul.semantic.md"
    atomic_write(target, render_semantic_card("Semantic Card: SOUL", body))
    return target
