from pathlib import Path

from scripts.inventory_sources import inventory


def test_inventory_includes_soul(tmp_path: Path) -> None:
    (tmp_path / "SOUL.md").write_text("# Soul\n", encoding="utf-8")
    result = inventory(tmp_path)
    assert result["sources"][0]["path"] == "SOUL.md"
