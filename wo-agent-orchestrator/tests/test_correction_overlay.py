import pytest

from agent_models import (
    CorrectionItem,
    CorrectionResult,
)

from correction_overlay import (
    apply_correction_overlay,
    accept_correction_overlay,
    build_effective_correction_context,
)

from workflow_state import WorkflowState


WO_ID = "SYN-WO-TEST"


def make_state(
    *,
    correction_attempts=1,
):
    return WorkflowState(
        wo_id=WO_ID,
        correction_attempts=correction_attempts,
    )


def make_correction_result(
    *,
    wo_id=WO_ID,
    stage="RESEARCH_CORRECTION",
    field="general_contractor.name",
    original_value="Synthetic Builder LLC",
    proposed_value="Synthetic Builders LLC",
):
    return CorrectionResult(
        wo_id=wo_id,
        stage=stage,
        corrections=[
            CorrectionItem(
                field=field,
                original_value=original_value,
                proposed_value=proposed_value,
                reason="Supported by synthetic documentary evidence.",
                evidence_ids=[
                    "E-NOC-TEST",
                    "E-PERMIT-TEST",
                ],
                resolution_status="PROPOSED",
            )
        ],
    )


# ============================================================
# APPLY OVERLAY TESTS
# ============================================================


def test_apply_correction_overlay_stores_proposal():
    state = make_state()
    result = make_correction_result()

    apply_correction_overlay(
        state,
        result,
    )

    assert len(state.correction_overlay) == 1

    item = state.correction_overlay[0]

    assert item["field"] == "general_contractor.name"
    assert item["original_value"] == "Synthetic Builder LLC"
    assert item["proposed_value"] == "Synthetic Builders LLC"
    assert item["resolution_status"] == "PROPOSED"
    assert item["correction_attempt"] == 1


def test_apply_overlay_preserves_evidence_ids():
    state = make_state()
    result = make_correction_result()

    apply_correction_overlay(
        state,
        result,
    )

    item = state.correction_overlay[0]

    assert item["evidence_ids"] == [
        "E-NOC-TEST",
        "E-PERMIT-TEST",
    ]


def test_apply_overlay_forces_proposed_status():
    state = make_state()

    result = make_correction_result()

    result.corrections[0].resolution_status = "RESOLVED"

    apply_correction_overlay(
        state,
        result,
    )

    assert (
        state.correction_overlay[0]["resolution_status"]
        == "PROPOSED"
    )


def test_duplicate_overlay_is_not_added_twice():
    state = make_state()
    result = make_correction_result()

    apply_correction_overlay(
        state,
        result,
    )

    apply_correction_overlay(
        state,
        result,
    )

    assert len(state.correction_overlay) == 1

    assert any(
        "Duplicate correction overlay ignored"
        in entry
        for entry in state.audit_log
    )


def test_overlay_records_current_correction_attempt():
    state = make_state(
        correction_attempts=2,
    )

    result = make_correction_result()

    apply_correction_overlay(
        state,
        result,
    )

    assert (
        state.correction_overlay[0]["correction_attempt"]
        == 2
    )


def test_apply_overlay_rejects_wrong_wo_id():
    state = make_state()

    result = make_correction_result(
        wo_id="SYN-WO-DIFFERENT",
    )

    with pytest.raises(
        ValueError,
        match="does not match workflow state",
    ):
        apply_correction_overlay(
            state,
            result,
        )

    assert state.correction_overlay == []


def test_apply_overlay_rejects_wrong_stage():
    state = make_state()

    result = make_correction_result(
        stage="RESEARCH",
    )

    with pytest.raises(
        ValueError,
        match="expected stage",
    ):
        apply_correction_overlay(
            state,
            result,
        )

    assert state.correction_overlay == []


# ============================================================
# ACCEPT OVERLAY TESTS
# ============================================================


def test_accept_overlay_changes_proposed_to_accepted():
    state = make_state()
    result = make_correction_result()

    apply_correction_overlay(
        state,
        result,
    )

    accept_correction_overlay(
        state,
        "general_contractor.name",
    )

    assert (
        state.correction_overlay[0]["resolution_status"]
        == "ACCEPTED"
    )


def test_accept_overlay_adds_audit_entry():
    state = make_state()
    result = make_correction_result()

    apply_correction_overlay(
        state,
        result,
    )

    accept_correction_overlay(
        state,
        "general_contractor.name",
    )

    assert any(
        "Correction overlay accepted"
        in entry
        for entry in state.audit_log
    )


def test_accept_missing_proposal_is_rejected():
    state = make_state()

    with pytest.raises(
        ValueError,
        match="No PROPOSED correction overlay found",
    ):
        accept_correction_overlay(
            state,
            "general_contractor.name",
        )


def test_accept_already_accepted_overlay_is_rejected():
    state = make_state()
    result = make_correction_result()

    apply_correction_overlay(
        state,
        result,
    )

    accept_correction_overlay(
        state,
        "general_contractor.name",
    )

    with pytest.raises(
        ValueError,
        match="No PROPOSED correction overlay found",
    ):
        accept_correction_overlay(
            state,
            "general_contractor.name",
        )


def test_accept_multiple_proposals_for_same_field_is_rejected():
    state = make_state()

    state.correction_overlay = [
        {
            "field": "general_contractor.name",
            "original_value": "Synthetic Builder A",
            "proposed_value": "Synthetic Builder B",
            "reason": "Synthetic reason one.",
            "evidence_ids": ["E-TEST-1"],
            "resolution_status": "PROPOSED",
            "correction_attempt": 1,
        },
        {
            "field": "general_contractor.name",
            "original_value": "Synthetic Builder A",
            "proposed_value": "Synthetic Builder C",
            "reason": "Synthetic reason two.",
            "evidence_ids": ["E-TEST-2"],
            "resolution_status": "PROPOSED",
            "correction_attempt": 2,
        },
    ]

    with pytest.raises(
        ValueError,
        match="Multiple PROPOSED correction overlays",
    ):
        accept_correction_overlay(
            state,
            "general_contractor.name",
        )


# ============================================================
# EFFECTIVE CONTEXT TESTS
# ============================================================


def test_build_effective_context_contains_overlay():
    state = make_state()
    result = make_correction_result()

    apply_correction_overlay(
        state,
        result,
    )

    context = build_effective_correction_context(
        state
    )

    assert len(context) == 1
    assert context[0]["field"] == "general_contractor.name"
    assert context[0]["proposed_value"] == "Synthetic Builders LLC"
    assert context[0]["resolution_status"] == "PROPOSED"


def test_effective_context_is_separate_from_overlay():
    state = make_state()
    result = make_correction_result()

    apply_correction_overlay(
        state,
        result,
    )

    context = build_effective_correction_context(
        state
    )

    context[0]["proposed_value"] = "Changed Outside State"
    context[0]["evidence_ids"].append("E-EXTERNAL")

    assert (
        state.correction_overlay[0]["proposed_value"]
        == "Synthetic Builders LLC"
    )

    assert (
        state.correction_overlay[0]["evidence_ids"]
        == [
            "E-NOC-TEST",
            "E-PERMIT-TEST",
        ]
    )


def test_empty_overlay_returns_empty_context():
    state = make_state()

    context = build_effective_correction_context(
        state
    )

    assert context == []