from agent_models import QCResult
from router import route_after_qc


def test_pass_route() -> None:
    result = QCResult(
        wo_id="SYN-WO-000001",
        outcome="PASS",
    )

    route = route_after_qc(result)

    assert route == "COMPLETE_RECOMMENDED"
    print("PASS -> COMPLETE_RECOMMENDED ✅")


def test_btp_route() -> None:
    result = QCResult(
        wo_id="SYN-WO-000116",
        outcome="BTP",
        btp_reasons=[
            {
                "code": "DATA_SPELLING_ERROR",
                "reason": "Synthetic GC name mismatch",
                "evidence_ids": [
                    "E-NOC-000116",
                    "E-PERMIT-000116",
                ],
            }
        ],
    )

    route = route_after_qc(result)

    assert route == "RESEARCH_CORRECTION"
    print("BTP -> RESEARCH_CORRECTION ✅")


def test_human_review_route() -> None:
    result = QCResult(
        wo_id="SYN-WO-000016",
        outcome="HUMAN_REVIEW",
        human_review_required=True,
    )

    route = route_after_qc(result)

    assert route == "HUMAN_REVIEW"
    print("HUMAN_REVIEW -> HUMAN_REVIEW ✅")


def main() -> None:
    test_pass_route()
    test_btp_route()
    test_human_review_route()

    print("\nAll deterministic QC routing tests passed.")


if __name__ == "__main__":
    main()