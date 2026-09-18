import pytest

from agent_models import (
    SpecialistResult,
    DiscrepancyResult,
    QCResult,
    CorrectionItem,
    CorrectionResult,
)

from router import (
    route_after_research,
    route_after_discrepancy,
    route_after_qc,
    route_after_correction,
)

from workflow_state import WorkflowState


WO_ID = "SYN-WO-TEST"


# ============================================================
# RESEARCH ROUTER TESTS
# ============================================================


def test_research_clean_routes_to_evidence():
    result = SpecialistResult(
        wo_id=WO_ID,
        stage="RESEARCH",
    )

    assert route_after_research(result) == "EVIDENCE"


def test_research_human_review_routes_to_human_review():
    result = SpecialistResult(
        wo_id=WO_ID,
        stage="RESEARCH",
        human_review_required=True,
    )

    assert route_after_research(result) == "HUMAN_REVIEW"


def test_research_material_conflict_routes_to_human_review():
    result = SpecialistResult(
        wo_id=WO_ID,
        stage="RESEARCH",
        material_conflicts=["documentary conflict"],
    )

    assert route_after_research(result) == "HUMAN_REVIEW"


def test_research_wrong_stage_raises_error():
    result = SpecialistResult(
        wo_id=WO_ID,
        stage="INTAKE",
    )

    with pytest.raises(ValueError):
        route_after_research(result)


# ============================================================
# DISCREPANCY ROUTER TESTS
# ============================================================


def test_discrepancy_clean_routes_to_qc():
    result = DiscrepancyResult(
        wo_id=WO_ID,
    )

    assert route_after_discrepancy(result) == "QC"


def test_discrepancy_conflict_alone_routes_to_qc():
    result = DiscrepancyResult(
        wo_id=WO_ID,
        conflicts=[
            {
                "classification": "CONFLICT",
                "field": "general_contractor.name",
            }
        ],
        human_review_recommended=False,
    )

    assert route_after_discrepancy(result) == "QC"


def test_discrepancy_explicit_human_review_escalates():
    result = DiscrepancyResult(
        wo_id=WO_ID,
        human_review_recommended=True,
    )

    assert (
        route_after_discrepancy(result)
        == "HUMAN_REVIEW"
    )


def test_discrepancy_advisory_next_stage_cannot_control_router():
    result = DiscrepancyResult(
        wo_id=WO_ID,
        recommended_next_stage="COMPLETE_RECOMMENDED",
        human_review_recommended=False,
    )

    assert route_after_discrepancy(result) == "QC"


def test_discrepancy_wrong_stage_raises_error():
    result = DiscrepancyResult(
        wo_id=WO_ID,
        stage="RESEARCH",
    )

    with pytest.raises(ValueError):
        route_after_discrepancy(result)


# ============================================================
# QC ROUTER TESTS
# ============================================================


def test_qc_pass_routes_to_complete_recommended():
    result = QCResult(
        wo_id=WO_ID,
        outcome="PASS",
    )

    assert (
        route_after_qc(result)
        == "COMPLETE_RECOMMENDED"
    )


def test_qc_btp_routes_to_research_correction():
    result = QCResult(
        wo_id=WO_ID,
        outcome="BTP",
    )

    assert (
        route_after_qc(result)
        == "RESEARCH_CORRECTION"
    )


def test_qc_human_review_routes_to_human_review():
    result = QCResult(
        wo_id=WO_ID,
        outcome="HUMAN_REVIEW",
        human_review_required=True,
    )

    assert route_after_qc(result) == "HUMAN_REVIEW"


def test_qc_invalid_outcome_raises_error():
    result = QCResult(
        wo_id=WO_ID,
        outcome="COMPLETE",
    )

    with pytest.raises(ValueError):
        route_after_qc(result)


def test_qc_wrong_stage_raises_error():
    result = QCResult(
        wo_id=WO_ID,
        stage="DISCREPANCY",
        outcome="PASS",
    )

    with pytest.raises(ValueError):
        route_after_qc(result)


# ============================================================
# CORRECTION ROUTER TESTS
# ============================================================


def make_correction_result(
    *,
    wo_id=WO_ID,
    human_review_required=False,
):
    return CorrectionResult(
        wo_id=wo_id,
        corrections=[
            CorrectionItem(
                field="general_contractor.name",
                original_value="Synthetic Builder LLC",
                proposed_value="Synthetic Builders LLC",
                reason="Supported by synthetic documentary evidence.",
                evidence_ids=[
                    "E-NOC-TEST",
                    "E-PERMIT-TEST",
                ],
            )
        ],
        human_review_required=human_review_required,
    )


def test_valid_correction_routes_to_qc_review():
    state = WorkflowState(
        wo_id=WO_ID,
    )

    result = make_correction_result()

    route = route_after_correction(
        result,
        state,
    )

    assert route == "QC_REVIEW"
    assert state.correction_attempts == 1
    assert state.human_review_required is False


def test_correction_explicit_human_review_escalates():
    state = WorkflowState(
        wo_id=WO_ID,
    )

    result = make_correction_result(
        human_review_required=True,
    )

    route = route_after_correction(
        result,
        state,
    )

    assert route == "HUMAN_REVIEW"
    assert state.human_review_required is True

    # No actual correction attempt should be counted.
    assert state.correction_attempts == 0


def test_correction_without_proposals_escalates():
    state = WorkflowState(
        wo_id=WO_ID,
    )

    result = CorrectionResult(
        wo_id=WO_ID,
        corrections=[],
    )

    route = route_after_correction(
        result,
        state,
    )

    assert route == "HUMAN_REVIEW"
    assert state.human_review_required is True
    assert state.correction_attempts == 0


def test_correction_second_attempt_is_allowed():
    state = WorkflowState(
        wo_id=WO_ID,
        correction_attempts=1,
        max_correction_attempts=2,
    )

    result = make_correction_result()

    route = route_after_correction(
        result,
        state,
    )

    assert route == "QC_REVIEW"
    assert state.correction_attempts == 2
    assert state.human_review_required is False


def test_correction_third_attempt_exceeds_limit():
    state = WorkflowState(
        wo_id=WO_ID,
        correction_attempts=2,
        max_correction_attempts=2,
    )

    result = make_correction_result()

    route = route_after_correction(
        result,
        state,
    )

    assert route == "HUMAN_REVIEW"

    # Router counts the attempted correction before enforcing
    # the upper bound.
    assert state.correction_attempts == 3
    assert state.human_review_required is True


def test_correction_wo_id_mismatch_raises_error():
    state = WorkflowState(
        wo_id=WO_ID,
    )

    result = make_correction_result(
        wo_id="SYN-WO-DIFFERENT",
    )

    with pytest.raises(ValueError):
        route_after_correction(
            result,
            state,
        )

    # Invalid WO must not mutate retry state.
    assert state.correction_attempts == 0


def test_correction_wrong_stage_raises_error():
    state = WorkflowState(
        wo_id=WO_ID,
    )

    result = make_correction_result()

    result.stage = "RESEARCH"

    with pytest.raises(ValueError):
        route_after_correction(
            result,
            state,
        )

    assert state.correction_attempts == 0