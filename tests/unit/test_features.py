import pytest


@pytest.mark.unit
def test_feature_names_are_stable(sample_txn):
    """Feature-name drift IS training/serving skew. Freeze the contract."""
    assert set(sample_txn.to_features().values) == {
        "amount_log", "channel", "mcc", "hour_of_day", "is_night"}


@pytest.mark.unit
@pytest.mark.parametrize("hour, expected", [(0, 1), (5, 1), (6, 0), (15, 0), (23, 0)])
def test_night_flag_boundaries(make_txn, sample_txn, hour, expected):
    txn = make_txn(timestamp=sample_txn.timestamp.replace(hour=hour))
    assert txn.to_features().values["is_night"] == expected


@pytest.mark.unit
def test_mcc_normalised_from_messy_input(make_txn):
    txn = make_txn(merchant_category="  home appliances ")
    assert txn.to_features().values["mcc"] == "HOME_APPLIANCES"
