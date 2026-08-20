"""Versioned data contracts shared by every rebirth stage."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Provenance:
    source_uri: str
    source_sha256: str
    generated_at: str
    generator_version: str
    trust_tier: str


@dataclass(frozen=True)
class SemanticCard:
    id: str
    kind: str
    markdown_path: str
    provenance: Provenance
    supersedes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RestoreAction:
    action_id: str
    tier: str
    target: str
    operation: str
    reason: str
    requires_human_approval: bool = True


def to_dict(value: object) -> dict[str, object]:
    """Serialize a dataclass contract into a JSON-compatible dictionary."""
    return asdict(value)
