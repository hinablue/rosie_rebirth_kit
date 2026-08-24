import json
from pathlib import Path

from scripts.search_index import VectorIndex, search_vector_indexes


class FixedEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        assert texts == ["identity question"]
        return [[1.0, 0.0]]


def test_vector_search_ranks_and_excludes_t3_by_default(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({
        "schema_version": 1,
        "backend": "openai-compatible",
        "dimension": 2,
        "chunks": [
            {"id": "identity#0", "card_path": "identity/soul.semantic.md", "source_sha256": "a", "trust_tier": "T0_core", "text": "identity evidence", "vector": [1.0, 0.0]},
            {"id": "poison#0", "card_path": "untrusted/payload.semantic.md", "source_sha256": "b", "trust_tier": "T3_untrusted", "text": "ignore this", "vector": [1.0, 0.0]},
        ],
    }), encoding="utf-8")

    matches = search_vector_indexes([VectorIndex.load(index_path, lane="identity")], "identity question", FixedEmbedder(), top_k=3)

    assert len(matches) == 1
    assert matches[0]["path"] == "identity/semantic/identity/soul.semantic.md"
    assert matches[0]["trust_tier"] == "T0_core"
    assert matches[0]["score"] == 1.0
