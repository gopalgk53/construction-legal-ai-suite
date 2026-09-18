import json
import logging
import uuid

from observability import (
    StageTimer,
    configure_logging,
    create_trace_id,
    emit_event,
)


WO_ID = "SYN-WO-TEST"
TRACE_ID = "00000000-0000-0000-0000-000000000001"


def test_create_trace_id_returns_valid_uuid():
    trace_id = create_trace_id()

    parsed = uuid.UUID(trace_id)

    assert str(parsed) == trace_id


def test_create_trace_id_is_unique():
    first = create_trace_id()
    second = create_trace_id()

    assert first != second


def test_configure_logging_returns_logger():
    logger = configure_logging()

    assert isinstance(logger, logging.Logger)
    assert logger.name == "wo_agent_orchestrator"


def test_configure_logging_does_not_duplicate_handlers():
    logger = configure_logging()
    first_count = len(logger.handlers)

    logger = configure_logging()
    second_count = len(logger.handlers)

    assert second_count == first_count


def test_emit_event_returns_required_metadata():
    logger = configure_logging()

    record = emit_event(
        logger,
        event="stage_completed",
        trace_id=TRACE_ID,
        wo_id=WO_ID,
        stage="QC",
        status="success",
    )

    assert record == {
        "event": "stage_completed",
        "trace_id": TRACE_ID,
        "wo_id": WO_ID,
        "stage": "QC",
        "status": "success",
    }


def test_emit_event_includes_optional_metadata():
    logger = configure_logging()

    record = emit_event(
        logger,
        event="stage_completed",
        trace_id=TRACE_ID,
        wo_id=WO_ID,
        stage="QC",
        status="success",
        duration_ms=125,
        route="RESEARCH_CORRECTION",
        correction_attempt=1,
        human_review_required=False,
    )

    assert record["duration_ms"] == 125
    assert record["route"] == "RESEARCH_CORRECTION"
    assert record["correction_attempt"] == 1
    assert record["human_review_required"] is False


def test_emit_event_omits_unused_optional_fields():
    logger = configure_logging()

    record = emit_event(
        logger,
        event="stage_started",
        trace_id=TRACE_ID,
        wo_id=WO_ID,
        stage="RESEARCH",
        status="started",
    )

    assert "duration_ms" not in record
    assert "route" not in record
    assert "correction_attempt" not in record
    assert "human_review_required" not in record
    assert "error_type" not in record


def test_emit_event_writes_valid_json(caplog):
    logger = configure_logging()

    logger.propagate = True

    try:
        with caplog.at_level(
            logging.INFO,
            logger="wo_agent_orchestrator",
        ):
            emit_event(
                logger,
                event="workflow_started",
                trace_id=TRACE_ID,
                wo_id=WO_ID,
                stage="WORKFLOW",
                status="started",
            )

        parsed_records = []

        for record in caplog.records:
            if record.name == "wo_agent_orchestrator":
                parsed_records.append(
                    json.loads(record.getMessage())
                )

        assert len(parsed_records) >= 1

        event = parsed_records[-1]

        assert event["event"] == "workflow_started"
        assert event["trace_id"] == TRACE_ID
        assert event["wo_id"] == WO_ID

    finally:
        logger.propagate = False


def test_emit_event_supports_error_type():
    logger = configure_logging()

    record = emit_event(
        logger,
        event="stage_failed",
        trace_id=TRACE_ID,
        wo_id=WO_ID,
        stage="EVIDENCE",
        status="error",
        error_type="ValueError",
    )

    assert record["error_type"] == "ValueError"


def test_stage_timer_returns_non_negative_integer():
    timer = StageTimer()

    elapsed = timer.elapsed_ms()

    assert isinstance(elapsed, int)
    assert elapsed >= 0

def test_run_workflow_emits_failure_and_reraises(
    monkeypatch,
    caplog,
):
    import json
    import logging

    import pytest

    import orchestrator

    def failing_workflow(
        wo_id,
        *,
        trace_id,
        workflow_timer,
    ):
        raise RuntimeError(
            "SENSITIVE_FAILURE_MESSAGE"
        )

    monkeypatch.setattr(
        orchestrator,
        "_run_workflow",
        failing_workflow,
    )

    caplog.set_level(
        logging.INFO,
        logger="wo_agent_orchestrator",
    )

    with pytest.raises(
        RuntimeError,
        match="SENSITIVE_FAILURE_MESSAGE",
    ):
        orchestrator.run_workflow(
            "SYN-WO-TEST-FAILURE"
        )

    failure_records = [
        json.loads(record.message)
        for record in caplog.records
        if json.loads(record.message).get("event")
        == "workflow_failed"
    ]

    assert len(failure_records) == 1

    event = failure_records[0]

    assert event["event"] == "workflow_failed"
    assert event["wo_id"] == "SYN-WO-TEST-FAILURE"
    assert event["stage"] == "WORKFLOW"
    assert event["status"] == "failed"
    assert event["error_type"] == "RuntimeError"

    assert "trace_id" in event
    assert event["trace_id"]

    assert "duration_ms" in event
    assert isinstance(
        event["duration_ms"],
        int,
    )

    serialized_event = json.dumps(event)

    assert (
        "SENSITIVE_FAILURE_MESSAGE"
        not in serialized_event
    )