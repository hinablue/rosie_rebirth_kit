"""Versioned embedding index with deterministic local and OpenAI-compatible backends."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import urllib.request
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

from scripts.common.hashes import sha256_file, sha256_json
from scripts.common.io_safe import write_json
from scripts.common.markdown import read_markdown, split_frontmatter

TOKEN_RE = re.compile(r"[\w-]+", re.UNICODE)


class EmbeddingBackend(Protocol):
    name: str
    dimension: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbeddingBackend:
    """Dependency-free baseline for test/dev only; not a semantic model."""

    name = "hash-v1"

    def __init__(self, dimension: int = 128) -> None:
        if dimension < 8:
            raise ValueError("Embedding dimension must be >= 8")
        self.dimension = dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimension
            for token in TOKEN_RE.findall(text.lower()):
                bucket = int.from_bytes(hashlib.sha256(token.encode("utf-8")).digest()[:8], "big") % self.dimension
                vector[bucket] += 1.0
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors


class OpenAICompatibleBackend:
    """Minimal client for an already-running OpenAI-compatible embedding API.

    The endpoint may be either the embeddings route itself or an API root such
    as ``http://localhost:8001/v1``.  This backend never starts or manages a
    model server.  Authentication is optional because local servers may not
    require it; when supplied, the key is only read at invocation time.
    """

    name = "openai-compatible"

    def __init__(self, endpoint: str, model: str, api_key: str | None = None, dimension: int | None = None) -> None:
        self.endpoint = normalize_embeddings_endpoint(endpoint)
        self.model, self.api_key, self.dimension = model, api_key, dimension or 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        payload = json.dumps({"model": self.model, "input": texts}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(self.endpoint, data=payload, method="POST", headers=headers)
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 - caller controls configured endpoint
            result = json.loads(response.read().decode("utf-8"))
        vectors = [list(item["embedding"]) for item in sorted(result["data"], key=lambda item: item["index"])]
        if len(vectors) != len(texts):
            raise ValueError("Embedding provider returned an unexpected vector count")
        self.dimension = len(vectors[0]) if vectors else self.dimension
        return vectors


def normalize_embeddings_endpoint(endpoint: str) -> str:
    """Accept an OpenAI-compatible API root or its explicit embeddings route."""
    parsed = urlsplit(endpoint.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Embedding endpoint must be an absolute http(s) URL")
    path = parsed.path.rstrip("/")
    if not path.endswith("/embeddings"):
        path = f"{path}/embeddings" if path else "/embeddings"
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def backend_from_environment() -> EmbeddingBackend:
    kind = os.getenv("REBIRTH_EMBEDDING_KIND", "hash").lower()
    endpoint, model, key = (os.getenv("REBIRTH_EMBEDDING_ENDPOINT"), os.getenv("REBIRTH_EMBEDDING_MODEL"), os.getenv("REBIRTH_EMBEDDING_API_KEY"))
    if kind == "hash":
        if endpoint or model or key:
            raise ValueError("Set REBIRTH_EMBEDDING_KIND=openai-compatible when configuring an embedding endpoint")
        return HashEmbeddingBackend()
    if kind not in {"openai-compatible", "llama.cpp"}:
        raise ValueError(f"Unsupported embedding backend: {kind}")
    if not all((endpoint, model)):
        raise ValueError("OpenAI-compatible embedding requires ENDPOINT and MODEL")
    return OpenAICompatibleBackend(endpoint, model, key)


def chunk_text(text: str, *, max_chars: int = 1200, overlap: int = 160) -> list[str]:
    if max_chars <= overlap or overlap < 0:
        raise ValueError("max_chars must exceed non-negative overlap")
    normalized = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not normalized:
        return []
    return [normalized[start : start + max_chars] for start in range(0, len(normalized), max_chars - overlap)]


def build_index(semantic_dir: Path, backend: EmbeddingBackend) -> dict[str, object]:
    chunks: list[dict[str, object]] = []
    texts: list[str] = []
    for card_path in sorted(semantic_dir.rglob("*.semantic.md")):
        markdown = read_markdown(card_path)
        metadata, body = split_frontmatter(markdown)
        for number, text in enumerate(chunk_text(body)):
            chunks.append({"id": f"{metadata.get('id', card_path.stem)}#{number}", "card_path": card_path.relative_to(semantic_dir).as_posix(), "source_sha256": metadata.get("source_sha256"), "trust_tier": metadata.get("trust_tier", "T3_untrusted"), "text": text})
            texts.append(text)
    vectors = backend.embed(texts) if texts else []
    for chunk, vector in zip(chunks, vectors, strict=True):
        chunk["vector"] = vector
    payload: dict[str, object] = {"schema_version": 1, "backend": backend.name, "dimension": backend.dimension, "chunks": chunks}
    payload["index_sha256"] = sha256_json(payload)
    return payload


def run(semantic_dir: Path, index_dir: Path, *, backend: EmbeddingBackend | None = None, dry_run: bool = False) -> dict[str, object]:
    result = build_index(semantic_dir, backend or backend_from_environment())
    if not dry_run:
        write_json(index_dir / "index.json", result)
    return result
