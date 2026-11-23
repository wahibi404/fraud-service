"""All configuration in ONE place. Nothing else in the codebase reads os.environ."""
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FRAUD_", env_file=".env")

    model_path: Path = Path("models/fraud_xgb_v3.joblib")
    block_threshold: float = Field(0.85, ge=0.5, le=0.99)
    log_level: str = "INFO"
    git_sha: str = "dev"
