"""Versioned, JSON-serializable data contracts for the rebirth toolchain."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

SCHEMA_VERSION = 1
TRUST_TIERS = ("T0_core", "T1_curated", "T2_observed", "T3_untrusted")


@dataclass(frozen=True)
class Provenance:
    source_uri: str
    source_sha256: str
    generated_at: str
    generator_version: str
    trust_tier: str
    source_mtime_ns: int | None = None


@dataclass(frozen=True)
class SourceRecord:
    id: str
    relative_path: str
    kind: str
    provenance: Provenance
    private: bool = False
    license_hint: str | None = None


@dataclass(frozen=True)
class SemanticCard:
    id: str
    kind: str
    markdown_path: str
    provenance: Provenance
    title: str
    supersedes: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class CapabilityCard:
    id: str
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    constraints: tuple[str, ...]
    preferred_adapters: tuple[str, ...]
    fallback_adapters: tuple[str, ...]
    verification: tuple[str, ...]
    provenance: Provenance


@dataclass(frozen=True)
class RestoreAction:
    action_id: str
    tier: str
    target: str
    operation: str
    reason: str
    source_ids: tuple[str, ...] = ()
    requires_human_approval: bool = True
    status: str = "planned"


@dataclass(frozen=True)
class RestorePlan:
    plan_id: str
    created_at: str
    manifest_sha256: str
    runtime_report_sha256: str
    actions: tuple[RestoreAction, ...]
    requires_human_approval: bool = True
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True)
class TransactionEntry:
    transaction_id: str
    action_id: str
    target: str
    before_sha256: str | None
    after_sha256: str | None
    backup_path: str | None
    created_at: str
    status: str
    schema_version: int = SCHEMA_VERSION


def to_dict(value: Any) -> dict[str, Any]:
    """Serialize an approved contract, preserving tuples as JSON arrays."""
    return asdict(value)
