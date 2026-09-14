from dashboard.repositories.athena_repository import AthenaRepository


class AnalyticsService:
    """Business analytics layer for the payment-risk dashboard."""

    def __init__(
        self,
        repository=None,
    ):
        self.repository = (
            repository
            or AthenaRepository()
        )

    def get_portfolio_summary(
        self,
    ) -> dict:

        raw = self.repository.get_portfolio_kpis()

        if not raw:
            return {}

        total = int(
            raw["total_workflows"]
        )

        critical = int(
            raw["critical_missing_count"]
        )

        multiple = int(
            raw["multiple_candidate_count"]
        )

        conflicting = int(
            raw["conflicting_info_count"]
        )

        deadline = int(
            raw["deadline_15d_count"]
        )

        return {
            "total_workflows": total,

            "avg_chain_completeness": float(
                raw[
                    "avg_chain_completeness"
                ]
            ),

            "avg_research_confidence": float(
                raw[
                    "avg_research_confidence"
                ]
            ),

            "critical_missing_count": critical,

            "critical_missing_rate": (
                critical / total
                if total
                else 0.0
            ),

            "multiple_candidate_count": multiple,

            "multiple_candidate_rate": (
                multiple / total
                if total
                else 0.0
            ),

            "conflicting_info_count": conflicting,

            "conflicting_info_rate": (
                conflicting / total
                if total
                else 0.0
            ),

            "deadline_15d_count": deadline,

            "deadline_15d_rate": (
                deadline / total
                if total
                else 0.0
            ),
        }

    def get_state_breakdown(
        self,
    ) -> list[dict]:

        rows = (
            self.repository
            .get_state_segments()
        )

        result = []

        for row in rows:

            count = int(
                row["workflow_count"]
            )

            critical = int(
                row[
                    "critical_missing_count"
                ]
            )

            result.append(
                {
                    "state": row["state"],

                    "workflow_count": count,

                    "avg_chain_completeness": float(
                        row[
                            "avg_chain_completeness"
                        ]
                    ),

                    "avg_research_confidence": float(
                        row[
                            "avg_research_confidence"
                        ]
                    ),

                    "critical_missing_count": critical,

                    "critical_missing_rate": (
                        critical / count
                        if count
                        else 0.0
                    ),
                }
            )

        return result
