from agent_models import SpecialistResult
from router import route_after_research


# ============================================================
# TEST 1 — CLEAN WORK ORDER
# ============================================================

clean_result = SpecialistResult(
    wo_id="SYN-WO-000001",
    stage="RESEARCH",
    human_review_required=False,
    recommended_next_stage="EVIDENCE",
    material_conflicts=[],
    unverified_items=[
        "job_amount",
    ],
    evidence_references=[
        "E-PC-000001",
        "E-NOC-000001",
        "E-PERMIT-000001",
    ],
)


clean_route = route_after_research(
    clean_result
)


assert clean_route == "EVIDENCE"


print(
    "CLEAN TEST PASSED:",
    clean_route,
)


# ============================================================
# TEST 2 — MATERIAL CONFLICT
# ============================================================

conflict_result = SpecialistResult(
    wo_id="SYN-WO-000016",
    stage="RESEARCH",
    human_review_required=True,
    recommended_next_stage="HUMAN_REVIEW",
    material_conflicts=[
        "General contractor conflict"
    ],
    evidence_references=[
        "E-PC-000016",
        "E-NOC-000016",
        "E-PERMIT-000016",
    ],
)


conflict_route = route_after_research(
    conflict_result
)


assert conflict_route == "HUMAN_REVIEW"


print(
    "CONFLICT TEST PASSED:",
    conflict_route,
)


# ============================================================
# TEST 3 — LLM CANNOT OVERRIDE ROUTER
# ============================================================

bad_recommendation = SpecialistResult(
    wo_id="SYN-WO-000001",
    stage="RESEARCH",
    human_review_required=False,

    # Imagine the LLM generated something wrong.
    recommended_next_stage="HUMAN_REVIEW",

    material_conflicts=[],
)


deterministic_route = route_after_research(
    bad_recommendation
)


assert deterministic_route == "EVIDENCE"


print(
    "DETERMINISTIC CONTROL TEST PASSED:",
    deterministic_route,
)


print(
    "\nALL RESEARCH ROUTER TESTS PASSED"
)