from agent_models import CorrectionItem, CorrectionResult
from router import route_after_correction
from workflow_state import WorkflowState


def make_correction(
    wo_id: str,
) -> CorrectionResult:
    return CorrectionResult(
        wo_id=wo_id,
        corrections=[
            CorrectionItem(
                field="general_contractor_name",
                original_value="Synthetic Builder A",
                proposed_value="Synthetic Builders A",
                reason="Synthetic documentary evidence supports correction.",
                evidence_ids=[
                    "E-NOC-TEST",
                    "E-PERMIT-TEST",
                ],
                resolution_status="PROPOSED",
            )
        ],
    )


def test_first_attempt() -> None:
    state = WorkflowState(
        wo_id="SYN-WO-TEST",
        max_correction_attempts=2,
    )

    result = make_correction(state.wo_id)

    route = route_after_correction(
        result,
        state,
    )

    assert route == "QC_REVIEW"
    assert state.correction_attempts == 1

    print("Attempt 1 -> QC_REVIEW ✅")


def test_second_attempt() -> None:
    state = WorkflowState(
        wo_id="SYN-WO-TEST",
        correction_attempts=1,
        max_correction_attempts=2,
    )

    result = make_correction(state.wo_id)

    route = route_after_correction(
        result,
        state,
    )

    assert route == "QC_REVIEW"
    assert state.correction_attempts == 2

    print("Attempt 2 -> QC_REVIEW ✅")


def test_third_attempt_blocked() -> None:
    state = WorkflowState(
        wo_id="SYN-WO-TEST",
        correction_attempts=2,
        max_correction_attempts=2,
    )

    result = make_correction(state.wo_id)

    route = route_after_correction(
        result,
        state,
    )

    assert route == "HUMAN_REVIEW"
    assert state.correction_attempts == 3
    assert state.human_review_required is True

    print("Attempt 3 -> HUMAN_REVIEW ✅")


def test_no_correction_escalates() -> None:
    state = WorkflowState(
        wo_id="SYN-WO-TEST",
    )

    result = CorrectionResult(
        wo_id=state.wo_id,
        corrections=[],
    )

    route = route_after_correction(
        result,
        state,
    )

    assert route == "HUMAN_REVIEW"
    assert state.human_review_required is True
    assert state.correction_attempts == 0

    print("No correction -> HUMAN_REVIEW ✅")


def test_explicit_human_review() -> None:
    state = WorkflowState(
        wo_id="SYN-WO-TEST",
    )

    result = CorrectionResult(
        wo_id=state.wo_id,
        corrections=[],
        unresolved_items=[
            {
                "item": "synthetic unresolved conflict",
            }
        ],
        human_review_required=True,
    )

    route = route_after_correction(
        result,
        state,
    )

    assert route == "HUMAN_REVIEW"
    assert state.human_review_required is True

    print("Unresolved conflict -> HUMAN_REVIEW ✅")


def main() -> None:
    test_first_attempt()
    test_second_attempt()
    test_third_attempt_blocked()
    test_no_correction_escalates()
    test_explicit_human_review()

    print(
        "\nAll deterministic correction routing tests passed. ✅"
    )


if __name__ == "__main__":
    main()