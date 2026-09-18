import uuid

from fastapi.testclient import TestClient

import api.main as api_main
from api.execution_store import ExecutionRecord, execution_store
from api.main import app
from api.service import (
    serialize_workflow_state,
    validate_synthetic_wo_id,
)
from workflow_state import WorkflowState


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["service"] == "wo-agent-orchestrator-api"


def test_demo_scenarios() -> None:
    response = client.get("/api/v1/demo-scenarios")

    assert response.status_code == 200

    scenarios = response.json()["scenarios"]

    ids = {scenario["wo_id"] for scenario in scenarios}

    assert ids == {
        "SYN-WO-000001",
        "SYN-WO-000111",
        "SYN-WO-000116",
    }


def test_rejects_non_synthetic_work_order() -> None:
    response = client.post(
        "/api/v1/workflows/REAL-WO-123/run"
    )

    assert response.status_code == 400

    assert "synthetic" in response.json()["detail"].lower()


def test_unknown_execution_returns_404() -> None:
    execution_id = str(uuid.uuid4())

    response = client.get(
        f"/api/v1/executions/{execution_id}"
    )

    assert response.status_code == 404


def test_start_workflow_returns_execution_id(
    monkeypatch,
) -> None:

    fake_record = ExecutionRecord(
        execution_id="test-execution-001",
        wo_id="SYN-WO-000001",
        status="RUNNING",
    )

    monkeypatch.setattr(
        api_main,
        "start_execution",
        lambda wo_id: fake_record,
    )

    response = client.post(
        "/api/v1/workflows/SYN-WO-000001/run"
    )

    assert response.status_code == 202

    payload = response.json()

    assert payload["execution_id"] == "test-execution-001"
    assert payload["wo_id"] == "SYN-WO-000001"
    assert payload["status"] == "RUNNING"


def test_execution_result_endpoint() -> None:
    execution_id = str(uuid.uuid4())

    record = ExecutionRecord(
        execution_id=execution_id,
        wo_id="SYN-WO-000001",
        status="RUNNING",
    )

    execution_store.create(record)

    execution_store.update(
        execution_id,
        status="COMPLETE_RECOMMENDED",
        result={
            "wo_id": "SYN-WO-000001",
            "current_stage": "COMPLETE_RECOMMENDED",
            "human_review_required": False,
            "correction_attempts": 0,
            "correction_overlay": [],
            "audit_log": [],
            "results": {},
        },
    )

    response = client.get(
        f"/api/v1/executions/{execution_id}"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "COMPLETE_RECOMMENDED"
    assert payload["current_stage"] == "COMPLETE_RECOMMENDED"
    assert payload["human_review_required"] is False
    assert payload["correction_attempts"] == 0


def test_work_order_id_normalization() -> None:
    assert (
        validate_synthetic_wo_id(" syn-wo-000116 ")
        == "SYN-WO-000116"
    )


def test_workflow_state_serialization_does_not_expose_unparsed_text() -> None:
    state = WorkflowState(
        wo_id="SYN-WO-000001",
        current_stage="COMPLETE_RECOMMENDED",
    )

    state.intake_result = (
        "unexpected raw text containing information "
        "that should not be returned"
    )

    payload = serialize_workflow_state(state)

    assert payload["results"]["intake"] == {
        "available": True,
        "structured": False,
    }

    assert "unexpected raw text" not in str(payload)