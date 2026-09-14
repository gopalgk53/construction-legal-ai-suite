import json
from pathlib import Path

import numpy as np


def load_business_explanation_map(path: str) -> dict:
    """Load the approved business explanation allowlist."""

    map_path = Path(path)

    if not map_path.exists():
        raise FileNotFoundError(
            f"Business explanation map not found: {map_path}"
        )

    with open(map_path, "r") as f:
        return json.load(f)


def explain_workflow(
    workflow_row,
    pipeline,
    business_map: dict,
    threshold: float,
    top_n: int = 5,
) -> dict:
    """
    Generate an exact local explanation for one
    Logistic Regression workflow prediction.

    Contributions are calculated in log-odds space.
    Only approved business-facing features are returned
    in the customer-safe explanation.
    """

    if len(workflow_row) != 1:
        raise ValueError(
            "workflow_row must contain exactly one row."
        )

    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]

    probability = float(
        pipeline.predict_proba(workflow_row)[0, 1]
    )

    decision = (
        "FLAGGED_BY_MODEL"
        if probability >= threshold
        else "NOT_FLAGGED_BY_MODEL"
    )

    transformed = preprocessor.transform(
        workflow_row
    )

    if hasattr(transformed, "toarray"):
        transformed_values = transformed.toarray()[0]
    else:
        transformed_values = np.asarray(
            transformed
        )[0]

    feature_names = (
        preprocessor.get_feature_names_out()
    )

    coefficients = model.coef_[0]
    intercept = float(model.intercept_[0])

    contributions = (
        transformed_values * coefficients
    )

    reconstructed_log_odds = (
        intercept + contributions.sum()
    )

    reconstructed_probability = float(
        1 / (
            1 + np.exp(
                -reconstructed_log_odds
            )
        )
    )

    reconstruction_error = abs(
        probability -
        reconstructed_probability
    )

    approved_factors = []

    for (
        feature_name,
        coefficient,
        contribution,
    ) in zip(
        feature_names,
        coefficients,
        contributions,
    ):

        contribution = float(
            contribution
        )

        base_feature = None

        for prefix in [
            "numeric__",
            "binary__",
        ]:
            if feature_name.startswith(prefix):
                base_feature = feature_name.replace(
                    prefix,
                    "",
                    1,
                )
                break

        if base_feature not in business_map:
            continue

        if abs(contribution) < 1e-8:
            continue

        direction = (
            "higher"
            if contribution > 0
            else "lower"
        )

        config = business_map[
            base_feature
        ]

        approved_factors.append(
            {
                "feature": base_feature,
                "label": config["label"],
                "direction": direction,
                "contribution_log_odds":
                    contribution,
                "absolute_contribution":
                    abs(contribution),
                "explanation":
                    config[direction],
            }
        )

    approved_factors = sorted(
        approved_factors,
        key=lambda item:
            item["absolute_contribution"],
        reverse=True,
    )[:top_n]

    return {
        "predicted_operational_risk":
            probability,

        "threshold":
            threshold,

        "model_decision":
            decision,

        "explanation": {
            "top_factors":
                approved_factors,

            "method":
                "exact_logistic_regression_"
                "log_odds_decomposition",

            "reconstruction_error":
                reconstruction_error,
        },

        "disclaimers": [
            (
                "Explanation describes model "
                "associations, not causation."
            ),
            (
                "Prediction does not determine "
                "legal rights or provide legal advice."
            ),
            (
                "Model was evaluated using synthetic "
                "construction payment-protection data."
            ),
        ],
    }
