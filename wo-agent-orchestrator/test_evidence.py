from orchestrator import call_agent
from result_parser import parse_evidence_result


WO_ID = "SYN-WO-000001"


def main() -> None:

    message = f"""
Extract and organize evidence for synthetic Work Order {WO_ID}.

Use the configured Work Order retrieval tool.

This is an evidence extraction task, not a workflow
decision task.

Rules:

- Use synthetic Work Order evidence only.
- Preserve evidence provenance.
- Never invent evidence.
- Never invent an evidence ID.
- Keep CUSTOMER CLAIM separate from DOCUMENTED EVIDENCE.
- Keep participant identity separate from contractual relationship.
- UNVERIFIED does not mean CONFLICT.
- MISSING does not automatically mean required.
- Do not make legal conclusions.
- Do not calculate legal deadlines.
- Do not decide whether the Work Order should be completed,
  mailed, cancelled, or returned for correction.
- Do not search the public web for fictional synthetic identifiers.

Return ONLY one valid JSON object.

No Markdown.
No ```json fences.
No explanatory text outside the JSON.

Use exactly this structure:

{{
    "wo_id": "{WO_ID}",
    "stage": "EVIDENCE",
    "evidence_facts": [],
    "participants_found": [],
    "contractual_relationships_supported": [],
    "confirmations_found": [],
    "approvals_found": [],
    "unverified_items": [],
    "potential_conflicts": [],
    "evidence_gaps": [],
    "evidence_references": []
}}

Requirements:

evidence_facts:
- concise documented facts with their evidence ID.

participants_found:
- participants actually present in customer input or evidence.
- identify whether customer-claimed or documented where useful.

contractual_relationships_supported:
- only relationships explicitly supported by available evidence.
- participant co-occurrence alone must not be treated as
  proof of a contractual relationship.

confirmations_found:
- direct confirmations actually present.

approvals_found:
- customer approvals actually present.

unverified_items:
- facts that remain unverified.

potential_conflicts:
- potential claim-versus-evidence conflicts.
- do not resolve them.

evidence_gaps:
- evidence that is absent.
- absence does not automatically mean the evidence was required.

evidence_references:
- only evidence IDs actually retrieved from this Work Order.
"""

    raw_result = call_agent(
        agent_name="wo-evidence-agent",
        agent_version="3",
        message=message,
        debug=False,
    )

    print("\n--- RAW EVIDENCE JSON ---")
    print(raw_result)

    parsed_result = parse_evidence_result(
        text=raw_result,
        expected_wo_id=WO_ID,
    )

    print("\n--- VALIDATED EVIDENCE RESULT ---")
    print(parsed_result)

    print("\n--- EVIDENCE SUMMARY ---")

    print(
        "WO ID:",
        parsed_result.wo_id,
    )

    print(
        "Evidence facts:",
        len(parsed_result.evidence_facts),
    )

    print(
        "Participants:",
        parsed_result.participants_found,
    )

    print(
        "Potential conflicts:",
        parsed_result.potential_conflicts,
    )

    print(
        "Evidence references:",
        parsed_result.evidence_references,
    )


if __name__ == "__main__":
    main()