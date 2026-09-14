from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VALID_PAYLOAD = {
    "state": "FL",
    "project_type": "commercial",
    "public_private": "private",
    "customer_role": "material_supplier",
    "hiring_party_type": "general_contractor",
    "payment_chain_completeness_score": 0.72,
    "research_confidence_score": 0.81,
    "deadline_days_remaining": 24,
    "prior_escalation_rate": 0.18,
    "prior_projects_with_hiring_party": 3,
    "expected_party_count": 5,
    "critical_field_missing": 0,
    "multiple_candidate_records": 1,
    "conflicting_project_information": 0,
}


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_model_metadata():
    response = client.get("/v1/model")

    assert response.status_code == 200

    body = response.json()

    assert body["model_version"] == "logistic-regression-v1"
    assert body["feature_contract_version"] == "1.0"
    assert body["threshold"] == 0.20
    assert body["status"] == "APPROVED_CHAMPION"


@patch("app.main.predict_workflow")
def test_prediction_contract(mock_predict):
    mock_predict.return_value = {
        "model_version": "logistic-regression-v1",
        "predicted_operational_risk": 0.33,
        "threshold": 0.20,
        "model_decision": "FLAGGED_BY_MODEL",
        "explanation": {
            "top_factors": [
                {
                    "feature": "research_confidence_score",
                    "direction": "LOWER_RISK",
                    "strength": 0.5,
                    "explanation": "Test explanation.",
                }
            ],
            "method": "exact_logistic_regression_log_odds_decomposition",
        },
        "disclaimers": [
            "Operational prioritization only."
        ],
    }

    response = client.post(
        "/v1/predict",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["model_version"] == "logistic-regression-v1"
    assert body["model_decision"] == "FLAGGED_BY_MODEL"
    assert body["threshold"] == 0.20

    mock_predict.assert_called_once()


def test_invalid_category_returns_422():
    payload = VALID_PAYLOAD.copy()
    payload["project_type"] = "commercial_project"

    response = client.post("/v1/predict", json=payload)

    assert response.status_code == 422


def test_invalid_numeric_range_returns_422():
    payload = VALID_PAYLOAD.copy()
    payload["payment_chain_completeness_score"] = 1.2

    response = client.post("/v1/predict", json=payload)

    assert response.status_code == 422


def test_forbidden_extra_field_returns_422():
    payload = VALID_PAYLOAD.copy()
    payload["escalation_required"] = 1

    response = client.post("/v1/predict", json=payload)

    assert response.status_code == 422


def test_missing_required_field_returns_422():
    payload = VALID_PAYLOAD.copy()
    del payload["research_confidence_score"]

    response = client.post("/v1/predict", json=payload)

    assert response.status_code == 422

@patch("app.main.emit_metric")
@patch("app.main.predict_workflow")
def test_prediction_contract(
    mock_predict,
    mock_emit_metric,
):
    mock_predict.return_value = {
        "model_version": "logistic-regression-v1",
        "predicted_operational_risk": 0.33,
        "threshold": 0.20,
        "model_decision": "FLAGGED_BY_MODEL",
        "explanation": {
            "top_factors": [
                {
                    "feature": "research_confidence_score",
                    "label": "Research confidence",
                    "direction": "lower",
                    "contribution_log_odds": -0.50,
                    "absolute_contribution": 0.50,
                    "explanation": (
                        "Higher research confidence is "
                        "associated with lower operational risk."
                    ),
                }
            ],
            "method": (
                "exact_logistic_regression_"
                "log_odds_decomposition"
            ),
        },
        "disclaimers": [
            "Operational prioritization only."
        ],
    }

    response = client.post(
        "/v1/predict",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["model_version"]
        == "logistic-regression-v1"
    )
    assert (
        body["predicted_operational_risk"]
        == 0.33
    )
    assert (
        body["model_decision"]
        == "FLAGGED_BY_MODEL"
    )
    assert body["threshold"] == 0.20
    assert len(
        body["explanation"]["top_factors"]
    ) == 1

    mock_predict.assert_called_once()
    assert mock_emit_metric.called

    prediction_count_calls = [
        call
        for call in mock_emit_metric.call_args_list
        if call.kwargs.get("metric_name")
        == "PredictionCount"
    ]

    assert len(prediction_count_calls) == 1

    flagged_count_calls = [
        call
        for call in mock_emit_metric.call_args_list
        if call.kwargs.get("metric_name")
        == "FlaggedCount"
    ]

    assert len(flagged_count_calls) == 1