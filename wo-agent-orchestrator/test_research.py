from orchestrator import call_agent
from result_parser import parse_specialist_result


WO_ID = "SYN-WO-000016"


def main() -> None:

    message = f"""
Research synthetic Work Order {WO_ID}.

Use the configured Work Order retrieval tool and available
synthetic evidence.

Important rules:

- Preserve evidence provenance.
- Distinguish CUSTOMER CLAIM from DOCUMENTED EVIDENCE.
- UNVERIFIED does not mean CONFLICT.
- MISSING does not automatically mean required.
- Participant identity and contractual relationship are separate.
- Do not invent legal requirements, deadlines, or workflow rules.
- Do not search the public web for fictional synthetic identifiers.

Return ONLY one valid JSON object.

Do not include Markdown.
Do not include ```json fences.
Do not include explanatory text before or after the JSON.

Use exactly this structure:

{{
    "wo_id": "{WO_ID}",
    "stage": "RESEARCH",
    "human_review_required": false,
    "recommended_next_stage": "EVIDENCE",
    "material_conflicts": [],
    "unverified_items": [],
    "evidence_references": [],
    "notes": []
}}

Field rules:

human_review_required:
- true only when a material conflict or established unresolved
  requirement requires human review.
- otherwise false.

recommended_next_stage:
- must be "EVIDENCE" when human review is not required.
- must be "HUMAN_REVIEW" when human review is required.

material_conflicts:
- short descriptions of actual material conflicts only.

unverified_items:
- short names/descriptions of facts that remain unverified.

evidence_references:
- evidence IDs actually found in the Work Order.
- never invent an evidence ID.

notes:
- only important research notes that downstream agents need.
- do not place long narrative analysis here.
"""

    raw_result = call_agent(
        agent_name="wo-research-agent",
        agent_version="5",
        message=message,
        debug=False,
    )

    print("\n--- RAW AGENT JSON ---")
    print(raw_result)

    parsed_result = parse_specialist_result(
        text=raw_result,
        expected_wo_id=WO_ID,
        expected_stage="RESEARCH",
    )

    print("\n--- VALIDATED SPECIALIST RESULT ---")
    print(parsed_result)

    print("\n--- ROUTING DATA ---")
    print(
        "Human review:",
        parsed_result.human_review_required,
    )

    print(
        "Recommended next stage:",
        parsed_result.recommended_next_stage,
    )

    print(
        "Material conflicts:",
        parsed_result.material_conflicts,
    )

    print(
        "Unverified items:",
        parsed_result.unverified_items,
    )

    print(
        "Evidence references:",
        parsed_result.evidence_references,
    )


if __name__ == "__main__":
    main()