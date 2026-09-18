from agent_models import DiscrepancyResult
from router import route_after_discrepancy


def main() -> None:

    # --------------------------------------------------------
    # Test 1: clean result
    # --------------------------------------------------------

    clean = DiscrepancyResult(
        wo_id="SYN-WO-000001",
        conflicts=[],
        human_review_recommended=False,
        recommended_next_stage="QC",
    )

    clean_route = route_after_discrepancy(
        clean
    )

    assert clean_route == "QC"

    print(
        "CLEAN TEST PASSED:",
        clean_route,
    )

    # --------------------------------------------------------
    # Test 2: material conflict
    # --------------------------------------------------------

    conflict = DiscrepancyResult(
        wo_id="SYN-WO-000016",
        conflicts=[
            {
                "field": "general_contractor",
                "classification": "CONFLICT",
            }
        ],
        human_review_recommended=True,
        recommended_next_stage="HUMAN_REVIEW",
    )

    conflict_route = route_after_discrepancy(
        conflict
    )

    assert conflict_route == "HUMAN_REVIEW"

    print(
        "CONFLICT TEST PASSED:",
        conflict_route,
    )

    # --------------------------------------------------------
    # Test 3:
    # prove the LLM recommendation cannot control routing
    # --------------------------------------------------------

    adversarial_recommendation = (
        DiscrepancyResult(
            wo_id="SYN-WO-000001",
            conflicts=[],
            human_review_recommended=False,

            # Deliberately wrong recommendation.
            recommended_next_stage="HUMAN_REVIEW",
        )
    )

    deterministic_route = (
        route_after_discrepancy(
            adversarial_recommendation
        )
    )

    assert deterministic_route == "QC"

    print(
        "DETERMINISTIC CONTROL TEST PASSED:",
        deterministic_route,
    )

    # --------------------------------------------------------
    # Test 4:
    # UNVERIFIED alone must not trigger human review
    # --------------------------------------------------------

    unverified_only = DiscrepancyResult(
        wo_id="SYN-WO-000001",
        conflicts=[],
        unverified_items=[
            {
                "field": "job_amount",
                "classification": "UNVERIFIED",
            }
        ],
        human_review_recommended=False,
        recommended_next_stage="QC",
    )

    unverified_route = (
        route_after_discrepancy(
            unverified_only
        )
    )

    assert unverified_route == "QC"

    print(
        "UNVERIFIED TEST PASSED:",
        unverified_route,
    )

    print(
        "\nALL DISCREPANCY ROUTER TESTS PASSED."
    )


if __name__ == "__main__":
    main()