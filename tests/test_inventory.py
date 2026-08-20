from pathlib import Path

from scripts.inventory_sources import inventory, run


def test_inventory_is_deterministic_and_does_not_follow_symlinks(tmp_path: Path) -> None:
    (tmp_path / "SOUL.md").write_text("# Soul\n", encoding="utf-8")
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "sample.md").write_text("skill", encoding="utf-8")
    (tmp_path / "ignored.bin").write_bytes(b"binary")
    (tmp_path / "escape.md").symlink_to(Path("/etc/hosts"))
    result = inventory(tmp_path)
    assert [record["relative_path"] for record in result["sources"]] == ["SOUL.md", "skills/sample.md"]
    assert result["sources"][0]["provenance"]["trust_tier"] == "T0_core"
    assert result["sources"][1]["kind"] == "capability"


def test_inventory_writes_only_manifest(tmp_path: Path) -> None:
    (tmp_path / "SOUL.md").write_text("# Soul\n", encoding="utf-8")
    output = tmp_path / "derived" / "manifest.json"
    run(tmp_path, output)
    assert output.is_file()
    assert (tmp_path / "SOUL.md").read_text(encoding="utf-8") == "# Soul\n"
