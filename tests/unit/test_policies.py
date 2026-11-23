import pytest

from fraud_service.domain.entities import Decision, RawScore
from fraud_service.domain.policies import decide


@pytest.mark.unit
@pytest.mark.parametrize("p, expected", [
    (0.849999, Decision.REVIEW),   # just under block => review band
    (0.85,     Decision.BLOCK),    # boundary is inclusive: documented rule
    (0.699999, Decision.ALLOW),    # just under the review band
    (0.70,     Decision.REVIEW),
    (0.0,      Decision.ALLOW),
    (1.0,      Decision.BLOCK),
])
def test_decision_bands(p, expected):
    assert decide(RawScore(value=p), block_threshold=0.85) is expected
