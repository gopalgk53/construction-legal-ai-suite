from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


ExecutionStatus = Literal[
    "RUNNING",
    "COMPLETE_RECOMMENDED",
    "HUMAN_REVIEW",
    "FAILED",
]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class RunWorkflowResponse(BaseModel):
    execution_id: str
    wo_id: str
    status: ExecutionStatus


class ExecutionResponse(BaseModel):
    execution_id: str
    wo_id: str
    status: ExecutionStatus

    current_stage: Optional[str] = None
    human_review_required: Optional[bool] = None
    correction_attempts: Optional[int] = None

    result: Optional[dict[str, Any]] = None
    error_type: Optional[str] = None

    created_at: str
    updated_at: str


class DemoScenario(BaseModel):
    wo_id: str
    scenario: str
    expected_path: str


class DemoScenariosResponse(BaseModel):
    scenarios: list[DemoScenario] = Field(default_factory=list)