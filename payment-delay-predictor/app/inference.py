from functools import lru_cache

import joblib
import pandas as pd

from app.config import (
    MODEL_VERSION,
    FINAL_THRESHOLD,
    MODEL_FEATURES,
    MODEL_ARTIFACT_PATH,
    EXPLAINABILITY_MAP_PATH,
)

from app.schemas import (
    PredictionRequest,
    PredictionResponse,
)

from app.explainability import (
    explain_workflow,
    load_business_explanation_map,
)


# ============================================================
# LAZY LOAD APPROVED MODEL ARTIFACTS
# ============================================================

@lru_cache(maxsize=1)
def get_model_pipeline():
    """
    Load the approved model only when inference is requested.

    This keeps application imports artifact-independent while
    ensuring the real serving path still uses the approved model.
    """
    return joblib.load(
        MODEL_ARTIFACT_PATH
    )


@lru_cache(maxsize=1)
def get_business_explanation_map():
    """
    Load and cache the approved customer-safe explanation map.
    """
    return load_business_explanation_map(
        EXPLAINABILITY_MAP_PATH
    )


# ============================================================
# PRODUCTION INFERENCE
# ============================================================

def predict_workflow(
    request: PredictionRequest,
) -> dict:
    """
    Run one validated workflow through the approved
    Logistic Regression v1 serving pipeline.
    """

    model_pipeline = get_model_pipeline()
    business_map = get_business_explanation_map()

    request_data = request.model_dump()

    workflow_row = pd.DataFrame(
        [request_data],
        columns=MODEL_FEATURES,
    )

    # Defensive serving contract check
    if list(workflow_row.columns) != MODEL_FEATURES:
        raise ValueError(
            "Prediction feature order does not match "
            "the approved model feature contract."
        )

    explanation_result = explain_workflow(
        workflow_row=workflow_row,
        pipeline=model_pipeline,
        business_map=business_map,
        threshold=FINAL_THRESHOLD,
        top_n=5,
    )

    response_payload = {
        "model_version":
            MODEL_VERSION,

        "predicted_operational_risk":
            explanation_result[
                "predicted_operational_risk"
            ],

        "threshold":
            explanation_result[
                "threshold"
            ],

        "model_decision":
            explanation_result[
                "model_decision"
            ],

        "explanation": {
            "top_factors":
                explanation_result[
                    "explanation"
                ]["top_factors"],

            "method":
                explanation_result[
                    "explanation"
                ]["method"],
        },

        "disclaimers":
            explanation_result[
                "disclaimers"
            ],
    }

    validated_response = (
        PredictionResponse(
            **response_payload
        )
    )

    return validated_response.model_dump()
