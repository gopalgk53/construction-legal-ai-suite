MODEL_VERSION = "logistic-regression-v1"
FEATURE_CONTRACT_VERSION = "1.0"
FINAL_THRESHOLD = 0.20

MODEL_FEATURES = [
    "state",
    "project_type",
    "public_private",
    "customer_role",
    "hiring_party_type",
    "payment_chain_completeness_score",
    "research_confidence_score",
    "deadline_days_remaining",
    "prior_escalation_rate",
    "prior_projects_with_hiring_party",
    "expected_party_count",
    "critical_field_missing",
    "multiple_candidate_records",
    "conflicting_project_information",
]

MODEL_ARTIFACT_PATH = (
    "artifacts/logistic-regression-v1/"
    "logistic_pipeline.joblib"
)

EXPLAINABILITY_MAP_PATH = (
    "artifacts/explainability/"
    "logistic-regression-v1/"
    "business-explanation-map-v1.json"
)

MODEL_REGISTRY_PATH = (
    "artifacts/registry/"
    "model-registry-v1.json"
)
