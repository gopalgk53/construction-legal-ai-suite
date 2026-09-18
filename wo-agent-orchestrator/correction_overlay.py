from agent_models import CorrectionResult
from workflow_state import WorkflowState


def apply_correction_overlay(
    state: WorkflowState,
    result: CorrectionResult,
) -> None:
    """
    Store proposed corrections separately from the immutable source
    Work Order.

    Duplicate proposals are not appended again.
    """

    if result.wo_id != state.wo_id:
        raise ValueError(
            "Correction Work Order ID does not match workflow state."
        )

    if result.stage != "RESEARCH_CORRECTION":
        raise ValueError(
            "apply_correction_overlay expected stage "
            f"'RESEARCH_CORRECTION', received {result.stage!r}."
        )

    for correction in result.corrections:

        # ----------------------------------------------------
        # DEDUPLICATION
        # ----------------------------------------------------

        duplicate = any(
            existing.get("field") == correction.field
            and existing.get("original_value")
            == correction.original_value
            and existing.get("proposed_value")
            == correction.proposed_value
            for existing in state.correction_overlay
        )

        if duplicate:
            state.audit_log.append(
                f"Duplicate correction overlay ignored for "
                f"{correction.field}"
            )
            continue

        # ----------------------------------------------------
        # STORE PROPOSAL
        # ----------------------------------------------------

        overlay_item = {
            "field": correction.field,
            "original_value": correction.original_value,
            "proposed_value": correction.proposed_value,
            "reason": correction.reason,
            "evidence_ids": list(correction.evidence_ids),

            # Research only proposes the correction.
            "resolution_status": "PROPOSED",

            "correction_attempt": state.correction_attempts,
        }

        state.correction_overlay.append(overlay_item)

        state.audit_log.append(
            f"Correction overlay added for "
            f"{correction.field} "
            f"at attempt {state.correction_attempts}"
        )

def accept_correction_overlay(
    state: WorkflowState,
    field: str,
) -> None:
    """
    Mark a proposed correction as accepted for workflow processing.

    This changes only the workflow overlay.

    It does NOT mutate the original Work Order in S3.
    """

    matching_items = [
        item
        for item in state.correction_overlay
        if item.get("field") == field
        and item.get("resolution_status") == "PROPOSED"
    ]

    if not matching_items:
        raise ValueError(
            f"No PROPOSED correction overlay found for {field!r}."
        )

    if len(matching_items) > 1:
        raise ValueError(
            f"Multiple PROPOSED correction overlays found for {field!r}."
        )

    item = matching_items[0]

    item["resolution_status"] = "ACCEPTED"

    state.audit_log.append(
        f"Correction overlay accepted for {field}"
    )

def build_effective_correction_context(
    state: WorkflowState,
) -> list[dict]:
    """
    Build the correction context supplied to QC.

    The original Work Order remains immutable.

    QC receives proposed/accepted overlay information so it can
    evaluate the effective workflow state.
    """

    return [
        {
            "field": item["field"],
            "original_value": item["original_value"],
            "proposed_value": item["proposed_value"],
            "reason": item["reason"],
            "evidence_ids": list(item["evidence_ids"]),
            "resolution_status": item["resolution_status"],
            "correction_attempt": item["correction_attempt"],
        }
        for item in state.correction_overlay
    ]