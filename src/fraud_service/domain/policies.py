"""Business policy: thresholds are BUSINESS decisions, not model decisions.

A pure function: easy to test, and a risk officer can read and sign it off.
"""
from fraud_service.domain.entities import Decision, RawScore

REVIEW_BAND = 0.15  # width of the manual-review band below the block threshold


def decide(score: RawScore, block_threshold: float) -> Decision:
    if score.value >= block_threshold:
        return Decision.BLOCK
    if score.value >= block_threshold - REVIEW_BAND:
        return Decision.REVIEW
    return Decision.ALLOW
