import json

from orchestrator import call_agent
from result_parser import parse_correction_result
from router import route_after_correction
from correction_overlay import apply_correction_overlay
from workflow_state import WorkflowState


WO_ID = "SYN-WO-000116"


def main() -> None:
    state = WorkflowState(
        wo_id=WO_ID,
        current_stage="RESEARCH_CORRECTION",
    )

    prompt = f"""
You are operating in RESEARCH_CORRECTION mode.

Work Order:
{WO_ID}

This is a 100% synthetic benchmark Work Order.

Use the get_work_order tool to retrieve the Work Order.

Your task is to investigate the discrepancy and propose a correction
artifact based only on evidence actually present in the Work Order.

Important rules:

1. Do not modify the original Work Order.
2. Preserve the original customer claim.
3. Compare the customer claim against documentary evidence.
4. Do not invent evidence.
5. Do not invent legal requirements.
6. UNVERIFIED does not mean MISSING.
7. Do not mark something missing merely because a verification flag
   says UNVERIFIED.
8. A proposed correction must cite the evidence IDs that support it.
9. Return PROPOSED for a correction proposal.
10. Do NOT claim that a proposed correction has already been applied.
11. Do NOT return RESOLVED merely because you proposed a value.
12. If the evidence cannot support a correction, place the issue in
    unresolved_items and set human_review_required to true.

Return ONLY one JSON object with exactly this structure:

{{
  "wo_id": "{WO_ID}",
  "stage": "RESEARCH_CORRECTION",
  "corrections": [
    {{
      "field": "string",
      "original_value": "value from original customer claim",
      "proposed_value": "value supported by evidence",
      "reason": "short evidence-grounded explanation",
      "evidence_ids": ["evidence-id"],
      "resolution_status": "PROPOSED"
    }}
  ],
  "unresolved_items": [],
  "evidence_references": ["evidence-id"],
  "human_review_required": false,
  "notes": []
}}

Do not include Markdown fences.
Do not include text before or after the JSON.
"""

    print(
        f"Calling Research Agent for correction of {WO_ID}..."
    )

    raw_output = call_agent(
        agent_name="wo-research-agent",
        agent_version="5",
        message=prompt,
    )

    print("\n--- RAW RESEARCH CORRECTION OUTPUT ---")
    print(raw_output)

    correction_result = parse_correction_result(
        raw_output,
        expected_wo_id=WO_ID,
    )

    print("\n--- PARSED CORRECTION RESULT ---")
    print(correction_result)

    route = route_after_correction(
        correction_result,
        state,
    )

    print("\n--- DETERMINISTIC ROUTE ---")
    print(route)

    if route == "QC_REVIEW":
        apply_correction_overlay(
            state,
            correction_result,
        )

    print("\n--- CORRECTION ATTEMPTS ---")
    print(state.correction_attempts)

    print("\n--- CORRECTION OVERLAY ---")
    print(
        json.dumps(
            state.correction_overlay,
            indent=2,
        )
    )

    print("\n--- AUDIT LOG ---")
    for event in state.audit_log:
        print(event)

    assert correction_result.wo_id == WO_ID
    assert correction_result.stage == "RESEARCH_CORRECTION"

    if route == "QC_REVIEW":
        assert state.correction_attempts == 1
        assert len(state.correction_overlay) > 0

    print(
        "\nReal Research Correction test PASSED ✅"
    )


if __name__ == "__main__":
    main()