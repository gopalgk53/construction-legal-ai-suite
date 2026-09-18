import json
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from workflow_state import WorkflowState

from .execution_store import ExecutionRecord, execution_store


SYNTHETIC_WO_PATTERN = re.compile(r"^SYN-WO-\d{6}$")

MAX_WORKERS = int(os.getenv("WO_API_MAX_WORKERS", "2"))

_executor = ThreadPoolExecutor(
    max_workers=MAX_WORKERS,
    thread_name_prefix="wo-workflow",
)


def validate_synthetic_wo_id(wo_id: str) -> str:
    """
    Enforce the portfolio privacy boundary.

    Only synthetic Work Order identifiers are accepted by this API.
    """

    normalized = wo_id.strip().upper()

    if not SYNTHETIC_WO_PATTERN.fullmatch(normalized):
        raise ValueError(
            "Only synthetic Work Order IDs in the format "
            "SYN-WO-000001 are accepted."
        )

    return normalized


def _safe_decode_json(value: Any) -> Any:
    """
    Decode validated agent JSON for frontend consumption.

    If an unexpected non-JSON string appears, do not expose the raw text.
    """

    if value is None:
        return None

    if isinstance(value, (dict, list, int, float, bool)):
        return value

    if not isinstance(value, str):
        return None

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {
            "available": True,
            "structured": False,
        }


def serialize_workflow_state(state: WorkflowState) -> dict[str, Any]:
    """
    Convert WorkflowState into a frontend-safe response.

    Source Work Order payloads remain outside this API execution record.
    """

    return {
        "wo_id": state.wo_id,
        "current_stage": state.current_stage,
        "human_review_required": state.human_review_required,
        "correction_attempts": state.correction_attempts,
        "max_correction_attempts": state.max_correction_attempts,
        "correction_overlay": list(state.correction_overlay),
        "audit_log": list(state.audit_log),
        "results": {
            "intake": _safe_decode_json(state.intake_result),
            "research": _safe_decode_json(state.research_result),
            "evidence": _safe_decode_json(state.evidence_result),
            "discrepancy": _safe_decode_json(state.discrepancy_result),
            "qc": _safe_decode_json(state.qc_result),
        },
    }


def _execute_workflow(execution_id: str, wo_id: str) -> None:
    """
    Execute the synchronous multi-agent workflow outside the HTTP request.

    Importing orchestrator lazily avoids unnecessary Azure initialization
    when the API module is imported for lightweight tests.
    """

    try:
        from orchestrator import run_workflow

        state = run_workflow(wo_id)

        if state.current_stage not in {
            "COMPLETE_RECOMMENDED",
            "HUMAN_REVIEW",
        }:
            execution_store.update(
                execution_id,
                status="FAILED",
                error_type="UnexpectedTerminalStage",
            )
            return

        execution_store.update(
            execution_id,
            status=state.current_stage,
            result=serialize_workflow_state(state),
        )

    except Exception as exc:
        # Privacy rule:
        # expose only the exception TYPE, never the exception message.
        execution_store.update(
            execution_id,
            status="FAILED",
            error_type=type(exc).__name__,
        )


def start_execution(wo_id: str) -> ExecutionRecord:
    normalized_wo_id = validate_synthetic_wo_id(wo_id)

    execution_id = str(uuid.uuid4())

    record = ExecutionRecord(
        execution_id=execution_id,
        wo_id=normalized_wo_id,
        status="RUNNING",
    )

    execution_store.create(record)

    _executor.submit(
        _execute_workflow,
        execution_id,
        normalized_wo_id,
    )

    return record