import json

from orchestrator import call_agent
from result_parser import parse_qc_result
from router import route_after_qc


WO_ID = "SYN-WO-000116"


CORRECTION_OVERLAY = [
    {
        "field": "general_contractor.name",
        "original_value": "Evergreen Builder LLC",
        "proposed_value": "Evergreen Builders LLC",
        "reason": (
            "Documentary evidence from the NOC and Permit "
            "supports the corrected general contractor name."
        ),
        "evidence_ids": [
            "E-NOC-000116",
            "E-PERMIT-000116",
        ],
        "resolution_status": "PROPOSED",
        "correction_attempt": 1,
    }
]


def main() -> None:

    overlay_json = json.dumps(
        CORRECTION_OVERLAY,
        indent=2,
    )

    prompt = f"""
Perform QC review for this 100% synthetic Work Order:

{WO_ID}

Use get_work_order to retrieve the original Work Order and its evidence.

A validated Research correction overlay was produced during the BTP
correction cycle.

CORRECTION OVERLAY:

{overlay_json}

Important correction-overlay rules:

1. The original Work Order remains immutable.
2. Do not pretend the original customer claim was overwritten.
3. Treat the correction overlay as a proposed working correction.
4. Verify the proposed value independently against the retrieved
   documentary evidence.
5. Do not accept the correction merely because the Research Agent
   proposed it.
6. Check that the evidence IDs actually support the proposed value.
7. If the proposed correction is supported by the documentary evidence,
   evaluate QC using that corrected working value while preserving the
   original claim for provenance.
8. If the correction is unsupported or conflicts with evidence,
   return BTP or HUMAN_REVIEW as appropriate.
9. UNVERIFIED does not mean MISSING.
10. Do not create MISSING_CONFIRMATION merely because a verification
    flag is UNVERIFIED.
11. Do not create MISSING_PARTICIPANT merely because participant
    verification status is UNVERIFIED.
12. Do not invent legal requirements.
13. Do not return COMPLETE, COMPLETED, MAILED, or CANCELLED.
14. Python owns the actual workflow transition.

For every item in "checks", result MUST be exactly one of:

PASS
FAIL
CONFLICT
MISSING
UNVERIFIED
NOT_APPLICABLE

Do not use:
FOUND
FOUND_WITH_NOTE
PARTIAL
SUPPORTED
WARNING
OK

Return ONLY one JSON object with this structure:

{{
  "wo_id": "{WO_ID}",
  "stage": "QC",
  "outcome": "PASS or BTP or HUMAN_REVIEW",
  "checks": [
    {{
      "check": "string",
      "result": "PASS",
      "reason": "string",
      "evidence_ids": ["evidence-id"]
    }}
  ],
  "btp_reasons": [],
  "material_conflicts": [],
  "unverified_items": [],
  "evidence_references": [],
  "human_review_required": false,
  "notes": []
}}

For btp_reasons, if any are necessary, use only these codes:

MISSING_PARTICIPANT
EVIDENCE_MISMATCH
MISSING_CONFIRMATION
DATA_SPELLING_ERROR
PROCESS_FAILURE
CUSTOMER_DATA_MISMATCH

PASS invariants:

- btp_reasons must be empty
- material_conflicts must be empty
- human_review_required must be false

BTP invariants:

- at least one btp_reason must exist
- human_review_required must be false

HUMAN_REVIEW invariant:

- human_review_required must be true

Do not include Markdown fences.
Do not include text before or after the JSON.
"""

    print(
        f"Calling QC Agent with correction overlay for {WO_ID}..."
    )

    raw_output = call_agent(
        agent_name="wo-qc-agent",
        agent_version="2",
        message=prompt,
    )

    print("\n--- RAW QC OUTPUT ---")
    print(raw_output)

    qc_result = parse_qc_result(
        raw_output,
        expected_wo_id=WO_ID,
    )

    print("\n--- PARSED QC RESULT ---")
    print(qc_result)

    route = route_after_qc(
        qc_result
    )

    print("\n--- DETERMINISTIC QC ROUTE ---")
    print(route)

    assert qc_result.wo_id == WO_ID
    assert qc_result.stage == "QC"

    print(
        "\nQC correction-overlay test PASSED ✅"
    )


if __name__ == "__main__":
    main()