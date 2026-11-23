import json
import pathlib

import pytest
from fastapi.testclient import TestClient

from fraud_service.api.app import create_app

MALFORMED = sorted(pathlib.Path("payloads/malformed").glob("*.json"))
SAMPLE = json.loads(pathlib.Path("payloads/sample.json").read_text(encoding="utf-8"))


@pytest.mark.integration
def test_predict_contract(client_factory):
    client = client_factory(probability=0.93)             # forces BLOCK
    r = client.post("/v1/predict", json=SAMPLE)
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"transaction_id", "fraud_probability", "decision",
                         "model_version", "trace_id"}     # nothing extra leaks
    assert body["decision"] == "block"
    assert r.headers["X-Trace-Id"] == body["trace_id"]    # tracing is contract too
    assert r.headers["X-Model-Version"] == "test-1"


@pytest.mark.integration
def test_caller_trace_id_is_propagated(client_factory):
    r = client_factory().post("/v1/predict", json=SAMPLE, headers={"X-Trace-Id": "abc123"})
    assert r.json()["trace_id"] == "abc123"


@pytest.mark.integration
@pytest.mark.parametrize("payload_file", MALFORMED, ids=lambda p: p.stem)
def test_malformed_corpus_rejected(client_factory, payload_file):
    """Every crafted bad payload must die at the validation wall."""
    r = client_factory().post("/v1/predict", content=payload_file.read_bytes(),
                              headers={"content-type": "application/json"})
    assert r.status_code == 422, payload_file.name
    assert r.json()["error"]["code"] == "INVALID_REQUEST"


@pytest.mark.integration
def test_validation_error_does_not_echo_input(client_factory):
    r = client_factory().post("/v1/predict", json={**SAMPLE, "amount_sar": -987654})
    assert "987654" not in r.text                         # no values, only field names
    assert r.json()["error"]["details"][0]["field"] == "amount_sar"


@pytest.mark.integration
def test_no_stack_trace_in_500(client_factory, monkeypatch):
    from fraud_service.service.scorer import FraudScorer
    monkeypatch.setattr(FraudScorer, "score", lambda self, txn: 1 / 0)   # force a crash
    r = client_factory().post("/v1/predict", json=SAMPLE)
    assert r.status_code == 500
    assert "ZeroDivisionError" not in r.text              # envelope only
    assert r.json()["error"]["code"] == "INTERNAL_ERROR"


@pytest.mark.integration
def test_not_ready_until_model_is_loaded():
    """No lifespan, no override: exactly the state of a container still starting."""
    client = TestClient(create_app(), raise_server_exceptions=False)
    for call in (client.get("/v1/ready"), client.post("/v1/predict", json=SAMPLE)):
        assert call.status_code == 503
        assert call.headers["Retry-After"] == "5"
        assert call.json()["error"]["code"] == "MODEL_UNAVAILABLE"


@pytest.mark.integration
def test_real_startup_serves_a_prediction(monkeypatch):
    """One end-to-end test with the real lifespan and the real artefact."""
    monkeypatch.setenv("FRAUD_MODEL_PATH", "models/fraud_xgb_v3.joblib")
    with TestClient(create_app()) as client:              # `with` runs the lifespan
        assert client.get("/v1/ready").status_code == 200
        assert client.get("/v1/health").json()["status"] == "ok"
        body = client.post("/v1/predict", json=SAMPLE).json()
    assert body["model_version"] == "v3.2.0"
    assert 0 <= body["fraud_probability"] <= 1
