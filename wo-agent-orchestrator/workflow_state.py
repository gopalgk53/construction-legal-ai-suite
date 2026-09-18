from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WorkflowState:
    """
    Shared state passed through the Work Order multi-agent workflow.
    """

    wo_id: str

    current_stage: str = "STARTED"

    intake_result: Optional[str] = None
    research_result: Optional[str] = None
    evidence_result: Optional[str] = None
    discrepancy_result: Optional[str] = None
    qc_result: Optional[str] = None

    human_review_required: bool = False

    # Controls the bounded BTP -> Research Correction -> QC loop
    correction_attempts: int = 0
    max_correction_attempts: int = 2

    # Stores correction artifacts separately.
    # The original Work Order remains unchanged.
    correction_overlay: list[dict] = field(default_factory=list)

    # Records important workflow actions for traceability.
    audit_log: list[str] = field(default_factory=list)