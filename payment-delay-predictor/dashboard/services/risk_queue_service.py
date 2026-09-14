from dashboard.clients.prediction_api_client import (
    PredictionApiClient,
)
from dashboard.config import (
    PREDICTION_API_BASE_URL,
    PREDICTION_API_TIMEOUT_SECONDS,
)
from dashboard.repositories.athena_repository import (
    AthenaRepository,
)


class RiskQueueService:
    """
    Build a ranked operational review queue.

    Athena selects candidate workflows.
    Prediction API supplies model risk and explanation.
    """

    def __init__(
        self,
        repository=None,
        prediction_client=None,
    ):
        self.repository = (
            repository
            or AthenaRepository()
        )

        self.prediction_client = (
            prediction_client
            or PredictionApiClient(
                base_url=PREDICTION_API_BASE_URL,
                timeout_seconds=(
                    PREDICTION_API_TIMEOUT_SECONDS
                ),
            )
        )

    @staticmethod
    def risk_band(
        risk_score: float,
    ) -> str:
        """
        Observational dashboard bands.

        Operational model threshold remains 0.20.
        """

        if risk_score < 0.20:
            return "LOW"

        if risk_score < 0.50:
            return "MEDIUM"

        return "HIGH"

    def build_queue(
        self,
        limit: int = 25,
    ) -> list[dict]:

        candidates = (
            self.repository
            .get_candidate_workflows(
                limit=limit
            )
        )

        queue = []

        for workflow in candidates:

            try:
                prediction = (
                    self.prediction_client
                    .predict(
                        workflow
                    )
                )

            except Exception as exc:
                queue.append(
                    {
                        "record_id":
                            workflow.get(
                                "record_id"
                            ),

                        "project_id":
                            workflow.get(
                                "project_id"
                            ),

                        "state":
                            workflow.get(
                                "state"
                            ),

                        "scoring_status":
                            "FAILED",

                        "scoring_error":
                            str(exc),
                    }
                )

                continue

            risk = float(
                prediction[
                    "predicted_operational_risk"
                ]
            )

            explanation = (
                prediction.get(
                    "explanation",
                    {}
                )
            )

            top_factors = (
                explanation.get(
                    "top_factors",
                    []
                )
            )

            top_factor = (
                top_factors[0]
                if top_factors
                else {}
            )

            queue.append(
                {
                    "record_id":
                        workflow[
                            "record_id"
                        ],

                    "project_id":
                        workflow[
                            "project_id"
                        ],

                    "assessment_date":
                        workflow[
                            "assessment_date"
                        ],

                    "state":
                        workflow[
                            "state"
                        ],

                    "project_type":
                        workflow[
                            "project_type"
                        ],

                    "customer_role":
                        workflow[
                            "customer_role"
                        ],

                    "deadline_days_remaining":
                        int(
                            workflow[
                                "deadline_days_remaining"
                            ]
                        ),

                    "critical_field_missing":
                        int(
                            workflow[
                                "critical_field_missing"
                            ]
                        ),

                    "multiple_candidate_records":
                        int(
                            workflow[
                                "multiple_candidate_records"
                            ]
                        ),

                    "conflicting_project_information":
                        int(
                            workflow[
                                "conflicting_project_information"
                            ]
                        ),

                    "predicted_operational_risk":
                        risk,

                    "risk_band":
                        self.risk_band(
                            risk
                        ),

                    "threshold":
                        float(
                            prediction[
                                "threshold"
                            ]
                        ),

                    "model_decision":
                        prediction[
                            "model_decision"
                        ],

                    "model_version":
                        prediction[
                            "model_version"
                        ],

                    "top_factor":
                        top_factor.get(
                            "label"
                        ),

                    "top_factor_direction":
                        top_factor.get(
                            "direction"
                        ),

                    "top_factor_explanation":
                        top_factor.get(
                            "explanation"
                        ),

                    "explanation":
                        prediction.get(
                            "explanation",
                            {}
                        ),

                    "disclaimers":
                        prediction.get(
                            "disclaimers",
                            []
                        ),

                    "scoring_status":
                        "SUCCESS",

                    "scoring_error":
                        None,
                }
            )

        successful = [
            item
            for item in queue
            if item[
                "scoring_status"
            ] == "SUCCESS"
        ]

        failed = [
            item
            for item in queue
            if item[
                "scoring_status"
            ] != "SUCCESS"
        ]

        successful.sort(
            key=lambda item: (
                item[
                    "predicted_operational_risk"
                ]
            ),
            reverse=True,
        )

        return successful + failed
