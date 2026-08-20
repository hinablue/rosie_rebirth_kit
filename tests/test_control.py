import json
from pathlib import Path

from scripts.diff_archives import run as diff
from scripts.export_portable_kit import run as export


def test_diff_and_private_export_filter(tmp_path: Path) -> None:
    left, right = tmp_path / "a.json", tmp_path / "b.json"
    left.write_text(json.dumps({"x": 1}), encoding="utf-8"); right.write_text(json.dumps({"x": 2}), encoding="utf-8")
    assert diff(left, right)["changed_keys"] == ["x"]
    source = tmp_path / "source"; source.mkdir(); (source / "public.md").write_text("ok", encoding="utf-8"); (source / "private.md").write_text("no", encoding="utf-8")
    manifest = tmp_path / "manifest.json"; manifest.write_text(json.dumps({"sources": [{"relative_path": "public.md", "private": False}, {"relative_path": "private.md", "private": True}]}), encoding="utf-8")
    result = export(source, manifest, tmp_path / "bundle.zip")
    assert result["included"] == ["sources/public.md"]
