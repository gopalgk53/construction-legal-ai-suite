from dataclasses import dataclass
from typing import Optional

from orchestrator import run_workflow


@dataclass(frozen=True)
class RegressionScenario:
    wo_id: str
    expected_stage: str
    expected_human_review: bool
    expected_correction_attempts: int
    expected_min_overlay_items: int = 0


SCENARIOS = [
    RegressionScenario(
        wo_id="SYN-WO-000001",
        expected_stage="COMPLETE_RECOMMENDED",
        expected_human_review=False,
        expected_correction_attempts=0,
        expected_min_overlay_items=0,
    ),
    RegressionScenario(
        wo_id="SYN-WO-000116",
        expected_stage="COMPLETE_RECOMMENDED",
        expected_human_review=False,
        expected_correction_attempts=1,
        expected_min_overlay_items=1,
    ),
    RegressionScenario(
        wo_id="SYN-WO-000111",
        expected_stage="HUMAN_REVIEW",
        expected_human_review=True,
        expected_correction_attempts=0,
        expected_min_overlay_items=0,
    ),
]


def validate_scenario(
    scenario: RegressionScenario,
) -> tuple[bool, list[str]]:
    """
    Execute one synthetic Work Order and validate its
    deterministic terminal workflow state.
    """

    failures: list[str] = []

    try:
        state = run_workflow(scenario.wo_id)

    except Exception as exc:
        return False, [
            f"Workflow raised {type(exc).__name__}: {exc}"
        ]

    # --------------------------------------------------------
    # TERMINAL STAGE
    # --------------------------------------------------------

    if state.current_stage != scenario.expected_stage:
        failures.append(
            "Terminal stage mismatch: "
            f"expected={scenario.expected_stage}, "
            f"actual={state.current_stage}"
        )

    # --------------------------------------------------------
    # HUMAN REVIEW
    # --------------------------------------------------------

    if (
        state.human_review_required
        != scenario.expected_human_review
    ):
        failures.append(
            "Human-review mismatch: "
            f"expected={scenario.expected_human_review}, "
            f"actual={state.human_review_required}"
        )

    # --------------------------------------------------------
    # CORRECTION ATTEMPTS
    # --------------------------------------------------------

    if (
        state.correction_attempts
        != scenario.expected_correction_attempts
    ):
        failures.append(
            "Correction-attempt mismatch: "
            f"expected={scenario.expected_correction_attempts}, "
            f"actual={state.correction_attempts}"
        )

    # --------------------------------------------------------
    # OVERLAY COUNT
    # --------------------------------------------------------

    overlay_count = len(state.correction_overlay)

    if overlay_count < scenario.expected_min_overlay_items:
        failures.append(
            "Correction-overlay count below expectation: "
            f"expected at least "
            f"{scenario.expected_min_overlay_items}, "
            f"actual={overlay_count}"
        )

    # --------------------------------------------------------
    # SAFETY INVARIANT
    # --------------------------------------------------------

    if (
        state.current_stage == "HUMAN_REVIEW"
        and state.human_review_required is not True
    ):
        failures.append(
            "Safety invariant violated: HUMAN_REVIEW stage "
            "requires human_review_required=True"
        )

    return len(failures) == 0, failures


def main() -> None:

    print()
    print("=" * 72)
    print("WORK ORDER INTELLIGENCE PLATFORM")
    print("GOLDEN-PATH REGRESSION SUITE")
    print("=" * 72)

    passed = 0
    failed = 0

    results: list[
        tuple[RegressionScenario, bool, list[str]]
    ] = []

    for scenario in SCENARIOS:

        print()
        print("-" * 72)
        print(f"Running: {scenario.wo_id}")
        print("-" * 72)

        success, failures = validate_scenario(
            scenario
        )

        results.append(
            (
                scenario,
                success,
                failures,
            )
        )

        if success:
            passed += 1
            print(
                f"PASS — {scenario.wo_id}"
            )
        else:
            failed += 1
            print(
                f"FAIL — {scenario.wo_id}"
            )

            for failure in failures:
                print(
                    f"  - {failure}"
                )

    print()
    print("=" * 72)
    print("REGRESSION SUMMARY")
    print("=" * 72)

    for scenario, success, failures in results:

        status = "PASS" if success else "FAIL"

        print(
            f"{scenario.wo_id:<18} "
            f"{scenario.expected_stage:<24} "
            f"{status}"
        )

    print()
    print(
        f"Passed: {passed}/{len(SCENARIOS)}"
    )

    print(
        f"Failed: {failed}/{len(SCENARIOS)}"
    )

    if failed:
        raise SystemExit(1)

    print()
    print(
        "All golden-path regression scenarios passed."
    )


if __name__ == "__main__":
    main()