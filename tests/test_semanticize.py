from pathlib import Path

from scripts.semanticize import run


def test_semanticize_creates_auditable_card(tmp_path: Path) -> None:
    (tmp_path / "SOUL.md").write_text("# Soul\n", encoding="utf-8")
    result = run(tmp_path, tmp_path / "semantic")
    assert result.is_file()
    assert "SOUL.md" in result.read_text(encoding="utf-8")
