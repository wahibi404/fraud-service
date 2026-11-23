import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request

from fraud_service.adapters.sklearn_model import SklearnModel
from fraud_service.api.routes import router
from fraud_service.config import Settings
from fraud_service.service.scorer import FraudScorer

log = logging.getLogger("fraud_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Composition root: the one place concrete classes meet.
    The model loads HERE: visible, timed, failable."""
    settings = Settings()
    logging.basicConfig(level=settings.log_level)
    app.state.settings = settings
    app.state.started_at = datetime.now(UTC)

    t0 = time.perf_counter()
    model = SklearnModel.load(settings.model_path)     # fail fast if absent
    app.state.scorer = FraudScorer(model=model, block_threshold=settings.block_threshold)
    log.info("model loaded: version=%s seconds=%.3f",
             model.model_version, time.perf_counter() - t0)
    yield
    log.info("shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(title="Fraud Scoring Service", version="1.0.0", lifespan=lifespan)
    app.include_router(router, prefix="/v1")

    @app.middleware("http")
    async def trace_and_time(request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id", uuid.uuid4().hex[:16])
        request.state.trace_id = trace_id
        t0 = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Response-Time-Ms"] = str(
            round((time.perf_counter() - t0) * 1000, 1))
        return response

    return app
