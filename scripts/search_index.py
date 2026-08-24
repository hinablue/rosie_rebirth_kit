"""Read-only, trust-aware vector retrieval over Rebirth index artifacts."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np


ALLOWED_TIERS = frozenset({"T0_core", "T1_curated", "T2_observed"})


class QueryEmbedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


@dataclass(frozen=True)
class VectorIndex:
    lane: str
    index_path: Path
    paths: list[str]
    source_hashes: list[str | None]
    trust_tiers: list[str]
    texts: list[str]
    vectors: np.ndarray

    @classmethod
    def load(cls, index_path: Path, *, lane: str) -> "VectorIndex":
        with index_path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if payload.get("schema_version") != 1:
            raise ValueError(f"Unsupported index schema: {index_path}")
        chunks = payload.get("chunks")
        dimension = payload.get("dimension")
        if not isinstance(chunks, list) or not isinstance(dimension, int) or dimension < 1:
            raise ValueError(f"Invalid index payload: {index_path}")
        vectors = np.asarray([chunk["vector"] for chunk in chunks], dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape != (len(chunks), dimension):
            raise ValueError(f"Vector dimensions do not match index metadata: {index_path}")
        return cls(
            lane=lane,
            index_path=index_path,
            paths=[str(chunk.get("card_path", "")) for chunk in chunks],
            source_hashes=[str(chunk["source_sha256"]) if chunk.get("source_sha256") is not None else None for chunk in chunks],
            trust_tiers=[str(chunk.get("trust_tier", "T3_untrusted")) for chunk in chunks],
            texts=[str(chunk.get("text", "")) for chunk in chunks],
            vectors=vectors,
        )


def discover_indexes(archive_root: Path) -> list[tuple[Path, str]]:
    found = [(path, path.parent.parent.name) for path in sorted(archive_root.glob("*/indexes/index.json"))]
    if not found:
        raise ValueError("No lane index.json files found under archive root")
    return found


def _excerpt(text: str, *, limit: int = 420) -> str:
    compact = " ".join(text.split())
    return compact[:limit] + ("…" if len(compact) > limit else "")


def search_vector_indexes(indexes: list[VectorIndex], query: str, embedder: QueryEmbedder, *, top_k: int = 8, allowed_tiers: frozenset[str] = ALLOWED_TIERS) -> list[dict[str, object]]:
    if not query.strip():
        raise ValueError("query is empty")
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    query_vector = np.asarray(embedder.embed([query])[0], dtype=np.float32)
    results: list[dict[str, object]] = []
    for index in indexes:
        if index.vectors.shape[1] != query_vector.shape[0]:
            raise ValueError(f"Query dimension does not match {index.index_path}")
        scores = index.vectors @ query_vector
        for position in np.argpartition(scores, -min(top_k, len(scores)))[-min(top_k, len(scores)):]:
            tier = index.trust_tiers[int(position)]
            if tier not in allowed_tiers:
                continue
            results.append({
                "score": round(float(scores[int(position)]), 6),
                "path": f"{index.lane}/semantic/{index.paths[int(position)]}",
                "source_sha256": index.source_hashes[int(position)],
                "trust_tier": tier,
                "snippet": _excerpt(index.texts[int(position)]),
            })
    return sorted(results, key=lambda item: (-float(item["score"]), str(item["path"])))[:top_k]
