from datetime import datetime, timezone
from uuid import uuid4


ALLOWED_DISPOSITIONS = {
    "NEEDS_FURTHER_REVIEW",
    "ESCALATE_OPERATIONAL_REVIEW",
    "INSUFFICIENT_INFORMATION",
    "NO_FURTHER_ATTENTION",
}


class HumanReviewService:
    """
    Create governed human-review records.

    Human review is stored separately from the
    model prediction and does not overwrite it.
    """

    @staticmethod
    def create_review(
        assessment: dict,
        review_disposition: str,
        review_note: str,
        reviewer_id: str = "dashboard-analyst",
    ) -> dict:

        if review_disposition not in ALLOWED_DISPOSITIONS:
            raise ValueError(
                "Invalid review disposition: "
                f"{review_disposition}"
            )

        note = (
            review_note.strip()
            if review_note
            else ""
        )

        if not note:
            raise ValueError(
                "Review note is required."
            )

        required_assessment_fields = {
            "workflow_id",
            "project_id",
            "model_version",
            "predicted_operational_risk",
            "model_decision",
        }

        missing = (
            required_assessment_fields
            - set(assessment.keys())
        )

        if missing:
            raise ValueError(
                "Assessment missing required fields: "
                f"{sorted(missing)}"
            )

        return {
            "review_id": (
                "REV-"
                + uuid4().hex[:12].upper()
            ),

            "workflow_id":
                assessment["workflow_id"],

            "project_id":
                assessment["project_id"],

            # Preserve model evidence
            "model_version":
                assessment["model_version"],

            "predicted_operational_risk":
                float(
                    assessment[
                        "predicted_operational_risk"
                    ]
                ),

            "model_decision":
                assessment["model_decision"],

            # Separate human decision
            "review_disposition":
                review_disposition,

            "review_note":
                note,

            "reviewer_id":
                reviewer_id,

            "reviewed_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "governance": {
                "decision_type":
                    "HUMAN_OPERATIONAL_REVIEW",

                "model_prediction_overwritten":
                    False,

                "legal_rights_decision":
                    False,

                "external_action_triggered":
                    False,
            },
        }
