import requests


CATEGORICAL_FEATURES = [
    "state",
    "project_type",
    "public_private",
    "customer_role",
    "hiring_party_type",
]

FLOAT_FEATURES = [
    "payment_chain_completeness_score",
    "research_confidence_score",
    "prior_escalation_rate",
]

INTEGER_FEATURES = [
    "deadline_days_remaining",
    "prior_projects_with_hiring_party",
    "expected_party_count",
    "critical_field_missing",
    "multiple_candidate_records",
    "conflicting_project_information",
]

MODEL_FEATURES = (
    CATEGORICAL_FEATURES
    + FLOAT_FEATURES
    + INTEGER_FEATURES
)


class PredictionApiClient:
    """Client for the payment-risk prediction API."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: int = 10,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def normalize_workflow(
        self,
        workflow: dict,
    ) -> dict:

        missing = [
            feature
            for feature in MODEL_FEATURES
            if feature not in workflow
        ]

        if missing:
            raise ValueError(
                f"Missing model features: {missing}"
            )

        normalized = {}

        for feature in CATEGORICAL_FEATURES:
            value = workflow[feature]

            if value is None:
                raise ValueError(
                    f"{feature} cannot be None"
                )

            normalized[feature] = str(value)

        for feature in FLOAT_FEATURES:
            value = workflow[feature]

            if value is None:
                raise ValueError(
                    f"{feature} cannot be None"
                )

            normalized[feature] = float(value)

        for feature in INTEGER_FEATURES:
            value = workflow[feature]

            if value is None:
                raise ValueError(
                    f"{feature} cannot be None"
                )

            normalized[feature] = int(value)

        return normalized

    def build_payload(
        self,
        workflow: dict,
    ) -> dict:

        return self.normalize_workflow(
            workflow
        )

    def predict(
        self,
        workflow: dict,
    ) -> dict:

        payload = self.build_payload(
            workflow
        )

        response = requests.post(
            f"{self.base_url}/v1/predict",
            json=payload,
            timeout=self.timeout_seconds,
        )

        response.raise_for_status()

        return response.json()

    def health(
        self,
    ) -> dict:

        response = requests.get(
            f"{self.base_url}/health",
            timeout=self.timeout_seconds,
        )

        response.raise_for_status()

        return response.json()
