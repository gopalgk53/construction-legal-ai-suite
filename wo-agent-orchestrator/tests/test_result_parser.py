import json

import pytest

from result_parser import (
    extract_json_object,
    parse_qc_result,
)


WO_ID = "SYN-WO-TEST"


# ============================================================
# STEP 20D.1
# RAW JSON EXTRACTION TESTS
# ============================================================


def test_extract_plain_json_object():
    raw = '{"wo_id": "SYN-WO-TEST"}'

    extracted = extract_json_object(raw)

    assert extracted == raw


def test_extract_json_with_explanatory_text():
    raw = (
        'Agent analysis complete.\n'
        '{"wo_id": "SYN-WO-TEST", "stage": "RESEARCH"}\n'
        'End of response.'
    )

    extracted = extract_json_object(raw)

    data = json.loads(extracted)

    assert data["wo_id"] == WO_ID
    assert data["stage"] == "RESEARCH"


def test_extract_handles_braces_inside_json_string():
    raw = (
        '{"wo_id": "SYN-WO-TEST", '
        '"notes": "Synthetic text containing { braces } safely."}'
    )

    extracted = extract_json_object(raw)

    data = json.loads(extracted)

    assert data["wo_id"] == WO_ID
    assert "{ braces }" in data["notes"]


def test_extract_empty_output_rejected():
    with pytest.raises(
        ValueError,
        match="empty output",
    ):
        extract_json_object("")


def test_extract_non_string_rejected():
    with pytest.raises(
        ValueError,
        match="must be a string",
    ):
        extract_json_object(None)


def test_extract_without_json_object_rejected():
    raw = "Agent returned no structured output."

    with pytest.raises(
        ValueError,
        match="No JSON object found",
    ):
        extract_json_object(raw)


def test_extract_incomplete_json_object_rejected():
    raw = '{"wo_id": "SYN-WO-TEST"'

    with pytest.raises(
        ValueError,
        match="Incomplete JSON object",
    ):
        extract_json_object(raw)


# ============================================================
# STEP 20D.2
# QC PARSER SAFETY TESTS
# ============================================================


def make_qc_payload(
    *,
    wo_id=WO_ID,
    stage="QC",
    outcome="PASS",
    checks=None,
    btp_reasons=None,
    material_conflicts=None,
    unverified_items=None,
    evidence_references=None,
    human_review_required=False,
    notes=None,
):
    return {
        "wo_id": wo_id,
        "stage": stage,
        "outcome": outcome,
        "checks": [] if checks is None else checks,
        "btp_reasons": [] if btp_reasons is None else btp_reasons,
        "material_conflicts": (
            []
            if material_conflicts is None
            else material_conflicts
        ),
        "unverified_items": (
            []
            if unverified_items is None
            else unverified_items
        ),
        "evidence_references": (
            []
            if evidence_references is None
            else evidence_references
        ),
        "human_review_required": human_review_required,
        "notes": [] if notes is None else notes,
    }


def parse_payload(payload):
    return parse_qc_result(
        json.dumps(payload),
        expected_wo_id=WO_ID,
    )


def test_qc_valid_pass_is_accepted():
    payload = make_qc_payload(
        outcome="PASS",
    )

    result = parse_payload(payload)

    assert result.wo_id == WO_ID
    assert result.stage == "QC"
    assert result.outcome == "PASS"
    assert result.human_review_required is False


def test_qc_wrong_wo_id_is_rejected():
    payload = make_qc_payload(
        wo_id="SYN-WO-DIFFERENT",
    )

    with pytest.raises(
        ValueError,
        match="wo_id mismatch",
    ):
        parse_payload(payload)


def test_qc_wrong_stage_is_rejected():
    payload = make_qc_payload(
        stage="DISCREPANCY",
    )

    with pytest.raises(
        ValueError,
        match="stage must be",
    ):
        parse_payload(payload)


