from agent_models import (
    SpecialistResult,
    DiscrepancyResult,
    QCResult,
    CorrectionResult,
)

from workflow_state import WorkflowState


# ============================================================
# RESEARCH ROUTER
# ============================================================

def route_after_research(
    result: SpecialistResult,
) -> str:
    """
    Deterministic routing after Research.

    Research recommendations are advisory.

    Python owns the actual workflow transition.
    """

    if result.stage != "RESEARCH":
        raise ValueError(
            "route_after_research expected stage "
            f"'RESEARCH', received {result.stage!r}."
        )

    if result.human_review_required:
        return "HUMAN_REVIEW"

    if result.material_conflicts:
        return "HUMAN_REVIEW"

    return "EVIDENCE"


# ============================================================
# DISCREPANCY ROUTER
# ============================================================

def route_after_discrepancy(
    result: DiscrepancyResult,
) -> str:
    """
    Deterministic routing after Discrepancy analysis.

    IMPORTANT DESIGN:

    Detecting a conflict does NOT automatically mean the Work Order
    must stop for human review.

    Discrepancy's job is to identify and classify differences.

    QC owns the next operational assessment:

        PASS
        BTP
        HUMAN_REVIEW

    Example:

        Customer claim:
            Evergreen Builder LLC

        NOC:
            Evergreen Builders LLC

        Permit:
            Evergreen Builders LLC

    This is a real discrepancy, but documentary evidence agrees
    internally. QC should evaluate whether the customer claim can
    be returned to Research through BTP.

    By contrast, when the Discrepancy Agent explicitly determines
    that the situation cannot safely proceed without human judgment,
    human_review_recommended=True remains an escalation gate.

    The LLM's recommended_next_stage remains advisory only.
    """

    if result.stage != "DISCREPANCY":
        raise ValueError(
            "route_after_discrepancy expected stage "
            f"'DISCREPANCY', received {result.stage!r}."
        )

    # Explicit escalation from the structured discrepancy assessment.
    #
    # This is intentionally different from merely having an item
    # classified as CONFLICT.
    if result.human_review_recommended:
        return "HUMAN_REVIEW"

    # Conflicts, missing items and unverified items are forwarded
    # to QC for operational assessment.
    #
    # QC then deterministically routes its structured outcome:
    #
    # PASS         -> COMPLETE_RECOMMENDED
    # BTP          -> RESEARCH_CORRECTION
    # HUMAN_REVIEW -> HUMAN_REVIEW
    return "QC"


# ============================================================
# QC ROUTER
# ============================================================

def route_after_qc(
    result: QCResult,
) -> str:
    """
    Deterministic routing after QC.

    The QC Agent provides an assessment.
    Python owns the workflow transition.

    PASS does NOT directly complete a Work Order.
    It produces COMPLETE_RECOMMENDED.
    """

    if result.stage != "QC":
        raise ValueError(
            "route_after_qc expected stage "
            f"'QC', received {result.stage!r}."
        )

    if result.outcome == "PASS":
        return "COMPLETE_RECOMMENDED"

    if result.outcome == "BTP":
        return "RESEARCH_CORRECTION"

    if result.outcome == "HUMAN_REVIEW":
        return "HUMAN_REVIEW"

    raise ValueError(
        f"Unsupported QC outcome: {result.outcome!r}"
    )


# ============================================================
# RESEARCH CORRECTION ROUTER
# ============================================================

def route_after_correction(
    result: CorrectionResult,
    state: WorkflowState,
) -> str:
    """
    Deterministic routing after Research Correction.

    The correction agent may PROPOSE a correction.

    It does not have authority to:
        - mutate the original Work Order
        - mark the correction operationally resolved
        - complete the Work Order

    A bounded retry counter prevents infinite:

        QC -> BTP -> Correction -> QC

    loops.
    """

    if result.stage != "RESEARCH_CORRECTION":
        raise ValueError(
            "route_after_correction expected stage "
            "'RESEARCH_CORRECTION', received "
            f"{result.stage!r}."
        )

    if result.wo_id != state.wo_id:
        raise ValueError(
            "Correction Work Order ID does not match "
            "workflow state."
        )

    # The correction agent explicitly determined that
    # human judgment is required.
    if result.human_review_required:
        state.human_review_required = True
        return "HUMAN_REVIEW"

    # A correction cycle that produces no correction cannot
    # safely return to QC indefinitely.
    if not result.corrections:
        state.human_review_required = True
        return "HUMAN_REVIEW"

    # Count an actual correction attempt.
    state.correction_attempts += 1

    # Bound the correction loop.
    if (
        state.correction_attempts
        > state.max_correction_attempts
    ):
        state.human_review_required = True
        return "HUMAN_REVIEW"

    return "QC_REVIEW"