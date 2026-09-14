from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any


logger = logging.getLogger("payment_risk_api")
logger.setLevel(logging.INFO)


def generate_request_id() -> str:
    return str(uuid.uuid4())


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit_structured_log(
    *,
    event_type: str,
    request_id: str,
    http_status: int,
    latency_ms: float,
    model_version: str | None = None,
    predicted_risk: float | None = None,
    model_decision: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    event = {
        "event_type": event_type,
        "request_id": request_id,
        "timestamp": utc_timestamp(),
        "http_status": http_status,
        "latency_ms": round(latency_ms, 3),
        "model_version": model_version,
        "predicted_risk": predicted_risk,
        "model_decision": model_decision,
    }

    if extra:
        event.update(extra)

    logger.info(json.dumps(event, default=str))


class RequestTimer:
    def __init__(self) -> None:
        self._start = time.perf_counter()

    def elapsed_ms(self) -> float:
        return (
            time.perf_counter() - self._start
        ) * 1000