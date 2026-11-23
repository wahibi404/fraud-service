"""Wire contract. These models exist for consumers; keep them stable.
They convert to/from domain entities in routes and never leak inward."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from fraud_service.domain.entities import Channel, Decision, Transaction


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")   # reject unknown fields loudly

    transaction_id: str = Field(min_length=8, max_length=64, examples=["TXN-2026-00042"])
    amount_sar: float = Field(gt=0, le=1_000_000, description="Transaction amount in SAR")
    channel: Channel
    merchant_category: str = Field(min_length=2, max_length=40, examples=["electronics"])
    customer_id: str = Field(min_length=4, max_length=64, examples=["CUST-00077"])
    timestamp: datetime

    def to_domain(self) -> Transaction:
        return Transaction(**self.model_dump())


class PredictResponse(BaseModel):
    transaction_id: str
    fraud_probability: float = Field(ge=0, le=1)
    decision: Decision
    model_version: str
    trace_id: str


class ErrorBody(BaseModel):
    code: str          # stable machine-readable contract
    message: str       # human-readable, may change
    trace_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorBody


class HealthResponse(BaseModel):
    status: str
    git_sha: str
    started_at: datetime
