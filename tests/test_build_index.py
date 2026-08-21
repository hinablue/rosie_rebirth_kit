from pathlib import Path

import json

import pytest

from scripts.build_index import HashEmbeddingBackend, OpenAICompatibleBackend, backend_from_environment, build_index, chunk_text, normalize_embeddings_endpoint


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


@pytest.mark.parametrize(
    ("configured", "expected"),
    [
        ("http://localhost:8001/v1", "http://localhost:8001/v1/embeddings"),
        ("http://localhost:8001/v1/", "http://localhost:8001/v1/embeddings"),
        ("http://localhost:8001/v1/embeddings", "http://localhost:8001/v1/embeddings"),
    ],
)
def test_normalize_embeddings_endpoint_accepts_api_root(configured: str, expected: str) -> None:
    assert normalize_embeddings_endpoint(configured) == expected


def test_network_backend_does_not_require_or_send_auth_when_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps({"data": [{"index": 0, "embedding": [0.5, 0.25]}]}).encode()

    def fake_urlopen(request: object, timeout: int) -> Response:
        captured["url"] = request.full_url  # type: ignore[attr-defined]
        captured["authorization"] = request.get_header("Authorization")  # type: ignore[attr-defined]
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr("scripts.build_index.urllib.request.urlopen", fake_urlopen)
    backend = OpenAICompatibleBackend("http://localhost:8001/v1", "bge-m3-Q8_0.gguf")
    assert backend.embed(["fixture text"]) == [[0.5, 0.25]]
    assert captured == {"url": "http://localhost:8001/v1/embeddings", "authorization": None, "timeout": 60}


def test_environment_selects_network_backend_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REBIRTH_EMBEDDING_KIND", "openai-compatible")
    monkeypatch.setenv("REBIRTH_EMBEDDING_ENDPOINT", "http://localhost:8001/v1")
    monkeypatch.setenv("REBIRTH_EMBEDDING_MODEL", "bge-m3-Q8_0.gguf")
    monkeypatch.delenv("REBIRTH_EMBEDDING_API_KEY", raising=False)
    backend = backend_from_environment()
    assert isinstance(backend, OpenAICompatibleBackend)
    assert backend.endpoint == "http://localhost:8001/v1/embeddings"
    assert backend.api_key is None
