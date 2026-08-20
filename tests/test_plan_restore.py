from pathlib import Path

from scripts.inspect_runtime import inspect_runtime
from scripts.plan_restore import plan_restore


def test_runtime_report_and_restore_plan_are_read_only() -> None:
    runtime = inspect_runtime()
    manifest = {"sources": [{"id": "source:SOUL.md", "relative_path": "SOUL.md", "provenance": {"trust_tier": "T0_core"}}, {"id": "source:note.md", "relative_path": "note.md", "provenance": {"trust_tier": "T2_observed"}}]}
    plan = plan_restore(manifest, runtime)
    assert plan["requires_human_approval"] is True
    assert [item["operation"] for item in plan["actions"]] == ["review", "index_only"]
