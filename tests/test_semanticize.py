from pathlib import Path

from scripts.inventory_sources import run as inventory_run
from scripts.semanticize import run


def test_semanticize_creates_cards_without_mutating_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    original = "# Soul\n\nHuman readable root.\n"
    (source / "SOUL.md").write_text(original, encoding="utf-8")
    manifest = tmp_path / "derived" / "sources.json"
    inventory_run(source, manifest)
    semantic = tmp_path / "semantic"
    cards = tmp_path / "derived" / "cards.json"
    result = run(source, manifest, semantic, cards)
    card = semantic / result["cards"][0]["markdown_path"]
    content = card.read_text(encoding="utf-8")
    assert "source_sha256:" in content
    assert "Human readable root" in content
    assert (source / "SOUL.md").read_text(encoding="utf-8") == original
