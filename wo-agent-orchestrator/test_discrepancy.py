import json

from orchestrator import call_agent


WO_ID = "SYN-WO-000016"


def main() -> None:

    message = f"""
Analyze discrepancies for synthetic Work Order {WO_ID}.

Use the configured Work Order retrieval tool.

Your responsibility is comparison and discrepancy detection.

Do NOT control the actual workflow transition.

Rules:

- Use synthetic Work Order data only.
- Preserve evidence provenance.
- Compare CUSTOMER CLAIMS against DOCUMENTED EVIDENCE.
- Never silently replace a customer claim.
- UNVERIFIED is not a CONFLICT.
- MISSING is not automatically an error.
- Missing evidence is not automatically required evidence.
- Do not treat absence of Bond evidence as a discrepancy
  for a private project merely because no Bond exists.
- Do not treat absence of communications or customer approval
  as a discrepancy unless the established Work Order facts
  show that they were required.
- Participant identity and contractual relationship are separate.
- Do not invent legal requirements.
- Do not calculate legal deadlines.
- Do not make legal conclusions.
- Do not set Work Order status.
- Do not complete, mail, cancel, or return the Work Order.
- Do not search the public web for fictional synthetic identifiers.

Classify findings into:

MATCH
MISSING
CONFLICT
UNVERIFIED

Human review should be recommended only for:

- an actual unresolved material conflict,
- materially conflicting evidence sources,
- an established required confirmation that remains unresolved,
- a consequential decision unsupported by available evidence,
- or another material ambiguity that cannot safely proceed.

Return ONLY one valid JSON object.

No Markdown.
No JSON fences.
No explanatory text outside the JSON.

Use exactly this top-level structure:

{{
    "wo_id": "{WO_ID}",
    "stage": "DISCREPANCY",
    "matches": [],
    "conflicts": [],
    "missing_items": [],
    "unverified_items": [],
    "evidence_references": [],
    "human_review_recommended": false,
    "recommended_next_stage": "QC"
}}

For each item in matches, conflicts, missing_items,
and unverified_items use an object where applicable.

Example:

{{
    "field": "general_contractor",
    "customer_value": "Example Customer Claim",
    "evidence_value": "Example Evidence Value",
    "evidence_ids": ["E-NOC-000001"],
    "classification": "CONFLICT",
    "reason": "Customer claim differs from documentary evidence"
}}

Classification rules:

- matches must contain classification MATCH.
- conflicts must contain classification CONFLICT.
- missing_items must contain classification MISSING.
- unverified_items must contain classification UNVERIFIED.

recommended_next_stage:

- use "HUMAN_REVIEW" only when a material issue meets
  the human-review conditions above.
- otherwise use "QC".

Remember:

Your recommendation is advisory.
Python owns the actual workflow transition.
"""

    raw_result = call_agent(
        agent_name="wo-discrepancy-agent",
        agent_version="2",
        message=message,
        debug=False,
    )

    print(
        "\n--- RAW DISCREPANCY JSON ---"
    )

    print(raw_result)

    # Temporary syntax validation.
    #
    # In the next step we will replace this with our
    # typed DiscrepancyResult parser.

    data = json.loads(raw_result)

    print(
        "\n--- DISCREPANCY SUMMARY ---"
    )

    print(
        "WO ID:",
        data.get("wo_id"),
    )

    print(
        "Matches:",
        len(data.get("matches", [])),
    )

    print(
        "Conflicts:",
        data.get("conflicts", []),
    )

    print(
        "Missing:",
        data.get("missing_items", []),
    )

    print(
        "Unverified:",
        data.get("unverified_items", []),
    )

    print(
        "Human review recommended:",
        data.get("human_review_recommended"),
    )

    print(
        "Recommended next stage:",
        data.get("recommended_next_stage"),
    )


if __name__ == "__main__":
    main()