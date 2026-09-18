from orchestrator import call_agent
from result_parser import parse_qc_result


WO_ID = "SYN-WO-000116"


def main() -> None:
    message = f"""
Perform Quality Control review for synthetic Work Order {WO_ID}.

Use the configured Work Order retrieval tool.

You are the QC specialist.

Your responsibility is to review the Work Order and determine
whether the available synthetic information supports a QC
recommendation.

IMPORTANT:

You recommend a QC outcome.
You do NOT change the Work Order status.
Python owns workflow transitions.

Review, where applicable:

- customer information alignment,
- researched evidence,
- project classification,
- participant information,
- contractual-chain information,
- Property Card,
- NOC,
- Permit,
- Bond information for applicable public-project workflows,
- confirmations,
- customer approvals,
- evidence mismatches,
- missing participants,
- spelling/data-quality problems,
- research-process issues.

Rules:

- Use synthetic Work Order data only.
- Preserve provenance.
- Never invent evidence.
- Never invent participants.
- Never invent legal requirements.
- Never calculate legal deadlines.
- Never make legal conclusions.
- Never silently resolve conflicting evidence.

Important distinction:

UNVERIFIED does not automatically mean QC failure.

MISSING does not automatically mean QC failure.

An absent Bond does not automatically mean QC failure
for a private project.

Absent communications or customer approval do not
automatically mean QC failure unless the established
workflow facts show they were required.

BTP should be recommended only when a correctable
Work Order/research/QC issue is actually established.

HUMAN_REVIEW should be recommended when a material
unresolved conflict or consequential ambiguity cannot
safely be resolved by the automated workflow.

PASS means the Work Order passes this synthetic QC review
based on the established workflow information.

Return ONLY one valid JSON object.

No Markdown.
No JSON fences.
No explanatory text outside the JSON.

Use exactly this structure:

{{
"wo_id": "{WO_ID}",
"stage": "QC",
"outcome": "PASS",
"checks": [],
"btp_reasons": [],
"material_conflicts": [],
"unverified_items": [],
"evidence_references": [],
"human_review_required": false,
"notes": []
}}

outcome must be exactly one of:

PASS
BTP
HUMAN_REVIEW

For checks use objects such as:

{{
"check": "OWNER_ALIGNMENT",
"result": "PASS",
"reason": "Customer claim aligns with documentary evidence",
"evidence_ids": ["E-PC-000001", "E-NOC-000001"]
}}

For btp_reasons:

Only include an item when outcome is BTP.

Use one of these controlled reason codes:

MISSING_PARTICIPANT
EVIDENCE_MISMATCH
MISSING_CONFIRMATION
DATA_SPELLING_ERROR
PROCESS_FAILURE
CUSTOMER_DATA_MISMATCH

Each BTP reason should use:

{{
"code": "EVIDENCE_MISMATCH",
"reason": "Explanation",
"evidence_ids": []
}}

For PASS:

- btp_reasons must be empty.
- material_conflicts must be empty.
- human_review_required must be false.

For HUMAN_REVIEW:

- human_review_required must be true.
- explain the unresolved material conflict.

Do not return COMPLETE.
Do not return COMPLETED.
Do not return MAILED.
Do not return CANCELLED.

Those are workflow/state-machine concerns outside
the QC Agent.
"""

    raw_result = call_agent(
        agent_name="wo-qc-agent",
        agent_version="2",
        message=message,
        debug=False,
    )

    print("\n--- RAW QC JSON ---")
    print(raw_result)

    # Convert the untrusted LLM response into our validated,
    # typed application-level QCResult.
    qc_result = parse_qc_result(
        raw_text=raw_result,
        expected_wo_id=WO_ID,
    )

    print("\n--- PARSED QC RESULT ---")
    print(qc_result)


if __name__ == "__main__":
    main()