from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from fraud_service.api.schemas import HealthResponse, PredictRequest, PredictResponse
from fraud_service.service.scorer import FraudScorer

router = APIRouter()


def get_scorer(request: Request) -> FraudScorer:
    """DI seam: tests override this one function to inject fakes."""
    scorer = getattr(request.app.state, "scorer", None)
    if scorer is None:                         # startup incomplete or failed
        raise HTTPException(status_code=503, detail="Model not ready",
                            headers={"Retry-After": "5"})
    return scorer


@router.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest, request: Request, response: Response,
            scorer: Annotated[FraudScorer, Depends(get_scorer)]):
    # Plain `def`: inference blocks, so FastAPI runs it in a worker thread.
    score = scorer.score(body.to_domain())
    response.headers["X-Model-Version"] = score.model_version
    return PredictResponse(
        transaction_id=score.transaction_id,
        fraud_probability=round(score.probability, 6),
        decision=score.decision,
        model_version=score.model_version,
        trace_id=request.state.trace_id,
    )


@router.get("/health", response_model=HealthResponse)
def health(request: Request):
    """Liveness: the process is up. NO I/O here."""
    return HealthResponse(status="ok",
                          git_sha=request.app.state.settings.git_sha,
                          started_at=request.app.state.started_at)


@router.get("/ready")
def ready(request: Request):
    """Readiness: safe to receive traffic. Checks the model is loaded."""
    if getattr(request.app.state, "scorer", None) is None:
        raise HTTPException(status_code=503, detail="warming up",
                            headers={"Retry-After": "5"})
    return {"status": "ready", "checked_at": datetime.now(UTC)}
