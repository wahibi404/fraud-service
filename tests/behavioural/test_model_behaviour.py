"""Claims about the MODEL, checked against the real artefact."""
import pandas as pd
import pytest

from fraud_service.domain.entities import Transaction

pytestmark = pytest.mark.behavioural


def _score(model, txn: Transaction) -> float:
    return model.predict_proba(txn.to_features()).value


def test_invariance_to_merchant_casing(real_model, make_txn):
    """Casing and stray spaces are noise, not signal."""
    a = _score(real_model, make_txn(merchant_category="electronics"))
    b = _score(real_model, make_txn(merchant_category="  ELECTRONICS "))
    assert a == pytest.approx(b, abs=1e-9)


def test_invariance_to_identifiers(real_model, make_txn):
    """Who you are and what the transaction is called must not move the score."""
    a = _score(real_model, make_txn())
    b = _score(real_model, make_txn(transaction_id="TXN-OTHER-9999", customer_id="CUST-1"))
    assert a == pytest.approx(b, abs=1e-9)


@pytest.mark.parametrize("small, large", [(50.0, 50_000.0), (5.0, 500.0), (900.0, 90_000.0)])
def test_directional_amount(real_model, make_txn, small, large):
    """All else equal, a much larger amount must not LOWER fraud probability."""
    assert _score(real_model, make_txn(amount_sar=large)) >= \
        _score(real_model, make_txn(amount_sar=small)) - 1e-6


@pytest.mark.slow
def test_golden_scores(real_model):
    """The skew tripwire: every reference row must reproduce (within tolerance)."""
    ref = pd.read_csv("data/golden_scores_v3.csv")
    drifted = []
    for row in ref.itertuples():
        txn = Transaction(
            transaction_id=row.transaction_id, amount_sar=row.amount_sar,
            channel=row.channel, merchant_category=row.mcc,
            customer_id=row.customer_id, timestamp=row.timestamp)
        if _score(real_model, txn) != pytest.approx(row.score, abs=1e-6):
            drifted.append(row.transaction_id)
    assert not drifted, f"skew on {len(drifted)} rows, first: {drifted[:5]}"
