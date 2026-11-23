# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

# If a dependency ever needs compiling, install build-essential HERE.
# Whatever this stage needs only for building never reaches the runtime stage.
COPY requirements.lock .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.lock

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime

# Non-root user: the first thing any security review checks
RUN useradd --create-home --uid 10001 appuser

# curl only for the container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) Dependencies: hundreds of MB, change rarely => cached across code edits
COPY --from=builder /opt/venv /opt/venv

# 2) Model: changes on retrain, not on every commit
COPY models/fraud_xgb_v3.joblib /models/fraud_xgb_v3.joblib

# 3) Source: a few KB, changes every commit => keep it LAST
COPY src/ /app/src

ARG GIT_SHA=dev
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    FRAUD_MODEL_PATH=/models/fraud_xgb_v3.joblib \
    FRAUD_GIT_SHA=$GIT_SHA

USER appuser
EXPOSE 8000

# Readiness-based healthcheck: /ready, not /health
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/v1/ready || exit 1

# Exec form => uvicorn is PID 1 => it receives SIGTERM => graceful shutdown
CMD ["uvicorn", "fraud_service.api.app:create_app", "--factory", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--no-access-log"]
