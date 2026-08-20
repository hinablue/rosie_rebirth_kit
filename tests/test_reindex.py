import json
from pathlib import Path

from scripts.build_index import HashEmbeddingBackend
from scripts.reindex_archive import run


def test_reindex_is_append_only(tmp_path: Path) -> None:
    semantic = tmp_path / "semantic"; semantic.mkdir()
    (semantic / "one.semantic.md").write_text("---\nid: semantic:one\nsource_sha256: x\ntrust_tier: T2_observed\n---\n\n# One\n\nhello\n", encoding="utf-8")
    result = run(semantic, tmp_path / "indexes", "embedding-v1", backend=HashEmbeddingBackend(8), activate=True)
    assert result["dimension"] == 8
    assert (tmp_path / "indexes" / "active-index.json").is_file()