def test_qc_invalid_outcome_is_rejected():
    payload = make_qc_payload(
        outcome="COMPLETE",
    )

    with pytest.raises(
        ValueError,
        match="Invalid QC outcome",
    ):
        parse_payload(payload)


def test_qc_pass_with_btp_reason_is_rejected():
    payload = make_qc_payload(
        outcome="PASS",
        btp_reasons=[
            {
                "code": "CUSTOMER_DATA_MISMATCH",
                "reason": "Synthetic mismatch.",
                "evidence_ids": ["E-NOC-TEST"],
            }
        ],
    )

    with pytest.raises(
        ValueError,
        match="PASS cannot contain BTP reasons",
    ):
        parse_payload(payload)


def test_qc_pass_with_material_conflict_is_rejected():
    payload = make_qc_payload(
        outcome="PASS",
        material_conflicts=[
            {
                "field": "general_contractor.name",
                "reason": "Synthetic documentary conflict.",
                "evidence_ids": [
                    "E-NOC-TEST",
                    "E-PERMIT-TEST",
                ],
            }
        ],
    )

    with pytest.raises(
        ValueError,
        match="PASS cannot contain material conflicts",
    ):
        parse_payload(payload)


def test_qc_pass_with_human_review_is_rejected():
    payload = make_qc_payload(
        outcome="PASS",
        human_review_required=True,
    )

    with pytest.raises(
        ValueError,
        match="PASS cannot require human review",
    ):
        parse_payload(payload)


def test_qc_btp_without_reason_is_rejected():
    payload = make_qc_payload(
        outcome="BTP",
        btp_reasons=[],
    )

    with pytest.raises(
        ValueError,
        match="BTP must contain at least one BTP reason",
    ):
        parse_payload(payload)


def test_qc_btp_with_valid_reason_is_accepted():
    payload = make_qc_payload(
        outcome="BTP",
        btp_reasons=[
            {
                "code": "CUSTOMER_DATA_MISMATCH",
                "reason": "Synthetic customer claim differs.",
                "evidence_ids": [
                    "E-NOC-TEST",
                    "E-PERMIT-TEST",
                ],
            }
        ],
    )

    result = parse_payload(payload)

    assert result.outcome == "BTP"
    assert len(result.btp_reasons) == 1
    assert result.human_review_required is False


def test_qc_btp_with_invalid_code_is_rejected():
    payload = make_qc_payload(
        outcome="BTP",
        btp_reasons=[
            {
                "code": "LLM_INVENTED_REASON",
                "reason": "Synthetic invalid reason.",
                "evidence_ids": ["E-TEST"],
            }
        ],
    )

    with pytest.raises(
        ValueError,
        match="Invalid QC BTP code",
    ):
        parse_payload(payload)


def test_qc_btp_and_human_review_together_is_rejected():
    payload = make_qc_payload(
        outcome="BTP",
        btp_reasons=[
            {
                "code": "EVIDENCE_MISMATCH",
                "reason": "Synthetic evidence mismatch.",
                "evidence_ids": ["E-TEST"],
            }
        ],
        human_review_required=True,
    )

    with pytest.raises(
        ValueError,
        match="cannot simultaneously require",
    ):
        parse_payload(payload)


def test_qc_human_review_without_flag_is_rejected():
    payload = make_qc_payload(
        outcome="HUMAN_REVIEW",
        human_review_required=False,
    )

    with pytest.raises(
        ValueError,
        match="requires human_review_required=true",
    ):
        parse_payload(payload)


def test_qc_valid_human_review_is_accepted():
    payload = make_qc_payload(
        outcome="HUMAN_REVIEW",
        material_conflicts=[
            {
                "field": "general_contractor.name",
                "reason": "Two synthetic documents disagree.",
                "evidence_ids": [
                    "E-NOC-TEST",
                    "E-PERMIT-TEST",
                ],
            }
        ],
        human_review_required=True,
    )

    result = parse_payload(payload)

    assert result.outcome == "HUMAN_REVIEW"
    assert result.human_review_required is True
    assert len(result.material_conflicts) == 1