import time
import uuid
from collections.abc import Mapping
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from fraud_service.adapters.sklearn_model import SklearnModel
from fraud_service.api.routes import router
from fraud_service.config import Settings
from fraud_service.domain.entities import Channel, FeatureVector, Transaction
from fraud_service.logging_setup import configure_logging, get_logger
from fraud_service.service.scorer import FraudScorer

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Composition root: the one place concrete classes meet.
    The model loads HERE: visible, timed, failable."""
    settings = Settings()                 # invalid config? crash here, with field names
    configure_logging(settings.log_level)
    # The config-drift guard: one line showing what this process REALLY runs with.
    log.info("settings_effective",
             **settings.model_dump(mode="json", exclude={"registry_token"}))
    app.state.settings = settings
    app.state.started_at = datetime.now(UTC)

    t0 = time.perf_counter()
    model = SklearnModel.load(settings.model_path)     # fail fast if absent
    model.predict_proba(_warmup_features())            # pay first-call cost now
    app.state.scorer = FraudScorer(model=model, block_threshold=settings.block_threshold)
    log.info("model_loaded", version=model.model_version,
             seconds=round(time.perf_counter() - t0, 3))
    yield
    log.info("shutdown_complete")


def create_app() -> FastAPI:
    app = FastAPI(title="Fraud Scoring Service", version="1.0.0", lifespan=lifespan)
    app.include_router(router, prefix="/v1")

    @app.middleware("http")
    async def trace_and_log(request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id", uuid.uuid4().hex[:16])
        request.state.trace_id = trace_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id=trace_id)   # on every log line
        t0 = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Response-Time-Ms"] = str(latency_ms)
        log.info("http_request", method=request.method, path=request.url.path,
                 status=response.status_code, latency_ms=latency_ms)
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        # Field names and problems only: never echo the offending values back.
        details = [{"field": ".".join(str(part) for part in err["loc"][1:]) or "body",
                    "problem": err["msg"]} for err in exc.errors()]
        log.warning("validation_rejected", fields=sorted({d["field"] for d in details}))
        return _error(request, 422, "INVALID_REQUEST", "Request body failed validation",
                      details=details)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        code = {404: "NOT_FOUND", 503: "MODEL_UNAVAILABLE"}.get(exc.status_code, "HTTP_ERROR")
        return _error(request, exc.status_code, code, str(exc.detail), headers=exc.headers)

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        # Never leak stack traces to clients; always give them a trace_id.
        log.error("unhandled_exception", exc_info=exc)
        return _error(request, 500, "INTERNAL_ERROR",
                      "Unexpected error; contact support with trace_id")

    return app


def _trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "unknown")


def _error(request: Request, status: int, code: str, message: str,
           headers: Mapping[str, str] | None = None, **extra: object) -> JSONResponse:
    """One error shape for every failure: {"error": {code, message, trace_id}}."""
    body = {"code": code, "message": message, "trace_id": _trace_id(request), **extra}
    return JSONResponse(status_code=status, content={"error": body}, headers=headers)


def _warmup_features() -> FeatureVector:
    return Transaction(
        transaction_id="WARMUP-0000", amount_sar=100.0, channel=Channel.POS,
        merchant_category="GROCERY", customer_id="warmup",
        timestamp=datetime.now(UTC)).to_features()
