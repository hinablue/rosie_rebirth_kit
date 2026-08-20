from scripts.common.provenance import can_promote, validate_trust_tier


def test_trust_tier_validation_and_promotion_direction() -> None:
    validate_trust_tier("T0_core")
    assert can_promote("T3_untrusted", "T1_curated")
    assert not can_promote("T1_curated", "T3_untrusted")
