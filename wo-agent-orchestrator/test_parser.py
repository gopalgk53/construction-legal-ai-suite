from result_parser import parse_specialist_result


sample_response = """
{
    "wo_id": "SYN-WO-000001",
    "stage": "RESEARCH",
    "human_review_required": false,
    "recommended_next_stage": "EVIDENCE",
    "material_conflicts": [],
    "unverified_items": [
        "job_amount",
        "first_day_on_job",
        "contractual_relationship"
    ],
    "evidence_references": [
        "E-PC-000001",
        "E-NOC-000001",
        "E-PERMIT-000001"
    ],
    "notes": []
}
"""


result = parse_specialist_result(
    text=sample_response,
    expected_wo_id="SYN-WO-000001",
    expected_stage="RESEARCH",
)


print("\n--- PARSED SPECIALIST RESULT ---")
print(result)

print("\n--- ROUTING FIELDS ---")
print(
    "Human review:",
    result.human_review_required,
)

print(
    "Next stage:",
    result.recommended_next_stage,
)

print(
    "Conflicts:",
    result.material_conflicts,
)

print(
    "Evidence:",
    result.evidence_references,
)