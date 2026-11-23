import pytest

from fraud_service.domain.entities import Decision
from fraud_service.service.scorer import FraudScorer
from tests.conftest import ConstantModel


@pytest.mark.unit
@pytest.mark.parametrize("p, expected", [
    (0.99, Decision.BLOCK), (0.75, Decision.REVIEW), (0.10, Decision.ALLOW)])
def test_scorer_applies_policy_and_carries_version(sample_txn, p, expected):
    scorer = FraudScorer(model=ConstantModel(p, version="test-9"), block_threshold=0.85)
    result = scorer.score(sample_txn)
    assert result.decision is expected
    assert result.probability == p
    assert result.model_version == "test-9"
    assert result.transaction_id == sample_txn.transaction_id
