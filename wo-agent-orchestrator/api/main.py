import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .execution_store import ExecutionRecord, execution_store
from .schemas import (
    DemoScenario,
    DemoScenariosResponse,
    ExecutionResponse,
    HealthResponse,
    RunWorkflowResponse,
)
from .service import start_execution


app = FastAPI(
    title="Autonomous Work Order Intelligence API",
    description=(
        "Synthetic-only API for the Autonomous Work Order "
        "Intelligence & Operations Platform."
    ),
    version="1.0.0",
)


def _cors_origins() -> list[str]:
    configured = os.getenv(
        "WO_API_CORS_ORIGINS",
        "http://localhost:3000",
    )

    return [
        origin.strip()
        for origin in configured.split(",")
        if origin.strip()
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _to_execution_response(
    record: ExecutionRecord,
) -> ExecutionResponse:

    current_stage = None
    human_review_required = None
    correction_attempts = None

    if record.result is not None:
        current_stage = record.result.get("current_stage")
        human_review_required = record.result.get(
            "human_review_required"
        )
        correction_attempts = record.result.get(
            "correction_attempts"
        )

    return ExecutionResponse(
        execution_id=record.execution_id,
        wo_id=record.wo_id,
        status=record.status,
        current_stage=current_stage,
        human_review_required=human_review_required,
        correction_attempts=correction_attempts,
        result=record.result,
        error_type=record.error_type,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="wo-agent-orchestrator-api",
    )


@app.get(
    "/api/v1/demo-scenarios",
    response_model=DemoScenariosResponse,
)
def demo_scenarios() -> DemoScenariosResponse:
    return DemoScenariosResponse(
        scenarios=[
            DemoScenario(
                wo_id="SYN-WO-000001",
                scenario="Clean synthetic Work Order",
                expected_path=(
                    "Intake → Research → Evidence → "
                    "Discrepancy → QC → Complete Recommended"
                ),
            ),
            DemoScenario(
                wo_id="SYN-WO-000116",
                scenario="Correctable customer-data mismatch",
                expected_path=(
                    "QC BTP → Research Correction → "
                    "QC Re-review → Complete Recommended"
                ),
            ),
            DemoScenario(
                wo_id="SYN-WO-000111",
                scenario="Unresolved documentary evidence conflict",
                expected_path=(
                    "Discrepancy → Human Review"
                ),
            ),
        ]
    )


@app.post(
    "/api/v1/workflows/{wo_id}/run",
    response_model=RunWorkflowResponse,
    status_code=202,
)
def run_workflow_endpoint(
    wo_id: str,
) -> RunWorkflowResponse:

    try:
        record = start_execution(wo_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return RunWorkflowResponse(
        execution_id=record.execution_id,
        wo_id=record.wo_id,
        status=record.status,
    )


@app.get(
    "/api/v1/executions/{execution_id}",
    response_model=ExecutionResponse,
)
def get_execution(
    execution_id: str,
) -> ExecutionResponse:

    record = execution_store.get(execution_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Execution not found.",
        )

    return _to_execution_response(record)