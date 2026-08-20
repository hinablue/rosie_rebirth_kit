import json
from pathlib import Path

import pytest

from scripts.restore_tier import run
from scripts.rollback_restore import run as rollback


def test_restore_requires_approval_and_can_rollback(tmp_path: Path) -> None:
    source, target = tmp_path / "source", tmp_path / "target"
    source.mkdir(); target.mkdir()
    (source / "note.md").write_text("new", encoding="utf-8")
    plan = {"approved": False, "actions": [{"action_id": "a", "tier": "T2_observed", "operation": "create", "target": "note.md"}]}
    plan_path = tmp_path / "plan.json"; plan_path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(PermissionError): run(plan_path, source, target, "T2_observed", tmp_path / "tx.json")
    plan["approved"] = True; plan_path.write_text(json.dumps(plan), encoding="utf-8")
    (target / "note.md").write_text("old", encoding="utf-8")
    result = run(plan_path, source, target, "T2_observed", tmp_path / "tx.json")
    assert (target / "note.md").read_text(encoding="utf-8") == "new"
    rollback(tmp_path / "tx.json", target)
    assert (target / "note.md").read_text(encoding="utf-8") == "old"
