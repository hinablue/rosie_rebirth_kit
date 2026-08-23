from pathlib import Path

import pytest

from scripts.build_capability_cards import build_cards
from scripts.capability_inventory import inventory_capabilities
from scripts.common.io_safe import write_json
from scripts.verify_capabilities import verify_capabilities


def test_capability_pipeline_builds_reviewable_skill_and_tool_cards(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    tools = tmp_path / "tools"
    skills.mkdir()
    tools.mkdir()
    (skills / "SKILL.md").write_text(
        "---\nname: sample-skill\ndescription: Safely do the sample task\n---\n\n# Sample Skill\n",
        encoding="utf-8",
    )
    (tools / "sample.json").write_text(
        '{"name":"sample.tool","description":"Inspect a fixture","parameters":{"properties":{"query":{"type":"string"}}}}',
        encoding="utf-8",
    )
    manifest = inventory_capabilities([skills], [tools])
    assert [item["source_kind"] for item in manifest["sources"]] == ["skill", "tool"]
    cards_dir = tmp_path / "cards"
    cards = build_cards(manifest, cards_dir)
    assert len(cards["cards"]) == 2
    tool_card = next(card for card in cards["cards"] if card["kind"] == "tool")
    assert tool_card["inputs"] == ["query"]
    manifest_path = tmp_path / "derived" / "sources.json"
    cards_path = tmp_path / "derived" / "capability-cards.json"
    write_json(manifest_path, manifest)
    write_json(cards_path, cards)
    assert verify_capabilities(manifest_path, cards_path, cards_dir) == []


def test_capability_cards_reject_source_drift(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    skills.mkdir()
    source = skills / "SKILL.md"
    source.write_text("# Original\n", encoding="utf-8")
    manifest = inventory_capabilities([skills], [])
    source.write_text("# Changed\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Source hash mismatch"):
        build_cards(manifest, tmp_path / "cards")


def test_capability_inventory_excludes_secret_named_paths(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    skills.mkdir()
    (skills / "SKILL.md").write_text("# Included\n", encoding="utf-8")
    (skills / "secrets").mkdir()
    (skills / "secrets" / "token.md").write_text("not included", encoding="utf-8")
    manifest = inventory_capabilities([skills], [])
    assert [item["relative_path"] for item in manifest["sources"]] == ["SKILL.md"]
