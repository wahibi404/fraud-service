import pytest
from pydantic import ValidationError

from fraud_service.config import Settings


@pytest.mark.unit
def test_missing_model_file_fails_fast(monkeypatch):
    monkeypatch.setenv("FRAUD_MODEL_PATH", "/nope/missing.joblib")
    with pytest.raises(ValidationError, match="model artefact not found"):
        Settings(_env_file=None)


@pytest.mark.unit
def test_threshold_outside_approved_range_is_rejected(monkeypatch):
    monkeypatch.setenv("FRAUD_MODEL_PATH", "models/fraud_xgb_v3.joblib")
    monkeypatch.setenv("FRAUD_BLOCK_THRESHOLD", "0.2")
    with pytest.raises(ValidationError, match="block_threshold"):
        Settings(_env_file=None)


@pytest.mark.unit
def test_secret_is_masked_when_printed(monkeypatch):
    monkeypatch.setenv("FRAUD_MODEL_PATH", "models/fraud_xgb_v3.joblib")
    monkeypatch.setenv("FRAUD_REGISTRY_TOKEN", "ghp_not_a_real_token")
    assert "ghp_not_a_real_token" not in repr(Settings(_env_file=None))
