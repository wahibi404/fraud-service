"""JSON logs to stdout. The platform owns shipping and retention."""
import logging
import sys
from typing import Any

import structlog
from structlog.typing import EventDict, WrappedLogger

SENSITIVE_KEYS = {"password", "token", "secret", "authorization",
                  "registry_token", "national_id", "card_number"}


def _mask_sensitive(logger: WrappedLogger, method: str, event_dict: EventDict) -> EventDict:
    """Defensive masking: even if someone logs a secret, it leaves masked."""
    for key in list(event_dict):
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "***MASKED***"
    return event_dict


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(stream=sys.stdout, level=level, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,      # trace_id bound per request
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),   # always UTC
            _mask_sensitive,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level)),
    )


def get_logger(name: str) -> Any:
    return structlog.get_logger(name)
