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
    assert response.json() == {
        "status": "ok"
    }


def test_model_metadata():
    response = client.get("/v1/model")

    assert response.status_code == 200

    body = response.json()

    assert body["model_version"] == (
        "logistic-regression-v1"
    )

    assert body[
        "feature_contract_version"
    ] == "1.0"

    assert body["threshold"] == 0.20

    assert body["status"] == (
        "APPROVED_CHAMPION"
    )


def test_valid_prediction():
    response = client.post(
        "/v1/predict",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        abs(
            body[
                "predicted_operational_risk"
            ]
            - 0.3319541555119854
        )
        < 1e-10
    )

    assert body[
        "model_decision"
    ] == "FLAGGED_BY_MODEL"

    assert body["threshold"] == 0.20

    assert (
        len(
            body[
                "explanation"
            ]["top_factors"]
        )
        > 0
    )


def test_invalid_category_returns_422():
    payload = VALID_PAYLOAD.copy()

    payload["project_type"] = (
        "commercial_project"
    )

    response = client.post(
        "/v1/predict",
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_numeric_range_returns_422():
    payload = VALID_PAYLOAD.copy()

    payload[
        "payment_chain_completeness_score"
    ] = 1.2

    response = client.post(
        "/v1/predict",
        json=payload,
    )

    assert response.status_code == 422


def test_forbidden_extra_field_returns_422():
    payload = VALID_PAYLOAD.copy()

    payload["escalation_required"] = 1

    response = client.post(
        "/v1/predict",
        json=payload,
    )

    assert response.status_code == 422


def test_missing_required_field_returns_422():
    payload = VALID_PAYLOAD.copy()

    del payload[
        "research_confidence_score"
    ]

    response = client.post(
        "/v1/predict",
        json=payload,
    )

    assert response.status_code == 422
