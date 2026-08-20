"""Trust-tier and provenance validation placeholders."""
from __future__ import annotations

VALID_TRUST_TIERS = frozenset({"T0_core", "T1_curated", "T2_observed", "T3_untrusted"})


def validate_trust_tier(tier: str) -> None:
    if tier not in VALID_TRUST_TIERS:
        raise ValueError(f"Unknown trust tier: {tier}")
