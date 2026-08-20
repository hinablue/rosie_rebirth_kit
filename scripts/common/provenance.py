"""Trust-tier policy and provenance helpers."""
from __future__ import annotations

from datetime import UTC, datetime

from scripts.common.models import TRUST_TIERS, Provenance


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def validate_trust_tier(tier: str) -> None:
    if tier not in TRUST_TIERS:
        raise ValueError(f"Unknown trust tier: {tier}")


def tier_rank(tier: str) -> int:
    validate_trust_tier(tier)
    return TRUST_TIERS.index(tier)


def can_promote(source_tier: str, target_tier: str) -> bool:
    """Promotion only moves toward a more trusted tier and always needs review."""
    return tier_rank(target_tier) < tier_rank(source_tier)


def provenance_from_dict(data: dict[str, object]) -> Provenance:
    tier = str(data["trust_tier"])
    validate_trust_tier(tier)
    return Provenance(
        source_uri=str(data["source_uri"]),
        source_sha256=str(data["source_sha256"]),
        generated_at=str(data["generated_at"]),
        generator_version=str(data["generator_version"]),
        trust_tier=tier,
        source_mtime_ns=int(data["source_mtime_ns"]) if data.get("source_mtime_ns") is not None else None,
    )
