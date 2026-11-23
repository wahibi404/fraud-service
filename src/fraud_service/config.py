"""All configuration in ONE place, typed and validated at startup.
Reading os.environ anywhere else in the codebase is a review-blocking offence."""
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FRAUD_",          # FRAUD_MODEL_PATH, FRAUD_LOG_LEVEL ...
        env_file=".env",              # dev convenience; real environments set real env vars
        env_file_encoding="utf-8",
        extra="forbid",               # an unknown FRAUD_* line in .env is a typo: crash
    )

    # --- model ---
    model_path: Path = Field(description="Path to the joblib bundle")       # required
    block_threshold: float = Field(0.85, ge=0.5, le=0.99,
                                   description="Risk-approved block threshold")

    # --- service ---
    log_level: str = Field("INFO")
    git_sha: str = Field("dev", description="Injected by CI at build time")

    # --- dependencies ---
    redis_url: str = Field("redis://localhost:6379/0")
    registry_token: SecretStr | None = Field(
        None, description="Only needed when pulling models at startup")

    @field_validator("model_path")
    @classmethod
    def model_file_must_exist(cls, v: Path) -> Path:
        if not v.exists():
            # Fail HERE, at startup, with a message an operator understands,
            # not with a 500 on the first request.
            raise ValueError(f"model artefact not found: {v}")
        return v

    @field_validator("log_level")
    @classmethod
    def valid_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {sorted(allowed)}")
        return v.upper()
