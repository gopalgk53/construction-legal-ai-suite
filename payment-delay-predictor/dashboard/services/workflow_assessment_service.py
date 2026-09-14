class WorkflowAssessmentService:
    """Prepare one scored workflow for dashboard review."""

    @staticmethod
    def build_assessment(
        queue_item: dict,
    ) -> dict:

        required = {
            "record_id",
            "project_id",
            "state",
            "project_type",
            "customer_role",
            "deadline_days_remaining",
            "predicted_operational_risk",
            "risk_band",
            "threshold",
            "model_decision",
            "model_version",
            "top_factor",
            "top_factor_explanation",
            "scoring_status",
        }

        missing = (
            required
            - set(queue_item.keys())
        )

        if missing:
            raise ValueError(
                f"Missing assessment fields: "
                f"{sorted(missing)}"
            )

        if (
            queue_item["scoring_status"]
            != "SUCCESS"
        ):
            raise ValueError(
                "Cannot build assessment "
                "for failed scoring result."
            )

        return {
            "workflow_id":
                queue_item["record_id"],

            "project_id":
                queue_item["project_id"],

            "state":
                queue_item["state"],

            "project_type":
                queue_item["project_type"],

            "customer_role":
                queue_item["customer_role"],

            "deadline_days_remaining":
                queue_item[
                    "deadline_days_remaining"
                ],

            "predicted_operational_risk":
                float(
                    queue_item[
                        "predicted_operational_risk"
                    ]
                ),

            "risk_band":
                queue_item["risk_band"],

            "threshold":
                float(
                    queue_item["threshold"]
                ),

            "model_decision":
                queue_item[
                    "model_decision"
                ],

            "model_version":
                queue_item[
                    "model_version"
                ],

            "top_factor":
                queue_item[
                    "top_factor"
                ],

            "top_factor_explanation":
                queue_item[
                    "top_factor_explanation"
                ],

            "explanation":
                queue_item.get(
                    "explanation",
                    {}
                ),

            "disclaimers":
                queue_item.get(
                    "disclaimers",
                    []
                ),
        }
