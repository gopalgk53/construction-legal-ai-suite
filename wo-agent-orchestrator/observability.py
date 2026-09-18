import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


LOGGER_NAME = "wo_agent_orchestrator"


def create_trace_id() -> str:
    """
    Create a unique identifier for one workflow execution.
    """
    return str(uuid.uuid4())


def configure_logging(
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure the workflow logger.

    Production logs should contain operational metadata only.
    Raw Work Order payloads, prompts, evidence contents,
    credentials, and model responses must not be logged.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()

        handler.setFormatter(
            logging.Formatter("%(message)s")
        )

        logger.addHandler(handler)

    logger.propagate = False

    return logger


def emit_event(
    logger: logging.Logger,
    *,
    event: str,
    trace_id: str,
    wo_id: str,
    stage: str,
    status: str,
    duration_ms: int | None = None,
    route: str | None = None,
    correction_attempt: int | None = None,
    human_review_required: bool | None = None,
    error_type: str | None = None,
) -> dict[str, Any]:
    """
    Emit one structured JSON workflow event.

    Only approved operational metadata is accepted by this
    function. Arbitrary payload dictionaries are intentionally
    not supported.
    """
    record: dict[str, Any] = {
        "event": event,
        "trace_id": trace_id,
        "wo_id": wo_id,
        "stage": stage,
        "status": status,
    }

    optional_fields = {
        "duration_ms": duration_ms,
        "route": route,
        "correction_attempt": correction_attempt,
        "human_review_required": human_review_required,
        "error_type": error_type,
    }

    for key, value in optional_fields.items():
        if value is not None:
            record[key] = value

    logger.info(
        json.dumps(
            record,
            sort_keys=True,
        )
    )

    return record


@dataclass
class StageTimer:
    """
    Measure elapsed time for one workflow stage.
    """

    started_at: float = field(
        default_factory=time.perf_counter
    )

    def elapsed_ms(self) -> int:
        elapsed_seconds = (
            time.perf_counter() - self.started_at
        )

        return round(
            elapsed_seconds * 1000
        )