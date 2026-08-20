from pathlib import Path

from scripts.build_index import HashEmbeddingBackend, build_index, chunk_text


def test_chunking_and_index_are_deterministic(tmp_path: Path) -> None:
    card = tmp_path / "memory" / "one.semantic.md"
    card.parent.mkdir()
    card.write_text("---\nid: semantic:one\nsource_sha256: abc\ntrust_tier: T2_observed\n---\n\n# One\n\nalpha beta alpha\n", encoding="utf-8")
    assert chunk_text("abcdef", max_chars=4, overlap=1) == ["abcd", "def"]
    first = build_index(tmp_path, HashEmbeddingBackend(16))
    second = build_index(tmp_path, HashEmbeddingBackend(16))
    assert first["index_sha256"] == second["index_sha256"]
    assert first["dimension"] == 16
    assert len(first["chunks"]) == 1
