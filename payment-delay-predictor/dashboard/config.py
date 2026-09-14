AWS_REGION = "ap-southeast-2"

ATHENA_DATABASE = "construction_payment_risk_dev"

ATHENA_TABLE = "payment_risk"

ATHENA_OUTPUT = (
    "s3://construction-payment-risk-dev-gk53/"
    "athena-results/dashboard/"
)

ATHENA_POLL_INTERVAL_SECONDS = 1


# Prediction API runtime configuration
import os

PREDICTION_API_BASE_URL = os.getenv(
    "PREDICTION_API_BASE_URL",
    "http://localhost:8000",
).rstrip("/")

PREDICTION_API_TIMEOUT_SECONDS = int(
    os.getenv(
        "PREDICTION_API_TIMEOUT_SECONDS",
        "10",
    )
)
